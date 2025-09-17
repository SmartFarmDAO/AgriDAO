"""
Tests for order service functionality.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from sqlmodel import Session, select

from app.models import (
    Order, OrderItem, OrderStatus, PaymentStatus, OrderStatusHistory,
    Product, User, UserRole, Farmer, ProductStatus
)
from app.services.order_service import OrderService
from app.database import engine


@pytest.fixture
def order_service():
    """Create order service instance."""
    return OrderService()


@pytest.fixture
def sample_user():
    """Create a sample user."""
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
def sample_farmer():
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


class TestOrderService:
    """Test cases for OrderService."""
    
    def test_create_order_success(self, order_service, sample_user, sample_product):
        """Test successful order creation."""
        
        items = [
            {
                "product_id": sample_product.id,
                "quantity": 2,
                "unit_price": 10.00
            }
        ]
        
        shipping_address = {
            "street": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345"
        }
        
        order = order_service.create_order(
            buyer_id=sample_user.id,
            items=items,
            shipping_address=shipping_address,
            subtotal=Decimal("20.00"),
            platform_fee=Decimal("1.60"),
            shipping_fee=Decimal("5.00"),
            tax_amount=Decimal("2.00")
        )
        
        assert order.id is not None
        assert order.buyer_id == sample_user.id
        assert order.status == OrderStatus.PENDING
        assert order.payment_status == PaymentStatus.UNPAID
        assert order.subtotal == Decimal("20.00")
        assert order.platform_fee == Decimal("1.60")
        assert order.shipping_fee == Decimal("5.00")
        assert order.tax_amount == Decimal("2.00")
        assert order.total == Decimal("28.60")
        assert order.shipping_address == shipping_address
        
        # Check order items were created
        with Session(engine) as session:
            order_items = session.exec(
                select(OrderItem).where(OrderItem.order_id == order.id)
            ).all()
            assert len(order_items) == 1
            assert order_items[0].product_id == sample_product.id
            assert order_items[0].quantity == Decimal("2")
            assert order_items[0].unit_price == Decimal("10.00")
            
            # Check status history was created
            history = session.exec(
                select(OrderStatusHistory).where(OrderStatusHistory.order_id == order.id)
            ).all()
            assert len(history) == 1
            assert history[0].status == OrderStatus.PENDING
            assert history[0].previous_status is None
            assert history[0].notes == "Order created"
    
    def test_create_order_invalid_product(self, order_service, sample_user):
        """Test order creation with invalid product."""
        
        items = [
            {
                "product_id": 99999,  # Non-existent product
                "quantity": 1,
                "unit_price": 10.00
            }
        ]
        
        shipping_address = {"street": "123 Test St"}
        
        with pytest.raises(Exception) as exc_info:
            order_service.create_order(
                buyer_id=sample_user.id,
                items=items,
                shipping_address=shipping_address,
                subtotal=Decimal("10.00"),
                platform_fee=Decimal("0.80")
            )
        
        assert "not found" in str(exc_info.value)
    
    def test_update_order_status_success(self, order_service, sample_user, sample_product):
        """Test successful order status update."""
        
        # Create order first
        items = [{"product_id": sample_product.id, "quantity": 1, "unit_price": 10.00}]
        order = order_service.create_order(
            buyer_id=sample_user.id,
            items=items,
            shipping_address={"street": "123 Test St"},
            subtotal=Decimal("10.00"),
            platform_fee=Decimal("0.80")
        )
        
        # Update status
        updated_order = order_service.update_order_status(
            order_id=order.id,
            new_status=OrderStatus.CONFIRMED,
            user_id=sample_user.id,
            notes="Payment received"
        )
        
        assert updated_order.status == OrderStatus.CONFIRMED
        
        # Check status history
        with Session(engine) as session:
            history = session.exec(
                select(OrderStatusHistory)
                .where(OrderStatusHistory.order_id == order.id)
                .order_by(OrderStatusHistory.created_at.desc())
            ).all()
            
            assert len(history) == 2  # Initial + update
            assert history[0].status == OrderStatus.CONFIRMED
            assert history[0].previous_status == OrderStatus.PENDING
            assert history[0].notes == "Payment received"
    
    def test_update_order_status_invalid_transition(self, order_service, sample_user, sample_product):
        """Test invalid status transition."""
        
        # Create order
        items = [{"product_id": sample_product.id, "quantity": 1, "unit_price": 10.00}]
        order = order_service.create_order(
            buyer_id=sample_user.id,
            items=items,
            shipping_address={"street": "123 Test St"},
            subtotal=Decimal("10.00"),
            platform_fee=Decimal("0.80")
        )
        
        # Try invalid transition (pending -> delivered)
        with pytest.raises(Exception) as exc_info:
            order_service.update_order_status(
                order_id=order.id,
                new_status=OrderStatus.DELIVERED,
                user_id=sample_user.id
            )
        
        assert "Invalid status transition" in str(exc_info.value)
    
    def test_update_payment_status_auto_confirm(self, order_service, sample_user, sample_product):
        """Test automatic order confirmation when payment is received."""
        
        # Create order
        items = [{"product_id": sample_product.id, "quantity": 1, "unit_price": 10.00}]
        order = order_service.create_order(
            buyer_id=sample_user.id,
            items=items,
            shipping_address={"street": "123 Test St"},
            subtotal=Decimal("10.00"),
            platform_fee=Decimal("0.80")
        )
        
        # Update payment status to paid
        updated_order = order_service.update_payment_status(
            order_id=order.id,
            payment_status=PaymentStatus.PAID,
            payment_intent_id="pi_test123"
        )
        
        assert updated_order.payment_status == PaymentStatus.PAID
        assert updated_order.status == OrderStatus.CONFIRMED
        assert updated_order.stripe_payment_intent_id == "pi_test123"
        
        # Check status history includes auto-confirmation
        with Session(engine) as session:
            history = session.exec(
                select(OrderStatusHistory)
                .where(OrderStatusHistory.order_id == order.id)
                .order_by(OrderStatusHistory.created_at.desc())
            ).all()
            
            assert len(history) == 2
            assert history[0].status == OrderStatus.CONFIRMED
            assert "Payment confirmed" in history[0].notes
    
    def test_get_order_with_details(self, order_service, sample_user, sample_product):
        """Test getting order with full details."""
        
        # Create order
        items = [{"product_id": sample_product.id, "quantity": 2, "unit_price": 10.00}]
        shipping_address = {"street": "123 Test St", "city": "Test City"}
        
        order = order_service.create_order(
            buyer_id=sample_user.id,
            items=items,
            shipping_address=shipping_address,
            subtotal=Decimal("20.00"),
            platform_fee=Decimal("1.60")
        )
        
        # Get order details
        details = order_service.get_order_with_details(order.id, sample_user.id)
        
        assert details["id"] == order.id
        assert details["status"] == OrderStatus.PENDING
        assert details["subtotal"] == 20.00
        assert details["platform_fee"] == 1.60
        assert details["shipping_address"] == shipping_address
        
        # Check items
        assert len(details["items"]) == 1
        item = details["items"][0]
        assert item["product_id"] == sample_product.id
        assert item["product_name"] == sample_product.name
        assert item["quantity"] == 2.0
        assert item["unit_price"] == 10.00
        
        # Check status history
        assert len(details["status_history"]) == 1
        history = details["status_history"][0]
        assert history["status"] == OrderStatus.PENDING
        assert history["notes"] == "Order created"
    
    def test_get_order_access_denied(self, order_service, sample_user, sample_product):
        """Test access denied for unauthorized user."""
        
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
        
        # Create order for first user
        items = [{"product_id": sample_product.id, "quantity": 1, "unit_price": 10.00}]
        order = order_service.create_order(
            buyer_id=sample_user.id,
            items=items,
            shipping_address={"street": "123 Test St"},
            subtotal=Decimal("10.00"),
            platform_fee=Decimal("0.80")
        )
        
        # Try to access with other user
        with pytest.raises(Exception) as exc_info:
            order_service.get_order_with_details(order.id, other_user.id)
        
        assert "Access denied" in str(exc_info.value)
    
    def test_get_user_orders(self, order_service, sample_user, sample_product):
        """Test getting user's orders."""
        
        # Create multiple orders
        items = [{"product_id": sample_product.id, "quantity": 1, "unit_price": 10.00}]
        
        order1 = order_service.create_order(
            buyer_id=sample_user.id,
            items=items,
            shipping_address={"street": "123 Test St"},
            subtotal=Decimal("10.00"),
            platform_fee=Decimal("0.80")
        )
        
        order2 = order_service.create_order(
            buyer_id=sample_user.id,
            items=items,
            shipping_address={"street": "456 Test Ave"},
            subtotal=Decimal("10.00"),
            platform_fee=Decimal("0.80")
        )
        
        # Get orders
        orders = order_service.get_user_orders(sample_user.id)
        
        assert len(orders) == 2
        # Should be ordered by created_at desc
        assert orders[0]["id"] == order2.id
        assert orders[1]["id"] == order1.id
        
        # Test with status filter
        filtered_orders = order_service.get_user_orders(
            sample_user.id,
            status_filter=[OrderStatus.PENDING]
        )
        assert len(filtered_orders) == 2
        
        # Test with limit
        limited_orders = order_service.get_user_orders(sample_user.id, limit=1)
        assert len(limited_orders) == 1
    
    def test_update_tracking_number(self, order_service, sample_user, sample_product):
        """Test updating tracking number."""
        
        # Create and confirm order
        items = [{"product_id": sample_product.id, "quantity": 1, "unit_price": 10.00}]
        order = order_service.create_order(
            buyer_id=sample_user.id,
            items=items,
            shipping_address={"street": "123 Test St"},
            subtotal=Decimal("10.00"),
            platform_fee=Decimal("0.80")
        )
        
        order_service.update_order_status(
            order_id=order.id,
            new_status=OrderStatus.CONFIRMED,
            user_id=sample_user.id
        )
        
        # Update tracking number
        delivery_date = datetime.utcnow() + timedelta(days=3)
        updated_order = order_service.update_tracking_number(
            order_id=order.id,
            tracking_number="TRACK123",
            user_id=sample_user.id,
            estimated_delivery_date=delivery_date
        )
        
        assert updated_order.tracking_number == "TRACK123"
        assert updated_order.estimated_delivery_date == delivery_date
        assert updated_order.status == OrderStatus.SHIPPED
    
    def test_cancel_order(self, order_service, sample_user, sample_product):
        """Test order cancellation."""
        
        # Create order
        items = [{"product_id": sample_product.id, "quantity": 1, "unit_price": 10.00}]
        order = order_service.create_order(
            buyer_id=sample_user.id,
            items=items,
            shipping_address={"street": "123 Test St"},
            subtotal=Decimal("10.00"),
            platform_fee=Decimal("0.80")
        )
        
        # Cancel order
        cancelled_order = order_service.cancel_order(
            order_id=order.id,
            user_id=sample_user.id,
            reason="Customer requested cancellation",
            refund_amount=Decimal("10.80")
        )
        
        assert cancelled_order.status == OrderStatus.CANCELLED
        assert cancelled_order.cancelled_at is not None
        assert cancelled_order.cancellation_reason == "Customer requested cancellation"
        
        # Check status history
        with Session(engine) as session:
            history = session.exec(
                select(OrderStatusHistory)
                .where(OrderStatusHistory.order_id == order.id)
                .order_by(OrderStatusHistory.created_at.desc())
            ).first()
            
            assert history.status == OrderStatus.CANCELLED
            assert "Customer requested cancellation" in history.notes
            assert history.status_metadata["refund_amount"] == 10.80
    
    def test_cancel_delivered_order_fails(self, order_service, sample_user, sample_product):
        """Test that delivered orders cannot be cancelled."""
        
        # Create and deliver order
        items = [{"product_id": sample_product.id, "quantity": 1, "unit_price": 10.00}]
        order = order_service.create_order(
            buyer_id=sample_user.id,
            items=items,
            shipping_address={"street": "123 Test St"},
            subtotal=Decimal("10.00"),
            platform_fee=Decimal("0.80")
        )
        
        # Manually set to delivered
        with Session(engine) as session:
            order_obj = session.get(Order, order.id)
            order_obj.status = OrderStatus.DELIVERED
            session.add(order_obj)
            session.commit()
        
        # Try to cancel
        with pytest.raises(Exception) as exc_info:
            order_service.cancel_order(
                order_id=order.id,
                user_id=sample_user.id,
                reason="Test cancellation"
            )
        
        assert "Cannot cancel order" in str(exc_info.value)
    
    def test_status_transition_validation(self, order_service):
        """Test status transition validation logic."""
        
        # Test valid transitions
        assert order_service._is_valid_status_transition(
            OrderStatus.PENDING, OrderStatus.CONFIRMED
        )
        assert order_service._is_valid_status_transition(
            OrderStatus.CONFIRMED, OrderStatus.PROCESSING
        )
        assert order_service._is_valid_status_transition(
            OrderStatus.PROCESSING, OrderStatus.SHIPPED
        )
        assert order_service._is_valid_status_transition(
            OrderStatus.SHIPPED, OrderStatus.DELIVERED
        )
        
        # Test invalid transitions
        assert not order_service._is_valid_status_transition(
            OrderStatus.PENDING, OrderStatus.DELIVERED
        )
        assert not order_service._is_valid_status_transition(
            OrderStatus.DELIVERED, OrderStatus.PENDING
        )
        assert not order_service._is_valid_status_transition(
            OrderStatus.CANCELLED, OrderStatus.CONFIRMED
        )
    
    @patch('app.services.order_service.NotificationService')
    def test_status_update_notifications(self, mock_notification_service, order_service, sample_user, sample_product):
        """Test that status updates trigger notifications."""
        
        # Create order
        items = [{"product_id": sample_product.id, "quantity": 1, "unit_price": 10.00}]
        order = order_service.create_order(
            buyer_id=sample_user.id,
            items=items,
            shipping_address={"street": "123 Test St"},
            subtotal=Decimal("10.00"),
            platform_fee=Decimal("0.80")
        )
        
        # Update status
        order_service.update_order_status(
            order_id=order.id,
            new_status=OrderStatus.CONFIRMED,
            user_id=sample_user.id
        )
        
        # Verify notification was called
        mock_notification_service.return_value.send_order_status_update.assert_called_once()
        call_args = mock_notification_service.return_value.send_order_status_update.call_args
        
        assert call_args[1]["order_id"] == order.id
        assert call_args[1]["new_status"] == "confirmed"