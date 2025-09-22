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
    planning_center_event_id: Optional[str] = Field(None, max_length=50)
    planning_center_event_name: Optional[str] = Field(None, max_length=200)
    event_start_date: Optional[datetime] = None
    event_end_date: Optional[datetime] = None
    max_capacity: Optional[int] = Field(None, ge=1)
    current_registrations: Optional[int] = Field(0, ge=0)
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
    planning_center_event_id: Optional[str] = Field(None, max_length=50)
    planning_center_event_name: Optional[str] = Field(None, max_length=200)
    event_start_date: Optional[datetime] = None
    event_end_date: Optional[datetime] = None
    max_capacity: Optional[int] = Field(None, ge=1)
    current_registrations: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class Course(CourseBase):
    """Schema for course response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
