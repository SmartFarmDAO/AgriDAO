"""
Unit tests for inventory service.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from decimal import Decimal
from fastapi import HTTPException

from app.models import Product, InventoryHistory, ProductStatus, OrderItem
from app.services.inventory_service import InventoryManager


class TestInventoryManager:
    """Test inventory manager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.manager = InventoryManager(self.mock_session)

    def test_update_stock_success(self):
        """Test successful stock update."""
        # Mock existing product
        mock_product = Product(
            id=1,
            name="Test Product",
            quantity_available=100,
            status=ProductStatus.ACTIVE
        )
        
        self.mock_session.get.return_value = mock_product
        
        result = self.manager.update_stock(
            product_id=1,
            quantity_change=50,
            change_type="restock",
            reason="New shipment",
            user_id=1
        )
        
        # Verify stock was updated
        assert mock_product.quantity_available == 150
        
        # Verify session operations
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        
        # Verify history record was created
        added_history = self.mock_session.add.call_args[0][0]
        assert isinstance(added_history, InventoryHistory)
        assert added_history.product_id == 1
        assert added_history.quantity_change == 50
        assert added_history.change_type == "restock"

    def test_update_stock_insufficient_inventory(self):
        """Test stock update with insufficient inventory."""
        # Mock existing product with low stock
        mock_product = Product(
            id=1,
            quantity_available=10,
            status=ProductStatus.ACTIVE
        )
        
        self.mock_session.get.return_value = mock_product
        
        with pytest.raises(HTTPException) as exc_info:
            self.manager.update_stock(
                product_id=1,
                quantity_change=-20,  # More than available
                change_type="sale"
            )
        
        assert exc_info.value.status_code == 400
        assert "Insufficient inventory" in str(exc_info.value.detail)

    def test_update_stock_product_not_found(self):
        """Test stock update for non-existent product."""
        self.mock_session.get.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            self.manager.update_stock(
                product_id=999,
                quantity_change=10,
                change_type="restock"
            )
        
        assert exc_info.value.status_code == 404
        assert "Product not found" in str(exc_info.value.detail)

    def test_update_stock_auto_status_change_to_out_of_stock(self):
        """Test automatic status change when stock becomes zero."""
        # Mock product with some stock
        mock_product = Product(
            id=1,
            quantity_available=10,
            status=ProductStatus.ACTIVE
        )
        
        self.mock_session.get.return_value = mock_product
        
        self.manager.update_stock(
            product_id=1,
            quantity_change=-10,  # Reduce to zero
            change_type="sale"
        )
        
        # Verify status changed to out of stock
        assert mock_product.status == ProductStatus.OUT_OF_STOCK

    def test_update_stock_auto_status_change_to_active(self):
        """Test automatic status change when stock is replenished."""
        # Mock product that's out of stock
        mock_product = Product(
            id=1,
            quantity_available=0,
            status=ProductStatus.OUT_OF_STOCK
        )
        
        self.mock_session.get.return_value = mock_product
        
        self.manager.update_stock(
            product_id=1,
            quantity_change=10,  # Add stock
            change_type="restock"
        )
        
        # Verify status changed to active
        assert mock_product.status == ProductStatus.ACTIVE

    def test_reserve_stock_success(self):
        """Test successful stock reservation."""
        mock_product = Product(
            id=1,
            quantity_available=100,
            status=ProductStatus.ACTIVE
        )
        
        self.mock_session.get.return_value = mock_product
        
        result = self.manager.reserve_stock(
            product_id=1,
            quantity=10,
            order_id=123
        )
        
        assert result is True
        assert mock_product.quantity_available == 90

    def test_reserve_stock_insufficient(self):
        """Test stock reservation with insufficient inventory."""
        mock_product = Product(
            id=1,
            quantity_available=5,
            status=ProductStatus.ACTIVE
        )
        
        self.mock_session.get.return_value = mock_product
        
        result = self.manager.reserve_stock(
            product_id=1,
            quantity=10,  # More than available
            order_id=123
        )
        
        assert result is False

    def test_release_stock_success(self):
        """Test successful stock release."""
        mock_product = Product(
            id=1,
            quantity_available=90,
            status=ProductStatus.ACTIVE
        )
        
        self.mock_session.get.return_value = mock_product
        
        result = self.manager.release_stock(
            product_id=1,
            quantity=10,
            order_id=123,
            reason="Order cancelled"
        )
        
        assert result is True
        assert mock_product.quantity_available == 100

    def test_restock_product(self):
        """Test product restocking."""
        mock_product = Product(
            id=1,
            quantity_available=50,
            status=ProductStatus.ACTIVE
        )
        
        self.mock_session.get.return_value = mock_product
        
        result = self.manager.restock_product(
            product_id=1,
            quantity=25,
            reason="Weekly delivery",
            user_id=1
        )
        
        assert mock_product.quantity_available == 75

    def test_adjust_stock(self):
        """Test stock adjustment to specific quantity."""
        mock_product = Product(
            id=1,
            quantity_available=100,
            status=ProductStatus.ACTIVE
        )
        
        self.mock_session.get.return_value = mock_product
        
        result = self.manager.adjust_stock(
            product_id=1,
            new_quantity=80,
            reason="Inventory count adjustment",
            user_id=1
        )
        
        assert mock_product.quantity_available == 80

    def test_mark_expired_stock(self):
        """Test marking stock as expired."""
        mock_product = Product(
            id=1,
            quantity_available=100,
            status=ProductStatus.ACTIVE
        )
        
        self.mock_session.get.return_value = mock_product
        
        result = self.manager.mark_expired_stock(
            product_id=1,
            quantity=10,
            reason="Expired products removed",
            user_id=1
        )
        
        assert mock_product.quantity_available == 90

    def test_get_inventory_history(self):
        """Test getting inventory history."""
        mock_history = [
            InventoryHistory(
                id=1,
                product_id=1,
                change_type="restock",
                quantity_change=50,
                created_at=datetime.utcnow()
            ),
            InventoryHistory(
                id=2,
                product_id=1,
                change_type="sale",
                quantity_change=-10,
                created_at=datetime.utcnow()
            )
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_history
        self.mock_session.exec.return_value = mock_result
        
        with patch('app.services.inventory_service.select') as mock_select:
            result = self.manager.get_inventory_history(
                product_id=1,
                days=30,
                limit=100
            )
        
        assert len(result) == 2
        self.mock_session.exec.assert_called_once()

    def test_get_low_stock_products(self):
        """Test getting low stock products."""
        mock_products = [
            Product(id=1, name="Low Stock 1", quantity_available=5),
            Product(id=2, name="Low Stock 2", quantity_available=8)
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_products
        self.mock_session.exec.return_value = mock_result
        
        with patch('app.services.inventory_service.select') as mock_select, \
             patch.object(self.manager, '_calculate_days_remaining') as mock_calc, \
             patch.object(self.manager, 'get_inventory_history') as mock_history:
            
            mock_calc.return_value = 3
            mock_history.return_value = []
            
            result = self.manager.get_low_stock_products(threshold=10)
        
        assert len(result) == 2
        assert result[0]['product'] == mock_products[0]
        assert 'days_remaining' in result[0]
        assert 'alert_level' in result[0]

    def test_get_stock_movements_summary(self):
        """Test getting stock movements summary."""
        mock_movements = [
            InventoryHistory(
                change_type="restock",
                quantity_change=50,
                created_at=datetime.utcnow()
            ),
            InventoryHistory(
                change_type="sale",
                quantity_change=-10,
                created_at=datetime.utcnow()
            ),
            InventoryHistory(
                change_type="sale",
                quantity_change=-5,
                created_at=datetime.utcnow()
            )
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_movements
        self.mock_session.exec.return_value = mock_result
        
        with patch('app.services.inventory_service.select') as mock_select:
            result = self.manager.get_stock_movements_summary(days=30)
        
        assert result['total_movements'] == 3
        assert result['by_type']['restock']['count'] == 1
        assert result['by_type']['sale']['count'] == 2
        assert result['net_change'] == 35  # 50 - 10 - 5

    def test_get_expiring_products(self):
        """Test getting expiring products."""
        mock_products = [
            Product(
                id=1,
                name="Expiring Soon",
                expiry_date=datetime.utcnow() + timedelta(days=3),
                quantity_available=10
            )
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_products
        self.mock_session.exec.return_value = mock_result
        
        with patch('app.services.inventory_service.select') as mock_select:
            result = self.manager.get_expiring_products(days_ahead=7)
        
        assert len(result) == 1
        assert result[0].name == "Expiring Soon"

    def test_bulk_update_inventory_success(self):
        """Test successful bulk inventory update."""
        mock_product = Product(
            id=1,
            quantity_available=100,
            status=ProductStatus.ACTIVE
        )
        
        self.mock_session.get.return_value = mock_product
        
        updates = [
            {
                'product_id': 1,
                'quantity_change': 10,
                'change_type': 'restock',
                'reason': 'Bulk restock'
            }
        ]
        
        result = self.manager.bulk_update_inventory(updates, user_id=1)
        
        assert result['total_processed'] == 1
        assert len(result['successful']) == 1
        assert len(result['failed']) == 0
        assert result['successful'][0]['product_id'] == 1

    def test_bulk_update_inventory_with_failures(self):
        """Test bulk inventory update with some failures."""
        # First call succeeds, second fails (product not found)
        self.mock_session.get.side_effect = [
            Product(id=1, quantity_available=100, status=ProductStatus.ACTIVE),
            None  # Product not found
        ]
        
        updates = [
            {'product_id': 1, 'quantity_change': 10},
            {'product_id': 999, 'quantity_change': 5}  # Non-existent product
        ]
        
        result = self.manager.bulk_update_inventory(updates, user_id=1)
        
        assert result['total_processed'] == 2
        assert len(result['successful']) == 1
        assert len(result['failed']) == 1
        assert result['failed'][0]['product_id'] == 999

    def test_calculate_days_remaining_with_sales_data(self):
        """Test calculating days remaining with sales data."""
        mock_sales = [
            InventoryHistory(quantity_change=-5, created_at=datetime.utcnow()),
            InventoryHistory(quantity_change=-3, created_at=datetime.utcnow() - timedelta(days=1)),
            InventoryHistory(quantity_change=-2, created_at=datetime.utcnow() - timedelta(days=2))
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_sales
        self.mock_session.exec.return_value = mock_result
        
        with patch('app.services.inventory_service.select') as mock_select:
            result = self.manager._calculate_days_remaining(product_id=1, current_stock=30)
        
        # Total sold: 10, Days with sales: 3, Avg daily: 3.33, Stock: 30
        # Expected: 30 / 3.33 ≈ 9 days
        assert result == 9

    def test_calculate_days_remaining_no_sales_data(self):
        """Test calculating days remaining with no sales data."""
        mock_result = Mock()
        mock_result.all.return_value = []
        self.mock_session.exec.return_value = mock_result
        
        with patch('app.services.inventory_service.select') as mock_select:
            result = self.manager._calculate_days_remaining(product_id=1, current_stock=30)
        
        assert result is None

    def test_get_alert_level(self):
        """Test getting alert levels."""
        assert self.manager._get_alert_level(0, 10) == "critical"
        assert self.manager._get_alert_level(2, 10) == "high"  # 2 <= 10 * 0.3
        assert self.manager._get_alert_level(5, 10) == "medium"  # 5 <= 10 * 0.6
        assert self.manager._get_alert_level(8, 10) == "low"

    def test_process_order_inventory_success(self):
        """Test successful order inventory processing."""
        mock_order_items = [
            OrderItem(product_id=1, quantity=5, order_id=123),
            OrderItem(product_id=2, quantity=3, order_id=123)
        ]
        
        mock_products = [
            Product(id=1, quantity_available=100, status=ProductStatus.ACTIVE),
            Product(id=2, quantity_available=50, status=ProductStatus.ACTIVE)
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_order_items
        self.mock_session.exec.return_value = mock_result
        self.mock_session.get.side_effect = mock_products
        
        with patch('app.services.inventory_service.select') as mock_select:
            result = self.manager.process_order_inventory(order_id=123)
        
        assert result is True
        # Verify stock was reserved
        assert mock_products[0].quantity_available == 95
        assert mock_products[1].quantity_available == 47

    def test_cancel_order_inventory_success(self):
        """Test successful order inventory cancellation."""
        mock_order_items = [
            OrderItem(product_id=1, quantity=5, order_id=123),
            OrderItem(product_id=2, quantity=3, order_id=123)
        ]
        
        mock_products = [
            Product(id=1, quantity_available=95, status=ProductStatus.ACTIVE),
            Product(id=2, quantity_available=47, status=ProductStatus.ACTIVE)
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_order_items
        self.mock_session.exec.return_value = mock_result
        self.mock_session.get.side_effect = mock_products
        
        with patch('app.services.inventory_service.select') as mock_select:
            result = self.manager.cancel_order_inventory(order_id=123)
        
        assert result is True
        # Verify stock was released
        assert mock_products[0].quantity_available == 100
        assert mock_products[1].quantity_available == 50