"""
Push notification API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.core.auth import get_current_user
from app.core.notifications import notification_manager
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])


class DeviceRegistration(BaseModel):
    device_token: str
    platform: str  # ios, android, web
    device_info: Optional[dict] = None


class NotificationRequest(BaseModel):
    user_id: str
    title: str
    body: str
    data: Optional[dict] = None
    platform: Optional[str] = None


class BulkNotificationRequest(BaseModel):
    user_ids: List[str]
    title: str
    body: str
    data: Optional[dict] = None


class NotificationTemplateRequest(BaseModel):
    name: str
    title_template: str
    body_template: str
    data_template: Optional[dict] = None
    description: Optional[str] = None


class UserPreferenceUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    notification_frequency: Optional[str] = None
    categories: Optional[List[str]] = None


@router.post("/register-device")
async def register_device(
    device: DeviceRegistration,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register a device for push notifications."""
    try:
        success = await notification_manager.register_device(
            str(current_user.id),
            device.device_token,
            device.platform,
            device.device_info
        )
        
        if success:
            return {"message": "Device registered successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to register device")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unregister-device")
async def unregister_device(
    device_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unregister a device from push notifications."""
    try:
        success = await notification_manager.unregister_device(device_token)
        
        if success:
            return {"message": "Device unregistered successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to unregister device")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-notification")
async def send_notification(
    notification: NotificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a push notification to a user."""
    try:
        # Check if current user has permission to send notifications
        # In production, implement proper authorization
        
        success = await notification_manager.send_push_notification(
            notification.user_id,
            notification.title,
            notification.body,
            notification.data,
            notification.platform
        )
        
        if success:
            return {"message": "Notification sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send notification")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-bulk-notifications")
async def send_bulk_notifications(
    notification: BulkNotificationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send bulk notifications to multiple users."""
    try:
        # In production, implement proper authorization
        
        # Process in background to avoid timeout
        background_tasks.add_task(
            notification_manager.send_bulk_notifications,
            notification.user_ids,
            notification.title,
            notification.body,
            notification.data
        )
        
        return {"message": "Bulk notification queued for processing"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-template")
async def create_template(
    template: NotificationTemplateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a notification template."""
    try:
        template_id = await notification_manager.create_notification_template(
            template.name,
            template.title_template,
            template.body_template,
            template.data_template,
            template.description
        )
        
        return {"template_id": template_id, "message": "Template created successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-templated-notification")
async def send_templated_notification(
    user_id: str,
    template_name: str,
    variables: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a notification using a template."""
    try:
        success = await notification_manager.send_templated_notification(
            user_id,
            template_name,
            variables or {}
        )
        
        if success:
            return {"message": "Templated notification sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send templated notification")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-notifications")
async def get_user_notifications(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification history for the current user."""
    try:
        notifications = await notification_manager.get_user_notifications(
            str(current_user.id),
            limit
        )
        
        return {"notifications": notifications}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences")
async def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notification preferences."""
    try:
        # In production, implement proper database queries
        # This is a simplified version
        return {
            "email_notifications": True,
            "push_notifications": True,
            "sms_notifications": False,
            "quiet_hours_start": None,
            "quiet_hours_end": None,
            "notification_frequency": "immediate",
            "categories": ["orders", "shipments", "payments", "bids"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preferences")
async def update_preferences(
    preferences: UserPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user notification preferences."""
    try:
        # In production, implement proper database updates
        return {"message": "Preferences updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process-queue")
async def process_notification_queue(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process queued notifications (admin endpoint)."""
    try:
        # In production, implement proper authorization for admin endpoints
        processed = await notification_manager.process_notification_queue(limit)
        
        return {"processed": processed, "message": f"Processed {processed} notifications"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_notifications(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clean up old notification records (admin endpoint)."""
    try:
        # In production, implement proper authorization for admin endpoints
        deleted = await notification_manager.cleanup_old_notifications(days)
        
        return {"deleted": deleted, "message": f"Cleaned up {deleted} old notifications"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))