"""
Shared Content Pydantic schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.course_content import ContentType, StorageType


class SharedContentBase(BaseModel):
    """Base shared content schema"""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    content_type: ContentType
    storage_type: StorageType
    
    # File information
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    file_path: Optional[str] = Field(None, max_length=500)
    mime_type: Optional[str] = Field(None, max_length=100)
    
    # External content
    external_url: Optional[str] = Field(None, max_length=1000)
    embedded_content: Optional[str] = None
    
    # Metadata
    duration: Optional[int] = Field(None, ge=0)  # Duration in seconds
    is_active: bool = True
    
    @field_validator("external_url")
    @classmethod
    def validate_external_url(cls, v, info):
        """Validate external URL when content type is external_link"""
        if info.data.get("content_type") == ContentType.EXTERNAL_LINK and not v:
            raise ValueError("external_url is required for external_link content type")
        return v
    
    @field_validator("embedded_content")
    @classmethod
    def validate_embedded_content(cls, v, info):
        """Validate embedded content when content type is embedded"""
        if info.data.get("content_type") == ContentType.EMBEDDED and not v:
            raise ValueError("embedded_content is required for embedded content type")
        return v


class SharedContentCreate(SharedContentBase):
    """Schema for creating shared content"""

    pass


class SharedContentUpdate(BaseModel):
    """Schema for updating shared content"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    storage_type: Optional[StorageType] = None
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    file_path: Optional[str] = Field(None, max_length=500)
    mime_type: Optional[str] = Field(None, max_length=100)
    external_url: Optional[str] = Field(None, max_length=1000)
    embedded_content: Optional[str] = None
    duration: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class SharedContent(SharedContentBase):
    """Schema for shared content response"""

    id: int
    used_in_courses: Optional[List[int]] = None
    used_in_programs: Optional[List[int]] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True

