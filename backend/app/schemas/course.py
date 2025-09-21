"""
Course Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CourseBase(BaseModel):
    """Base course schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    duration_weeks: Optional[int] = Field(None, ge=1)
    prerequisites: Optional[List[str]] = Field(None)
    is_active: bool = True


class CourseCreate(CourseBase):
    """Schema for creating a course"""
    pass


class CourseUpdate(BaseModel):
    """Schema for updating a course"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    duration_weeks: Optional[int] = Field(None, ge=1)
    prerequisites: Optional[List[str]] = None
    is_active: Optional[bool] = None


class Course(CourseBase):
    """Schema for course response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
