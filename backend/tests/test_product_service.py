"""
Unit tests for product service.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.models import Product, User, ProductStatus, UserRole
from app.services.product_service import ProductService
from app.services.product_validation import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductSearchRequest,
    InventoryUpdateRequest
)


class TestProductService:
    """Test product service operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.service = ProductService(self.mock_session)

    def test_create_product_success(self):
        """Test successful product creation."""
        # Mock user (farmer)
        mock_user = User(id=1, role=UserRole.FARMER, name="Test Farmer")
        self.mock_session.get.return_value = mock_user
        
        # Mock no existing SKU
        self.mock_session.exec.return_value.first.return_value = None
        
        product_data = ProductCreateRequest(
            name="Test Product",
            description="A test product",
            category="vegetables",
            price=Decimal("10.99"),
            quantity_available=100,
            unit="kg",
            sku="TEST-001"
        )
        
        # Mock product creation
        mock_product = Product(
            id=1,
            name=product_data.name,
            price=product_data.price,
            quantity_available=product_data.quantity_available
        )
        self.mock_session.refresh = Mock()
        
        result = self.service.create_product(product_data, user_id=1)
        
        # Verify session operations
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called()
        assert self.mock_session.add.call_args[0][0].name == "Test Product"

    def test_create_product_unauthorized_user(self):
        """Test product creation by unauthorized user."""
        # Mock user (buyer - not authorized)
        mock_user = User(id=1, role=UserRole.BUYER, name="Test Buyer")
        self.mock_session.get.return_value = mock_user
        
        product_data = ProductCreateRequest(
            name="Test Product",
            price=Decimal("10.99"),
            quantity_available=100
        )
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.create_product(product_data, user_id=1)
        
        assert exc_info.value.status_code == 403
        assert "Only farmers can create products" in str(exc_info.value.detail)

    def test_create_product_duplicate_sku(self):
        """Test product creation with duplicate SKU."""
        # Mock user (farmer)
        mock_user = User(id=1, role=UserRole.FARMER, name="Test Farmer")
        self.mock_session.get.return_value = mock_user
        
        # Mock existing product with same SKU
        existing_product = Product(id=2, sku="TEST-001")
        self.mock_session.exec.return_value.first.return_value = existing_product
        
        product_data = ProductCreateRequest(
            name="Test Product",
            price=Decimal("10.99"),
            quantity_available=100,
            sku="TEST-001"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.create_product(product_data, user_id=1)
        
        assert exc_info.value.status_code == 400
        assert "SKU already exists" in str(exc_info.value.detail)

    def test_update_product_success(self):
        """Test successful product update."""
        # Mock existing product
        mock_product = Product(
            id=1,
            name="Original Product",
            price=Decimal("10.99"),
            quantity_available=100,
            farmer_id=1,
            status=ProductStatus.ACTIVE
        )
        
        # Mock user (owner)
        mock_user = User(id=1, role=UserRole.FARMER, name="Test Farmer")
        
        self.mock_session.get.side_effect = [mock_product, mock_user]
        self.mock_session.exec.return_value.first.return_value = None  # No SKU conflict
        
        update_data = ProductUpdateRequest(
            name="Updated Product",
            price=Decimal("12.99")
        )
        
        result = self.service.update_product(1, update_data, user_id=1)
        
        # Verify updates
        assert mock_product.name == "Updated Product"
        assert mock_product.price == Decimal("12.99")
        self.mock_session.commit.assert_called()

    def test_update_product_not_found(self):
        """Test updating non-existent product."""
        self.mock_session.get.return_value = None
        
        update_data = ProductUpdateRequest(name="Updated Product")
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.update_product(999, update_data, user_id=1)
        
        assert exc_info.value.status_code == 404
        assert "Product not found" in str(exc_info.value.detail)

    def test_update_product_unauthorized(self):
        """Test updating product by unauthorized user."""
        # Mock existing product owned by farmer 1
        mock_product = Product(id=1, farmer_id=1)
        
        # Mock different user (farmer 2)
        mock_user = User(id=2, role=UserRole.FARMER, name="Other Farmer")
        
        self.mock_session.get.side_effect = [mock_product, mock_user]
        
        update_data = ProductUpdateRequest(name="Updated Product")
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.update_product(1, update_data, user_id=2)
        
        assert exc_info.value.status_code == 403
        assert "Not authorized to update this product" in str(exc_info.value.detail)

    def test_update_product_auto_status_change(self):
        """Test automatic status change when quantity becomes zero."""
        # Mock existing product
        mock_product = Product(
            id=1,
            quantity_available=10,
            farmer_id=1,
            status=ProductStatus.ACTIVE
        )
        
        # Mock user (owner)
        mock_user = User(id=1, role=UserRole.FARMER, name="Test Farmer")
        
        self.mock_session.get.side_effect = [mock_product, mock_user]
        self.mock_session.exec.return_value.first.return_value = None
        
        update_data = ProductUpdateRequest(quantity_available=0)
        
        result = self.service.update_product(1, update_data, user_id=1)
        
        # Verify status changed to out of stock
        assert mock_product.status == ProductStatus.OUT_OF_STOCK

    def test_delete_product_success(self):
        """Test successful product deletion (soft delete)."""
        # Mock existing product
        mock_product = Product(id=1, farmer_id=1, status=ProductStatus.ACTIVE)
        
        # Mock user (owner)
        mock_user = User(id=1, role=UserRole.FARMER, name="Test Farmer")
        
        self.mock_session.get.side_effect = [mock_product, mock_user]
        
        result = self.service.delete_product(1, user_id=1)
        
        assert result is True
        assert mock_product.status == ProductStatus.INACTIVE
        self.mock_session.commit.assert_called()

    def test_search_products_basic(self):
        """Test basic product search."""
        # Mock search results
        mock_products = [
            Product(id=1, name="Product 1"),
            Product(id=2, name="Product 2")
        ]
        
        # Mock query execution
        mock_query_result = Mock()
        mock_query_result.all.return_value = mock_products
        self.mock_session.exec.side_effect = [5, mock_query_result]  # count, then products
        
        search_params = ProductSearchRequest(
            query="test",
            limit=10,
            offset=0
        )
        
        with patch('app.services.product_service.select') as mock_select, \
             patch('app.services.product_service.func') as mock_func:
            
            result = self.service.search_products(search_params)
        
        assert len(result["products"]) == 2
        assert result["total_count"] == 5
        assert result["has_more"] is True

    def test_update_inventory_success(self):
        """Test successful inventory update."""
        # Mock existing product
        mock_product = Product(
            id=1,
            quantity_available=100,
            farmer_id=1,
            status=ProductStatus.ACTIVE
        )
        
        # Mock user (owner)
        mock_user = User(id=1, role=UserRole.FARMER, name="Test Farmer")
        
        self.mock_session.get.side_effect = [mock_product, mock_user]
        
        inventory_update = InventoryUpdateRequest(
            quantity_change=50,
            change_type="restock",
            reason="New shipment"
        )
        
        result = self.service.update_inventory(1, inventory_update, user_id=1)
        
        # Verify inventory updated
        assert mock_product.quantity_available == 150
        self.mock_session.commit.assert_called()

    def test_update_inventory_insufficient_stock(self):
        """Test inventory update with insufficient stock."""
        # Mock existing product
        mock_product = Product(
            id=1,
            quantity_available=10,
            farmer_id=1
        )
        
        # Mock user (owner)
        mock_user = User(id=1, role=UserRole.FARMER, name="Test Farmer")
        
        self.mock_session.get.side_effect = [mock_product, mock_user]
        
        inventory_update = InventoryUpdateRequest(
            quantity_change=-20,  # More than available
            change_type="sale"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            self.service.update_inventory(1, inventory_update, user_id=1)
        
        assert exc_info.value.status_code == 400
        assert "Insufficient inventory" in str(exc_info.value.detail)

    def test_get_low_stock_products(self):
        """Test getting low stock products."""
        mock_products = [
            Product(id=1, name="Low Stock 1", quantity_available=5),
            Product(id=2, name="Low Stock 2", quantity_available=8)
        ]
        
        mock_query_result = Mock()
        mock_query_result.all.return_value = mock_products
        self.mock_session.exec.return_value = mock_query_result
        
        with patch('app.services.product_service.select') as mock_select:
            result = self.service.get_low_stock_products(threshold=10)
        
        assert len(result) == 2

    def test_get_categories(self):
        """Test getting product categories."""
        mock_categories = ["vegetables", "fruits", "grains"]
        
        mock_query_result = Mock()
        mock_query_result.all.return_value = mock_categories
        self.mock_session.exec.return_value = mock_query_result
        
        with patch('app.services.product_service.select') as mock_select:
            result = self.service.get_categories()
        
        assert result == mock_categories

    def test_create_inventory_history(self):
        """Test creating inventory history record."""
        history = self.service._create_inventory_history(
            product_id=1,
            change_type="restock",
            quantity_change=50,
            previous_quantity=100,
            new_quantity=150,
            reason="Test restock",
            created_by=1
        )
        
        # Verify history record was added
        self.mock_session.add.assert_called()
        self.mock_session.commit.assert_called()
        
        # Verify the added record has correct data
        added_history = self.mock_session.add.call_args[0][0]
        assert added_history.product_id == 1
        assert added_history.change_type == "restock"
        assert added_history.quantity_change == 50