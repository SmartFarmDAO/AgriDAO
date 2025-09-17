"""
Tests for notification service functionality.
"""

import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

from sqlmodel import Session

from app.database import engine
from app.models import User, Order, OrderItem, Product, UserRole, UserStatus, Notification
from app.services.notification_service import NotificationService, NotificationType


@pytest.fixture
def notification_service():
    """Create notification service instance."""
    return NotificationService()


@pytest.fixture
def test_user():
    """Create test user."""
    with Session(engine) as session:
        user = User(
            name="Test User",
            email="test@example.com",
            phone="+1234567890",
            role=UserRole.BUYER,
            status=UserStatus.ACTIVE,
            email_verified=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        yield user
        
        # Cleanup
        session.delete(user)
        session.commit()


@pytest.fixture
def test_order(test_user):
    """Create test order."""
    with Session(engine) as session:
        order = Order(
            buyer_id=test_user.id,
            subtotal=10.99,
            platform_fee=0.88,
            total=11.87,
            payment_status="paid",
            status="confirmed"
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        yield order
        
        # Cleanup
        session.delete(order)
        session.commit()


@pytest.fixture
def test_product():
    """Create test product."""
    with Session(engine) as session:
        product = Product(
            name="Test Product",
            description="Test description",
            price=Decimal("10.99"),
            quantity_available=100
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        yield product
        
        # Cleanup
        session.delete(product)
        session.commit()


class TestNotificationService:
    """Test notification service operations."""
    
    def test_create_in_app_notification(self, notification_service, test_user):
        """Test creating in-app notification."""
        
        success = notification_service._create_in_app_notification(
            user_id=test_user.id,
            notification_type=NotificationType.ORDER_CONFIRMATION,
            title="Test Notification",
            message="This is a test notification",
            metadata={"test": "data"}
        )
        
        assert success is True
        
        # Verify notification was created
        with Session(engine) as session:
            notification = session.query(Notification).filter(
                Notification.user_id == test_user.id,
                Notification.title == "Test Notification"
            ).first()
            
            assert notification is not None
            assert notification.type == NotificationType.ORDER_CONFIRMATION.value
            assert notification.message == "This is a test notification"
            assert notification.notification_metadata == {"test": "data"}
            
            # Cleanup
            session.delete(notification)
            session.commit()
    
    def test_get_user_notifications(self, notification_service, test_user):
        """Test getting user notifications."""
        
        # Create test notifications
        notification_service._create_in_app_notification(
            user_id=test_user.id,
            notification_type=NotificationType.ORDER_CONFIRMATION,
            title="Test Notification 1",
            message="First notification"
        )
        
        notification_service._create_in_app_notification(
            user_id=test_user.id,
            notification_type=NotificationType.ORDER_STATUS_UPDATE,
            title="Test Notification 2",
            message="Second notification"
        )
        
        notifications = notification_service.get_user_notifications(test_user.id)
        
        assert len(notifications) >= 2
        assert any(n["title"] == "Test Notification 1" for n in notifications)
        assert any(n["title"] == "Test Notification 2" for n in notifications)
        
        # Cleanup
        with Session(engine) as session:
            session.query(Notification).filter(
                Notification.user_id == test_user.id
            ).delete()
            session.commit()
    
    def test_mark_notification_read(self, notification_service, test_user):
        """Test marking notification as read."""
        
        # Create test notification
        notification_service._create_in_app_notification(
            user_id=test_user.id,
            notification_type=NotificationType.ORDER_CONFIRMATION,
            title="Test Notification",
            message="Test message"
        )
        
        # Get notification ID
        with Session(engine) as session:
            notification = session.query(Notification).filter(
                Notification.user_id == test_user.id,
                Notification.title == "Test Notification"
            ).first()
            
            notification_id = notification.id
            assert notification.read_at is None
        
        # Mark as read
        success = notification_service.mark_notification_read(notification_id, test_user.id)
        assert success is True
        
        # Verify it's marked as read
        with Session(engine) as session:
            notification = session.get(Notification, notification_id)
            assert notification.read_at is not None
            
            # Cleanup
            session.delete(notification)
            session.commit()
    
    def test_mark_notification_read_wrong_user(self, notification_service, test_user):
        """Test marking notification as read with wrong user."""
        
        # Create test notification
        notification_service._create_in_app_notification(
            user_id=test_user.id,
            notification_type=NotificationType.ORDER_CONFIRMATION,
            title="Test Notification",
            message="Test message"
        )
        
        # Get notification ID
        with Session(engine) as session:
            notification = session.query(Notification).filter(
                Notification.user_id == test_user.id,
                Notification.title == "Test Notification"
            ).first()
            
            notification_id = notification.id
        
        # Try to mark as read with wrong user ID
        success = notification_service.mark_notification_read(notification_id, 99999)
        assert success is False
        
        # Cleanup
        with Session(engine) as session:
            session.delete(notification)
            session.commit()
    
    @patch('smtplib.SMTP')
    def test_send_email_notification_success(self, mock_smtp, notification_service):
        """Test successful email notification sending."""
        
        # Mock SMTP server
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        user_data = {"name": "Test User", "email": "test@example.com"}
        template_data = {
            "order": {"order_id": 123, "total": 10.99},
            "user": user_data
        }
        
        result = notification_service._send_email_notification(
            user_data=user_data,
            notification_type=NotificationType.ORDER_CONFIRMATION,
            template_data=template_data
        )
        
        assert result["success"] is True
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_notification_failure(self, mock_smtp, notification_service):
        """Test email notification sending failure."""
        
        # Mock SMTP server to raise exception
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        user_data = {"name": "Test User", "email": "test@example.com"}
        template_data = {
            "order": {"order_id": 123, "total": 10.99},
            "user": user_data
        }
        
        result = notification_service._send_email_notification(
            user_data=user_data,
            notification_type=NotificationType.ORDER_CONFIRMATION,
            template_data=template_data
        )
        
        assert result["success"] is False
        assert "error" in result
    
    def test_send_order_confirmation_order_not_found(self, notification_service):
        """Test sending order confirmation for non-existent order."""
        
        result = notification_service.send_order_confirmation(99999)
        
        assert result["success"] is False
        assert result["error"] == "Order not found"
    
    def test_send_order_status_update_order_not_found(self, notification_service):
        """Test sending order status update for non-existent order."""
        
        result = notification_service.send_order_status_update(99999, "shipped")
        
        assert result["success"] is False
        assert result["error"] == "Order not found"
    
    def test_get_email_subject(self, notification_service):
        """Test email subject generation."""
        
        template_data = {"order": {"order_id": 123}}
        
        subject = notification_service._get_email_subject(
            NotificationType.ORDER_CONFIRMATION,
            template_data
        )
        
        assert "123" in subject
        assert "Order Confirmation" in subject
    
    def test_get_status_message(self, notification_service):
        """Test status message generation."""
        
        message = notification_service._get_status_message("shipped")
        assert "shipped" in message.lower()
        
        message = notification_service._get_status_message("unknown_status")
        assert "unknown_status" in message
    
    def test_render_sms_template(self, notification_service):
        """Test SMS template rendering."""
        
        template_data = {
            "order": {"order_id": 123, "total": 10.99},
            "message": "Your order has shipped"
        }
        
        message = notification_service._render_sms_template(
            NotificationType.ORDER_CONFIRMATION,
            template_data
        )
        
        assert "123" in message
        assert "10.99" in message
    
    def test_should_send_sms(self, notification_service):
        """Test SMS sending decision logic."""
        
        # Important notifications should send SMS
        should_send = notification_service._should_send_sms(
            1, NotificationType.ORDER_CONFIRMATION
        )
        assert should_send is True
        
        should_send = notification_service._should_send_sms(
            1, NotificationType.SHIPPING_UPDATE
        )
        assert should_send is True
        
        # Less important notifications might not send SMS
        should_send = notification_service._should_send_sms(
            1, NotificationType.EMAIL_VERIFICATION
        )
        assert should_send is False