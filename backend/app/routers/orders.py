"""
Order management API endpoints.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from ..models import User, OrderStatus, PaymentStatus
from ..deps import get_current_user
from ..services.order_service import OrderService


router = APIRouter()
order_service = OrderService()


class OrderStatusUpdateRequest(BaseModel):
    """Request model for updating order status."""
    status: OrderStatus
    notes: Optional[str] = Field(None, max_length=1000)
    metadata: Optional[Dict[str, Any]] = None


class TrackingUpdateRequest(BaseModel):
    """Request model for updating tracking information."""
    tracking_number: str = Field(..., max_length=100)
    estimated_delivery_date: Optional[datetime] = None


class OrderCancellationRequest(BaseModel):
    """Request model for order cancellation."""
    reason: str = Field(..., max_length=500)
    refund_amount: Optional[float] = None


class ShippingAddressUpdateRequest(BaseModel):
    """Request model for updating shipping address."""
    street: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=50)
    zip_code: str = Field(..., max_length=20)
    country: str = Field(default="US", max_length=50)


class OrderReviewRequest(BaseModel):
    """Request model for creating order reviews."""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: Optional[str] = Field(None, max_length=2000, description="Review text")
    is_anonymous: bool = Field(default=False, description="Whether to post anonymously")


@router.get("/orders")
def get_my_orders(
    status: Optional[List[OrderStatus]] = Query(None, description="Filter by order status"),
    limit: int = Query(50, ge=1, le=100, description="Number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip"),
    current_user: User = Depends(get_current_user)
):
    """Get current user's orders with optional filtering."""
    
    try:
        orders = order_service.get_user_orders(
            user_id=current_user.id,
            status_filter=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "orders": orders,
            "total": len(orders),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve orders: {str(e)}")


@router.get("/orders/{order_id}")
def get_order_details(
    order_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific order."""
    
    try:
        order_details = order_service.get_order_with_details(order_id, current_user.id)
        return order_details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve order: {str(e)}")


@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    request: OrderStatusUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update order status (admin or farmer only)."""
    
    # Check permissions - only admin or farmers can update order status
    if current_user.role.value not in ["admin", "farmer"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        updated_order = order_service.update_order_status(
            order_id=order_id,
            new_status=request.status,
            user_id=current_user.id,
            notes=request.notes,
            metadata=request.metadata
        )
        
        return {
            "id": updated_order.id,
            "status": updated_order.status,
            "updated_at": updated_order.updated_at.isoformat(),
            "message": f"Order status updated to {request.status.value}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")


@router.put("/orders/{order_id}/tracking")
def update_tracking_info(
    order_id: int,
    request: TrackingUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update order tracking information (admin or farmer only)."""
    
    # Check permissions
    if current_user.role.value not in ["admin", "farmer"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        updated_order = order_service.update_tracking_number(
            order_id=order_id,
            tracking_number=request.tracking_number,
            user_id=current_user.id,
            estimated_delivery_date=request.estimated_delivery_date
        )
        
        return {
            "id": updated_order.id,
            "tracking_number": updated_order.tracking_number,
            "estimated_delivery_date": updated_order.estimated_delivery_date.isoformat() if updated_order.estimated_delivery_date else None,
            "status": updated_order.status,
            "updated_at": updated_order.updated_at.isoformat(),
            "message": "Tracking information updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update tracking: {str(e)}")


@router.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int,
    request: OrderCancellationRequest,
    current_user: User = Depends(get_current_user)
):
    """Cancel an order."""
    
    try:
        cancelled_order = order_service.cancel_order(
            order_id=order_id,
            user_id=current_user.id,
            reason=request.reason,
            refund_amount=request.refund_amount
        )
        
        return {
            "id": cancelled_order.id,
            "status": cancelled_order.status,
            "cancelled_at": cancelled_order.cancelled_at.isoformat(),
            "cancellation_reason": cancelled_order.cancellation_reason,
            "message": "Order cancelled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")


@router.get("/orders/{order_id}/status-history")
def get_order_status_history(
    order_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get status history for an order."""
    
    try:
        order_details = order_service.get_order_with_details(order_id, current_user.id)
        return {
            "order_id": order_id,
            "status_history": order_details["status_history"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve status history: {str(e)}")


# Buyer-specific endpoints
@router.get("/orders/{order_id}/tracking")
def get_order_tracking(
    order_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get detailed tracking information for an order."""
    
    try:
        tracking_info = order_service.get_order_tracking_info(order_id, current_user.id)
        return tracking_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tracking info: {str(e)}")


@router.put("/orders/{order_id}/shipping-address")
def update_shipping_address(
    order_id: int,
    request: ShippingAddressUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update shipping address for a pending order."""
    
    try:
        result = order_service.modify_order_shipping_address(
            order_id=order_id,
            user_id=current_user.id,
            new_address=request.dict()
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update shipping address: {str(e)}")


@router.post("/orders/{order_id}/request-cancellation")
def request_order_cancellation(
    order_id: int,
    request: OrderCancellationRequest,
    current_user: User = Depends(get_current_user)
):
    """Request order cancellation."""
    
    try:
        result = order_service.request_order_cancellation(
            order_id=order_id,
            user_id=current_user.id,
            reason=request.reason
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to request cancellation: {str(e)}")


@router.get("/orders/search")
def search_orders(
    q: Optional[str] = Query(None, description="Search query for product names"),
    status: Optional[List[OrderStatus]] = Query(None, description="Filter by order status"),
    date_from: Optional[datetime] = Query(None, description="Filter orders from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter orders to this date"),
    limit: int = Query(20, ge=1, le=100, description="Number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip"),
    current_user: User = Depends(get_current_user)
):
    """Search and filter user orders."""
    
    try:
        results = order_service.search_user_orders(
            user_id=current_user.id,
            search_query=q,
            status_filter=status,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search orders: {str(e)}")


@router.post("/orders/{order_id}/review")
def create_order_review(
    order_id: int,
    request: OrderReviewRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a review for a completed order."""
    
    try:
        result = order_service.create_order_review(
            order_id=order_id,
            user_id=current_user.id,
            rating=request.rating,
            review_text=request.review_text,
            is_anonymous=request.is_anonymous
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create review: {str(e)}")


@router.get("/orders/{order_id}/reviews")
def get_order_reviews(
    order_id: int,
    limit: int = Query(10, ge=1, le=50, description="Number of reviews to return"),
    offset: int = Query(0, ge=0, description="Number of reviews to skip")
):
    """Get reviews for an order (public endpoint)."""
    
    try:
        reviews = order_service.get_order_reviews(
            order_id=order_id,
            limit=limit,
            offset=offset
        )
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve reviews: {str(e)}")


# Farmer-specific endpoints
@router.get("/farmer/orders")
def get_farmer_orders(
    status: Optional[List[str]] = Query(None, description="Filter by order status"),
    limit: int = Query(50, ge=1, le=100, description="Number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip"),
    current_user: User = Depends(get_current_user)
):
    """Get orders containing products from the current farmer."""
    
    # Check if user is a farmer
    if current_user.role.value != "farmer":
        raise HTTPException(status_code=403, detail="Only farmers can access this endpoint")
    
    try:
        orders = order_service.get_farmer_orders(
            farmer_id=current_user.id,
            status_filter=status,
            limit=limit,
            offset=offset
        )
        
        return {
            "orders": orders,
            "total": len(orders),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve farmer orders: {str(e)}")


class ItemFulfillmentUpdateRequest(BaseModel):
    """Request model for updating item fulfillment status."""
    fulfillment_status: str = Field(..., pattern="^(pending|processing|shipped|delivered)$")
    notes: Optional[str] = Field(None, max_length=500)


class BulkOrderUpdateRequest(BaseModel):
    """Request model for bulk order updates."""
    order_ids: List[int] = Field(..., min_length=1, max_length=50)
    status: OrderStatus
    notes: Optional[str] = Field(None, max_length=500)


class ShippingLabelRequest(BaseModel):
    """Request model for generating shipping labels."""
    shipping_service: str = Field(default="standard", pattern="^(standard|express|overnight)$")


@router.put("/farmer/orders/items/{item_id}/fulfillment")
def update_item_fulfillment(
    item_id: int,
    request: ItemFulfillmentUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update fulfillment status for a specific order item."""
    
    # Check if user is a farmer
    if current_user.role.value != "farmer":
        raise HTTPException(status_code=403, detail="Only farmers can access this endpoint")
    
    try:
        result = order_service.update_item_fulfillment_status(
            order_item_id=item_id,
            farmer_id=current_user.id,
            fulfillment_status=request.fulfillment_status,
            notes=request.notes
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update fulfillment status: {str(e)}")


@router.put("/farmer/orders/bulk-update")
def bulk_update_orders(
    request: BulkOrderUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Bulk update status for multiple orders."""
    
    # Check if user is a farmer
    if current_user.role.value != "farmer":
        raise HTTPException(status_code=403, detail="Only farmers can access this endpoint")
    
    try:
        result = order_service.bulk_update_order_status(
            order_ids=request.order_ids,
            new_status=request.status,
            farmer_id=current_user.id,
            notes=request.notes
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to bulk update orders: {str(e)}")


@router.get("/farmer/orders/analytics")
def get_farmer_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: User = Depends(get_current_user)
):
    """Get order analytics for the current farmer."""
    
    # Check if user is a farmer
    if current_user.role.value != "farmer":
        raise HTTPException(status_code=403, detail="Only farmers can access this endpoint")
    
    try:
        analytics = order_service.get_farmer_order_analytics(
            farmer_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")


@router.post("/farmer/orders/{order_id}/shipping-label")
def generate_shipping_label(
    order_id: int,
    request: ShippingLabelRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate shipping label for an order."""
    
    # Check if user is a farmer
    if current_user.role.value != "farmer":
        raise HTTPException(status_code=403, detail="Only farmers can access this endpoint")
    
    try:
        result = order_service.generate_shipping_label(
            order_id=order_id,
            farmer_id=current_user.id,
            shipping_service=request.shipping_service
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate shipping label: {str(e)}")


# Admin-specific endpoints
@router.get("/admin/orders")
def get_all_orders(
    status: Optional[List[OrderStatus]] = Query(None, description="Filter by order status"),
    payment_status: Optional[List[PaymentStatus]] = Query(None, description="Filter by payment status"),
    limit: int = Query(50, ge=1, le=100, description="Number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip"),
    current_user: User = Depends(get_current_user)
):
    """Get all orders (admin only)."""
    
    # Check if user is admin
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # This would need to be implemented in the order service
    # For now, return a placeholder
    return {
        "message": "Admin order listing not yet implemented",
        "orders": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


@router.get("/admin/orders/analytics")
def get_order_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: User = Depends(get_current_user)
):
    """Get order analytics (admin only)."""
    
    # Check if user is admin
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # This would need to be implemented in the order service
    # For now, return a placeholder
    return {
        "message": "Order analytics not yet implemented",
        "total_orders": 0,
        "total_revenue": 0.0,
        "average_order_value": 0.0,
        "orders_by_status": {},
        "orders_by_date": []
    }


@router.put("/admin/orders/{order_id}/payment-status")
def update_payment_status(
    order_id: int,
    payment_status: PaymentStatus,
    payment_intent_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Update payment status (admin only)."""
    
    # Check if user is admin
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        updated_order = order_service.update_payment_status(
            order_id=order_id,
            payment_status=payment_status,
            payment_intent_id=payment_intent_id
        )
        
        return {
            "id": updated_order.id,
            "payment_status": updated_order.payment_status,
            "status": updated_order.status,
            "updated_at": updated_order.updated_at.isoformat(),
            "message": f"Payment status updated to {payment_status.value}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update payment status: {str(e)}")