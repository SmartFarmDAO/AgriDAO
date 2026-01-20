"""
Unit tests for product models and validation.
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from pydantic import ValidationError

from app.models import Product, ProductImage, InventoryHistory, ProductStatus
from app.services.product_validation import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductSearchRequest,
    InventoryUpdateRequest
)


class TestProductModels:
    """Test product model validation and business logic."""

    def test_product_model_creation(self):
        """Test basic product model creation."""
        product = Product(
            name="Test Product",
            description="A test product",
            category="vegetables",
            price=Decimal("10.99"),
            quantity_available=100,
            unit="kg",
            farmer_id=1,
            status=ProductStatus.ACTIVE
        )
        
        assert product.name == "Test Product"
        assert product.price == Decimal("10.99")
        assert product.quantity_available == 100
        assert product.status == ProductStatus.ACTIVE
        assert product.min_order_quantity == 1  # default value

    def test_product_image_model(self):
        """Test product image model."""
        image = ProductImage(
            product_id=1,
            image_url="https://example.com/image.jpg",
            alt_text="Test image",
            sort_order=1,
            is_primary=True,
            width=800,
            height=600,
            file_size=1024000,
            file_format="jpg"
        )
        
        assert image.product_id == 1
        assert image.is_primary is True
        assert image.width == 800

    def test_inventory_history_model(self):
        """Test inventory history model."""
        history = InventoryHistory(
            product_id=1,
            change_type="restock",
            quantity_change=50,
            previous_quantity=100,
            new_quantity=150,
            reason="New shipment received",
            created_by=1
        )
        
        assert history.change_type == "restock"
        assert history.quantity_change == 50
        assert history.new_quantity == 150


class TestProductValidation:
    """Test product validation models."""

    def test_product_create_request_valid(self):
        """Test valid product creation request."""
        data = {
            "name": "Fresh Tomatoes",
            "description": "Organic tomatoes from local farm",
            "category": "vegetables",
            "price": Decimal("5.99"),
            "quantity_available": 100,
            "unit": "kg",
            "farmer_id": 1,
            "sku": "TOM-001",
            "weight": Decimal("1.0"),
            "dimensions": {"length": 10.0, "width": 8.0, "height": 6.0},
            "tags": ["organic", "local", "fresh"],
            "min_order_quantity": 1,
            "max_order_quantity": 50,
            "harvest_date": datetime.now() - timedelta(days=1),
            "expiry_date": datetime.now() + timedelta(days=7)
        }
        
        request = ProductCreateRequest(**data)
        assert request.name == "Fresh Tomatoes"
        assert request.price == Decimal("5.99")
        assert len(request.tags) == 3
        assert request.unit == "kg"

    def test_product_create_request_invalid_name(self):
        """Test product creation with invalid name."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreateRequest(
                name="",
                price=Decimal("5.99"),
                quantity_available=100
            )
        
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_product_create_request_invalid_price(self):
        """Test product creation with invalid price."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreateRequest(
                name="Test Product",
                price=Decimal("-5.99"),
                quantity_available=100
            )
        
        assert "Input should be greater than 0" in str(exc_info.value)

    def test_product_create_request_invalid_sku(self):
        """Test product creation with invalid SKU."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreateRequest(
                name="Test Product",
                price=Decimal("5.99"),
                quantity_available=100,
                sku="INVALID SKU!"
            )
        
        assert "SKU can only contain letters, numbers, hyphens, and underscores" in str(exc_info.value)

    def test_product_create_request_invalid_dimensions(self):
        """Test product creation with invalid dimensions."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreateRequest(
                name="Test Product",
                price=Decimal("5.99"),
                quantity_available=100,
                dimensions={"length": 10.0, "width": 8.0}  # missing height
            )
        
        assert "Dimensions must include length, width, and height" in str(exc_info.value)

    def test_product_create_request_too_many_tags(self):
        """Test product creation with too many tags."""
        tags = [f"tag{i}" for i in range(25)]  # 25 tags, limit is 20
        
        with pytest.raises(ValidationError) as exc_info:
            ProductCreateRequest(
                name="Test Product",
                price=Decimal("5.99"),
                quantity_available=100,
                tags=tags
            )
        
        assert "Maximum 20 tags allowed" in str(exc_info.value)

    def test_product_create_request_invalid_order_quantities(self):
        """Test product creation with invalid order quantities."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreateRequest(
                name="Test Product",
                price=Decimal("5.99"),
                quantity_available=100,
                min_order_quantity=10,
                max_order_quantity=5  # max < min
            )
        
        assert "Maximum order quantity must be greater than or equal to minimum order quantity" in str(exc_info.value)

    def test_product_create_request_invalid_dates(self):
        """Test product creation with invalid dates."""
        harvest_date = datetime.now()
        expiry_date = harvest_date - timedelta(days=1)  # expiry before harvest
        
        with pytest.raises(ValidationError) as exc_info:
            ProductCreateRequest(
                name="Test Product",
                price=Decimal("5.99"),
                quantity_available=100,
                harvest_date=harvest_date,
                expiry_date=expiry_date
            )
        
        assert "Expiry date must be after harvest date" in str(exc_info.value)

    def test_product_create_request_invalid_unit(self):
        """Test product creation with invalid unit."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreateRequest(
                name="Test Product",
                price=Decimal("5.99"),
                quantity_available=100,
                unit="invalid_unit"
            )
        
        assert "Unit must be one of:" in str(exc_info.value)

    def test_product_update_request_valid(self):
        """Test valid product update request."""
        data = {
            "name": "Updated Product Name",
            "price": Decimal("7.99"),
            "quantity_available": 150,
            "status": "active"
        }
        
        request = ProductUpdateRequest(**data)
        assert request.name == "Updated Product Name"
        assert request.price == Decimal("7.99")
        assert request.status == "active"

    def test_product_update_request_partial(self):
        """Test partial product update request."""
        data = {
            "price": Decimal("8.99")
        }
        
        request = ProductUpdateRequest(**data)
        assert request.price == Decimal("8.99")
        assert request.name is None  # not provided

    def test_product_search_request_valid(self):
        """Test valid product search request."""
        data = {
            "query": "tomatoes",
            "category": "vegetables",
            "min_price": Decimal("1.00"),
            "max_price": Decimal("10.00"),
            "tags": ["organic", "local"],
            "sort_by": "price",
            "sort_order": "asc",
            "limit": 10,
            "offset": 0
        }
        
        request = ProductSearchRequest(**data)
        assert request.query == "tomatoes"
        assert request.min_price == Decimal("1.00")
        assert request.sort_by == "price"

    def test_product_search_request_invalid_price_range(self):
        """Test product search with invalid price range."""
        with pytest.raises(ValidationError) as exc_info:
            ProductSearchRequest(
                min_price=Decimal("10.00"),
                max_price=Decimal("5.00")  # max < min
            )
        
        assert "Maximum price must be greater than minimum price" in str(exc_info.value)

    def test_product_search_request_invalid_sort(self):
        """Test product search with invalid sort parameters."""
        with pytest.raises(ValidationError) as exc_info:
            ProductSearchRequest(
                sort_by="invalid_field"
            )
        
        assert "String should match pattern" in str(exc_info.value)

    def test_inventory_update_request_valid(self):
        """Test valid inventory update request."""
        data = {
            "quantity_change": 50,
            "change_type": "restock",
            "reason": "New shipment received",
            "reference_id": 123
        }
        
        request = InventoryUpdateRequest(**data)
        assert request.quantity_change == 50
        assert request.change_type == "restock"
        assert request.reason == "New shipment received"

    def test_inventory_update_request_invalid_change_type(self):
        """Test inventory update with invalid change type."""
        with pytest.raises(ValidationError) as exc_info:
            InventoryUpdateRequest(
                quantity_change=50,
                change_type="invalid_type"
            )
        
        assert "String should match pattern" in str(exc_info.value)

    def test_tag_normalization(self):
        """Test that tags are normalized to lowercase."""
        data = {
            "name": "Test Product",
            "price": Decimal("5.99"),
            "quantity_available": 100,
            "tags": ["ORGANIC", "Local", "FRESH"]
        }
        
        request = ProductCreateRequest(**data)
        assert request.tags == ["organic", "local", "fresh"]

    def test_string_field_trimming(self):
        """Test that string fields are trimmed."""
        data = {
            "name": "  Test Product  ",
            "description": "  A test description  ",
            "category": "  vegetables  ",
            "price": Decimal("5.99"),
            "quantity_available": 100
        }
        
        request = ProductCreateRequest(**data)
        assert request.name == "Test Product"
        assert request.description == "A test description"
        assert request.category == "vegetables"