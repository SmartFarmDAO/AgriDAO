"""
Notification Service for email and SMS notifications.
Handles order confirmations, status updates, and user preferences.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
try:
    import smtplib
    from email.mime.text import MIMEText as MimeText
    from email.mime.multipart import MIMEMultipart as MimeMultipart
    from email.mime.base import MIMEBase as MimeBase
    from email import encoders
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    logger.warning("Email libraries not available. Email notifications disabled.")
import json

from sqlmodel import Session, select
from jinja2 import Environment, FileSystemLoader, Template

from ..database import engine
from ..models import User, Order, OrderItem, Product, Notification
from ..services.redis_service import RedisService


logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    ORDER_CONFIRMATION = "order_confirmation"
    ORDER_STATUS_UPDATE = "order_status_update"
    PAYMENT_CONFIRMATION = "payment_confirmation"
    PAYMENT_FAILED = "payment_failed"
    SHIPPING_UPDATE = "shipping_update"
    DELIVERY_CONFIRMATION = "delivery_confirmation"
    REFUND_PROCESSED = "refund_processed"
    ACCOUNT_CREATED = "account_created"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"


class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationService:
    """Service for managing notifications across multiple channels."""
    
    def __init__(self):
        self.redis_service = RedisService()
        
        # Email configuration
        self.smtp_host = os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        self.from_email = os.getenv("FROM_EMAIL", "noreply@agridao.com")
        self.from_name = os.getenv("FROM_NAME", "AgriDAO")
        
        # SMS configuration (Twilio)
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER", "")
        
        # Template configuration
        template_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "notifications")
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir) if os.path.exists(template_dir) else None,
            autoescape=True
        )
        
        # Initialize Twilio client if configured
        self.twilio_client = None
        if self.twilio_account_sid and self.twilio_auth_token:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
            except ImportError:
                logger.warning("Twilio library not installed. SMS notifications disabled.")
    
    def send_order_confirmation(self, order_id: int) -> Dict[str, Any]:
        """Send order confirmation notification."""
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                return {"success": False, "error": "Order not found"}
            
            user = session.get(User, order.buyer_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Get order items with product details
            order_items = session.exec(
                select(OrderItem).where(OrderItem.order_id == order_id)
            ).all()
            
            product_ids = [item.product_id for item in order_items]
            products = {
                p.id: p for p in session.exec(
                    select(Product).where(Product.id.in_(product_ids))
                ).all()
            }
            
            # Prepare order data for template
            order_data = {
                "order_id": order.id,
                "order_date": order.created_at.strftime("%B %d, %Y"),
                "subtotal": order.subtotal,
                "platform_fee": order.platform_fee,
                "total": order.total,
                "payment_status": order.payment_status,
                "status": order.status,
                "items": [
                    {
                        "product_name": products.get(item.product_id).name if products.get(item.product_id) else "Unknown Product",
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "total_price": item.unit_price * item.quantity
                    }
                    for item in order_items
                ]
            }
            
            user_data = {
                "name": user.name,
                "email": user.email
            }
            
            # Send email notification
            email_result = self._send_email_notification(
                user_data=user_data,
                notification_type=NotificationType.ORDER_CONFIRMATION,
                template_data={"order": order_data, "user": user_data}
            )
            
            # Send SMS notification if phone number available
            sms_result = None
            if user.phone and self._should_send_sms(user.id, NotificationType.ORDER_CONFIRMATION):
                sms_result = self._send_sms_notification(
                    phone_number=user.phone,
                    notification_type=NotificationType.ORDER_CONFIRMATION,
                    template_data={"order": order_data, "user": user_data}
                )
            
            # Create in-app notification
            self._create_in_app_notification(
                user_id=user.id,
                notification_type=NotificationType.ORDER_CONFIRMATION,
                title="Order Confirmed",
                message=f"Your order #{order.id} has been confirmed and is being processed.",
                metadata={"order_id": order.id}
            )
            
            return {
                "success": True,
                "email_sent": email_result.get("success", False) if email_result else False,
                "sms_sent": sms_result.get("success", False) if sms_result else False,
                "in_app_created": True
            }
    
    def send_order_status_update(self, order_id: int, new_status: str, message: Optional[str] = None) -> Dict[str, Any]:
        """Send order status update notification."""
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                return {"success": False, "error": "Order not found"}
            
            user = session.get(User, order.buyer_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Prepare notification data
            template_data = {
                "order": {
                    "order_id": order.id,
                    "old_status": order.status,
                    "new_status": new_status,
                    "total": order.total
                },
                "user": {"name": user.name, "email": user.email},
                "message": message or self._get_status_message(new_status)
            }
            
            # Send email notification
            email_result = self._send_email_notification(
                user_data={"name": user.name, "email": user.email},
                notification_type=NotificationType.ORDER_STATUS_UPDATE,
                template_data=template_data
            )
            
            # Send SMS for important status changes
            sms_result = None
            important_statuses = ["shipped", "delivered", "cancelled"]
            if (user.phone and new_status.lower() in important_statuses and 
                self._should_send_sms(user.id, NotificationType.ORDER_STATUS_UPDATE)):
                sms_result = self._send_sms_notification(
                    phone_number=user.phone,
                    notification_type=NotificationType.ORDER_STATUS_UPDATE,
                    template_data=template_data
                )
            
            # Create in-app notification
            self._create_in_app_notification(
                user_id=user.id,
                notification_type=NotificationType.ORDER_STATUS_UPDATE,
                title=f"Order #{order.id} Update",
                message=template_data["message"],
                metadata={"order_id": order.id, "new_status": new_status}
            )
            
            return {
                "success": True,
                "email_sent": email_result.get("success", False) if email_result else False,
                "sms_sent": sms_result.get("success", False) if sms_result else False,
                "in_app_created": True
            }
    
    def send_payment_confirmation(self, order_id: int, payment_intent_id: str) -> Dict[str, Any]:
        """Send payment confirmation notification."""
        
        with Session(engine) as session:
            order = session.get(Order, order_id)
            if not order:
                return {"success": False, "error": "Order not found"}
            
            user = session.get(User, order.buyer_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            template_data = {
                "order": {
                    "order_id": order.id,
                    "total": order.total,
                    "payment_intent_id": payment_intent_id
                },
                "user": {"name": user.name, "email": user.email}
            }
            
            # Send email notification
            email_result = self._send_email_notification(
                user_data={"name": user.name, "email": user.email},
                notification_type=NotificationType.PAYMENT_CONFIRMATION,
                template_data=template_data
            )
            
            # Create in-app notification
            self._create_in_app_notification(
                user_id=user.id,
                notification_type=NotificationType.PAYMENT_CONFIRMATION,
                title="Payment Confirmed",
                message=f"Payment for order #{order.id} has been processed successfully.",
                metadata={"order_id": order.id, "payment_intent_id": payment_intent_id}
            )
            
            return {
                "success": True,
                "email_sent": email_result.get("success", False) if email_result else False,
                "in_app_created": True
            }
    
    def _send_email_notification(
        self, 
        user_data: Dict[str, Any], 
        notification_type: NotificationType,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send email notification using SMTP."""
        
        if not EMAIL_AVAILABLE:
            return {"success": False, "error": "Email libraries not available"}
        
        if not self.smtp_username or not user_data.get("email"):
            return {"success": False, "error": "Email not configured or recipient email missing"}
        
        try:
            # Get email template
            subject, html_body, text_body = self._render_email_template(notification_type, template_data)
            
            # Create message
            msg = MimeMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = user_data["email"]
            
            # Add text and HTML parts
            if text_body:
                msg.attach(MimeText(text_body, "plain"))
            if html_body:
                msg.attach(MimeText(html_body, "html"))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {user_data['email']} for {notification_type}")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Failed to send email to {user_data.get('email')}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _send_sms_notification(
        self, 
        phone_number: str, 
        notification_type: NotificationType,
        template_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send SMS notification using Twilio."""
        
        if not self.twilio_client or not self.twilio_phone_number:
            return {"success": False, "error": "SMS not configured"}
        
        try:
            # Get SMS template
            message_body = self._render_sms_template(notification_type, template_data)
            
            # Send SMS
            message = self.twilio_client.messages.create(
                body=message_body,
                from_=self.twilio_phone_number,
                to=phone_number
            )
            
            logger.info(f"SMS sent successfully to {phone_number} for {notification_type}")
            return {"success": True, "message_sid": message.sid}
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {phone_number}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _create_in_app_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create in-app notification record."""
        
        try:
            with Session(engine) as session:
                notification = Notification(
                    user_id=user_id,
                    type=notification_type.value,
                    title=title,
                    message=message,
                    notification_metadata=metadata or {}
                )
                session.add(notification)
                session.commit()
                
                # Cache notification for real-time delivery
                cache_key = f"user_notifications:{user_id}"
                try:
                    self.redis_service.lpush(cache_key, json.dumps({
                        "id": notification.id,
                        "type": notification_type.value,
                        "title": title,
                        "message": message,
                        "created_at": datetime.utcnow().isoformat(),
                        "metadata": metadata or {}
                    }))
                    # Keep only last 50 notifications
                    self.redis_service.ltrim(cache_key, 0, 49)
                except Exception:
                    pass  # Cache failure is not critical
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to create in-app notification: {str(e)}")
            return False
    
    def _render_email_template(
        self, 
        notification_type: NotificationType, 
        template_data: Dict[str, Any]
    ) -> tuple[str, str, str]:
        """Render email template for notification type."""
        
        # Default templates if Jinja environment not available
        if not self.jinja_env:
            return self._get_default_email_template(notification_type, template_data)
        
        try:
            # Try to load custom templates
            html_template = self.jinja_env.get_template(f"{notification_type.value}.html")
            text_template = self.jinja_env.get_template(f"{notification_type.value}.txt")
            
            subject = self._get_email_subject(notification_type, template_data)
            html_body = html_template.render(**template_data)
            text_body = text_template.render(**template_data)
            
            return subject, html_body, text_body
            
        except Exception as e:
            logger.warning(f"Failed to render template for {notification_type}: {str(e)}")
            return self._get_default_email_template(notification_type, template_data)
    
    def _render_sms_template(
        self, 
        notification_type: NotificationType, 
        template_data: Dict[str, Any]
    ) -> str:
        """Render SMS template for notification type."""
        
        # SMS templates are simple text messages
        templates = {
            NotificationType.ORDER_CONFIRMATION: "Your order #{order_id} has been confirmed! Total: ${total}. Thank you for your purchase.",
            NotificationType.ORDER_STATUS_UPDATE: "Order #{order_id} update: {message}",
            NotificationType.PAYMENT_CONFIRMATION: "Payment confirmed for order #{order_id}. Amount: ${total}.",
            NotificationType.SHIPPING_UPDATE: "Your order #{order_id} has shipped! Track your package for updates.",
            NotificationType.DELIVERY_CONFIRMATION: "Your order #{order_id} has been delivered. Enjoy your purchase!"
        }
        
        template = templates.get(notification_type, "AgriDAO notification: {message}")
        
        try:
            return template.format(**template_data.get("order", {}), **template_data)
        except Exception:
            return f"AgriDAO notification for order #{template_data.get('order', {}).get('order_id', 'N/A')}"
    
    def _get_default_email_template(
        self, 
        notification_type: NotificationType, 
        template_data: Dict[str, Any]
    ) -> tuple[str, str, str]:
        """Get default email template when custom templates are not available."""
        
        subject = self._get_email_subject(notification_type, template_data)
        
        if notification_type == NotificationType.ORDER_CONFIRMATION:
            order = template_data.get("order", {})
            user = template_data.get("user", {})
            
            html_body = f"""
            <h2>Order Confirmation</h2>
            <p>Dear {user.get('name', 'Customer')},</p>
            <p>Thank you for your order! Your order #{order.get('order_id')} has been confirmed.</p>
            <h3>Order Details:</h3>
            <ul>
                <li>Order ID: #{order.get('order_id')}</li>
                <li>Order Date: {order.get('order_date')}</li>
                <li>Total: ${order.get('total', 0):.2f}</li>
            </ul>
            <p>We'll send you updates as your order is processed.</p>
            <p>Best regards,<br>The AgriDAO Team</p>
            """
            
            text_body = f"""
            Order Confirmation
            
            Dear {user.get('name', 'Customer')},
            
            Thank you for your order! Your order #{order.get('order_id')} has been confirmed.
            
            Order Details:
            - Order ID: #{order.get('order_id')}
            - Order Date: {order.get('order_date')}
            - Total: ${order.get('total', 0):.2f}
            
            We'll send you updates as your order is processed.
            
            Best regards,
            The AgriDAO Team
            """
            
        else:
            # Generic template for other notification types
            html_body = f"<p>You have a new notification from AgriDAO.</p>"
            text_body = "You have a new notification from AgriDAO."
        
        return subject, html_body, text_body
    
    def _get_email_subject(self, notification_type: NotificationType, template_data: Dict[str, Any]) -> str:
        """Get email subject for notification type."""
        
        subjects = {
            NotificationType.ORDER_CONFIRMATION: "Order Confirmation #{order_id}",
            NotificationType.ORDER_STATUS_UPDATE: "Order #{order_id} Update",
            NotificationType.PAYMENT_CONFIRMATION: "Payment Confirmed - Order #{order_id}",
            NotificationType.PAYMENT_FAILED: "Payment Failed - Order #{order_id}",
            NotificationType.SHIPPING_UPDATE: "Your Order Has Shipped - #{order_id}",
            NotificationType.DELIVERY_CONFIRMATION: "Order Delivered - #{order_id}",
            NotificationType.REFUND_PROCESSED: "Refund Processed - Order #{order_id}"
        }
        
        subject_template = subjects.get(notification_type, "AgriDAO Notification")
        
        try:
            return subject_template.format(**template_data.get("order", {}))
        except Exception:
            return "AgriDAO Notification"
    
    def _get_status_message(self, status: str) -> str:
        """Get user-friendly status message."""
        
        messages = {
            "confirmed": "Your order has been confirmed and is being prepared.",
            "processing": "Your order is being processed.",
            "shipped": "Your order has been shipped and is on its way!",
            "delivered": "Your order has been delivered. Enjoy your purchase!",
            "cancelled": "Your order has been cancelled.",
            "refunded": "Your order has been refunded."
        }
        
        return messages.get(status.lower(), f"Your order status has been updated to {status}.")
    
    def _should_send_sms(self, user_id: int, notification_type: NotificationType) -> bool:
        """Check if SMS should be sent based on user preferences."""
        
        # TODO: Implement user notification preferences
        # For now, send SMS for important notifications only
        important_types = [
            NotificationType.ORDER_CONFIRMATION,
            NotificationType.SHIPPING_UPDATE,
            NotificationType.DELIVERY_CONFIRMATION
        ]
        
        return notification_type in important_types
    
    def get_user_notifications(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's in-app notifications."""
        
        with Session(engine) as session:
            notifications = session.exec(
                select(Notification)
                .where(Notification.user_id == user_id)
                .order_by(Notification.created_at.desc())
                .limit(limit)
            ).all()
            
            return [
                {
                    "id": n.id,
                    "type": n.type,
                    "title": n.title,
                    "message": n.message,
                    "read_at": n.read_at.isoformat() if n.read_at else None,
                    "created_at": n.created_at.isoformat(),
                    "metadata": n.notification_metadata or {}
                }
                for n in notifications
            ]
    
    def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
        """Mark notification as read."""
        
        with Session(engine) as session:
            notification = session.get(Notification, notification_id)
            
            if not notification or notification.user_id != user_id:
                return False
            
            notification.read_at = datetime.utcnow()
            session.add(notification)
            session.commit()
            
            return True