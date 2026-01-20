"""
Tests for cart service functionality.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from sqlmodel import Session, select

from app.database import engine
from app.models import Cart, CartItem, Product, User, UserRole, CartStatus
from app.services.cart_service import CartService


@pytest.fixture
def cart_service():
    """Create cart service instance."""
    return CartService()


@pytest.fixture
def test_user():
    """Create test user."""
    with Session(engine) as session:
        user = User(
            name="Test User",
            email="test@example.com",
            role=UserRole.BUYER
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        yield user
        
        # Cleanup
        session.delete(user)
        session.commit()


@pytest.fixture
def test_product():
    """Create test product."""
    with Session(engine) as session:
        product = Product(
            name="Test Product",
            description="Test description",
            price=Decimal("10.99"),
            quantity_available=100
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        yield product
        
        # Cleanup
        session.delete(product)
        session.commit()


class TestCartService:
    """Test cart service operations."""
    
    def test_get_or_create_cart_for_user(self, cart_service, test_user):
        """Test creating cart for authenticated user."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        
        assert cart is not None
        assert cart.user_id == test_user.id
        assert cart.session_id is None
        assert cart.status == CartStatus.ACTIVE
        assert cart.expires_at is not None
        
        # Test getting existing cart
        cart2 = cart_service.get_or_create_cart(user_id=test_user.id)
        assert cart2.id == cart.id
    
    def test_get_or_create_cart_for_session(self, cart_service):
        """Test creating cart for anonymous session."""
        session_id = "test-session-123"
        cart = cart_service.get_or_create_cart(session_id=session_id)
        
        assert cart is not None
        assert cart.user_id is None
        assert cart.session_id == session_id
        assert cart.status == CartStatus.ACTIVE
        assert cart.expires_at is not None
    
    def test_get_or_create_cart_no_identifier(self, cart_service):
        """Test error when no user_id or session_id provided."""
        with pytest.raises(Exception):
            cart_service.get_or_create_cart()
    
    def test_add_item_to_cart(self, cart_service, test_user, test_product):
        """Test adding item to cart."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        
        cart_item = cart_service.add_item(
            cart_id=cart.id,
            product_id=test_product.id,
            quantity=2
        )
        
        assert cart_item is not None
        assert cart_item.cart_id == cart.id
        assert cart_item.product_id == test_product.id
        assert cart_item.quantity == 2
        assert cart_item.unit_price == test_product.price
    
    def test_add_existing_item_updates_quantity(self, cart_service, test_user, test_product):
        """Test adding existing item updates quantity."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        
        # Add item first time
        cart_service.add_item(cart_id=cart.id, product_id=test_product.id, quantity=2)
        
        # Add same item again
        cart_item = cart_service.add_item(cart_id=cart.id, product_id=test_product.id, quantity=3)
        
        assert cart_item.quantity == 5  # 2 + 3
    
    def test_add_item_insufficient_stock(self, cart_service, test_user, test_product):
        """Test adding item with insufficient stock raises error."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        
        with pytest.raises(Exception) as exc_info:
            cart_service.add_item(
                cart_id=cart.id,
                product_id=test_product.id,
                quantity=200  # More than available (100)
            )
        
        assert "available" in str(exc_info.value)
    
    def test_update_item_quantity(self, cart_service, test_user, test_product):
        """Test updating cart item quantity."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        cart_service.add_item(cart_id=cart.id, product_id=test_product.id, quantity=2)
        
        cart_item = cart_service.update_item_quantity(
            cart_id=cart.id,
            product_id=test_product.id,
            quantity=5
        )
        
        assert cart_item is not None
        assert cart_item.quantity == 5
    
    def test_update_item_quantity_to_zero_removes_item(self, cart_service, test_user, test_product):
        """Test updating quantity to zero removes item."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        cart_service.add_item(cart_id=cart.id, product_id=test_product.id, quantity=2)
        
        result = cart_service.update_item_quantity(
            cart_id=cart.id,
            product_id=test_product.id,
            quantity=0
        )
        
        assert result is None
        
        # Verify item is removed
        items = cart_service.get_cart_items(cart.id)
        assert len(items) == 0
    
    def test_remove_item(self, cart_service, test_user, test_product):
        """Test removing item from cart."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        cart_service.add_item(cart_id=cart.id, product_id=test_product.id, quantity=2)
        
        removed = cart_service.remove_item(cart_id=cart.id, product_id=test_product.id)
        
        assert removed is True
        
        # Verify item is removed
        items = cart_service.get_cart_items(cart.id)
        assert len(items) == 0
    
    def test_remove_nonexistent_item(self, cart_service, test_user):
        """Test removing non-existent item returns False."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        
        removed = cart_service.remove_item(cart_id=cart.id, product_id=999)
        
        assert removed is False
    
    def test_get_cart_items(self, cart_service, test_user, test_product):
        """Test getting cart items with product details."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        cart_service.add_item(cart_id=cart.id, product_id=test_product.id, quantity=2)
        
        items = cart_service.get_cart_items(cart.id)
        
        assert len(items) == 1
        item = items[0]
        assert item["product_id"] == test_product.id
        assert item["product_name"] == test_product.name
        assert item["quantity"] == 2
        assert item["unit_price"] == float(test_product.price)
        assert item["total_price"] == float(test_product.price * 2)
    
    def test_get_cart_summary(self, cart_service, test_user, test_product):
        """Test getting cart summary."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        cart_service.add_item(cart_id=cart.id, product_id=test_product.id, quantity=2)
        
        summary = cart_service.get_cart_summary(cart.id)
        
        assert summary["cart_id"] == cart.id
        assert summary["item_count"] == 2
        assert summary["subtotal"] == float(test_product.price * 2)
        assert len(summary["items"]) == 1
    
    def test_validate_cart_items_valid(self, cart_service, test_user, test_product):
        """Test validating cart with valid items."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        cart_service.add_item(cart_id=cart.id, product_id=test_product.id, quantity=2)
        
        validation = cart_service.validate_cart_items(cart.id)
        
        assert validation["valid"] is True
        assert len(validation["issues"]) == 0
    
    def test_validate_cart_items_insufficient_stock(self, cart_service, test_user, test_product):
        """Test validating cart with insufficient stock."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        cart_service.add_item(cart_id=cart.id, product_id=test_product.id, quantity=2)
        
        # Reduce product stock
        with Session(engine) as session:
            product = session.get(Product, test_product.id)
            product.quantity_available = 1
            session.add(product)
            session.commit()
        
        validation = cart_service.validate_cart_items(cart.id)
        
        assert validation["valid"] is False
        assert len(validation["issues"]) == 1
        assert validation["issues"][0]["type"] == "insufficient_stock"
    
    def test_clear_cart(self, cart_service, test_user, test_product):
        """Test clearing cart."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        cart_service.add_item(cart_id=cart.id, product_id=test_product.id, quantity=2)
        
        cleared = cart_service.clear_cart(cart.id)
        
        assert cleared is True
        
        # Verify cart is empty
        items = cart_service.get_cart_items(cart.id)
        assert len(items) == 0
    
    def test_merge_carts(self, cart_service, test_user, test_product):
        """Test merging carts."""
        # Create user cart
        user_cart = cart_service.get_or_create_cart(user_id=test_user.id)
        cart_service.add_item(cart_id=user_cart.id, product_id=test_product.id, quantity=1)
        
        # Create session cart
        session_cart = cart_service.get_or_create_cart(session_id="test-session")
        cart_service.add_item(cart_id=session_cart.id, product_id=test_product.id, quantity=2)
        
        # Merge carts
        merged = cart_service.merge_carts(user_cart.id, session_cart.id)
        
        assert merged is True
        
        # Verify merged quantities
        items = cart_service.get_cart_items(user_cart.id)
        assert len(items) == 1
        assert items[0]["quantity"] == 3  # 1 + 2
        
        # Verify source cart is expired
        with Session(engine) as session:
            source_cart = session.get(Cart, session_cart.id)
            assert source_cart.status == CartStatus.EXPIRED
    
    def test_cleanup_expired_carts(self, cart_service):
        """Test cleaning up expired carts."""
        # Create expired cart
        with Session(engine) as session:
            expired_cart = Cart(
                session_id="expired-session",
                expires_at=datetime.utcnow() - timedelta(hours=1),
                status=CartStatus.ACTIVE
            )
            session.add(expired_cart)
            session.commit()
            session.refresh(expired_cart)
            
            # Add item to expired cart
            cart_item = CartItem(
                cart_id=expired_cart.id,
                product_id=1,  # Assuming product exists
                quantity=1,
                unit_price=Decimal("10.00")
            )
            session.add(cart_item)
            session.commit()
        
        # Clean up expired carts
        count = cart_service.cleanup_expired_carts()
        
        assert count >= 1
        
        # Verify cart is marked as expired
        with Session(engine) as session:
            cart = session.get(Cart, expired_cart.id)
            assert cart.status == CartStatus.EXPIRED