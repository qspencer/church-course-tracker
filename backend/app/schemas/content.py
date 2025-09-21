"""
Content Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ContentBase(BaseModel):
    """Base content schema"""
    course_id: int
    title: str = Field(..., min_length=1, max_length=200)
    content_type_id: int
    order_sequence: int = Field(default=0, ge=0)
    file_path: Optional[str] = Field(None, max_length=500)
    url: Optional[str] = Field(None, max_length=500)
    duration_minutes: Optional[int] = Field(None, ge=0)
    is_required: bool = Field(default=True)
    is_active: bool = Field(default=True)


class ContentCreate(ContentBase):
    """Schema for creating content"""
    pass


class ContentUpdate(BaseModel):
    """Schema for updating content"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content_type_id: Optional[int] = None
    order_sequence: Optional[int] = Field(None, ge=0)
    file_path: Optional[str] = Field(None, max_length=500)
    url: Optional[str] = Field(None, max_length=500)
    duration_minutes: Optional[int] = Field(None, ge=0)
    is_required: Optional[bool] = None
    is_active: Optional[bool] = None


class Content(ContentBase):
    """Schema for content response"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True
