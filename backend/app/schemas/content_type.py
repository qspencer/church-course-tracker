"""
ContentType Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ContentTypeBase(BaseModel):
    """Base content type schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon_class: Optional[str] = Field(None, max_length=100)
    is_active: bool = Field(default=True)


class ContentTypeCreate(ContentTypeBase):
    """Schema for creating a content type"""
    pass


class ContentTypeUpdate(BaseModel):
    """Schema for updating a content type"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon_class: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class ContentType(ContentTypeBase):
    """Schema for content type response"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True
