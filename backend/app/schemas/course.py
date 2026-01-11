"""
Course Pydantic schemas
"""

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class CourseBase(BaseModel):
    """Base course schema"""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    duration_weeks: Optional[int] = Field(None, ge=1)
    prerequisites: Optional[List[int]] = Field(None, description="List of prerequisite course IDs")
    instructors: Optional[List[Union[int, str]]] = Field(
        None, 
        description="List of instructor user IDs (integers) and/or 'TBD' string"
    )
    locations: Optional[List[str]] = Field(
        None,
        description="List of location strings (e.g., 'Room 101', 'Online', 'Zoom')"
    )
    delivery_modes: Optional[List[str]] = Field(
        None,
        description="List of delivery mode strings (e.g., 'In-person', 'Online', 'Hybrid', 'Self-paced')"
    )
    planning_center_event_template_id: Optional[str] = Field(None, max_length=50, description="Planning Center event template/series ID")
    planning_center_event_id: Optional[str] = Field(None, max_length=50)
    planning_center_event_name: Optional[str] = Field(None, max_length=200)
    event_start_date: Optional[datetime] = None
    event_end_date: Optional[datetime] = None
    max_capacity: Optional[int] = Field(None, ge=1)
    current_registrations: Optional[int] = Field(0, ge=0)
    is_active: bool = True
    
    @field_validator('instructors')
    @classmethod
    def validate_instructors(cls, v):
        """Validate that instructor strings are only 'TBD'"""
        if v is None:
            return v
        for item in v:
            if isinstance(item, str) and item != "TBD":
                raise ValueError(f"Instructor string must be 'TBD', got '{item}'")
        return v


class CourseCreate(CourseBase):
    """Schema for creating a course"""

    pass


class CourseUpdate(BaseModel):
    """Schema for updating a course"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    duration_weeks: Optional[int] = Field(None, ge=1)
    prerequisites: Optional[List[str]] = None
    instructors: Optional[List[Union[int, str]]] = Field(
        None,
        description="List of instructor user IDs (integers) and/or 'TBD' string"
    )
    locations: Optional[List[str]] = Field(
        None,
        description="List of location strings"
    )
    delivery_modes: Optional[List[str]] = Field(
        None,
        description="List of delivery mode strings"
    )
    planning_center_event_template_id: Optional[str] = Field(None, max_length=50, description="Planning Center event template/series ID")
    planning_center_event_id: Optional[str] = Field(None, max_length=50)
    planning_center_event_name: Optional[str] = Field(None, max_length=200)
    event_start_date: Optional[datetime] = None
    event_end_date: Optional[datetime] = None
    max_capacity: Optional[int] = Field(None, ge=1)
    current_registrations: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    
    @field_validator('instructors')
    @classmethod
    def validate_instructors(cls, v):
        """Validate that instructor strings are only 'TBD'"""
        if v is None:
            return v
        for item in v:
            if isinstance(item, str) and item != "TBD":
                raise ValueError(f"Instructor string must be 'TBD', got '{item}'")
        return v


class Course(CourseBase):
    """Schema for course response"""

    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_by_user_name: Optional[str] = None
    updated_by_user_name: Optional[str] = None

    class Config:
        from_attributes = True
