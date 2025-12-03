"""
Privacy compliance database models for GDPR, CCPA, and user privacy rights.
"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class PrivacyConsent(Base):
    """User consent records for data processing."""
    
    __tablename__ = "privacy_consents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    consent_type = Column(String(50), nullable=False, index=True)
    granted = Column(Boolean, nullable=False, default=True)
    ip_address = Column(String(45))  # IPv4/IPv6
    user_agent = Column(Text)
    policy_version = Column(String(20), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="privacy_consents")
    
    def __repr__(self):
        return f"<PrivacyConsent(user_id={self.user_id}, type={self.consent_type}, granted={self.granted})>"


class DataRequest(Base):
    """User data requests (access, portability, correction)."""
    
    __tablename__ = "data_requests"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    request_type = Column(String(20), nullable=False)  # access, portability, correction
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed, failed
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    data_url = Column(String(500))
    metadata = Column(JSON)  # Additional request metadata
    
    # Relationships
    user = relationship("User", back_populates="data_requests")
    
    def __repr__(self):
        return f"<DataRequest(user_id={self.user_id}, type={self.request_type}, status={self.status})>"


class DataDeletionRequest(Base):
    """User data deletion requests."""
    
    __tablename__ = "data_deletion_requests"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    request_type = Column(String(20), nullable=False, default="deletion")
    deletion_scope = Column(String(50), nullable=False)  # full, personal, activity
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed, failed
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    deletion_log = Column(JSON)  # Log of what was deleted
    
    # Relationships
    user = relationship("User", back_populates="deletion_requests")
    
    def __repr__(self):
        return f"<DataDeletionRequest(user_id={self.user_id}, scope={self.deletion_scope}, status={self.status})>"


class DataProcessingLog(Base):
    """Log of data processing activities for compliance."""
    
    __tablename__ = "data_processing_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    processing_type = Column(String(50), nullable=False)
    data_categories = Column(JSON)  # Categories of data processed
    legal_basis = Column(String(50), nullable=False)  # consent, contract, legal, vital, public, legitimate
    purpose = Column(String(200), nullable=False)
    retention_period = Column(String(50))
    third_parties = Column(JSON)  # Third parties data shared with
    location = Column(String(100))  # Geographic location of processing
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="processing_logs")
    
    def __repr__(self):
        return f"<DataProcessingLog(user_id={self.user_id}, type={self.processing_type}, purpose={self.purpose})>"


class CookieConsent(Base):
    """User cookie consent preferences."""
    
    __tablename__ = "cookie_consents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    cookie_categories = Column(JSON)  # Categories of cookies consented to
    essential = Column(Boolean, nullable=False, default=True)
    analytics = Column(Boolean, nullable=False, default=False)
    marketing = Column(Boolean, nullable=False, default=False)
    personalization = Column(Boolean, nullable=False, default=False)
    
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cookie_consents")
    
    def __repr__(self):
        return f"<CookieConsent(user_id={self.user_id}, essential={self.essential}, analytics={self.analytics})>"


# Update User model relationships (add to existing User model)
# These should be added to the existing User model in app/models/user.py

# User.privacy_consents = relationship("PrivacyConsent", back_populates="user")
# User.data_requests = relationship("DataRequest", back_populates="user")
# User.deletion_requests = relationship("DataDeletionRequest", back_populates="user")
# User.processing_logs = relationship("DataProcessingLog", back_populates="user")
# User.cookie_consents = relationship("CookieConsent", back_populates="user")