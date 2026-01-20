"""
File upload models for cloud storage integration.
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from app.database import Base


class FileUpload(Base):
    """Model for tracking uploaded files."""
    __tablename__ = "file_uploads"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False, unique=True)
    file_url = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)  # aws, gcp, azure
    folder = Column(String(255), default="uploads")
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="uploaded_files")
    metadata = relationship("FileMetadata", back_populates="file", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index("idx_file_uploads_user", "uploaded_by"),
        Index("idx_file_uploads_folder", "folder"),
        Index("idx_file_uploads_date", "upload_date"),
        Index("idx_file_uploads_provider", "provider"),
    )
    
    def __repr__(self):
        return f"<FileUpload(id={self.id}, filename={self.filename}, size={self.file_size})>"


class FileMetadata(Base):
    """Model for storing additional file metadata."""
    __tablename__ = "file_metadata"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String(36), ForeignKey("file_uploads.id"), nullable=False)
    checksum = Column(String(64), nullable=False)  # SHA-256 hash
    checksum_type = Column(String(20), default="sha256")
    width = Column(Integer)  # For images
    height = Column(Integer)  # For images
    duration = Column(Integer)  # For videos/audio (seconds)
    exif_data = Column(Text)  # JSON string for EXIF data
    custom_metadata = Column(Text)  # JSON string for custom metadata
    tags = Column(Text)  # JSON array of tags
    
    # Relationships
    file = relationship("FileUpload", back_populates="metadata")
    
    # Indexes
    __table_args__ = (
        Index("idx_file_metadata_file", "file_id"),
        Index("idx_file_metadata_checksum", "checksum"),
    )
    
    def __repr__(self):
        return f"<FileMetadata(file_id={self.file_id}, checksum={self.checksum})>"


class FileShare(Base):
    """Model for file sharing with other users."""
    __tablename__ = "file_shares"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String(36), ForeignKey("file_uploads.id"), nullable=False)
    shared_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    shared_with = Column(String(36), ForeignKey("users.id"), nullable=False)
    permission = Column(String(20), default="read")  # read, write, admin
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    file = relationship("FileUpload")
    shared_by_user = relationship("User", foreign_keys=[shared_by])
    shared_with_user = relationship("User", foreign_keys=[shared_with])
    
    # Indexes
    __table_args__ = (
        Index("idx_file_shares_file", "file_id"),
        Index("idx_file_shares_shared_with", "shared_with"),
        Index("idx_file_shares_active", "is_active"),
    )
    
    def __repr__(self):
        return f"<FileShare(file_id={self.file_id}, shared_with={self.shared_with})>"


class FileVersion(Base):
    """Model for file versioning."""
    __tablename__ = "file_versions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String(36), ForeignKey("file_uploads.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=False)
    checksum = Column(String(64), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    change_notes = Column(Text)
    
    # Relationships
    file = relationship("FileUpload")
    created_by_user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("idx_file_versions_file", "file_id"),
        Index("idx_file_versions_version", "file_id", "version_number"),
    )
    
    def __repr__(self):
        return f"<FileVersion(file_id={self.file_id}, version={self.version_number})>"


class StorageUsage(Base):
    """Model for tracking storage usage per user."""
    __tablename__ = "storage_usage"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)
    total_bytes = Column(Integer, default=0)
    aws_bytes = Column(Integer, default=0)
    gcp_bytes = Column(Integer, default=0)
    azure_bytes = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("idx_storage_usage_user", "user_id"),
    )
    
    def __repr__(self):
        return f"<StorageUsage(user_id={self.user_id}, total={self.total_bytes})>"


# Update User model to include file relationships
# Add these relationships to your existing User model:
# 
# uploaded_files = relationship("FileUpload", back_populates="user")
# shared_files = relationship("FileShare", back_populates="shared_with_user")
# storage_usage = relationship("StorageUsage", back_populates="user", uselist=False)