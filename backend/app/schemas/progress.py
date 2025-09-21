"""
ContentCompletion Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ContentCompletionBase(BaseModel):
    """Base content completion schema"""
    course_enrollment_id: int
    content_id: int
    completed_at: Optional[datetime] = None
    time_spent_minutes: Optional[int] = Field(None, ge=0)
    score: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = Field(None, max_length=500)


class ContentCompletionCreate(ContentCompletionBase):
    """Schema for creating content completion"""
    pass


class ContentCompletionUpdate(BaseModel):
    """Schema for updating content completion"""
    completed_at: Optional[datetime] = None
    time_spent_minutes: Optional[int] = Field(None, ge=0)
    score: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = Field(None, max_length=500)


class ContentCompletion(ContentCompletionBase):
    """Schema for content completion response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
