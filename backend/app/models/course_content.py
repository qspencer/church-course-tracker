"""
Course Content Models

This module defines the database models for course content management,
including modules, content items, and access tracking.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class ContentType(str, enum.Enum):
    """Enumeration of supported content types"""
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    EXTERNAL_LINK = "external_link"
    EMBEDDED = "embedded"


class StorageType(str, enum.Enum):
    """Enumeration of storage types for content"""
    DATABASE = "database"
    S3 = "s3"
    EXTERNAL = "external"


class CourseModule(Base):
    """Model for course modules/lessons"""
    __tablename__ = "course_modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    course = relationship("Course", back_populates="modules")
    content_items = relationship("CourseContent", back_populates="module", cascade="all, delete-orphan")
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])


class CourseContent(Base):
    """Model for course content items"""
    __tablename__ = "course_content"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("course_modules.id"), nullable=True)  # Optional module
    
    # Content details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(Enum(ContentType), nullable=False)
    storage_type = Column(Enum(StorageType), nullable=False)
    
    # File information (for uploaded content)
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    file_path = Column(String(500), nullable=True)  # Path to file or S3 key
    mime_type = Column(String(100), nullable=True)
    
    # External content information
    external_url = Column(String(1000), nullable=True)  # For external links
    embedded_content = Column(Text, nullable=True)  # For embedded content (HTML/iframe)
    
    # Content metadata
    duration = Column(Integer, nullable=True)  # Duration in seconds (for video/audio)
    download_count = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    
    # Organization
    order_index = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    course = relationship("Course", back_populates="course_content")
    module = relationship("CourseModule", back_populates="content_items")
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    access_logs = relationship("ContentAccessLog", back_populates="content", cascade="all, delete-orphan")


class ContentAccessLog(Base):
    """Model for tracking content access by users"""
    __tablename__ = "content_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("course_content.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Access details
    access_type = Column(String(20), nullable=False)  # 'view', 'download', 'complete'
    access_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Additional metadata
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    session_id = Column(String(100), nullable=True)
    
    # Progress tracking (for videos/audio)
    progress_percentage = Column(Integer, nullable=True)  # 0-100
    time_spent = Column(Integer, nullable=True)  # Time spent in seconds

    # Relationships
    content = relationship("CourseContent", back_populates="access_logs")
    user = relationship("User")


class ContentAuditLog(Base):
    """Model for tracking content changes (audit trail)"""
    __tablename__ = "content_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("course_content.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Change details
    action = Column(String(20), nullable=False)  # 'create', 'update', 'delete', 'view'
    change_timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Change data
    old_values = Column(JSON, nullable=True)  # Previous values
    new_values = Column(JSON, nullable=True)  # New values
    change_summary = Column(Text, nullable=True)  # Human-readable summary
    
    # Additional context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Relationships
    content = relationship("CourseContent")
    user = relationship("User")
