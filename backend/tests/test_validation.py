import pytest
from pydantic import ValidationError
from app.services.validation import (
    sanitize_html,
    validate_phone_number,
    validate_password_strength,
    UserCreateRequest,
    UserUpdateRequest,
    ProductCreateRequest,
    ProductUpdateRequest,
    OrderCreateRequest,
    ProductSearchRequest,
    ValidationError as CustomValidationError
)


class TestSanitization:
    
    def test_sanitize_html_basic(self):
        """Test basic HTML sanitization."""
        input_text = "<script>alert('xss')</script>Hello World"
        result = sanitize_html(input_text)
        assert "<script>" not in result
        assert "Hello World" in result
    
    def test_sanitize_html_javascript(self):
        """Test JavaScript removal."""
        input_text = "javascript:alert('xss')"
        result = sanitize_html(input_text)
        assert "javascript:" not in result
    
    def test_sanitize_html_event_handlers(self):
        """Test event handler removal."""
        input_text = '<div onclick="alert(\'xss\')">Click me</div>'
        result = sanitize_html(input_text)
        assert "onclick" not in result
    
    def test_sanitize_html_empty_string(self):
        """Test empty string handling."""
        assert sanitize_html("") == ""
        assert sanitize_html(None) is None


class TestPhoneValidation:
    
    def test_valid_phone_numbers(self):
        """Test valid phone number formats."""
        valid_phones = [
            "1234567890",
            "+1-234-567-8900",
            "(123) 456-7890",
            "123.456.7890"
        ]
        
        for phone in valid_phones:
            result = validate_phone_number(phone)
            assert result.isdigit()
            assert len(result) >= 10
    
    def test_invalid_phone_numbers(self):
        """Test invalid phone number formats."""
        invalid_phones = [
            "123",  # Too short
            "12345678901234567890",  # Too long
            "abcdefghij"  # Non-numeric
        ]
        
        for phone in invalid_phones:
            with pytest.raises(CustomValidationError):
                validate_phone_number(phone)
    
    def test_empty_phone_number(self):
        """Test empty phone number handling."""
        assert validate_phone_number("") == ""
        assert validate_phone_number(None) is None


class TestPasswordValidation:
    
    def test_valid_passwords(self):
        """Test valid password formats."""
        valid_passwords = [
            "Password123!",
            "MySecure@Pass1",
            "Complex#Password9"
        ]
        
        for password in valid_passwords:
            result = validate_password_strength(password)
            assert result == password
    
    def test_invalid_passwords(self):
        """Test invalid password formats."""
        invalid_passwords = [
            "short",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoNumbers!",  # No numbers
            "NoSpecialChars123"  # No special characters
        ]
        
        for password in invalid_passwords:
            with pytest.raises(CustomValidationError):
                validate_password_strength(password)


class TestUserValidation:
    
    def test_valid_user_create_request(self):
        """Test valid user creation request."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "role": "buyer"
        }
        
        user_request = UserCreateRequest(**data)
        assert user_request.name == "John Doe"
        assert user_request.email == "john@example.com"
        assert user_request.phone == "1234567890"
        assert user_request.role == "buyer"
    
    def test_user_create_request_sanitization(self):
        """Test user creation request sanitization."""
        data = {
            "name": "<script>alert('xss')</script>John Doe",
            "email": "john@example.com",
            "role": "buyer"
        }
        
        user_request = UserCreateRequest(**data)
        assert "<script>" not in user_request.name
        assert "John Doe" in user_request.name
    
    def test_invalid_user_create_request(self):
        """Test invalid user creation request."""
        # Missing required fields
        with pytest.raises(ValidationError):
            UserCreateRequest(email="john@example.com")
        
        # Invalid email
        with pytest.raises(ValidationError):
            UserCreateRequest(name="John", email="invalid-email")
        
        # Invalid role
        with pytest.raises(ValidationError):
            UserCreateRequest(name="John", email="john@example.com", role="invalid")


class TestProductValidation:
    
    def test_valid_product_create_request(self):
        """Test valid product creation request."""
        data = {
            "name": "Fresh Tomatoes",
            "description": "Organic tomatoes from local farm",
            "category": "vegetables",
            "price": 5.99,
            "quantity": "10 lbs",
            "farmer_id": 1
        }
        
        product_request = ProductCreateRequest(**data)
        assert product_request.name == "Fresh Tomatoes"
        assert product_request.price == 5.99
    
    def test_product_create_request_sanitization(self):
        """Test product creation request sanitization."""
        data = {
            "name": "<script>alert('xss')</script>Tomatoes",
            "description": "Fresh <b>organic</b> tomatoes",
            "category": "vegetables",
            "price": 5.99,
            "quantity": "10 lbs"
        }
        
        product_request = ProductCreateRequest(**data)
        assert "<script>" not in product_request.name
        assert "Tomatoes" in product_request.name
    
    def test_invalid_product_create_request(self):
        """Test invalid product creation request."""
        # Negative price
        with pytest.raises(ValidationError):
            ProductCreateRequest(
                name="Tomatoes",
                category="vegetables", 
                price=-5.99,
                quantity="10 lbs"
            )
        
        # Invalid category format
        with pytest.raises(ValidationError):
            ProductCreateRequest(
                name="Tomatoes",
                category="vegetables@#$",
                price=5.99,
                quantity="10 lbs"
            )


class TestOrderValidation:
    
    def test_valid_order_create_request(self):
        """Test valid order creation request."""
        data = {
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 1.5}
            ],
            "shipping_address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "12345",
                "country": "USA"
            }
        }
        
        order_request = OrderCreateRequest(**data)
        assert len(order_request.items) == 2
        assert order_request.shipping_address["city"] == "Anytown"
    
    def test_invalid_order_create_request(self):
        """Test invalid order creation request."""
        # Empty items
        with pytest.raises(ValidationError):
            OrderCreateRequest(
                items=[],
                shipping_address={
                    "street": "123 Main St",
                    "city": "Anytown", 
                    "state": "CA",
                    "zip_code": "12345",
                    "country": "USA"
                }
            )
        
        # Invalid zip code
        with pytest.raises(CustomValidationError):
            OrderCreateRequest(
                items=[{"product_id": 1, "quantity": 2}],
                shipping_address={
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state": "CA", 
                    "zip_code": "invalid",
                    "country": "USA"
                }
            )
        
        # Missing required address fields
        with pytest.raises(CustomValidationError):
            OrderCreateRequest(
                items=[{"product_id": 1, "quantity": 2}],
                shipping_address={
                    "street": "123 Main St",
                    "city": "Anytown"
                    # Missing state, zip_code, country
                }
            )


class TestSearchValidation:
    
    def test_valid_product_search_request(self):
        """Test valid product search request."""
        data = {
            "query": "tomatoes",
            "category": "vegetables",
            "min_price": 1.0,
            "max_price": 10.0,
            "limit": 20,
            "offset": 0
        }
        
        search_request = ProductSearchRequest(**data)
        assert search_request.query == "tomatoes"
        assert search_request.min_price == 1.0
        assert search_request.max_price == 10.0
    
    def test_search_request_sanitization(self):
        """Test search request sanitization."""
        data = {
            "query": "<script>alert('xss')</script>tomatoes",
            "category": "vegetables"
        }
        
        search_request = ProductSearchRequest(**data)
        assert "<script>" not in search_request.query
        assert "tomatoes" in search_request.query
    
    def test_invalid_search_request(self):
        """Test invalid search request."""
        # Invalid price range
        with pytest.raises(CustomValidationError):
            ProductSearchRequest(
                min_price=10.0,
                max_price=5.0  # max < min
            )
        
        # Invalid limit
        with pytest.raises(ValidationError):
            ProductSearchRequest(limit=0)  # Must be >= 1
        
        # Invalid offset
        with pytest.raises(ValidationError):
            ProductSearchRequest(offset=-1)  # Must be >= 0