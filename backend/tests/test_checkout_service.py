"""
Tests for checkout service functionality.
"""

import pytest
from decimal import Decimal

from sqlmodel import Session

from app.database import engine
from app.models import Product, User, UserRole, UserStatus
from app.services.checkout_service import CheckoutValidator
from app.services.cart_service import CartService


@pytest.fixture
def checkout_validator():
    """Create checkout validator instance."""
    return CheckoutValidator()


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
            role=UserRole.BUYER,
            status=UserStatus.ACTIVE,
            email_verified=True
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
            quantity_available=100,
            weight=Decimal("2.5")
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        yield product
        
        # Cleanup
        session.delete(product)
        session.commit()


class TestCheckoutValidator:
    """Test checkout validation functionality."""
    
    def test_validate_user_eligibility_valid(self, checkout_validator, test_user):
        """Test validating eligible user."""
        result = checkout_validator.validate_user_eligibility(test_user.id)
        
        assert result["valid"] is True
        assert "user" in result
    
    def test_validate_user_eligibility_inactive(self, checkout_validator, test_user):
        """Test validating inactive user."""
        # Make user inactive
        with Session(engine) as session:
            user = session.get(User, test_user.id)
            user.status = UserStatus.INACTIVE
            session.add(user)
            session.commit()
        
        result = checkout_validator.validate_user_eligibility(test_user.id)
        
        assert result["valid"] is False
        assert result["error_type"] == "user_inactive"
    
    def test_validate_user_eligibility_not_found(self, checkout_validator):
        """Test validating non-existent user."""
        result = checkout_validator.validate_user_eligibility(99999)
        
        assert result["valid"] is False
        assert result["error_type"] == "user_not_found"
    
    def test_validate_pricing_valid(self, checkout_validator, cart_service, test_user, test_product):
        """Test validating pricing with valid cart."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        cart_service.add_item(cart.id, test_product.id, 2)
        
        result = checkout_validator.validate_pricing(cart.id)
        
        assert result["valid"] is True
        assert "pricing" in result
        assert result["pricing"]["subtotal"] == float(test_product.price * 2)
        assert result["pricing"]["platform_fee"] > 0
        assert result["pricing"]["tax_amount"] >= 0
        assert result["pricing"]["total"] > result["pricing"]["subtotal"]
    
    def test_validate_pricing_empty_cart(self, checkout_validator, cart_service, test_user):
        """Test validating pricing with empty cart."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        
        result = checkout_validator.validate_pricing(cart.id)
        
        assert result["valid"] is False
        assert result["error_type"] == "empty_cart"
    
    def test_validate_shipping_address_valid(self, checkout_validator):
        """Test validating valid US shipping address."""
        address = {
            "first_name": "John",
            "last_name": "Doe",
            "address_line_1": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "94102",
            "country": "US",
            "phone": "555-123-4567"
        }
        
        result = checkout_validator.validate_shipping_address(address)
        
        assert result["valid"] is True
        assert "formatted_address" in result
        assert result["formatted_address"]["first_name"] == "John"
        assert result["formatted_address"]["state"] == "CA"
        assert result["formatted_address"]["postal_code"] == "94102"
    
    def test_validate_shipping_address_missing_fields(self, checkout_validator):
        """Test validating address with missing required fields."""
        address = {
            "first_name": "John",
            "last_name": "Doe"
            # Missing other required fields
        }
        
        result = checkout_validator.validate_shipping_address(address)
        
        assert result["valid"] is False
        assert result["error_type"] == "address_validation"
        assert "missing_fields" in result
        assert "address_line_1" in result["missing_fields"]
    
    def test_validate_shipping_address_invalid_zip(self, checkout_validator):
        """Test validating address with invalid ZIP code."""
        address = {
            "first_name": "John",
            "last_name": "Doe",
            "address_line_1": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "invalid",
            "country": "US"
        }
        
        result = checkout_validator.validate_shipping_address(address)
        
        assert result["valid"] is False
        assert result["error_type"] == "address_format"
        assert any(error["field"] == "postal_code" for error in result["errors"])
    
    def test_validate_canadian_address(self, checkout_validator):
        """Test validating Canadian address."""
        address = {
            "first_name": "John",
            "last_name": "Doe",
            "address_line_1": "123 Main St",
            "city": "Toronto",
            "state": "ON",
            "postal_code": "M5V 3A8",
            "country": "CA"
        }
        
        result = checkout_validator.validate_shipping_address(address)
        
        assert result["valid"] is True
        assert result["formatted_address"]["postal_code"] == "M5V 3A8"
    
    def test_create_checkout_session_valid(self, checkout_validator, cart_service, test_user, test_product):
        """Test creating valid checkout session."""
        cart = cart_service.get_or_create_cart(user_id=test_user.id)
        cart_service.add_item(cart.id, test_product.id, 2)
        
        address = {
            "first_name": "John",
            "last_name": "Doe",
            "address_line_1": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "94102",
            "country": "US"
        }
        
        result = checkout_validator.create_checkout_session(
            user_id=test_user.id,
            cart_id=cart.id,
            shipping_address=address
        )
        
        assert result["valid"] is True
        assert "checkout_session" in result
        session_data = result["checkout_session"]
        assert session_data["user_id"] == test_user.id
        assert session_data["cart_id"] == cart.id
        assert "session_id" in session_data
        assert "pricing" in session_data
        assert "shipping_address" in session_data
    
    def test_create_checkout_session_invalid_user(self, checkout_validator, cart_service, test_product):
        """Test creating checkout session with invalid user."""
        cart = cart_service.get_or_create_cart(session_id="test-session")
        cart_service.add_item(cart.id, test_product.id, 2)
        
        address = {
            "first_name": "John",
            "last_name": "Doe",
            "address_line_1": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "94102",
            "country": "US"
        }
        
        result = checkout_validator.create_checkout_session(
            user_id=99999,  # Non-existent user
            cart_id=cart.id,
            shipping_address=address
        )
        
        assert result["valid"] is False
        assert result["error_type"] == "user_not_found"
    
    def test_calculate_tax_california(self, checkout_validator):
        """Test tax calculation for California."""
        subtotal = Decimal("100.00")
        address = {"state": "CA", "country": "US"}
        
        tax = checkout_validator.calculate_tax(subtotal, address)
        
        assert tax == Decimal("8.75")  # 8.75% CA tax
    
    def test_calculate_tax_unknown_state(self, checkout_validator):
        """Test tax calculation for unknown state."""
        subtotal = Decimal("100.00")
        address = {"state": "XX", "country": "US"}
        
        tax = checkout_validator.calculate_tax(subtotal, address)
        
        # Should use default tax rate
        assert tax > 0
    
    def test_estimate_shipping_light_package(self, checkout_validator, test_product):
        """Test shipping estimation for light package."""
        cart_items = [
            {
                "product_id": test_product.id,
                "quantity": 1
            }
        ]
        
        address = {"state": "CA", "country": "US"}
        
        shipping_cost = checkout_validator.estimate_shipping(cart_items, address)
        
        # Base rate + CA surcharge
        assert shipping_cost >= Decimal("5.99")
    
    def test_estimate_shipping_heavy_package(self, checkout_validator, test_product):
        """Test shipping estimation for heavy package."""
        cart_items = [
            {
                "product_id": test_product.id,
                "quantity": 5  # 5 * 2.5 lbs = 12.5 lbs
            }
        ]
        
        address = {"state": "TX", "country": "US"}
        
        shipping_cost = checkout_validator.estimate_shipping(cart_items, address)
        
        # Should be more than base rate due to weight
        assert shipping_cost > Decimal("5.99")