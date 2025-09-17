"""
Push notification system for mobile and web applications.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import messaging, credentials
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.logging import get_logger
from app.database import SessionLocal
from app.models.notification import NotificationDevice, NotificationQueue, NotificationTemplate
from app.models.user import User

logger = get_logger("notifications")


class NotificationManager:
    """Manages push notifications for web and mobile platforms."""
    
    def __init__(self):
        self.firebase_app = None
        self.logger = get_logger("notification_manager")
        
    def initialize_firebase(self, credentials_path: str):
        """Initialize Firebase Admin SDK."""
        try:
            cred = credentials.Certificate(credentials_path)
            self.firebase_app = firebase_admin.initialize_app(cred)
            self.logger.info("Firebase initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    async def register_device(self, user_id: str, device_token: str, platform: str, 
                            device_info: Dict[str, Any] = None) -> bool:
        """Register a device for push notifications."""
        try:
            with SessionLocal() as db:
                # Check if device already exists
                existing = db.query(NotificationDevice).filter(
                    NotificationDevice.device_token == device_token
                ).first()
                
                if existing:
                    # Update existing device
                    existing.user_id = user_id
                    existing.platform = platform
                    existing.device_info = json.dumps(device_info or {})
                    existing.is_active = True
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new device record
                    device = NotificationDevice(
                        user_id=user_id,
                        device_token=device_token,
                        platform=platform,
                        device_info=json.dumps(device_info or {}),
                        is_active=True
                    )
                    db.add(device)
                
                db.commit()
                self.logger.info(f"Device registered for user {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to register device: {e}")
            return False
    
    async def unregister_device(self, device_token: str) -> bool:
        """Unregister a device from push notifications."""
        try:
            with SessionLocal() as db:
                device = db.query(NotificationDevice).filter(
                    NotificationDevice.device_token == device_token
                ).first()
                
                if device:
                    device.is_active = False
                    device.updated_at = datetime.utcnow()
                    db.commit()
                    self.logger.info(f"Device unregistered: {device_token}")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to unregister device: {e}")
            return False
    
    async def send_push_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        data: Dict[str, Any] = None,
        platform: str = None
    ) -> bool:
        """Send a push notification to a user."""
        try:
            with SessionLocal() as db:
                # Get active devices for the user
                devices = db.query(NotificationDevice).filter(
                    and_(
                        NotificationDevice.user_id == user_id,
                        NotificationDevice.is_active == True
                    )
                ).all()
                
                if platform:
                    devices = [d for d in devices if d.platform == platform]
                
                if not devices:
                    self.logger.warning(f"No active devices found for user {user_id}")
                    return False
                
                # Queue notifications for each device
                for device in devices:
                    await self._queue_notification(
                        device.id, title, body, data or {}
                    )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            return False
    
    async def send_bulk_notifications(
        self,
        user_ids: List[str],
        title: str,
        body: str,
        data: Dict[str, Any] = None
    ) -> Dict[str, int]:
        """Send bulk notifications to multiple users."""
        results = {"sent": 0, "failed": 0, "skipped": 0}
        
        try:
            with SessionLocal() as db:
                # Get active devices for all users
                devices = db.query(NotificationDevice).filter(
                    and_(
                        NotificationDevice.user_id.in_(user_ids),
                        NotificationDevice.is_active == True
                    )
                ).all()
                
                # Group devices by user
                user_devices = {}
                for device in devices:
                    if device.user_id not in user_devices:
                        user_devices[device.user_id] = []
                    user_devices[device.user_id].append(device)
                
                # Send notifications
                for user_id, user_devices_list in user_devices.items():
                    try:
                        for device in user_devices_list:
                            await self._queue_notification(
                                device.id, title, body, data or {}
                            )
                        results["sent"] += 1
                    except Exception as e:
                        self.logger.error(f"Failed to send to user {user_id}: {e}")
                        results["failed"] += 1
                
                results["skipped"] = len(user_ids) - len(user_devices)
                
        except Exception as e:
            self.logger.error(f"Failed to send bulk notifications: {e}")
            results["failed"] = len(user_ids)
        
        return results
    
    async def _queue_notification(
        self,
        device_id: str,
        title: str,
        body: str,
        data: Dict[str, Any]
    ) -> bool:
        """Queue a notification for processing."""
        try:
            with SessionLocal() as db:
                notification = NotificationQueue(
                    device_id=device_id,
                    title=title,
                    body=body,
                    data=json.dumps(data),
                    status='pending'
                )
                db.add(notification)
                db.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to queue notification: {e}")
            return False
    
    async def process_notification_queue(self, limit: int = 100) -> int:
        """Process queued notifications."""
        processed = 0
        
        try:
            with SessionLocal() as db:
                # Get pending notifications
                notifications = db.query(NotificationQueue).filter(
                    NotificationQueue.status == 'pending'
                ).limit(limit).all()
                
                for notification in notifications:
                    try:
                        await self._send_notification(notification)
                        notification.status = 'sent'
                        notification.sent_at = datetime.utcnow()
                        processed += 1
                    except Exception as e:
                        notification.status = 'failed'
                        notification.error_message = str(e)
                        self.logger.error(f"Failed to send notification: {e}")
                
                db.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to process notification queue: {e}")
        
        return processed
    
    async def _send_notification(self, notification: NotificationQueue) -> bool:
        """Send a single notification."""
        try:
            with SessionLocal() as db:
                device = db.query(NotificationDevice).filter(
                    NotificationDevice.id == notification.device_id
                ).first()
                
                if not device or not device.is_active:
                    raise Exception("Device not found or inactive")
                
                # Prepare message
                message_data = {
                    'token': device.device_token,
                    'notification': {
                        'title': notification.title,
                        'body': notification.body
                    },
                    'data': json.loads(notification.data) if notification.data else {}
                }
                
                # Send via Firebase
                response = messaging.send(message_data)
                self.logger.info(f"Notification sent: {response}")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            raise
    
    async def create_notification_template(
        self,
        name: str,
        title_template: str,
        body_template: str,
        data_template: Dict[str, str],
        description: str = None
    ) -> str:
        """Create a notification template."""
        try:
            with SessionLocal() as db:
                template = NotificationTemplate(
                    name=name,
                    title_template=title_template,
                    body_template=body_template,
                    data_template=json.dumps(data_template),
                    description=description
                )
                db.add(template)
                db.commit()
                
                return template.id
                
        except Exception as e:
            self.logger.error(f"Failed to create template: {e}")
            raise
    
    async def send_templated_notification(
        self,
        user_id: str,
        template_name: str,
        variables: Dict[str, Any] = None
    ) -> bool:
        """Send a notification using a template."""
        try:
            with SessionLocal() as db:
                template = db.query(NotificationTemplate).filter(
                    NotificationTemplate.name == template_name
                ).first()
                
                if not template:
                    raise Exception(f"Template not found: {template_name}")
                
                # Render templates
                variables = variables or {}
                title = template.title_template.format(**variables)
                body = template.body_template.format(**variables)
                
                data = {}
                if template.data_template:
                    data_template = json.loads(template.data_template)
                    data = {k: v.format(**variables) for k, v in data_template.items()}
                
                return await self.send_push_notification(user_id, title, body, data)
                
        except Exception as e:
            self.logger.error(f"Failed to send templated notification: {e}")
            return False
    
    async def get_user_notifications(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get notification history for a user."""
        try:
            with SessionLocal() as db:
                notifications = db.query(NotificationQueue).join(
                    NotificationDevice, NotificationQueue.device_id == NotificationDevice.id
                ).filter(
                    NotificationDevice.user_id == user_id
                ).order_by(NotificationQueue.created_at.desc()).limit(limit).all()
                
                return [
                    {
                        "id": n.id,
                        "title": n.title,
                        "body": n.body,
                        "status": n.status,
                        "created_at": n.created_at.isoformat(),
                        "sent_at": n.sent_at.isoformat() if n.sent_at else None,
                        "error_message": n.error_message
                    }
                    for n in notifications
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get notifications: {e}")
            return []
    
    async def cleanup_old_notifications(self, days: int = 30) -> int:
        """Clean up old notification records."""
        try:
            with SessionLocal() as db:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                
                deleted = db.query(NotificationQueue).filter(
                    NotificationQueue.created_at < cutoff_date
                ).delete()
                
                db.commit()
                self.logger.info(f"Cleaned up {deleted} old notifications")
                
                return deleted
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup notifications: {e}")
            return 0


# Global notification manager instance
notification_manager = NotificationManager()


# Common notification templates
NOTIFICATION_TEMPLATES = {
    "order_confirmed": {
        "title": "Order Confirmed",
        "body": "Your order #{order_id} has been confirmed and is being processed.",
        "data": {"type": "order", "order_id": "{order_id}"}
    },
    "order_shipped": {
        "title": "Order Shipped",
        "body": "Your order #{order_id} has been shipped. Track your package for updates.",
        "data": {"type": "shipment", "order_id": "{order_id}"}
    },
    "payment_received": {
        "title": "Payment Received",
        "body": "Payment of ${amount} has been received for order #{order_id}.",
        "data": {"type": "payment", "order_id": "{order_id}", "amount": "{amount}"}
    },
    "bid_accepted": {
        "title": "Bid Accepted",
        "body": "Your bid of ${amount} for {product_name} has been accepted.",
        "data": {"type": "bid", "product_id": "{product_id}", "amount": "{amount}"}
    },
    "low_inventory": {
        "title": "Low Inventory Alert",
        "body": "{product_name} is running low on stock ({current_stock} remaining).",
        "data": {"type": "inventory", "product_id": "{product_id}", "current_stock": "{current_stock}"}
    },
    "price_alert": {
        "title": "Price Alert",
        "body": "{product_name} price has dropped to ${new_price}.",
        "data": {"type": "price", "product_id": "{product_id}", "new_price": "{new_price}"}
    }
}