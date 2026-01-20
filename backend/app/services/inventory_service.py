"""
Inventory management service for real-time stock tracking and management.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal

from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException

from ..models import Product, InventoryHistory, ProductStatus, User, Order, OrderItem
from ..database import engine
from .product_validation import InventoryUpdateRequest


class InventoryManager:
    """Service class for inventory management operations."""

    def __init__(self, session: Session):
        self.session = session

    def update_stock(
        self,
        product_id: int,
        quantity_change: int,
        change_type: str,
        reason: Optional[str] = None,
        reference_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> Product:
        """Update product stock with history tracking."""
        product = self.session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        old_quantity = product.quantity_available
        new_quantity = old_quantity + quantity_change

        if new_quantity < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient inventory. Available: {old_quantity}, Requested: {abs(quantity_change)}"
            )

        # Update product quantity
        product.quantity_available = new_quantity
        product.updated_at = datetime.utcnow()

        # Auto-update status based on quantity
        old_status = product.status
        if new_quantity == 0 and product.status == ProductStatus.ACTIVE:
            product.status = ProductStatus.OUT_OF_STOCK
        elif new_quantity > 0 and product.status == ProductStatus.OUT_OF_STOCK:
            product.status = ProductStatus.ACTIVE

        # Create inventory history record
        history = InventoryHistory(
            product_id=product_id,
            change_type=change_type,
            quantity_change=quantity_change,
            previous_quantity=old_quantity,
            new_quantity=new_quantity,
            reason=reason,
            reference_id=reference_id,
            created_by=user_id,
            created_at=datetime.utcnow()
        )

        self.session.add(history)
        self.session.commit()
        self.session.refresh(product)

        # Check for low stock alerts
        self._check_low_stock_alert(product)

        return product

    def reserve_stock(self, product_id: int, quantity: int, order_id: int) -> bool:
        """Reserve stock for an order (reduces available quantity)."""
        try:
            self.update_stock(
                product_id=product_id,
                quantity_change=-quantity,
                change_type="sale",
                reason=f"Stock reserved for order #{order_id}",
                reference_id=order_id
            )
            return True
        except HTTPException:
            return False

    def release_stock(self, product_id: int, quantity: int, order_id: int, reason: str = "Order cancelled") -> bool:
        """Release reserved stock back to available inventory."""
        try:
            self.update_stock(
                product_id=product_id,
                quantity_change=quantity,
                change_type="adjustment",
                reason=f"{reason} - Order #{order_id}",
                reference_id=order_id
            )
            return True
        except HTTPException:
            return False

    def restock_product(self, product_id: int, quantity: int, reason: str, user_id: int) -> Product:
        """Add stock to a product."""
        return self.update_stock(
            product_id=product_id,
            quantity_change=quantity,
            change_type="restock",
            reason=reason,
            user_id=user_id
        )

    def adjust_stock(self, product_id: int, new_quantity: int, reason: str, user_id: int) -> Product:
        """Adjust stock to a specific quantity."""
        product = self.session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        quantity_change = new_quantity - product.quantity_available

        return self.update_stock(
            product_id=product_id,
            quantity_change=quantity_change,
            change_type="adjustment",
            reason=reason,
            user_id=user_id
        )

    def mark_expired_stock(self, product_id: int, quantity: int, reason: str, user_id: int) -> Product:
        """Mark stock as expired/damaged."""
        return self.update_stock(
            product_id=product_id,
            quantity_change=-quantity,
            change_type="expired",
            reason=reason,
            user_id=user_id
        )

    def get_inventory_history(
        self,
        product_id: Optional[int] = None,
        farmer_id: Optional[int] = None,
        change_type: Optional[str] = None,
        days: int = 30,
        limit: int = 100
    ) -> List[InventoryHistory]:
        """Get inventory history with filtering options."""
        query = select(InventoryHistory)
        conditions = []

        if product_id:
            conditions.append(InventoryHistory.product_id == product_id)

        if farmer_id:
            # Join with Product to filter by farmer
            query = query.join(Product, InventoryHistory.product_id == Product.id)
            conditions.append(Product.farmer_id == farmer_id)

        if change_type:
            conditions.append(InventoryHistory.change_type == change_type)

        # Filter by date range
        start_date = datetime.utcnow() - timedelta(days=days)
        conditions.append(InventoryHistory.created_at >= start_date)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(InventoryHistory.created_at.desc()).limit(limit)

        return self.session.exec(query).all()

    def get_low_stock_products(
        self,
        farmer_id: Optional[int] = None,
        threshold: int = 10,
        include_out_of_stock: bool = False
    ) -> List[Dict[str, Any]]:
        """Get products with low stock."""
        query = select(Product)
        conditions = [Product.status == ProductStatus.ACTIVE]

        if include_out_of_stock:
            conditions = [
                or_(
                    Product.status == ProductStatus.ACTIVE,
                    Product.status == ProductStatus.OUT_OF_STOCK
                )
            ]

        # Stock level conditions
        if include_out_of_stock:
            conditions.append(Product.quantity_available <= threshold)
        else:
            conditions.append(
                and_(
                    Product.quantity_available <= threshold,
                    Product.quantity_available > 0
                )
            )

        if farmer_id:
            conditions.append(Product.farmer_id == farmer_id)

        query = query.where(and_(*conditions)).order_by(Product.quantity_available.asc())

        products = self.session.exec(query).all()

        # Enrich with additional information
        result = []
        for product in products:
            # Calculate days of stock remaining based on recent sales
            days_remaining = self._calculate_days_remaining(product.id, product.quantity_available)
            
            # Get recent stock changes
            recent_changes = self.get_inventory_history(
                product_id=product.id,
                days=7,
                limit=5
            )

            result.append({
                'product': product,
                'days_remaining': days_remaining,
                'recent_changes': recent_changes,
                'alert_level': self._get_alert_level(product.quantity_available, threshold)
            })

        return result

    def get_stock_movements_summary(
        self,
        farmer_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get summary of stock movements."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(InventoryHistory)
        conditions = [InventoryHistory.created_at >= start_date]

        if farmer_id:
            query = query.join(Product, InventoryHistory.product_id == Product.id)
            conditions.append(Product.farmer_id == farmer_id)

        query = query.where(and_(*conditions))
        movements = self.session.exec(query).all()

        # Aggregate by change type
        summary = {
            'total_movements': len(movements),
            'by_type': {},
            'net_change': 0,
            'period_start': start_date,
            'period_end': datetime.utcnow()
        }

        for movement in movements:
            change_type = movement.change_type
            if change_type not in summary['by_type']:
                summary['by_type'][change_type] = {
                    'count': 0,
                    'total_quantity': 0
                }
            
            summary['by_type'][change_type]['count'] += 1
            summary['by_type'][change_type]['total_quantity'] += movement.quantity_change
            summary['net_change'] += movement.quantity_change

        return summary

    def get_expiring_products(
        self,
        farmer_id: Optional[int] = None,
        days_ahead: int = 7
    ) -> List[Product]:
        """Get products that are expiring soon."""
        expiry_threshold = datetime.utcnow() + timedelta(days=days_ahead)
        
        query = select(Product).where(
            and_(
                Product.expiry_date.is_not(None),
                Product.expiry_date <= expiry_threshold,
                Product.quantity_available > 0,
                Product.status == ProductStatus.ACTIVE
            )
        )

        if farmer_id:
            query = query.where(Product.farmer_id == farmer_id)

        return self.session.exec(query.order_by(Product.expiry_date.asc())).all()

    def bulk_update_inventory(
        self,
        updates: List[Dict[str, Any]],
        user_id: int
    ) -> Dict[str, Any]:
        """Perform bulk inventory updates."""
        results = {
            'successful': [],
            'failed': [],
            'total_processed': len(updates)
        }

        for update in updates:
            try:
                product_id = update['product_id']
                quantity_change = update['quantity_change']
                change_type = update.get('change_type', 'adjustment')
                reason = update.get('reason', 'Bulk update')

                product = self.update_stock(
                    product_id=product_id,
                    quantity_change=quantity_change,
                    change_type=change_type,
                    reason=reason,
                    user_id=user_id
                )

                results['successful'].append({
                    'product_id': product_id,
                    'new_quantity': product.quantity_available
                })

            except Exception as e:
                results['failed'].append({
                    'product_id': update.get('product_id'),
                    'error': str(e)
                })

        return results

    def _calculate_days_remaining(self, product_id: int, current_stock: int) -> Optional[int]:
        """Calculate estimated days of stock remaining based on recent sales."""
        if current_stock <= 0:
            return 0

        # Get sales from last 30 days
        start_date = datetime.utcnow() - timedelta(days=30)
        
        query = select(InventoryHistory).where(
            and_(
                InventoryHistory.product_id == product_id,
                InventoryHistory.change_type == "sale",
                InventoryHistory.created_at >= start_date
            )
        )

        sales = self.session.exec(query).all()
        
        if not sales:
            return None  # No sales data available

        total_sold = sum(abs(sale.quantity_change) for sale in sales)
        days_with_sales = len(set(sale.created_at.date() for sale in sales))

        if days_with_sales == 0:
            return None

        avg_daily_sales = total_sold / days_with_sales
        
        if avg_daily_sales <= 0:
            return None

        return int(current_stock / avg_daily_sales)

    def _get_alert_level(self, current_stock: int, threshold: int) -> str:
        """Get alert level based on stock quantity."""
        if current_stock == 0:
            return "critical"
        elif current_stock <= threshold * 0.3:
            return "high"
        elif current_stock <= threshold * 0.6:
            return "medium"
        else:
            return "low"

    def _check_low_stock_alert(self, product: Product):
        """Check if product needs low stock alert (placeholder for future notification system)."""
        # This would integrate with a notification system
        # For now, just log the alert condition
        if product.quantity_available <= 5:  # Critical threshold
            print(f"CRITICAL: Product {product.name} (ID: {product.id}) has only {product.quantity_available} units left")
        elif product.quantity_available <= 10:  # Warning threshold
            print(f"WARNING: Product {product.name} (ID: {product.id}) is running low with {product.quantity_available} units")

    def process_order_inventory(self, order_id: int) -> bool:
        """Process inventory changes for an order."""
        # Get order items
        query = select(OrderItem).where(OrderItem.order_id == order_id)
        order_items = self.session.exec(query).all()

        if not order_items:
            return False

        try:
            for item in order_items:
                self.reserve_stock(
                    product_id=item.product_id,
                    quantity=int(item.quantity),
                    order_id=order_id
                )
            return True
        except Exception:
            # Rollback any successful reservations
            for item in order_items:
                try:
                    self.release_stock(
                        product_id=item.product_id,
                        quantity=int(item.quantity),
                        order_id=order_id,
                        reason="Order processing failed - rollback"
                    )
                except Exception:
                    pass  # Best effort rollback
            return False

    def cancel_order_inventory(self, order_id: int) -> bool:
        """Release inventory for a cancelled order."""
        # Get order items
        query = select(OrderItem).where(OrderItem.order_id == order_id)
        order_items = self.session.exec(query).all()

        if not order_items:
            return False

        try:
            for item in order_items:
                self.release_stock(
                    product_id=item.product_id,
                    quantity=int(item.quantity),
                    order_id=order_id,
                    reason="Order cancelled"
                )
            return True
        except Exception:
            return False


def get_inventory_manager(session: Session = None) -> InventoryManager:
    """Dependency to get inventory manager."""
    if session is None:
        session = Session(engine)
    return InventoryManager(session)