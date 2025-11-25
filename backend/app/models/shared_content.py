"""
Shared Content Model

This module defines the database model for shared content that can be
reused across both courses and programs.
"""

import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

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


class SharedContent(Base):
    """Shared content library that can be used by both courses and programs"""

    __tablename__ = "shared_content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    content_type = Column(Enum(ContentType), nullable=False)
    storage_type = Column(Enum(StorageType), nullable=False)
    
    # File information
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    file_path = Column(String(500), nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # External content
    external_url = Column(String(1000), nullable=True)
    embedded_content = Column(Text, nullable=True)  # For embedded HTML/iframe content
    
    # Metadata
    duration = Column(Integer, nullable=True)  # Duration in minutes
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Usage tracking (denormalized for quick lookups)
    # These are updated when content is added/removed from courses/programs
    used_in_courses = Column(JSON, nullable=True)  # JSON array of course IDs
    used_in_programs = Column(JSON, nullable=True)  # JSON array of program IDs
    
    # CSV source tracking
    data_source = Column(String(20), nullable=True)
    csv_loaded_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # User ID
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # User ID
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by], lazy="select")
    updated_by_user = relationship("User", foreign_keys=[updated_by], lazy="select")
