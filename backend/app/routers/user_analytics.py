"""
User-specific analytics router for personalized insights.
Provides buyer and farmer specific analytics and recommendations.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..deps import get_current_user
from ..models import User, UserRole
from ..services.metrics_service import MetricsCollector
from ..services.redis_service import redis_service
from ..services.order_service import OrderService
from ..services.product_service import ProductService

router = APIRouter()
order_service = OrderService()
product_service = ProductService()


class BuyerAnalyticsResponse(BaseModel):
    """Response model for buyer analytics."""
    total_spent: float
    total_orders: int
    average_order_value: float
    favorite_categories: List[str]
    purchase_history: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    spending_trends: Dict[str, Any]


class FarmerAnalyticsResponse(BaseModel):
    """Response model for enhanced farmer analytics."""
    total_revenue: float
    total_orders: int
    average_order_value: float
    top_products: List[Dict[str, Any]]
    monthly_revenue: List[Dict[str, Any]]
    customer_insights: Dict[str, Any]
    performance_metrics: Dict[str, Any]


@router.get("/buyer", response_model=BuyerAnalyticsResponse)
async def get_buyer_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive buyer analytics for the current user."""
    
    if current_user.role.value != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can access this endpoint")
    
    try:
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=90)
        if not end_date:
            end_date = datetime.utcnow()
            
        # Get buyer-specific analytics
        analytics = await _calculate_buyer_analytics(
            current_user.id, start_date, end_date
        )
        
        # Get personalized recommendations
        recommendations = await _get_buyer_recommendations(current_user.id)
        
        return BuyerAnalyticsResponse(
            total_spent=analytics["total_spent"],
            total_orders=analytics["total_orders"],
            average_order_value=analytics["average_order_value"],
            favorite_categories=analytics["favorite_categories"],
            purchase_history=analytics["purchase_history"],
            recommendations=recommendations,
            spending_trends=analytics["spending_trends"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve buyer analytics: {str(e)}"
        )


@router.get("/farmer/enhanced")
async def get_enhanced_farmer_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get enhanced farmer analytics with customer insights."""
    
    if current_user.role.value != "farmer":
        raise HTTPException(status_code=403, detail="Only farmers can access this endpoint")
    
    try:
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=90)
        if not end_date:
            end_date = datetime.utcnow()
            
        # Get basic farmer analytics
        basic_analytics = order_service.get_farmer_order_analytics(
            farmer_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Enhance with customer insights
        enhanced_analytics = await _enhance_farmer_analytics(
            current_user.id, start_date, end_date, basic_analytics
        )
        
        return enhanced_analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve enhanced farmer analytics: {str(e)}"
        )


@router.get("/buyer/recommendations")
async def get_buyer_recommendations(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """Get personalized product recommendations for buyers."""
    
    if current_user.role.value != "buyer":
        raise HTTPException(status_code=403, detail="Only buyers can access this endpoint")
    
    try:
        recommendations = await _get_buyer_recommendations(current_user.id, limit)
        return {"recommendations": recommendations}
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve recommendations: {str(e)}"
        )


async def _calculate_buyer_analytics(
    user_id: int, 
    start_date: datetime, 
    end_date: datetime
) -> Dict[str, Any]:
    """Calculate detailed buyer analytics."""
    
    from ..models import Order, OrderItem, Product
    from sqlmodel import select, func
    from ..database import engine
    
    with engine.Session() as session:
        # Get user's orders
        orders_query = select(Order).where(
            Order.buyer_id == user_id,
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.payment_status.value == "paid"
        )
        orders = session.exec(orders_query).all()
        
        total_spent = sum(order.total_amount for order in orders)
        total_orders = len(orders)
        average_order_value = total_spent / total_orders if total_orders > 0 else 0
        
        # Get favorite categories
        categories_query = select(
            Product.category,
            func.sum(OrderItem.quantity).label('total_quantity')
        ).join(OrderItem).join(Order).where(
            Order.buyer_id == user_id,
            Order.created_at >= start_date,
            Order.created_at <= end_date
        ).group_by(Product.category)
        
        category_data = session.exec(categories_query).all()
        favorite_categories = [cat.category for cat in category_data if cat.category]
        
        # Get purchase history
        purchase_history = []
        for order in orders:
            items = session.exec(
                select(OrderItem).where(OrderItem.order_id == order.id)
            ).all()
            
            purchase_history.append({
                "order_id": order.id,
                "date": order.created_at.isoformat(),
                "total": float(order.total_amount),
                "items": [
                    {
                        "product_name": item.product.name,
                        "quantity": item.quantity,
                        "price": float(item.price)
                    }
                    for item in items
                ]
            })
        
        # Calculate spending trends
        monthly_spending = {}
        for order in orders:
            month_key = order.created_at.strftime("%Y-%m")
            if month_key not in monthly_spending:
                monthly_spending[month_key] = 0
            monthly_spending[month_key] += float(order.total_amount)
        
        spending_trends = {
            "monthly_spending": monthly_spending,
            "trend": "increasing" if len(monthly_spending) > 1 and list(monthly_spending.values())[-1] > list(monthly_spending.values())[0] else "stable"
        }
        
        return {
            "total_spent": total_spent,
            "total_orders": total_orders,
            "average_order_value": average_order_value,
            "favorite_categories": favorite_categories,
            "purchase_history": purchase_history,
            "spending_trends": spending_trends
        }


async def _get_buyer_recommendations(
    user_id: int, 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Generate personalized product recommendations for buyers."""
    
    from ..models import Order, OrderItem, Product
    from sqlmodel import select
    from ..database import engine
    
    with engine.Session() as session:
        # Get user's purchase history
        user_orders = session.exec(
            select(Order).where(
                Order.buyer_id == user_id,
                Order.payment_status.value == "paid"
            )
        ).all()
        
        # Get categories user has purchased from
        purchased_categories = set()
        for order in user_orders:
            items = session.exec(
                select(OrderItem).where(OrderItem.order_id == order.id)
            ).all()
            for item in items:
                purchased_categories.add(item.product.category)
        
        # Get products from similar categories user hasn't purchased
        recommendations = []
        for category in purchased_categories:
            products = session.exec(
                select(Product).where(
                    Product.category == category,
                    Product.status.value == "active"
                ).limit(limit // len(purchased_categories) + 1)
            ).all()
            
            for product in products:
                # Check if user hasn't already purchased this product
                existing_purchase = session.exec(
                    select(OrderItem).join(Order).where(
                        Order.buyer_id == user_id,
                        OrderItem.product_id == product.id
                    )
                ).first()
                
                if not existing_purchase:
                    recommendations.append({
                        "product_id": product.id,
                        "name": product.name,
                        "price": float(product.price),
                        "category": product.category,
                        "image_url": product.images[0].url if product.images else None,
                        "reason": f"Based on your interest in {category}"
                    })
        
        return recommendations[:limit]


async def _enhance_farmer_analytics(
    farmer_id: int,
    start_date: datetime,
    end_date: datetime,
    basic_analytics: Dict[str, Any]
) -> Dict[str, Any]:
    """Enhance farmer analytics with customer insights."""
    
    from ..models import Order, OrderItem, User
    from sqlmodel import select, func
    from ..database import engine
    
    with engine.Session() as session:
        # Get customer insights
        customer_query = select(
            Order.buyer_id,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_spent')
        ).where(
            Order.farmer_id == farmer_id,
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.payment_status.value == "paid"
        ).group_by(Order.buyer_id)
        
        customers = session.exec(customer_query).all()
        
        customer_insights = {
            "total_customers": len(customers),
            "repeat_customers": len([c for c in customers if c.order_count > 1]),
            "top_customers": []
        }
        
        # Get top customers
        for customer in sorted(customers, key=lambda x: x.total_spent, reverse=True)[:5]:
            user = session.get(User, customer.buyer_id)
            customer_insights["top_customers"].append({
                "user_id": customer.buyer_id,
                "name": user.name if user else "Unknown",
                "total_spent": float(customer.total_spent),
                "order_count": customer.order_count
            })
        
        # Monthly revenue trends
        monthly_revenue_query = select(
            func.date_trunc('month', Order.created_at).label('month'),
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('order_count')
        ).where(
            Order.farmer_id == farmer_id,
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.payment_status.value == "paid"
        ).group_by('month').order_by('month')
        
        monthly_data = session.exec(monthly_revenue_query).all()
        
        monthly_revenue = [
            {
                "month": month.month.strftime("%Y-%m"),
                "revenue": float(month.revenue),
                "orders": month.order_count
            }
            for month in monthly_data
        ]
        
        return {
            **basic_analytics,
            "customer_insights": customer_insights,
            "monthly_revenue": monthly_revenue,
            "performance_metrics": {
                "customer_retention_rate": customer_insights["repeat_customers"] / customer_insights["total_customers"] if customer_insights["total_customers"] > 0 else 0,
                "average_customer_value": basic_analytics.get("total_revenue", 0) / customer_insights["total_customers"] if customer_insights["total_customers"] > 0 else 0
            }
        }