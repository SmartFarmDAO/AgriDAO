"""
Order management service with comprehensive status tracking and business logic.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal

from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException

from ..models import (
    Order, OrderItem, OrderStatus, PaymentStatus, OrderStatusHistory,
    Product, User, Farmer
)
from ..database import engine
from .notification_service import NotificationService


class OrderService:
    """Service for managing orders with comprehensive status tracking."""
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    def create_order(
        self,
        buyer_id: int,
        items: List[Dict[str, Any]],
        shipping_address: Dict[str, Any],
        subtotal: Decimal,
        platform_fee: Decimal,
        shipping_fee: Decimal = Decimal("0.00"),
        tax_amount: Decimal = Decimal("0.00")
    ) -> Order:
        """Create a new order with initial status tracking."""
        
        with Session(engine) as session:
            # Calculate total
            total = subtotal + platform_fee + shipping_fee + tax_amount
            
            # Create order
            order = Order(
                buyer_id=buyer_id,
                status=OrderStatus.PENDING,
                subtotal=subtotal,
                platform_fee=platform_fee,
                shipping_fee=shipping_fee,
                tax_amount=tax_amount,
                total=total,
                shipping_address=shipping_address,
                payment_status=PaymentStatus.UNPAID
            )
            
            session.add(order)
            session.commit()
            session.refresh(order)
            
            # Create order items
            for item_data in items:
                # Get product and farmer info
                product = session.get(Product, item_data["product_id"])
                if not product:
                    raise HTTPException(status_code=400, detail=f"Product {item_data['product_id']} not found")
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item_data["product_id"],
                    quantity=Decimal(str(item_data["quantity"])),
                    unit_price=Decimal(str(item_data["unit_price"])),
                    farmer_id=product.farmer_id,
                    fulfillment_status="pending"
                )
                session.add(order_item)
            
            session.commit()
            
            # Create initial status history
            self._create_status_history(
                session=session,
                order_id=order.id,
                status=OrderStatus.PENDING,
                previous_status=None,
                notes="Order created",
                created_by=buyer_id
            )
            
            session.commit()
            session.refresh(order)
            
            # Return a detached copy with the ID populated
            return Order(
                id=order.id,
                buyer_id=order.buyer_id,
                status=order.status,
                subtotal=order.subtotal,
                platform_fee=order.platform_fee,
                shipping_fee=order.shipping_fee,
                tax_amount=order.tax_amount,
                total=order.total,
                payment_status=order.payment_status,
                shipping_address=order.shipping_address,
                created_at=order.created_at,
                updated_at=order.updated_at
            )
    
    def update_order_status(
        self,
        order_id: int,
        new_status: OrderStatus,
        user_id: int,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Order:
        """Update order status with validation and history tracking."""
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Validate status transition
            if not self._is_valid_status_transition(order.status, new_status):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status transition from {order.status} to {new_status}"
                )
            
            previous_status = order.status
            order.status = new_status
            order.updated_at = datetime.utcnow()
            
            # Update specific timestamps based on status
            if new_status == OrderStatus.DELIVERED:
                order.delivered_at = datetime.utcnow()
            elif new_status == OrderStatus.CANCELLED:
                order.cancelled_at = datetime.utcnow()
                if notes:
                    order.cancellation_reason = notes
            
            session.add(order)
            
            # Create status history entry
            self._create_status_history(
                session=session,
                order_id=order_id,
                status=new_status,
                previous_status=previous_status,
                notes=notes,
                created_by=user_id,
                metadata=metadata or {}
            )
            
            session.commit()
            session.refresh(order)
            
            # Send notifications
            self._send_status_update_notifications(order, previous_status, new_status)
            
            return order
    
    def update_payment_status(
        self,
        order_id: int,
        payment_status: PaymentStatus,
        payment_intent_id: Optional[str] = None
    ) -> Order:
        """Update payment status and trigger automatic status updates."""
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            order.payment_status = payment_status
            order.updated_at = datetime.utcnow()
            
            if payment_intent_id:
                order.stripe_payment_intent_id = payment_intent_id
            
            session.add(order)
            
            # Auto-update order status based on payment
            if payment_status == PaymentStatus.PAID and order.status == OrderStatus.PENDING:
                order.status = OrderStatus.CONFIRMED
                self._create_status_history(
                    session=session,
                    order_id=order_id,
                    status=OrderStatus.CONFIRMED,
                    previous_status=OrderStatus.PENDING,
                    notes="Payment confirmed - order automatically confirmed",
                    metadata={"payment_intent_id": payment_intent_id}
                )
            
            session.commit()
            session.refresh(order)
            
            return order
    
    def get_order_with_details(self, order_id: int, user_id: int) -> Dict[str, Any]:
        """Get order with full details including items and status history."""
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Check access permissions
            if not self._user_can_access_order(order, user_id):
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Get order items with product details
            items_query = select(OrderItem, Product, Farmer).join(
                Product, OrderItem.product_id == Product.id
            ).outerjoin(
                Farmer, OrderItem.farmer_id == Farmer.id
            ).where(OrderItem.order_id == order_id)
            
            items_result = session.exec(items_query).all()
            
            # Get status history
            history_query = select(OrderStatusHistory, User).outerjoin(
                User, OrderStatusHistory.created_by == User.id
            ).where(OrderStatusHistory.order_id == order_id).order_by(
                OrderStatusHistory.created_at.desc()
            )
            
            history_result = session.exec(history_query).all()
            
            # Format response
            return {
                "id": order.id,
                "status": order.status,
                "payment_status": order.payment_status,
                "subtotal": float(order.subtotal),
                "platform_fee": float(order.platform_fee),
                "shipping_fee": float(order.shipping_fee),
                "tax_amount": float(order.tax_amount),
                "total": float(order.total),
                "shipping_address": order.shipping_address,
                "tracking_number": order.tracking_number,
                "notes": order.notes,
                "estimated_delivery_date": order.estimated_delivery_date.isoformat() if order.estimated_delivery_date else None,
                "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
                "cancelled_at": order.cancelled_at.isoformat() if order.cancelled_at else None,
                "cancellation_reason": order.cancellation_reason,
                "created_at": order.created_at.isoformat(),
                "updated_at": order.updated_at.isoformat(),
                "items": [
                    {
                        "id": item.id,
                        "product_id": item.product_id,
                        "product_name": product.name,
                        "quantity": float(item.quantity),
                        "unit_price": float(item.unit_price),
                        "fulfillment_status": item.fulfillment_status,
                        "farmer_name": farmer.name if farmer else None,
                        "farmer_id": item.farmer_id,
                        "shipped_at": item.shipped_at.isoformat() if item.shipped_at else None,
                        "delivered_at": item.delivered_at.isoformat() if item.delivered_at else None
                    }
                    for item, product, farmer in items_result
                ],
                "status_history": [
                    {
                        "id": history.id,
                        "status": history.status,
                        "previous_status": history.previous_status,
                        "notes": history.notes,
                        "created_by_name": user.name if user else None,
                        "metadata": history.status_metadata,
                        "created_at": history.created_at.isoformat()
                    }
                    for history, user in history_result
                ]
            }
    
    def get_user_orders(
        self,
        user_id: int,
        status_filter: Optional[List[OrderStatus]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get orders for a user with optional filtering."""
        
        with Session(engine) as session:
            query = select(Order).where(Order.buyer_id == user_id)
            
            if status_filter:
                query = query.where(Order.status.in_(status_filter))
            
            query = query.order_by(Order.created_at.desc()).offset(offset).limit(limit)
            
            orders = session.exec(query).all()
            
            return [
                {
                    "id": order.id,
                    "status": order.status,
                    "payment_status": order.payment_status,
                    "total": float(order.total),
                    "created_at": order.created_at.isoformat(),
                    "updated_at": order.updated_at.isoformat()
                }
                for order in orders
            ]
    
    def get_farmer_orders(
        self,
        farmer_id: int,
        status_filter: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get orders containing products from a specific farmer."""
        
        with Session(engine) as session:
            # Get orders that contain items from this farmer
            query = select(Order).join(
                OrderItem, Order.id == OrderItem.order_id
            ).where(OrderItem.farmer_id == farmer_id)
            
            if status_filter:
                query = query.where(Order.status.in_(status_filter))
            
            query = query.order_by(Order.created_at.desc()).offset(offset).limit(limit)
            
            orders = session.exec(query).all()
            
            # Get items for each order that belong to this farmer
            result = []
            for order in orders:
                items_query = select(OrderItem, Product).join(
                    Product, OrderItem.product_id == Product.id
                ).where(
                    and_(
                        OrderItem.order_id == order.id,
                        OrderItem.farmer_id == farmer_id
                    )
                )
                
                items_result = session.exec(items_query).all()
                
                result.append({
                    "id": order.id,
                    "status": order.status,
                    "payment_status": order.payment_status,
                    "total": float(order.total),
                    "created_at": order.created_at.isoformat(),
                    "updated_at": order.updated_at.isoformat(),
                    "items": [
                        {
                            "id": item.id,
                            "product_name": product.name,
                            "quantity": float(item.quantity),
                            "unit_price": float(item.unit_price),
                            "fulfillment_status": item.fulfillment_status
                        }
                        for item, product in items_result
                    ]
                })
            
            return result
    
    def update_item_fulfillment_status(
        self,
        order_item_id: int,
        farmer_id: int,
        fulfillment_status: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update fulfillment status for a specific order item."""
        
        with Session(engine) as session:
            order_item = session.get(OrderItem, order_item_id)
            if not order_item:
                raise HTTPException(status_code=404, detail="Order item not found")
            
            # Verify farmer owns this item
            if order_item.farmer_id != farmer_id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            order_item.fulfillment_status = fulfillment_status
            
            # Update timestamps based on status
            if fulfillment_status == "shipped":
                order_item.shipped_at = datetime.utcnow()
            elif fulfillment_status == "delivered":
                order_item.delivered_at = datetime.utcnow()
            
            session.add(order_item)
            
            # Check if all items in the order are fulfilled
            order = session.get(Order, order_item.order_id)
            all_items = session.exec(
                select(OrderItem).where(OrderItem.order_id == order.id)
            ).all()
            
            # Auto-update order status based on item fulfillment
            if fulfillment_status == "shipped" and all(
                item.fulfillment_status in ["shipped", "delivered"] for item in all_items
            ):
                if order.status == OrderStatus.PROCESSING:
                    self.update_order_status(
                        order_id=order.id,
                        new_status=OrderStatus.SHIPPED,
                        user_id=farmer_id,
                        notes="All items shipped"
                    )
            
            session.commit()
            session.refresh(order_item)
            
            return {
                "id": order_item.id,
                "fulfillment_status": order_item.fulfillment_status,
                "shipped_at": order_item.shipped_at.isoformat() if order_item.shipped_at else None,
                "delivered_at": order_item.delivered_at.isoformat() if order_item.delivered_at else None,
                "message": f"Item fulfillment status updated to {fulfillment_status}"
            }
    
    def bulk_update_order_status(
        self,
        order_ids: List[int],
        new_status: OrderStatus,
        farmer_id: int,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Bulk update status for multiple orders."""
        
        with Session(engine) as session:
            # Verify farmer has access to all orders
            orders = []
            for order_id in order_ids:
                order = session.get(Order, order_id)
                if not order:
                    raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
                
                # Check if farmer has items in this order
                farmer_items = session.exec(
                    select(OrderItem).where(
                        and_(
                            OrderItem.order_id == order_id,
                            OrderItem.farmer_id == farmer_id
                        )
                    )
                ).first()
                
                if not farmer_items:
                    raise HTTPException(
                        status_code=403, 
                        detail=f"Access denied for order {order_id}"
                    )
                
                orders.append(order)
            
            # Update all orders
            updated_orders = []
            for order in orders:
                try:
                    updated_order = self.update_order_status(
                        order_id=order.id,
                        new_status=new_status,
                        user_id=farmer_id,
                        notes=notes
                    )
                    updated_orders.append({
                        "id": updated_order.id,
                        "status": updated_order.status,
                        "success": True
                    })
                except Exception as e:
                    updated_orders.append({
                        "id": order.id,
                        "status": order.status,
                        "success": False,
                        "error": str(e)
                    })
            
            return {
                "updated_orders": updated_orders,
                "total_processed": len(order_ids),
                "successful_updates": len([o for o in updated_orders if o["success"]]),
                "failed_updates": len([o for o in updated_orders if not o["success"]])
            }
    
    def get_farmer_order_analytics(
        self,
        farmer_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get analytics for farmer's orders."""
        
        with Session(engine) as session:
            # Base query for farmer's order items
            base_query = select(OrderItem, Order).join(
                Order, OrderItem.order_id == Order.id
            ).where(OrderItem.farmer_id == farmer_id)
            
            if start_date:
                base_query = base_query.where(Order.created_at >= start_date)
            if end_date:
                base_query = base_query.where(Order.created_at <= end_date)
            
            items_and_orders = session.exec(base_query).all()
            
            # Calculate metrics
            total_orders = len(set(order.id for _, order in items_and_orders))
            total_revenue = sum(
                float(item.quantity * item.unit_price) 
                for item, _ in items_and_orders
            )
            
            # Status breakdown
            status_counts = {}
            for _, order in items_and_orders:
                status = order.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Fulfillment status breakdown
            fulfillment_counts = {}
            for item, _ in items_and_orders:
                status = item.fulfillment_status
                fulfillment_counts[status] = fulfillment_counts.get(status, 0) + 1
            
            return {
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "average_order_value": total_revenue / total_orders if total_orders > 0 else 0,
                "order_status_breakdown": status_counts,
                "fulfillment_status_breakdown": fulfillment_counts,
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                }
            }
    
    def generate_shipping_label(
        self,
        order_id: int,
        farmer_id: int,
        shipping_service: str = "standard"
    ) -> Dict[str, Any]:
        """Generate shipping label for an order (placeholder implementation)."""
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Verify farmer has items in this order
            farmer_items = session.exec(
                select(OrderItem).where(
                    and_(
                        OrderItem.order_id == order_id,
                        OrderItem.farmer_id == farmer_id
                    )
                )
            ).all()
            
            if not farmer_items:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # This is a placeholder - in a real implementation, you would integrate
            # with shipping providers like UPS, FedEx, USPS, etc.
            tracking_number = f"AGRI{order_id}{farmer_id}{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Update order with tracking number
            self.update_tracking_number(
                order_id=order_id,
                tracking_number=tracking_number,
                user_id=farmer_id,
                estimated_delivery_date=datetime.utcnow() + timedelta(days=3)
            )
            
            return {
                "tracking_number": tracking_number,
                "shipping_service": shipping_service,
                "label_url": f"https://api.agridao.com/shipping/labels/{tracking_number}",
                "estimated_delivery": (datetime.utcnow() + timedelta(days=3)).isoformat(),
                "message": "Shipping label generated successfully"
            }
    
    def get_order_tracking_info(self, order_id: int, user_id: int) -> Dict[str, Any]:
        """Get detailed tracking information for an order."""
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Check access permissions
            if not self._user_can_access_order(order, user_id):
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Get status history
            history_query = select(OrderStatusHistory).where(
                OrderStatusHistory.order_id == order_id
            ).order_by(OrderStatusHistory.created_at.asc())
            
            status_history = session.exec(history_query).all()
            
            # Calculate estimated delivery if not set
            estimated_delivery = order.estimated_delivery_date
            if not estimated_delivery and order.status == OrderStatus.SHIPPED:
                # Default to 3 days from shipped date
                shipped_history = next(
                    (h for h in status_history if h.status == OrderStatus.SHIPPED),
                    None
                )
                if shipped_history:
                    estimated_delivery = shipped_history.created_at + timedelta(days=3)
            
            return {
                "order_id": order.id,
                "current_status": order.status,
                "payment_status": order.payment_status,
                "tracking_number": order.tracking_number,
                "estimated_delivery_date": estimated_delivery.isoformat() if estimated_delivery else None,
                "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
                "shipping_address": order.shipping_address,
                "tracking_timeline": [
                    {
                        "status": history.status,
                        "timestamp": history.created_at.isoformat(),
                        "notes": history.notes,
                        "is_current": history.status == order.status
                    }
                    for history in status_history
                ],
                "can_cancel": order.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED],
                "can_modify": order.status == OrderStatus.PENDING
            }
    
    def modify_order_shipping_address(
        self,
        order_id: int,
        user_id: int,
        new_address: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Modify shipping address for a pending order."""
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Check permissions
            if order.buyer_id != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Check if modification is allowed
            if order.status != OrderStatus.PENDING:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot modify order with status {order.status}"
                )
            
            old_address = order.shipping_address
            order.shipping_address = new_address
            order.updated_at = datetime.utcnow()
            
            session.add(order)
            
            # Create status history entry
            self._create_status_history(
                session=session,
                order_id=order_id,
                status=order.status,
                previous_status=order.status,
                notes="Shipping address updated",
                created_by=user_id,
                metadata={
                    "old_address": old_address,
                    "new_address": new_address
                }
            )
            
            session.commit()
            
            return {
                "order_id": order.id,
                "updated_address": new_address,
                "message": "Shipping address updated successfully"
            }
    
    def request_order_cancellation(
        self,
        order_id: int,
        user_id: int,
        reason: str
    ) -> Dict[str, Any]:
        """Request order cancellation (buyer-initiated)."""
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Check permissions
            if order.buyer_id != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Check if cancellation is allowed
            if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot cancel order with status {order.status}"
                )
            
            # For confirmed orders, create a cancellation request
            if order.status == OrderStatus.CONFIRMED:
                # Create status history for cancellation request
                self._create_status_history(
                    session=session,
                    order_id=order_id,
                    status=order.status,  # Keep current status
                    previous_status=order.status,
                    notes=f"Cancellation requested by buyer: {reason}",
                    created_by=user_id,
                    metadata={"cancellation_requested": True, "reason": reason}
                )
                
                session.commit()
                
                return {
                    "order_id": order.id,
                    "status": "cancellation_requested",
                    "message": "Cancellation request submitted. Admin will review and process."
                }
            else:
                # For pending orders, cancel immediately
                return self.cancel_order(order_id, user_id, reason)
    
    def search_user_orders(
        self,
        user_id: int,
        search_query: Optional[str] = None,
        status_filter: Optional[List[OrderStatus]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search and filter user orders with advanced criteria."""
        
        with Session(engine) as session:
            # Base query
            query = select(Order).where(Order.buyer_id == user_id)
            
            # Apply filters
            if status_filter:
                query = query.where(Order.status.in_(status_filter))
            
            if date_from:
                query = query.where(Order.created_at >= date_from)
            
            if date_to:
                query = query.where(Order.created_at <= date_to)
            
            # Text search in order items (product names)
            if search_query:
                query = query.join(OrderItem).join(Product).where(
                    Product.name.ilike(f"%{search_query}%")
                )
            
            # Get total count
            total_query = select(func.count()).select_from(query.subquery())
            total_count = session.exec(total_query).one()
            
            # Apply pagination and ordering
            query = query.order_by(Order.created_at.desc()).offset(offset).limit(limit)
            
            orders = session.exec(query).all()
            
            # Format results
            results = []
            for order in orders:
                # Get order items
                items_query = select(OrderItem, Product).join(
                    Product, OrderItem.product_id == Product.id
                ).where(OrderItem.order_id == order.id)
                
                items_result = session.exec(items_query).all()
                
                results.append({
                    "id": order.id,
                    "status": order.status,
                    "payment_status": order.payment_status,
                    "total": float(order.total),
                    "created_at": order.created_at.isoformat(),
                    "updated_at": order.updated_at.isoformat(),
                    "tracking_number": order.tracking_number,
                    "items_preview": [
                        {
                            "product_name": product.name,
                            "quantity": float(item.quantity)
                        }
                        for item, product in items_result[:3]  # Show first 3 items
                    ],
                    "total_items": len(items_result)
                })
            
            return {
                "orders": results,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(results) < total_count
            }
    
    def create_order_review(
        self,
        order_id: int,
        user_id: int,
        rating: int,
        review_text: Optional[str] = None,
        is_anonymous: bool = False
    ) -> Dict[str, Any]:
        """Create a review for a completed order."""
        
        from ..models import OrderReview  # Import here to avoid circular imports
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Check permissions
            if order.buyer_id != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Check if order is completed
            if order.status != OrderStatus.DELIVERED:
                raise HTTPException(
                    status_code=400,
                    detail="Can only review delivered orders"
                )
            
            # Check if review already exists
            existing_review = session.exec(
                select(OrderReview).where(
                    and_(
                        OrderReview.order_id == order_id,
                        OrderReview.buyer_id == user_id
                    )
                )
            ).first()
            
            if existing_review:
                raise HTTPException(
                    status_code=400,
                    detail="Review already exists for this order"
                )
            
            # Create review
            review = OrderReview(
                order_id=order_id,
                buyer_id=user_id,
                rating=rating,
                review_text=review_text,
                is_anonymous=is_anonymous,
                is_verified_purchase=True
            )
            
            session.add(review)
            session.commit()
            session.refresh(review)
            
            return {
                "id": review.id,
                "order_id": order_id,
                "rating": rating,
                "review_text": review_text,
                "is_anonymous": is_anonymous,
                "created_at": review.created_at.isoformat(),
                "message": "Review created successfully"
            }
    
    def get_order_reviews(
        self,
        order_id: int,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get reviews for an order."""
        
        from ..models import OrderReview  # Import here to avoid circular imports
        
        with Session(engine) as session:
            # Get reviews with user info (if not anonymous)
            query = select(OrderReview, User).outerjoin(
                User, and_(
                    OrderReview.buyer_id == User.id,
                    OrderReview.is_anonymous == False
                )
            ).where(OrderReview.order_id == order_id).order_by(
                OrderReview.created_at.desc()
            ).offset(offset).limit(limit)
            
            reviews_result = session.exec(query).all()
            
            # Get total count
            total_count = session.exec(
                select(func.count()).select_from(
                    select(OrderReview).where(OrderReview.order_id == order_id).subquery()
                )
            ).one()
            
            reviews = []
            for review, user in reviews_result:
                reviews.append({
                    "id": review.id,
                    "rating": review.rating,
                    "review_text": review.review_text,
                    "reviewer_name": user.name if user and not review.is_anonymous else "Anonymous",
                    "is_verified_purchase": review.is_verified_purchase,
                    "helpful_votes": review.helpful_votes,
                    "created_at": review.created_at.isoformat()
                })
            
            return {
                "reviews": reviews,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(reviews) < total_count
            }
    
    def update_tracking_number(
        self,
        order_id: int,
        tracking_number: str,
        user_id: int,
        estimated_delivery_date: Optional[datetime] = None
    ) -> Order:
        """Update order tracking number and estimated delivery."""
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            order.tracking_number = tracking_number
            order.updated_at = datetime.utcnow()
            
            if estimated_delivery_date:
                order.estimated_delivery_date = estimated_delivery_date
            
            session.add(order)
            
            # Auto-update to shipped if not already
            if order.status in [OrderStatus.CONFIRMED, OrderStatus.PROCESSING]:
                order.status = OrderStatus.SHIPPED
                self._create_status_history(
                    session=session,
                    order_id=order_id,
                    status=OrderStatus.SHIPPED,
                    previous_status=order.status,
                    notes=f"Tracking number added: {tracking_number}",
                    created_by=user_id,
                    metadata={"tracking_number": tracking_number}
                )
            
            session.commit()
            
            return order
    
    def cancel_order(
        self,
        order_id: int,
        user_id: int,
        reason: str,
        refund_amount: Optional[Decimal] = None
    ) -> Order:
        """Cancel an order with proper validation and refund handling."""
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Validate cancellation is allowed
            if order.status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot cancel order with status {order.status}"
                )
            
            # Check user permissions
            if not self._user_can_modify_order(order, user_id):
                raise HTTPException(status_code=403, detail="Access denied")
            
            previous_status = order.status
            order.status = OrderStatus.CANCELLED
            order.cancelled_at = datetime.utcnow()
            order.cancellation_reason = reason
            order.updated_at = datetime.utcnow()
            
            session.add(order)
            
            # Create status history
            self._create_status_history(
                session=session,
                order_id=order_id,
                status=OrderStatus.CANCELLED,
                previous_status=previous_status,
                notes=f"Order cancelled: {reason}",
                created_by=user_id,
                metadata={"refund_amount": float(refund_amount) if refund_amount else None}
            )
            
            session.commit()
            
            return order
    
    def _create_status_history(
        self,
        session: Session,
        order_id: int,
        status: OrderStatus,
        previous_status: Optional[OrderStatus],
        notes: Optional[str] = None,
        created_by: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OrderStatusHistory:
        """Create a status history entry."""
        
        history = OrderStatusHistory(
            order_id=order_id,
            status=status,
            previous_status=previous_status,
            notes=notes,
            created_by=created_by,
            status_metadata=metadata or {}
        )
        
        session.add(history)
        return history
    
    def _is_valid_status_transition(
        self,
        current_status: OrderStatus,
        new_status: OrderStatus
    ) -> bool:
        """Validate if a status transition is allowed."""
        
        # Define valid transitions
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED, OrderStatus.CANCELLED],
            OrderStatus.DELIVERED: [],  # Terminal state
            OrderStatus.CANCELLED: [],  # Terminal state
            OrderStatus.REFUNDED: []   # Terminal state
        }
        
        return new_status in valid_transitions.get(current_status, [])
    
    def _user_can_access_order(self, order: Order, user_id: int) -> bool:
        """Check if user can access order details."""
        
        with Session(engine) as session:
            # Buyer can always access their orders
            if order.buyer_id == user_id:
                return True
            
            # Check if user is a farmer with items in this order
            farmer_check = session.exec(
                select(OrderItem).where(
                    and_(
                        OrderItem.order_id == order.id,
                        OrderItem.farmer_id == user_id
                    )
                )
            ).first()
            
            if farmer_check:
                return True
            
            # Check if user is admin
            user = session.get(User, user_id)
            if user and user.role.value == "admin":
                return True
            
            return False
    
    def _user_can_modify_order(self, order: Order, user_id: int) -> bool:
        """Check if user can modify order."""
        
        with Session(engine) as session:
            # Buyer can modify their own orders
            if order.buyer_id == user_id:
                return True
            
            # Admin can modify any order
            user = session.get(User, user_id)
            if user and user.role.value == "admin":
                return True
            
            return False
    
    def _send_status_update_notifications(
        self,
        order: Order,
        previous_status: OrderStatus,
        new_status: OrderStatus
    ) -> None:
        """Send notifications for status updates."""
        
        # Define notification messages
        status_messages = {
            OrderStatus.CONFIRMED: "Your order has been confirmed and is being prepared.",
            OrderStatus.PROCESSING: "Your order is being processed and will ship soon.",
            OrderStatus.SHIPPED: "Your order has been shipped and is on its way.",
            OrderStatus.DELIVERED: "Your order has been delivered. Thank you for your purchase!",
            OrderStatus.CANCELLED: "Your order has been cancelled."
        }
        
        message = status_messages.get(new_status)
        if message:
            self.notification_service.send_order_status_update(
                order_id=order.id,
                new_status=new_status.value,
                message=message
            )