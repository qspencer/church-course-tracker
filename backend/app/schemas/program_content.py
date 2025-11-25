"""
Program Content Pydantic schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.course_content import ContentType, StorageType


class ProgramModuleBase(BaseModel):
    """Base schema for program modules"""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    order_index: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)


class ProgramModuleCreate(ProgramModuleBase):
    """Schema for creating a program module"""

    program_id: int = Field(..., gt=0)


class ProgramModuleUpdate(BaseModel):
    """Schema for updating a program module"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProgramModule(ProgramModuleBase):
    """Schema for program module response"""

    id: int
    program_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    content_items: List["ProgramContent"] = []

    class Config:
        from_attributes = True


class ProgramContentBase(BaseModel):
    """Base schema for program content"""

    # Either shared_content_id OR program-specific content fields must be provided
    shared_content_id: Optional[int] = Field(None, gt=0)
    
    # Program-specific content (nullable if using shared_content)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    storage_type: Optional[StorageType] = None
    
    # File upload fields
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    
    # External content fields
    external_url: Optional[str] = Field(None, max_length=1000)
    embedded_content: Optional[str] = None
    
    # Metadata
    duration: Optional[int] = Field(None, ge=0)  # Duration in seconds
    order_index: int = Field(default=0, ge=0)
    is_active: bool = Field(default=True)
    
    @field_validator("external_url")
    @classmethod
    def validate_external_url(cls, v, info):
        """Validate external URL when content type is external_link"""
        content_type = info.data.get("content_type")
        if content_type == ContentType.EXTERNAL_LINK and not v and not info.data.get("shared_content_id"):
            raise ValueError("external_url is required for external_link content type")
        return v
    
    @field_validator("embedded_content")
    @classmethod
    def validate_embedded_content(cls, v, info):
        """Validate embedded content when content type is embedded"""
        content_type = info.data.get("content_type")
        if content_type == ContentType.EMBEDDED and not v and not info.data.get("shared_content_id"):
            raise ValueError("embedded_content is required for embedded content type")
        return v


class ProgramContentCreate(ProgramContentBase):
    """Schema for creating program content"""

    program_id: int = Field(..., gt=0)
    module_id: Optional[int] = Field(None, gt=0)


class ProgramContentUpdate(BaseModel):
    """Schema for updating program content"""

    shared_content_id: Optional[int] = Field(None, gt=0)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    content_type: Optional[ContentType] = None
    storage_type: Optional[StorageType] = None
    file_name: Optional[str] = Field(None, max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    external_url: Optional[str] = Field(None, max_length=1000)
    embedded_content: Optional[str] = None
    duration: Optional[int] = Field(None, ge=0)
    order_index: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    module_id: Optional[int] = Field(None, gt=0)


class ProgramContent(ProgramContentBase):
    """Schema for program content response"""

    id: int
    program_id: int
    module_id: Optional[int] = None
    download_count: int = 0
    view_count: int = 0
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True

