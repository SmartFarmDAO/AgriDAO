"""
Notification API endpoints for managing user notifications.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from ..services.notification_service import NotificationService, NotificationType
from ..deps import get_current_user
from ..models import User


router = APIRouter()
notification_service = NotificationService()


class SendNotificationRequest(BaseModel):
    user_id: int
    notification_type: str
    title: str
    message: str
    metadata: Dict[str, Any] = {}


class MarkReadRequest(BaseModel):
    notification_ids: List[int]


@router.get("/notifications")
def get_notifications(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get user's notifications."""
    
    notifications = notification_service.get_user_notifications(
        user_id=current_user.id,
        limit=limit
    )
    
    return {
        "notifications": notifications,
        "total": len(notifications)
    }


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read."""
    
    success = notification_service.mark_notification_read(
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}


@router.post("/notifications/mark_read")
def mark_notifications_read(
    request: MarkReadRequest,
    current_user: User = Depends(get_current_user)
):
    """Mark multiple notifications as read."""
    
    results = []
    for notification_id in request.notification_ids:
        success = notification_service.mark_notification_read(
            notification_id=notification_id,
            user_id=current_user.id
        )
        results.append({
            "notification_id": notification_id,
            "success": success
        })
    
    return {"results": results}


@router.post("/orders/{order_id}/send_confirmation")
def send_order_confirmation(
    order_id: int,
    current_user: User = Depends(get_current_user)
):
    """Send order confirmation notification (admin only)."""
    
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = notification_service.send_order_confirmation(order_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to send notification"))
    
    return result


@router.post("/orders/{order_id}/send_status_update")
def send_order_status_update(
    order_id: int,
    new_status: str,
    message: str = None,
    current_user: User = Depends(get_current_user)
):
    """Send order status update notification (admin only)."""
    
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = notification_service.send_order_status_update(
        order_id=order_id,
        new_status=new_status,
        message=message
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to send notification"))
    
    return result


@router.post("/orders/{order_id}/send_payment_confirmation")
def send_payment_confirmation(
    order_id: int,
    payment_intent_id: str,
    current_user: User = Depends(get_current_user)
):
    """Send payment confirmation notification (admin only)."""
    
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = notification_service.send_payment_confirmation(
        order_id=order_id,
        payment_intent_id=payment_intent_id
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to send notification"))
    
    return result


@router.get("/notification_types")
def get_notification_types():
    """Get available notification types."""
    
    return {
        "notification_types": [
            {
                "value": nt.value,
                "name": nt.value.replace("_", " ").title(),
                "description": _get_notification_description(nt)
            }
            for nt in NotificationType
        ]
    }


def _get_notification_description(notification_type: NotificationType) -> str:
    """Get description for notification type."""
    
    descriptions = {
        NotificationType.ORDER_CONFIRMATION: "Sent when an order is confirmed",
        NotificationType.ORDER_STATUS_UPDATE: "Sent when order status changes",
        NotificationType.PAYMENT_CONFIRMATION: "Sent when payment is processed",
        NotificationType.PAYMENT_FAILED: "Sent when payment fails",
        NotificationType.SHIPPING_UPDATE: "Sent when order ships",
        NotificationType.DELIVERY_CONFIRMATION: "Sent when order is delivered",
        NotificationType.REFUND_PROCESSED: "Sent when refund is processed",
        NotificationType.ACCOUNT_CREATED: "Sent when account is created",
        NotificationType.PASSWORD_RESET: "Sent for password reset",
        NotificationType.EMAIL_VERIFICATION: "Sent for email verification"
    }
    
    return descriptions.get(notification_type, "System notification")