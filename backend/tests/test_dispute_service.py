"""
Tests for dispute resolution functionality.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from sqlmodel import Session, select

from app.models import (
    Order, OrderItem, OrderStatus, PaymentStatus,
    Product, User, UserRole, Farmer, ProductStatus,
    Dispute, DisputeMessage, DisputeStatus, DisputeType
)
from app.services.dispute_service import DisputeService
from app.database import engine


@pytest.fixture
def dispute_service():
    """Create dispute service instance."""
    return DisputeService()


@pytest.fixture
def sample_buyer():
    """Create a sample buyer."""
    with Session(engine) as session:
        user = User(
            name="Test Buyer",
            email="buyer@test.com",
            role=UserRole.BUYER
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@pytest.fixture
def sample_farmer_user():
    """Create a sample farmer user."""
    with Session(engine) as session:
        user = User(
            name="Test Farmer",
            email="farmer@test.com",
            role=UserRole.FARMER
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@pytest.fixture
def sample_admin():
    """Create a sample admin user."""
    with Session(engine) as session:
        user = User(
            name="Test Admin",
            email="admin@test.com",
            role=UserRole.ADMIN
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@pytest.fixture
def sample_farmer(sample_farmer_user):
    """Create a sample farmer."""
    with Session(engine) as session:
        farmer = Farmer(
            name="Test Farmer",
            email="farmer@test.com",
            phone="1234567890"
        )
        session.add(farmer)
        session.commit()
        session.refresh(farmer)
        return farmer


@pytest.fixture
def sample_product(sample_farmer):
    """Create a sample product."""
    with Session(engine) as session:
        product = Product(
            name="Test Product",
            description="A test product",
            price=Decimal("10.00"),
            quantity_available=100,
            farmer_id=sample_farmer.id,
            status=ProductStatus.ACTIVE
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        return product


@pytest.fixture
def sample_order_with_items(sample_buyer, sample_product, sample_farmer_user):
    """Create a sample order with items."""
    with Session(engine) as session:
        order = Order(
            buyer_id=sample_buyer.id,
            status=OrderStatus.DELIVERED,
            subtotal=Decimal("20.00"),
            platform_fee=Decimal("1.60"),
            total=Decimal("21.60"),
            payment_status=PaymentStatus.PAID,
            shipping_address={"street": "123 Test St"}
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=sample_product.id,
            quantity=Decimal("2"),
            unit_price=Decimal("10.00"),
            farmer_id=sample_farmer_user.id,
            fulfillment_status="delivered"
        )
        session.add(order_item)
        session.commit()
        
        return {"order_id": order.id, "order_item_id": order_item.id}


class TestDisputeService:
    """Test cases for dispute service."""
    
    def test_create_dispute_by_buyer(self, dispute_service, sample_order_with_items, sample_buyer):
        """Test creating a dispute by the buyer."""
        
        order_data = sample_order_with_items
        
        result = dispute_service.create_dispute(
            order_id=order_data["order_id"],
            filed_by=sample_buyer.id,
            dispute_type=DisputeType.ITEM_NOT_AS_DESCRIBED,
            subject="Product not as described",
            description="The product I received was different from what was advertised.",
            evidence_urls=["https://example.com/photo1.jpg"]
        )
        
        assert result["order_id"] == order_data["order_id"]
        assert result["dispute_type"] == DisputeType.ITEM_NOT_AS_DESCRIBED
        assert result["status"] == DisputeStatus.OPEN
        assert result["subject"] == "Product not as described"
        assert result["priority"] >= 1
        
        # Verify in database
        with Session(engine) as session:
            dispute = session.exec(
                select(Dispute).where(Dispute.order_id == order_data["order_id"])
            ).first()
            
            assert dispute is not None
            assert dispute.filed_by == sample_buyer.id
            assert dispute.dispute_type == DisputeType.ITEM_NOT_AS_DESCRIBED
            assert dispute.status == DisputeStatus.OPEN
    
    def test_create_dispute_by_farmer(self, dispute_service, sample_order_with_items, sample_farmer_user):
        """Test creating a dispute by the farmer."""
        
        order_data = sample_order_with_items
        
        result = dispute_service.create_dispute(
            order_id=order_data["order_id"],
            filed_by=sample_farmer_user.id,
            dispute_type=DisputeType.REFUND_REQUEST,
            subject="Buyer requesting unreasonable refund",
            description="Buyer is requesting refund without valid reason."
        )
        
        assert result["order_id"] == order_data["order_id"]
        assert result["dispute_type"] == DisputeType.REFUND_REQUEST
        assert result["status"] == DisputeStatus.OPEN
    
    def test_create_dispute_access_denied(self, dispute_service, sample_order_with_items):
        """Test access denied when user doesn't have access to order."""
        
        # Create another user
        with Session(engine) as session:
            other_user = User(
                name="Other User",
                email="other@test.com",
                role=UserRole.BUYER
            )
            session.add(other_user)
            session.commit()
            session.refresh(other_user)
        
        order_data = sample_order_with_items
        
        with pytest.raises(Exception) as exc_info:
            dispute_service.create_dispute(
                order_id=order_data["order_id"],
                filed_by=other_user.id,
                dispute_type=DisputeType.OTHER,
                subject="Test dispute",
                description="Test description"
            )
        
        assert "Access denied" in str(exc_info.value)
    
    def test_create_duplicate_dispute(self, dispute_service, sample_order_with_items, sample_buyer):
        """Test that duplicate disputes are not allowed."""
        
        order_data = sample_order_with_items
        
        # Create first dispute
        dispute_service.create_dispute(
            order_id=order_data["order_id"],
            filed_by=sample_buyer.id,
            dispute_type=DisputeType.QUALITY_ISSUE,
            subject="First dispute",
            description="First dispute description"
        )
        
        # Try to create second dispute
        with pytest.raises(Exception) as exc_info:
            dispute_service.create_dispute(
                order_id=order_data["order_id"],
                filed_by=sample_buyer.id,
                dispute_type=DisputeType.OTHER,
                subject="Second dispute",
                description="Second dispute description"
            )
        
        assert "active dispute already exists" in str(exc_info.value)
    
    def test_add_dispute_message(self, dispute_service, sample_order_with_items, sample_buyer):
        """Test adding a message to a dispute."""
        
        order_data = sample_order_with_items
        
        # Create dispute
        dispute_result = dispute_service.create_dispute(
            order_id=order_data["order_id"],
            filed_by=sample_buyer.id,
            dispute_type=DisputeType.DAMAGED_ITEM,
            subject="Damaged item",
            description="Item arrived damaged"
        )
        
        # Add message
        message_result = dispute_service.add_dispute_message(
            dispute_id=dispute_result["id"],
            sender_id=sample_buyer.id,
            message="Here are additional photos of the damage",
            attachments=["https://example.com/damage1.jpg", "https://example.com/damage2.jpg"]
        )
        
        assert message_result["dispute_id"] == dispute_result["id"]
        assert "Message added successfully" in message_result["message"]
        
        # Verify in database
        with Session(engine) as session:
            message = session.exec(
                select(DisputeMessage).where(DisputeMessage.dispute_id == dispute_result["id"])
            ).first()
            
            assert message is not None
            assert message.sender_id == sample_buyer.id
            assert message.message == "Here are additional photos of the damage"
            assert len(message.attachments) == 2
            
            # Check that dispute status was updated to IN_REVIEW
            dispute = session.get(Dispute, dispute_result["id"])
            assert dispute.status == DisputeStatus.IN_REVIEW
    
    def test_update_dispute_status_admin(self, dispute_service, sample_order_with_items, sample_buyer, sample_admin):
        """Test updating dispute status by admin."""
        
        order_data = sample_order_with_items
        
        # Create dispute
        dispute_result = dispute_service.create_dispute(
            order_id=order_data["order_id"],
            filed_by=sample_buyer.id,
            dispute_type=DisputeType.WRONG_ITEM,
            subject="Wrong item received",
            description="Received different product"
        )
        
        # Update status as admin
        update_result = dispute_service.update_dispute_status(
            dispute_id=dispute_result["id"],
            new_status=DisputeStatus.RESOLVED,
            admin_id=sample_admin.id,
            resolution="Refund processed for the buyer"
        )
        
        assert update_result["old_status"] == DisputeStatus.OPEN
        assert update_result["new_status"] == DisputeStatus.RESOLVED
        assert update_result["resolution"] == "Refund processed for the buyer"
        
        # Verify in database
        with Session(engine) as session:
            dispute = session.get(Dispute, dispute_result["id"])
            assert dispute.status == DisputeStatus.RESOLVED
            assert dispute.resolution == "Refund processed for the buyer"
            assert dispute.resolved_by == sample_admin.id
            assert dispute.resolved_at is not None
    
    def test_update_dispute_status_non_admin(self, dispute_service, sample_order_with_items, sample_buyer):
        """Test that non-admin users cannot update dispute status."""
        
        order_data = sample_order_with_items
        
        # Create dispute
        dispute_result = dispute_service.create_dispute(
            order_id=order_data["order_id"],
            filed_by=sample_buyer.id,
            dispute_type=DisputeType.OTHER,
            subject="Test dispute",
            description="Test description"
        )
        
        # Try to update status as non-admin
        with pytest.raises(Exception) as exc_info:
            dispute_service.update_dispute_status(
                dispute_id=dispute_result["id"],
                new_status=DisputeStatus.RESOLVED,
                admin_id=sample_buyer.id
            )
        
        assert "Admin access required" in str(exc_info.value)
    
    def test_get_dispute_details(self, dispute_service, sample_order_with_items, sample_buyer):
        """Test getting detailed dispute information."""
        
        order_data = sample_order_with_items
        
        # Create dispute
        dispute_result = dispute_service.create_dispute(
            order_id=order_data["order_id"],
            filed_by=sample_buyer.id,
            dispute_type=DisputeType.ORDER_NOT_RECEIVED,
            subject="Order not received",
            description="I haven't received my order after 2 weeks"
        )
        
        # Add a message
        dispute_service.add_dispute_message(
            dispute_id=dispute_result["id"],
            sender_id=sample_buyer.id,
            message="Still waiting for the order"
        )
        
        # Get details
        details = dispute_service.get_dispute_details(
            dispute_id=dispute_result["id"],
            user_id=sample_buyer.id
        )
        
        assert details["id"] == dispute_result["id"]
        assert details["order_id"] == order_data["order_id"]
        assert details["dispute_type"] == DisputeType.ORDER_NOT_RECEIVED
        assert details["subject"] == "Order not received"
        assert details["filed_by"]["id"] == sample_buyer.id
        assert details["filed_by"]["name"] == sample_buyer.name
        assert len(details["messages"]) == 1
        assert details["messages"][0]["message"] == "Still waiting for the order"
        assert details["order_info"]["id"] == order_data["order_id"]
    
    def test_get_user_disputes(self, dispute_service, sample_order_with_items, sample_buyer):
        """Test getting disputes for a user."""
        
        order_data = sample_order_with_items
        
        # Create multiple disputes
        dispute1 = dispute_service.create_dispute(
            order_id=order_data["order_id"],
            filed_by=sample_buyer.id,
            dispute_type=DisputeType.QUALITY_ISSUE,
            subject="Quality issue 1",
            description="First quality issue"
        )
        
        # Create another order and dispute
        with Session(engine) as session:
            order2 = Order(
                buyer_id=sample_buyer.id,
                status=OrderStatus.DELIVERED,
                subtotal=Decimal("15.00"),
                platform_fee=Decimal("1.20"),
                total=Decimal("16.20"),
                payment_status=PaymentStatus.PAID,
                shipping_address={"street": "456 Test Ave"}
            )
            session.add(order2)
            session.commit()
            session.refresh(order2)
            
            order2_id = order2.id
        
        dispute2 = dispute_service.create_dispute(
            order_id=order2_id,
            filed_by=sample_buyer.id,
            dispute_type=DisputeType.DAMAGED_ITEM,
            subject="Damaged item",
            description="Item was damaged"
        )
        
        # Get user disputes
        user_disputes = dispute_service.get_user_disputes(
            user_id=sample_buyer.id,
            limit=10
        )
        
        assert user_disputes["total_count"] == 2
        assert len(user_disputes["disputes"]) == 2
        
        # Check ordering (newest first)
        assert user_disputes["disputes"][0]["id"] == dispute2["id"]
        assert user_disputes["disputes"][1]["id"] == dispute1["id"]
        
        # Test status filter
        filtered_disputes = dispute_service.get_user_disputes(
            user_id=sample_buyer.id,
            status_filter=[DisputeStatus.OPEN]
        )
        
        assert filtered_disputes["total_count"] == 2  # Both are open
    
    def test_get_admin_disputes(self, dispute_service, sample_order_with_items, sample_buyer, sample_admin):
        """Test getting all disputes for admin."""
        
        order_data = sample_order_with_items
        
        # Create dispute
        dispute_service.create_dispute(
            order_id=order_data["order_id"],
            filed_by=sample_buyer.id,
            dispute_type=DisputeType.ORDER_NOT_RECEIVED,
            subject="Order not received",
            description="Order missing"
        )
        
        # Get admin disputes
        admin_disputes = dispute_service.get_admin_disputes(
            admin_id=sample_admin.id,
            limit=10
        )
        
        assert admin_disputes["total_count"] == 1
        assert len(admin_disputes["disputes"]) == 1
        
        dispute = admin_disputes["disputes"][0]
        assert dispute["dispute_type"] == DisputeType.ORDER_NOT_RECEIVED
        assert dispute["filed_by"]["id"] == sample_buyer.id
        assert dispute["message_count"] == 0
        assert dispute["days_open"] >= 0
    
    def test_get_admin_disputes_non_admin(self, dispute_service, sample_buyer):
        """Test that non-admin users cannot access admin disputes."""
        
        with pytest.raises(Exception) as exc_info:
            dispute_service.get_admin_disputes(
                admin_id=sample_buyer.id,
                limit=10
            )
        
        assert "Admin access required" in str(exc_info.value)
    
    def test_auto_escalate_disputes(self, dispute_service, sample_order_with_items, sample_buyer):
        """Test automatic dispute escalation."""
        
        order_data = sample_order_with_items
        
        # Create dispute
        dispute_result = dispute_service.create_dispute(
            order_id=order_data["order_id"],
            filed_by=sample_buyer.id,
            dispute_type=DisputeType.OTHER,
            subject="Old dispute",
            description="This is an old dispute"
        )
        
        # Manually set creation date to 4 days ago
        with Session(engine) as session:
            dispute = session.get(Dispute, dispute_result["id"])
            dispute.created_at = datetime.utcnow() - timedelta(days=4)
            session.add(dispute)
            session.commit()
        
        # Run auto-escalation
        escalation_result = dispute_service.auto_escalate_disputes()
        
        assert escalation_result["escalated_count"] == 1
        
        # Verify dispute was escalated
        with Session(engine) as session:
            dispute = session.get(Dispute, dispute_result["id"])
            assert dispute.status == DisputeStatus.ESCALATED
            assert dispute.escalated_at is not None
            assert dispute.priority > 1  # Priority should be increased
    
    def test_dispute_priority_calculation(self, dispute_service, sample_order_with_items, sample_buyer):
        """Test dispute priority calculation based on type and order value."""
        
        order_data = sample_order_with_items
        
        # Create high-priority dispute type
        high_priority_dispute = dispute_service.create_dispute(
            order_id=order_data["order_id"],
            filed_by=sample_buyer.id,
            dispute_type=DisputeType.ORDER_NOT_RECEIVED,
            subject="Order not received",
            description="High priority issue"
        )
        
        # Verify high priority was assigned
        with Session(engine) as session:
            dispute = session.get(Dispute, high_priority_dispute["id"])
            assert dispute.priority >= 4  # ORDER_NOT_RECEIVED should have high priority
    
    def test_internal_admin_messages(self, dispute_service, sample_order_with_items, sample_buyer, sample_admin):
        """Test internal admin messages that are not visible to users."""
        
        order_data = sample_order_with_items
        
        # Create dispute
        dispute_result = dispute_service.create_dispute(
            order_id=order_data["order_id"],
            filed_by=sample_buyer.id,
            dispute_type=DisputeType.OTHER,
            subject="Test dispute",
            description="Test description"
        )
        
        # Add internal admin message
        dispute_service.add_dispute_message(
            dispute_id=dispute_result["id"],
            sender_id=sample_admin.id,
            message="Internal admin note - investigating this case",
            is_internal=True
        )
        
        # Add regular message
        dispute_service.add_dispute_message(
            dispute_id=dispute_result["id"],
            sender_id=sample_admin.id,
            message="We are looking into your case",
            is_internal=False
        )
        
        # Get details as buyer (should not see internal message)
        buyer_details = dispute_service.get_dispute_details(
            dispute_id=dispute_result["id"],
            user_id=sample_buyer.id
        )
        
        assert len(buyer_details["messages"]) == 1
        assert buyer_details["messages"][0]["message"] == "We are looking into your case"
        
        # Get details as admin (should see both messages)
        admin_details = dispute_service.get_dispute_details(
            dispute_id=dispute_result["id"],
            user_id=sample_admin.id
        )
        
        assert len(admin_details["messages"]) == 2