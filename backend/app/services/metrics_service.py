"""
Enhanced metrics collection and aggregation service.
Provides comprehensive platform KPIs, real-time data collection, and caching.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from decimal import Decimal
from enum import Enum
import json
import asyncio
from dataclasses import dataclass

from sqlmodel import Session, select, func, and_, or_
from sqlalchemy import text

from ..database import engine
from ..models import (
    Order, OrderItem, OrderStatus, PaymentStatus, User, UserRole, Product, 
    ProductStatus, Dispute, DisputeStatus, OrderReview, Notification,
    Cart, CartItem, InventoryHistory, FundingRequest
)
from .redis_service import RedisService


class MetricType(str, Enum):
    REVENUE = "revenue"
    ORDERS = "orders"
    USERS = "users"
    PRODUCTS = "products"
    DISPUTES = "disputes"
    ENGAGEMENT = "engagement"
    INVENTORY = "inventory"
    FUNDING = "funding"


class MetricPeriod(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


@dataclass
class MetricValue:
    """Represents a metric value with metadata."""
    value: Union[int, float, Decimal]
    timestamp: datetime
    period: MetricPeriod
    metadata: Optional[Dict[str, Any]] = None


class MetricsCollector:
    """Enhanced metrics collection and aggregation service."""
    
    def __init__(self, redis_service: Optional[RedisService] = None):
        self.redis_service = redis_service or RedisService()
        self.cache_ttl = 300  # 5 minutes default cache
    
    async def get_comprehensive_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_cache: bool = True
    ) -> Dict[str, Any]:
        """Get comprehensive platform metrics."""
        
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        cache_key = f"metrics:comprehensive:{start_date.date()}:{end_date.date()}"
        
        if include_cache:
            cached_data = await self.redis_service.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        
        metrics = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "revenue": await self._get_revenue_metrics(start_date, end_date),
            "orders": await self._get_order_metrics(start_date, end_date),
            "users": await self._get_user_metrics(start_date, end_date),
            "products": await self._get_product_metrics(start_date, end_date),
            "disputes": await self._get_dispute_metrics(start_date, end_date),
            "engagement": await self._get_engagement_metrics(start_date, end_date),
            "inventory": await self._get_inventory_metrics(start_date, end_date),
            "funding": await self._get_funding_metrics(start_date, end_date),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Cache the results
        await self.redis_service.set(
            cache_key, 
            json.dumps(metrics, default=str), 
            expire=self.cache_ttl
        )
        
        return metrics
    
    async def _get_revenue_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate comprehensive revenue metrics."""
        
        with Session(engine) as session:
            # Base query for paid orders in period
            paid_orders_query = select(Order).where(
                and_(
                    Order.payment_status == PaymentStatus.PAID,
                    Order.created_at >= start_date,
                    Order.created_at <= end_date
                )
            )
            paid_orders = session.exec(paid_orders_query).all()
            
            # Calculate basic revenue metrics
            gmv = sum(float(order.total) for order in paid_orders)
            platform_fees = sum(float(order.platform_fee) for order in paid_orders)
            shipping_fees = sum(float(order.shipping_fee) for order in paid_orders)
            tax_collected = sum(float(order.tax_amount) for order in paid_orders)
            
            # Calculate take rate
            take_rate = (platform_fees / gmv) if gmv > 0 else 0
            
            # Revenue by day for trend analysis
            daily_revenue = {}
            for order in paid_orders:
                day_key = order.created_at.date().isoformat()
                if day_key not in daily_revenue:
                    daily_revenue[day_key] = {
                        "gmv": 0,
                        "platform_fees": 0,
                        "order_count": 0
                    }
                daily_revenue[day_key]["gmv"] += float(order.total)
                daily_revenue[day_key]["platform_fees"] += float(order.platform_fee)
                daily_revenue[day_key]["order_count"] += 1
            
            # Average order value
            aov = gmv / len(paid_orders) if paid_orders else 0
            
            # Revenue by farmer (top performers)
            farmer_revenue = {}
            for order in paid_orders:
                order_items = session.exec(
                    select(OrderItem).where(OrderItem.order_id == order.id)
                ).all()
                
                for item in order_items:
                    if item.farmer_id:
                        farmer_id = item.farmer_id
                        item_revenue = float(item.quantity * item.unit_price)
                        
                        if farmer_id not in farmer_revenue:
                            farmer_revenue[farmer_id] = {
                                "revenue": 0,
                                "orders": set(),
                                "items_sold": 0
                            }
                        
                        farmer_revenue[farmer_id]["revenue"] += item_revenue
                        farmer_revenue[farmer_id]["orders"].add(order.id)
                        farmer_revenue[farmer_id]["items_sold"] += float(item.quantity)
            
            # Convert sets to counts for JSON serialization
            top_farmers = []
            for farmer_id, data in farmer_revenue.items():
                top_farmers.append({
                    "farmer_id": farmer_id,
                    "revenue": data["revenue"],
                    "order_count": len(data["orders"]),
                    "items_sold": data["items_sold"]
                })
            
            top_farmers.sort(key=lambda x: x["revenue"], reverse=True)
            
            return {
                "gmv": round(gmv, 2),
                "platform_fees": round(platform_fees, 2),
                "shipping_fees": round(shipping_fees, 2),
                "tax_collected": round(tax_collected, 2),
                "take_rate": round(take_rate, 4),
                "average_order_value": round(aov, 2),
                "daily_revenue": daily_revenue,
                "top_farmers": top_farmers[:10],  # Top 10 farmers by revenue
                "total_paid_orders": len(paid_orders)
            }
    
    async def _get_order_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate comprehensive order metrics."""
        
        with Session(engine) as session:
            # All orders in period
            orders_query = select(Order).where(
                and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date
                )
            )
            orders = session.exec(orders_query).all()
            
            # Order status breakdown
            status_breakdown = {}
            for status in OrderStatus:
                status_breakdown[status.value] = 0
            
            for order in orders:
                status_breakdown[order.status.value] += 1
            
            # Payment status breakdown
            payment_breakdown = {}
            for status in PaymentStatus:
                payment_breakdown[status.value] = 0
            
            for order in orders:
                payment_breakdown[order.payment_status.value] += 1
            
            # Order fulfillment metrics
            fulfillment_times = []
            for order in orders:
                if order.status == OrderStatus.DELIVERED and order.delivered_at:
                    fulfillment_time = (order.delivered_at - order.created_at).days
                    fulfillment_times.append(fulfillment_time)
            
            avg_fulfillment_time = (
                sum(fulfillment_times) / len(fulfillment_times) 
                if fulfillment_times else 0
            )
            
            # Cancellation rate
            cancelled_orders = [o for o in orders if o.status == OrderStatus.CANCELLED]
            cancellation_rate = len(cancelled_orders) / len(orders) if orders else 0
            
            # Orders by day
            daily_orders = {}
            for order in orders:
                day_key = order.created_at.date().isoformat()
                if day_key not in daily_orders:
                    daily_orders[day_key] = 0
                daily_orders[day_key] += 1
            
            return {
                "total_orders": len(orders),
                "status_breakdown": status_breakdown,
                "payment_breakdown": payment_breakdown,
                "average_fulfillment_days": round(avg_fulfillment_time, 1),
                "cancellation_rate": round(cancellation_rate, 4),
                "daily_orders": daily_orders,
                "cancelled_orders": len(cancelled_orders)
            }
    
    async def _get_user_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate comprehensive user metrics."""
        
        with Session(engine) as session:
            # New users in period
            new_users_query = select(User).where(
                and_(
                    User.created_at >= start_date,
                    User.created_at <= end_date
                )
            )
            new_users = session.exec(new_users_query).all()
            
            # Total users
            total_users = session.exec(select(func.count(User.id))).first()
            
            # User role breakdown
            role_breakdown = {}
            for role in UserRole:
                count = session.exec(
                    select(func.count(User.id)).where(User.role == role)
                ).first()
                role_breakdown[role.value] = count
            
            # Active users (users with orders in period)
            active_users_query = select(func.count(func.distinct(Order.buyer_id))).where(
                and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date
                )
            )
            active_users = session.exec(active_users_query).first()
            
            # User registration by day
            daily_registrations = {}
            for user in new_users:
                day_key = user.created_at.date().isoformat()
                if day_key not in daily_registrations:
                    daily_registrations[day_key] = 0
                daily_registrations[day_key] += 1
            
            # User retention (users who made multiple orders)
            repeat_buyers_query = select(
                Order.buyer_id,
                func.count(Order.id).label('order_count')
            ).where(
                and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date
                )
            ).group_by(Order.buyer_id).having(func.count(Order.id) > 1)
            
            repeat_buyers = session.exec(repeat_buyers_query).all()
            
            return {
                "total_users": total_users,
                "new_users": len(new_users),
                "active_users": active_users,
                "role_breakdown": role_breakdown,
                "daily_registrations": daily_registrations,
                "repeat_buyers": len(repeat_buyers),
                "user_retention_rate": len(repeat_buyers) / active_users if active_users > 0 else 0
            }
    
    async def _get_product_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate comprehensive product metrics."""
        
        with Session(engine) as session:
            # Total products
            total_products = session.exec(select(func.count(Product.id))).first()
            
            # Products by status
            status_breakdown = {}
            for status in ProductStatus:
                count = session.exec(
                    select(func.count(Product.id)).where(Product.status == status)
                ).first()
                status_breakdown[status.value] = count
            
            # New products in period
            new_products_query = select(Product).where(
                and_(
                    Product.created_at >= start_date,
                    Product.created_at <= end_date
                )
            )
            new_products = session.exec(new_products_query).all()
            
            # Product performance (sales in period)
            product_sales_query = select(
                OrderItem.product_id,
                func.sum(OrderItem.quantity).label('total_quantity'),
                func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue'),
                func.count(func.distinct(OrderItem.order_id)).label('order_count')
            ).join(Order).where(
                and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date,
                    Order.payment_status == PaymentStatus.PAID
                )
            ).group_by(OrderItem.product_id)
            
            product_sales = session.exec(product_sales_query).all()
            
            # Top selling products
            top_products = []
            for sale in product_sales:
                product = session.get(Product, sale.product_id)
                if product:
                    top_products.append({
                        "product_id": sale.product_id,
                        "product_name": product.name,
                        "quantity_sold": float(sale.total_quantity),
                        "revenue": float(sale.total_revenue),
                        "order_count": sale.order_count
                    })
            
            top_products.sort(key=lambda x: x["revenue"], reverse=True)
            
            # Category breakdown
            category_query = select(
                Product.category,
                func.count(Product.id).label('product_count')
            ).where(Product.category.isnot(None)).group_by(Product.category)
            
            categories = session.exec(category_query).all()
            category_breakdown = {cat.category: cat.product_count for cat in categories}
            
            return {
                "total_products": total_products,
                "new_products": len(new_products),
                "status_breakdown": status_breakdown,
                "category_breakdown": category_breakdown,
                "top_products": top_products[:10],
                "products_with_sales": len(product_sales)
            }
    
    async def _get_dispute_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate comprehensive dispute metrics."""
        
        with Session(engine) as session:
            # Disputes in period
            disputes_query = select(Dispute).where(
                and_(
                    Dispute.created_at >= start_date,
                    Dispute.created_at <= end_date
                )
            )
            disputes = session.exec(disputes_query).all()
            
            # Status breakdown
            status_breakdown = {}
            for status in DisputeStatus:
                status_breakdown[status.value] = 0
            
            for dispute in disputes:
                status_breakdown[dispute.status.value] += 1
            
            # Resolution time analysis
            resolved_disputes = [
                d for d in disputes 
                if d.status == DisputeStatus.RESOLVED and d.resolved_at
            ]
            
            resolution_times = []
            for dispute in resolved_disputes:
                resolution_time = (dispute.resolved_at - dispute.created_at).days
                resolution_times.append(resolution_time)
            
            avg_resolution_time = (
                sum(resolution_times) / len(resolution_times) 
                if resolution_times else 0
            )
            
            # Dispute rate (disputes per order)
            total_orders_query = select(func.count(Order.id)).where(
                and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date
                )
            )
            total_orders = session.exec(total_orders_query).first()
            
            dispute_rate = len(disputes) / total_orders if total_orders > 0 else 0
            
            return {
                "total_disputes": len(disputes),
                "status_breakdown": status_breakdown,
                "resolved_disputes": len(resolved_disputes),
                "average_resolution_days": round(avg_resolution_time, 1),
                "dispute_rate": round(dispute_rate, 4)
            }
    
    async def _get_engagement_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate user engagement metrics."""
        
        with Session(engine) as session:
            # Cart metrics
            carts_query = select(Cart).where(
                and_(
                    Cart.created_at >= start_date,
                    Cart.created_at <= end_date
                )
            )
            carts = session.exec(carts_query).all()
            
            # Cart conversion rate
            converted_carts = [c for c in carts if c.status.value == "converted"]
            cart_conversion_rate = len(converted_carts) / len(carts) if carts else 0
            
            # Reviews in period
            reviews_query = select(OrderReview).where(
                and_(
                    OrderReview.created_at >= start_date,
                    OrderReview.created_at <= end_date
                )
            )
            reviews = session.exec(reviews_query).all()
            
            # Average rating
            avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
            
            # Notifications sent
            notifications_query = select(func.count(Notification.id)).where(
                and_(
                    Notification.created_at >= start_date,
                    Notification.created_at <= end_date
                )
            )
            notifications_sent = session.exec(notifications_query).first()
            
            return {
                "total_carts": len(carts),
                "cart_conversion_rate": round(cart_conversion_rate, 4),
                "total_reviews": len(reviews),
                "average_rating": round(avg_rating, 2),
                "notifications_sent": notifications_sent
            }
    
    async def _get_inventory_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate inventory metrics."""
        
        with Session(engine) as session:
            # Inventory changes in period
            inventory_changes_query = select(InventoryHistory).where(
                and_(
                    InventoryHistory.created_at >= start_date,
                    InventoryHistory.created_at <= end_date
                )
            )
            inventory_changes = session.exec(inventory_changes_query).all()
            
            # Low stock products (less than 10 units)
            low_stock_query = select(func.count(Product.id)).where(
                and_(
                    Product.quantity_available < 10,
                    Product.status == ProductStatus.ACTIVE
                )
            )
            low_stock_count = session.exec(low_stock_query).first()
            
            # Out of stock products
            out_of_stock_query = select(func.count(Product.id)).where(
                Product.status == ProductStatus.OUT_OF_STOCK
            )
            out_of_stock_count = session.exec(out_of_stock_query).first()
            
            # Total inventory value
            inventory_value_query = select(
                func.sum(Product.quantity_available * Product.price)
            ).where(Product.status == ProductStatus.ACTIVE)
            
            total_inventory_value = session.exec(inventory_value_query).first() or 0
            
            return {
                "inventory_changes": len(inventory_changes),
                "low_stock_products": low_stock_count,
                "out_of_stock_products": out_of_stock_count,
                "total_inventory_value": float(total_inventory_value)
            }
    
    async def _get_funding_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate funding metrics."""
        
        with Session(engine) as session:
            # Funding requests in period
            funding_requests_query = select(FundingRequest).where(
                and_(
                    FundingRequest.created_at >= start_date,
                    FundingRequest.created_at <= end_date
                )
            )
            funding_requests = session.exec(funding_requests_query).all()
            
            # Total funding metrics
            total_requested = sum(fr.amount_needed for fr in funding_requests)
            total_raised = sum(fr.amount_raised for fr in funding_requests)
            
            funding_success_rate = total_raised / total_requested if total_requested > 0 else 0
            
            return {
                "total_requests": len(funding_requests),
                "total_amount_requested": total_requested,
                "total_amount_raised": total_raised,
                "funding_success_rate": round(funding_success_rate, 4)
            }
    
    async def track_event(
        self,
        event_type: str,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track user events for analytics."""
        
        event_data = {
            "event_type": event_type,
            "user_id": user_id,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store in Redis for real-time processing
        await self.redis_service.lpush(
            "events:queue",
            json.dumps(event_data, default=str)
        )
        
        # Set expiration on the queue (keep last 1000 events)
        await self.redis_service.ltrim("events:queue", 0, 999)
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics from Redis cache."""
        
        # Get recent events
        events_data = await self.redis_service.lrange("events:queue", 0, 99)
        events = [json.loads(event) for event in events_data]
        
        # Process events for real-time metrics
        current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        
        hourly_events = {}
        for event in events:
            event_time = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
            if event_time >= current_hour:
                event_type = event["event_type"]
                if event_type not in hourly_events:
                    hourly_events[event_type] = 0
                hourly_events[event_type] += 1
        
        return {
            "current_hour_events": hourly_events,
            "total_events_tracked": len(events),
            "last_updated": datetime.utcnow().isoformat()
        }