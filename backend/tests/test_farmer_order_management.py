"""
Tests for farmer order management functionality.
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
            status=OrderStatus.CONFIRMED,
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
            fulfillment_status="pending"
        )
        session.add(order_item)
        session.commit()
        session.refresh(order_item)
        
        # Return IDs instead of objects to avoid session issues
        return {"order_id": order.id, "order_item_id": order_item.id}


class TestFarmerOrderManagement:
    """Test cases for farmer order management."""
    
    def test_get_farmer_orders(self, order_service, sample_order_with_items, sample_farmer_user):
        """Test getting orders for a farmer."""
        
        order_data = sample_order_with_items
        
        orders = order_service.get_farmer_orders(
            farmer_id=sample_farmer_user.id,
            limit=10
        )
        
        assert len(orders) == 1
        assert orders[0]["id"] == order_data["order_id"]
        assert orders[0]["status"] == OrderStatus.CONFIRMED
        assert len(orders[0]["items"]) == 1
        assert orders[0]["items"][0]["fulfillment_status"] == "pending"
    
    def test_update_item_fulfillment_status(self, order_service, sample_order_with_items, sample_farmer_user):
        """Test updating item fulfillment status."""
        
        order_data = sample_order_with_items
        
        result = order_service.update_item_fulfillment_status(
            order_item_id=order_data["order_item_id"],
            farmer_id=sample_farmer_user.id,
            fulfillment_status="shipped",
            notes="Item shipped via UPS"
        )
        
        assert result["fulfillment_status"] == "shipped"
        assert result["shipped_at"] is not None
        assert "shipped" in result["message"]
        
        # Verify in database
        with Session(engine) as session:
            updated_item = session.get(OrderItem, order_data["order_item_id"])
            assert updated_item.fulfillment_status == "shipped"
            assert updated_item.shipped_at is not None
    
    def test_update_item_fulfillment_access_denied(self, order_service, sample_order_with_items):
        """Test access denied when farmer doesn't own the item."""
        
        # Create another farmer
        with Session(engine) as session:
            other_farmer = User(
                name="Other Farmer",
                email="other@test.com",
                role=UserRole.FARMER
            )
            session.add(other_farmer)
            session.commit()
            session.refresh(other_farmer)
        
        order_data = sample_order_with_items
        
        with pytest.raises(Exception) as exc_info:
            order_service.update_item_fulfillment_status(
                order_item_id=order_data["order_item_id"],
                farmer_id=other_farmer.id,
                fulfillment_status="shipped"
            )
        
        assert "Access denied" in str(exc_info.value)
    
    def test_bulk_update_order_status(self, order_service, sample_farmer_user, sample_buyer, sample_product):
        """Test bulk updating order status."""
        
        # Create multiple orders
        orders = []
        with Session(engine) as session:
            for i in range(3):
                order = Order(
                    buyer_id=sample_buyer.id,
                    status=OrderStatus.CONFIRMED,
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
                    farmer_id=sample_farmer_user.id,
                    fulfillment_status="pending"
                )
                session.add(order_item)
                orders.append(order)
            
            session.commit()
        
        # Bulk update
        result = order_service.bulk_update_order_status(
            order_ids=[order.id for order in orders],
            new_status=OrderStatus.PROCESSING,
            farmer_id=sample_farmer_user.id,
            notes="Bulk processing started"
        )
        
        assert result["total_processed"] == 3
        assert result["successful_updates"] == 3
        assert result["failed_updates"] == 0
        
        # Verify updates
        with Session(engine) as session:
            for order in orders:
                updated_order = session.get(Order, order.id)
                assert updated_order.status == OrderStatus.PROCESSING
    
    def test_bulk_update_access_denied(self, order_service, sample_buyer, sample_product):
        """Test bulk update access denied for unauthorized farmer."""
        
        # Create another farmer
        with Session(engine) as session:
            other_farmer = User(
                name="Other Farmer",
                email="other@test.com",
                role=UserRole.FARMER
            )
            session.add(other_farmer)
            session.commit()
            session.refresh(other_farmer)
            
            # Create order with different farmer
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
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=sample_product.id,
                quantity=Decimal("1"),
                unit_price=Decimal("10.00"),
                farmer_id=999,  # Different farmer
                fulfillment_status="pending"
            )
            session.add(order_item)
            session.commit()
        
        # Try bulk update with wrong farmer
        with pytest.raises(Exception) as exc_info:
            order_service.bulk_update_order_status(
                order_ids=[order.id],
                new_status=OrderStatus.PROCESSING,
                farmer_id=other_farmer.id
            )
        
        assert "Access denied" in str(exc_info.value)
    
    def test_get_farmer_order_analytics(self, order_service, sample_order_with_items, sample_farmer_user):
        """Test getting farmer order analytics."""
        
        analytics = order_service.get_farmer_order_analytics(
            farmer_id=sample_farmer_user.id
        )
        
        assert analytics["total_orders"] == 1
        assert analytics["total_revenue"] == 20.0  # 2 * 10.00
        assert analytics["average_order_value"] == 20.0
        assert "confirmed" in analytics["order_status_breakdown"]
        assert "pending" in analytics["fulfillment_status_breakdown"]
    
    def test_get_farmer_order_analytics_with_date_filter(self, order_service, sample_farmer_user):
        """Test analytics with date filtering."""
        
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow() + timedelta(days=1)
        
        analytics = order_service.get_farmer_order_analytics(
            farmer_id=sample_farmer_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        assert analytics["period"]["start_date"] is not None
        assert analytics["period"]["end_date"] is not None
    
    def test_generate_shipping_label(self, order_service, sample_order_with_items, sample_farmer_user):
        """Test generating shipping label."""
        
        order_data = sample_order_with_items
        
        result = order_service.generate_shipping_label(
            order_id=order_data["order_id"],
            farmer_id=sample_farmer_user.id,
            shipping_service="express"
        )
        
        assert "tracking_number" in result
        assert result["shipping_service"] == "express"
        assert "label_url" in result
        assert "estimated_delivery" in result
        
        # Verify tracking number was added to order
        with Session(engine) as session:
            updated_order = session.get(Order, order_data["order_id"])
            assert updated_order.tracking_number is not None
            assert updated_order.estimated_delivery_date is not None
    
    def test_generate_shipping_label_access_denied(self, order_service, sample_order_with_items):
        """Test shipping label generation access denied."""
        
        # Create another farmer
        with Session(engine) as session:
            other_farmer = User(
                name="Other Farmer",
                email="other@test.com",
                role=UserRole.FARMER
            )
            session.add(other_farmer)
            session.commit()
            session.refresh(other_farmer)
        
        order_data = sample_order_with_items
        
        with pytest.raises(Exception) as exc_info:
            order_service.generate_shipping_label(
                order_id=order_data["order_id"],
                farmer_id=other_farmer.id
            )
        
        assert "Access denied" in str(exc_info.value)
    
    def test_auto_update_order_status_when_all_items_shipped(self, order_service, sample_farmer_user, sample_buyer, sample_product):
        """Test automatic order status update when all items are shipped."""
        
        # Create order with processing status
        with Session(engine) as session:
            order = Order(
                buyer_id=sample_buyer.id,
                status=OrderStatus.PROCESSING,
                subtotal=Decimal("20.00"),
                platform_fee=Decimal("1.60"),
                total=Decimal("21.60"),
                payment_status=PaymentStatus.PAID,
                shipping_address={"street": "123 Test St"}
            )
            session.add(order)
            session.commit()
            session.refresh(order)
            
            # Create two order items
            item1 = OrderItem(
                order_id=order.id,
                product_id=sample_product.id,
                quantity=Decimal("1"),
                unit_price=Decimal("10.00"),
                farmer_id=sample_farmer_user.id,
                fulfillment_status="pending"
            )
            item2 = OrderItem(
                order_id=order.id,
                product_id=sample_product.id,
                quantity=Decimal("1"),
                unit_price=Decimal("10.00"),
                farmer_id=sample_farmer_user.id,
                fulfillment_status="pending"
            )
            session.add(item1)
            session.add(item2)
            session.commit()
            session.refresh(item1)
            session.refresh(item2)
        
        # Ship first item
        order_service.update_item_fulfillment_status(
            order_item_id=item1.id,
            farmer_id=sample_farmer_user.id,
            fulfillment_status="shipped"
        )
        
        # Order should still be processing
        with Session(engine) as session:
            order_check = session.get(Order, order.id)
            assert order_check.status == OrderStatus.PROCESSING
        
        # Ship second item
        order_service.update_item_fulfillment_status(
            order_item_id=item2.id,
            farmer_id=sample_farmer_user.id,
            fulfillment_status="shipped"
        )
        
        # Order should now be shipped
        with Session(engine) as session:
            order_check = session.get(Order, order.id)
            assert order_check.status == OrderStatus.SHIPPED