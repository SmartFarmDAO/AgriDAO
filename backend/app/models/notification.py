"""
Notification models for push notifications.
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.database import Base


class NotificationDevice(Base):
    """Model for storing registered devices for push notifications."""
    __tablename__ = "notification_devices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    device_token = Column(String(500), nullable=False, unique=True)
    platform = Column(String(50), nullable=False)  # ios, android, web
    device_info = Column(Text)  # JSON string with device details
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notification_devices")
    notifications = relationship("NotificationQueue", back_populates="device")
    
    # Indexes
    __table_args__ = (
        # Create indexes for performance
        {'sqlite_autoincrement': True},
    )
    
    def __repr__(self):
        return f"<NotificationDevice(id={self.id}, user_id={self.user_id}, platform={self.platform})>"


class NotificationQueue(Base):
    """Model for queued notifications."""
    __tablename__ = "notification_queue"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String(36), ForeignKey("notification_devices.id"), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(String(500), nullable=False)
    data = Column(Text)  # JSON string with additional data
    status = Column(String(20), default='pending')  # pending, sent, failed
    priority = Column(Integer, default=1)  # 1=low, 5=high
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    scheduled_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    device = relationship("NotificationDevice", back_populates="notifications")
    
    # Indexes
    __table_args__ = (
        # Create indexes for performance
        {'sqlite_autoincrement': True},
    )
    
    def __repr__(self):
        return f"<NotificationQueue(id={self.id}, status={self.status})>"


class NotificationTemplate(Base):
    """Model for notification templates."""
    __tablename__ = "notification_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    title_template = Column(String(200), nullable=False)
    body_template = Column(String(500), nullable=False)
    data_template = Column(Text)  # JSON string with template variables
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<NotificationTemplate(name={self.name})>"


class UserNotificationPreference(Base):
    """Model for user notification preferences."""
    __tablename__ = "user_notification_preferences"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5))  # HH:MM format
    quiet_hours_end = Column(String(5))  # HH:MM format
    notification_frequency = Column(String(20), default='immediate')  # immediate, daily, weekly
    categories = Column(Text)  # JSON array of enabled notification categories
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<UserNotificationPreference(user_id={self.user_id})>"


class NotificationHistory(Base):
    """Model for notification history."""
    __tablename__ = "notification_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    body = Column(String(500), nullable=False)
    data = Column(Text)  # JSON string with notification data
    type = Column(String(50))  # order, shipment, payment, etc.
    status = Column(String(20), default='delivered')  # delivered, read, clicked
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        # Create indexes for performance
        {'sqlite_autoincrement': True},
    )
    
    def __repr__(self):
        return f"<NotificationHistory(user_id={self.user_id}, type={self.type})>"


class NotificationAnalytics(Base):
    """Model for notification analytics."""
    __tablename__ = "notification_analytics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    notification_id = Column(String(36), ForeignKey("notification_history.id"), nullable=False)
    delivery_status = Column(String(20))  # delivered, failed, bounced
    delivery_time = Column(DateTime(timezone=True))
    open_time = Column(DateTime(timezone=True))
    click_time = Column(DateTime(timezone=True))
    device_type = Column(String(50))
    platform = Column(String(50))
    error_code = Column(String(50))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    notification = relationship("NotificationHistory")
    
    def __repr__(self):
        return f"<NotificationAnalytics(notification_id={self.notification_id})>"


# Update User model to include notification relationships
# Add these relationships to your existing User model:
# 
# notification_devices = relationship("NotificationDevice", back_populates="user")
# notification_preferences = relationship("UserNotificationPreference", back_populates="user", uselist=False)
# notification_history = relationship("NotificationHistory", back_populates="user")