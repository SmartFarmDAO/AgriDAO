"""
Tests for buyer order tracking functionality.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from sqlmodel import Session, select

from app.models import (
    Order, OrderItem, OrderStatus, PaymentStatus, OrderStatusHistory,
    Product, User, UserRole, Farmer, ProductStatus, OrderReview
)
from app.services.order_service import OrderService
from app.database import engine


@pytest.fixture
def order_service():
    """Create order service instance."""
    return OrderService()


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


@pytest.fixture
def sample_delivered_order(sample_buyer, sample_product, sample_farmer):
    """Create a sample delivered order."""
    with Session(engine) as session:
        order = Order(
            buyer_id=sample_buyer.id,
            status=OrderStatus.DELIVERED,
            subtotal=Decimal("20.00"),
            platform_fee=Decimal("1.60"),
            total=Decimal("21.60"),
            payment_status=PaymentStatus.PAID,
            shipping_address={"street": "123 Test St", "city": "Test City"},
            tracking_number="TRACK123",
            delivered_at=datetime.utcnow()
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=sample_product.id,
            quantity=Decimal("2"),
            unit_price=Decimal("10.00"),
            farmer_id=sample_farmer.id,
            fulfillment_status="delivered"
        )
        session.add(order_item)
        session.commit()
        
        return {"order_id": order.id, "order_item_id": order_item.id}


class TestBuyerOrderTracking:
    """Test cases for buyer order tracking."""
    
    def test_get_order_tracking_info(self, order_service, sample_buyer, sample_product):
        """Test getting order tracking information."""
        
        # Create order with tracking
        order_id = None
        with Session(engine) as session:
            order = Order(
                buyer_id=sample_buyer.id,
                status=OrderStatus.SHIPPED,
                subtotal=Decimal("10.00"),
                platform_fee=Decimal("0.80"),
                total=Decimal("10.80"),
                payment_status=PaymentStatus.PAID,
                shipping_address={"street": "123 Test St"},
                tracking_number="TRACK123",
                estimated_delivery_date=datetime.utcnow() + timedelta(days=2)
            )
            session.add(order)
            session.commit()
            session.refresh(order)
            order_id = order.id
            
            # Add status history
            history = OrderStatusHistory(
                order_id=order_id,
                status=OrderStatus.SHIPPED,
                previous_status=OrderStatus.CONFIRMED,
                notes="Order shipped via UPS"
            )
            session.add(history)
            session.commit()
        
        tracking_info = order_service.get_order_tracking_info(order_id, sample_buyer.id)
        
        assert tracking_info["order_id"] == order_id
        assert tracking_info["current_status"] == OrderStatus.SHIPPED
        assert tracking_info["tracking_number"] == "TRACK123"
        assert tracking_info["estimated_delivery_date"] is not None
        assert len(tracking_info["tracking_timeline"]) >= 1
        assert tracking_info["can_cancel"] == False  # Shipped orders can't be cancelled
        assert tracking_info["can_modify"] == False  # Shipped orders can't be modified
    
    def test_get_order_tracking_access_denied(self, order_service, sample_buyer, sample_product):
        """Test access denied for tracking info."""
        
        # Create another buyer
        with Session(engine) as session:
            other_buyer = User(
                name="Other Buyer",
                email="other@test.com",
                role=UserRole.BUYER
            )
            session.add(other_buyer)
            session.commit()
            session.refresh(other_buyer)
            
            # Create order for first buyer
            order = Order(
                buyer_id=sample_buyer.id,
                status=OrderStatus.SHIPPED,
                subtotal=Decimal("10.00"),
                platform_fee=Decimal("0.80"),
                total=Decimal("10.80"),
                payment_status=PaymentStatus.PAID,
                shipping_address={"street": "123 Test St"}
            )
            session.add(order)
            session.commit()
            session.refresh(order)
        
        # Try to access with other buyer
        with pytest.raises(Exception) as exc_info:
            order_service.get_order_tracking_info(order.id, other_buyer.id)
        
        assert "Access denied" in str(exc_info.value)
    
    def test_modify_order_shipping_address(self, order_service, sample_buyer, sample_product):
        """Test modifying shipping address for pending order."""
        
        # Create pending order
        with Session(engine) as session:
            order = Order(
                buyer_id=sample_buyer.id,
                status=OrderStatus.PENDING,
                subtotal=Decimal("10.00"),
                platform_fee=Decimal("0.80"),
                total=Decimal("10.80"),
                payment_status=PaymentStatus.UNPAID,
                shipping_address={"street": "123 Old St", "city": "Old City"}
            )
            session.add(order)
            session.commit()
            session.refresh(order)
        
        new_address = {
            "street": "456 New Ave",
            "city": "New City",
            "state": "NY",
            "zip_code": "12345"
        }
        
        result = order_service.modify_order_shipping_address(
            order_id=order.id,
            user_id=sample_buyer.id,
            new_address=new_address
        )
        
        assert result["order_id"] == order.id
        assert result["updated_address"] == new_address
        
        # Verify in database
        with Session(engine) as session:
            updated_order = session.get(Order, order.id)
            assert updated_order.shipping_address == new_address
    
    def test_modify_shipping_address_not_allowed(self, order_service, sample_buyer, sample_product):
        """Test that shipping address cannot be modified for non-pending orders."""
        
        # Create confirmed order
        with Session(engine) as session:
            order = Order(
                buyer_id=sample_buyer.id,
                status=OrderStatus.CONFIRMED,
                subtotal=Decimal("10.00"),
                platform_fee=Decimal("0.80"),
                total=Decimal("10.80"),
                payment_status=PaymentStatus.PAID,
                shipping_address={"street": "123 Test St"}
            )
            session.add(order)
            session.commit()
            session.refresh(order)
        
        new_address = {"street": "456 New Ave"}
        
        with pytest.raises(Exception) as exc_info:
            order_service.modify_order_shipping_address(
                order_id=order.id,
                user_id=sample_buyer.id,
                new_address=new_address
            )
        
        assert "Cannot modify order" in str(exc_info.value)
    
    def test_request_order_cancellation_pending(self, order_service, sample_buyer, sample_product):
        """Test requesting cancellation for pending order (immediate cancellation)."""
        
        # Create pending order
        with Session(engine) as session:
            order = Order(
                buyer_id=sample_buyer.id,
                status=OrderStatus.PENDING,
                subtotal=Decimal("10.00"),
                platform_fee=Decimal("0.80"),
                total=Decimal("10.80"),
                payment_status=PaymentStatus.UNPAID,
                shipping_address={"street": "123 Test St"}
            )
            session.add(order)
            session.commit()
            session.refresh(order)
        
        result = order_service.request_order_cancellation(
            order_id=order.id,
            user_id=sample_buyer.id,
            reason="Changed my mind"
        )
        
        # Should be cancelled immediately
        assert result["status"] == OrderStatus.CANCELLED
        
        # Verify in database
        with Session(engine) as session:
            cancelled_order = session.get(Order, order.id)
            assert cancelled_order.status == OrderStatus.CANCELLED
    
    def test_request_order_cancellation_confirmed(self, order_service, sample_buyer, sample_product):
        """Test requesting cancellation for confirmed order (creates request)."""
        
        # Create confirmed order
        with Session(engine) as session:
            order = Order(
                buyer_id=sample_buyer.id,
                status=OrderStatus.CONFIRMED,
                subtotal=Decimal("10.00"),
                platform_fee=Decimal("0.80"),
                total=Decimal("10.80"),
                payment_status=PaymentStatus.PAID,
                shipping_address={"street": "123 Test St"}
            )
            session.add(order)
            session.commit()
            session.refresh(order)
        
        result = order_service.request_order_cancellation(
            order_id=order.id,
            user_id=sample_buyer.id,
            reason="Product no longer needed"
        )
        
        # Should create cancellation request
        assert result["status"] == "cancellation_requested"
        assert "Admin will review" in result["message"]
        
        # Verify order status unchanged but history created
        with Session(engine) as session:
            order_check = session.get(Order, order.id)
            assert order_check.status == OrderStatus.CONFIRMED
            
            # Check status history for cancellation request
            history = session.exec(
                select(OrderStatusHistory)
                .where(OrderStatusHistory.order_id == order.id)
                .order_by(OrderStatusHistory.created_at.desc())
            ).first()
            
            assert "Cancellation requested" in history.notes
            assert history.status_metadata.get("cancellation_requested") == True
    
    def test_search_user_orders(self, order_service, sample_buyer, sample_product):
        """Test searching user orders with filters."""
        
        # Create multiple orders
        orders = []
        with Session(engine) as session:
            for i in range(3):
                order = Order(
                    buyer_id=sample_buyer.id,
                    status=OrderStatus.DELIVERED if i == 0 else OrderStatus.CONFIRMED,
                    subtotal=Decimal("10.00"),
                    platform_fee=Decimal("0.80"),
                    total=Decimal("10.80"),
                    payment_status=PaymentStatus.PAID,
                    shipping_address={"street": f"12{i} Test St"}
                )
                session.add(order)
                session.commit()
                session.refresh(order)
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=sample_product.id,
                    quantity=Decimal("1"),
                    unit_price=Decimal("10.00"),
                    farmer_id=sample_farmer.id
                )
                session.add(order_item)
                orders.append(order)
            
            session.commit()
        
        # Search all orders
        results = order_service.search_user_orders(
            user_id=sample_buyer.id,
            limit=10
        )
        
        assert results["total_count"] == 3
        assert len(results["orders"]) == 3
        
        # Search with status filter
        delivered_results = order_service.search_user_orders(
            user_id=sample_buyer.id,
            status_filter=[OrderStatus.DELIVERED]
        )
        
        assert delivered_results["total_count"] == 1
        assert delivered_results["orders"][0]["status"] == OrderStatus.DELIVERED
        
        # Search with product name
        product_results = order_service.search_user_orders(
            user_id=sample_buyer.id,
            search_query="Test Product"
        )
        
        assert product_results["total_count"] == 3  # All orders have the test product
    
    def test_create_order_review(self, order_service, sample_delivered_order, sample_buyer):
        """Test creating a review for delivered order."""
        
        order_data = sample_delivered_order
        
        result = order_service.create_order_review(
            order_id=order_data["order_id"],
            user_id=sample_buyer.id,
            rating=5,
            review_text="Great product, fast delivery!",
            is_anonymous=False
        )
        
        assert result["rating"] == 5
        assert result["review_text"] == "Great product, fast delivery!"
        assert result["is_anonymous"] == False
        
        # Verify in database
        with Session(engine) as session:
            review = session.exec(
                select(OrderReview).where(OrderReview.order_id == order_data["order_id"])
            ).first()
            
            assert review is not None
            assert review.rating == 5
            assert review.buyer_id == sample_buyer.id
    
    def test_create_review_not_delivered(self, order_service, sample_buyer, sample_product):
        """Test that reviews can only be created for delivered orders."""
        
        # Create confirmed order (not delivered)
        with Session(engine) as session:
            order = Order(
                buyer_id=sample_buyer.id,
                status=OrderStatus.CONFIRMED,
                subtotal=Decimal("10.00"),
                platform_fee=Decimal("0.80"),
                total=Decimal("10.80"),
                payment_status=PaymentStatus.PAID,
                shipping_address={"street": "123 Test St"}
            )
            session.add(order)
            session.commit()
            session.refresh(order)
        
        with pytest.raises(Exception) as exc_info:
            order_service.create_order_review(
                order_id=order.id,
                user_id=sample_buyer.id,
                rating=5,
                review_text="Great!"
            )
        
        assert "Can only review delivered orders" in str(exc_info.value)
    
    def test_create_duplicate_review(self, order_service, sample_delivered_order, sample_buyer):
        """Test that duplicate reviews are not allowed."""
        
        order_data = sample_delivered_order
        
        # Create first review
        order_service.create_order_review(
            order_id=order_data["order_id"],
            user_id=sample_buyer.id,
            rating=5,
            review_text="First review"
        )
        
        # Try to create second review
        with pytest.raises(Exception) as exc_info:
            order_service.create_order_review(
                order_id=order_data["order_id"],
                user_id=sample_buyer.id,
                rating=4,
                review_text="Second review"
            )
        
        assert "Review already exists" in str(exc_info.value)
    
    def test_get_order_reviews(self, order_service, sample_delivered_order, sample_buyer):
        """Test getting reviews for an order."""
        
        order_data = sample_delivered_order
        
        # Create a review
        order_service.create_order_review(
            order_id=order_data["order_id"],
            user_id=sample_buyer.id,
            rating=4,
            review_text="Good product",
            is_anonymous=False
        )
        
        reviews = order_service.get_order_reviews(
            order_id=order_data["order_id"],
            limit=10
        )
        
        assert reviews["total_count"] == 1
        assert len(reviews["reviews"]) == 1
        
        review = reviews["reviews"][0]
        assert review["rating"] == 4
        assert review["review_text"] == "Good product"
        assert review["reviewer_name"] == sample_buyer.name  # Not anonymous
        assert review["is_verified_purchase"] == True
    
    def test_get_order_reviews_anonymous(self, order_service, sample_delivered_order, sample_buyer):
        """Test getting anonymous reviews."""
        
        order_data = sample_delivered_order
        
        # Create anonymous review
        order_service.create_order_review(
            order_id=order_data["order_id"],
            user_id=sample_buyer.id,
            rating=3,
            review_text="Anonymous feedback",
            is_anonymous=True
        )
        
        reviews = order_service.get_order_reviews(
            order_id=order_data["order_id"],
            limit=10
        )
        
        review = reviews["reviews"][0]
        assert review["reviewer_name"] == "Anonymous"