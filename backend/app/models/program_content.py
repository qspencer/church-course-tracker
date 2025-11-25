"""
Program Content Models

This module defines the database models for program content,
including modules and content items that can reference shared content.
"""

import enum
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer, JSON,
                        String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.shared_content import ContentType, StorageType


class ProgramModule(Base):
    """Module/unit organization for program content"""

    __tablename__ = "program_modules"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # CSV source tracking
    data_source = Column(String(20), nullable=True)
    csv_loaded_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    program = relationship("Program", back_populates="program_modules")
    program_content = relationship(
        "ProgramContent", back_populates="module", cascade="all, delete-orphan"
    )


class ProgramContent(Base):
    """Content items for programs (can reference shared content or be program-specific)"""

    __tablename__ = "program_content"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("program_modules.id"), nullable=True, index=True)
    
    # Reference to shared content (if reusable)
    shared_content_id = Column(Integer, ForeignKey("shared_content.id"), nullable=True, index=True)
    
    # OR program-specific content (if not shared)
    title = Column(String(200), nullable=True)  # Nullable if using shared_content
    description = Column(Text, nullable=True)
    content_type = Column(Enum(ContentType), nullable=True)  # Nullable if using shared_content
    storage_type = Column(Enum(StorageType), nullable=True)  # Nullable if using shared_content
    
    # File information
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    file_path = Column(String(500), nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # External content
    external_url = Column(String(1000), nullable=True)
    embedded_content = Column(Text, nullable=True)
    
    # Metadata
    duration = Column(Integer, nullable=True)  # Duration in minutes
    download_count = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # CSV source tracking
    data_source = Column(String(20), nullable=True)
    csv_loaded_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    program = relationship("Program", back_populates="program_content")
    module = relationship("ProgramModule", back_populates="program_content")
    shared_content = relationship("SharedContent", foreign_keys=[shared_content_id])
    program_progress = relationship(
        "ProgramProgress", foreign_keys="ProgramProgress.content_id", back_populates="content"
    )
