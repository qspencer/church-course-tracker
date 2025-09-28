"""
Course Content Pydantic Schemas

This module defines the Pydantic schemas for course content management API.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from ..models.course_content import ContentType, StorageType


class CourseModuleBase(BaseModel):
    """Base schema for course modules"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    order_index: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)


class CourseModuleCreate(CourseModuleBase):
    """Schema for creating a course module"""
    course_id: int = Field(..., gt=0)


class CourseModuleUpdate(BaseModel):
    """Schema for updating a course module"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class CourseModule(CourseModuleBase):
    """Schema for course module response"""
    id: int
    course_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    content_items: List["CourseContent"] = []

    class Config:
        from_attributes = True


class CourseContentBase(BaseModel):
    """Base schema for course content"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    content_type: ContentType
    order_index: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)


class CourseContentCreate(CourseContentBase):
    """Schema for creating course content"""
    course_id: int = Field(..., gt=0)
    module_id: Optional[int] = Field(None, gt=0)
    
    # File upload fields
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    
    # External content fields
    external_url: Optional[str] = Field(None, max_length=1000)
    embedded_content: Optional[str] = None
    
    # Metadata
    duration: Optional[int] = Field(None, ge=0)  # Duration in seconds

    @field_validator('external_url')
    @classmethod
    def validate_external_url(cls, v, info):
        """Validate external URL when content type is external_link"""
        if info.data.get('content_type') == ContentType.EXTERNAL_LINK and not v:
            raise ValueError('external_url is required for external_link content type')
        return v

    @field_validator('embedded_content')
    @classmethod
    def validate_embedded_content(cls, v, info):
        """Validate embedded content when content type is embedded"""
        if info.data.get('content_type') == ContentType.EMBEDDED and not v:
            raise ValueError('embedded_content is required for embedded content type')
        return v


class CourseContentUpdate(BaseModel):
    """Schema for updating course content"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    module_id: Optional[int] = Field(None, gt=0)
    order_index: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    
    # External content fields
    external_url: Optional[str] = Field(None, max_length=1000)
    embedded_content: Optional[str] = None
    
    # Metadata
    duration: Optional[int] = Field(None, ge=0)


class CourseContent(CourseContentBase):
    """Schema for course content response"""
    id: int
    course_id: int
    module_id: Optional[int] = None
    storage_type: StorageType
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    file_path: Optional[str] = None
    mime_type: Optional[str] = None
    external_url: Optional[str] = None
    embedded_content: Optional[str] = None
    duration: Optional[int] = None
    download_count: int = 0
    view_count: int = 0
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class ContentAccessLogBase(BaseModel):
    """Base schema for content access logs"""
    access_type: str = Field(..., pattern="^(view|download|complete)$")
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    time_spent: Optional[int] = Field(None, ge=0)  # Time in seconds


class ContentAccessLogCreate(ContentAccessLogBase):
    """Schema for creating content access logs"""
    content_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None


class ContentAccessLog(ContentAccessLogBase):
    """Schema for content access log response"""
    id: int
    content_id: int
    user_id: int
    access_timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

    class Config:
        from_attributes = True


class ContentAuditLogBase(BaseModel):
    """Base schema for content audit logs"""
    action: str = Field(..., pattern="^(create|update|delete|view)$")
    change_summary: Optional[str] = None


class ContentAuditLogCreate(ContentAuditLogBase):
    """Schema for creating content audit logs"""
    content_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ContentAuditLog(ContentAuditLogBase):
    """Schema for content audit log response"""
    id: int
    content_id: int
    user_id: int
    change_timestamp: datetime
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


class ContentUploadResponse(BaseModel):
    """Schema for file upload response"""
    content_id: int
    file_path: str
    file_size: int
    storage_type: StorageType
    message: str


class ContentDownloadRequest(BaseModel):
    """Schema for content download request"""
    content_id: int = Field(..., gt=0)
    access_type: str = Field(default="download", pattern="^(view|download|complete)$")


class ContentProgressUpdate(BaseModel):
    """Schema for updating content progress"""
    content_id: int = Field(..., gt=0)
    progress_percentage: int = Field(..., ge=0, le=100)
    time_spent: Optional[int] = Field(None, ge=0)


class CourseContentSummary(BaseModel):
    """Schema for course content summary"""
    course_id: int
    total_content_items: int
    total_modules: int
    total_file_size: int
    content_by_type: Dict[str, int]
    recent_uploads: List[CourseContent] = []


# Update forward references
CourseModule.model_rebuild()
CourseContent.model_rebuild()
