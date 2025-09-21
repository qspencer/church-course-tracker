"""
CourseEnrollment Pydantic schemas (Maps to Planning Center Registrations)
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CourseEnrollmentBase(BaseModel):
    """Base course enrollment schema"""
    people_id: int
    course_id: int
    enrollment_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="enrolled", regex="^(enrolled|in_progress|completed|dropped)$")
    progress_percentage: float = Field(default=0.0, ge=0, le=100)
    completion_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    dependency_override: bool = Field(default=False)
    dependency_override_by: Optional[int] = None
    planning_center_synced: bool = Field(default=False)
    registration_status: Optional[str] = Field(None, regex="^(registered|cancelled|waitlisted)$")
    registration_notes: Optional[str] = Field(None, max_length=500)


class CourseEnrollmentCreate(CourseEnrollmentBase):
    """Schema for creating a course enrollment"""
    pass


class CourseEnrollmentUpdate(BaseModel):
    """Schema for updating a course enrollment"""
    status: Optional[str] = Field(None, regex="^(enrolled|in_progress|completed|dropped)$")
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    completion_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    dependency_override: Optional[bool] = None
    dependency_override_by: Optional[int] = None
    planning_center_synced: Optional[bool] = None
    registration_status: Optional[str] = Field(None, regex="^(registered|cancelled|waitlisted)$")
    registration_notes: Optional[str] = Field(None, max_length=500)


class CourseEnrollment(CourseEnrollmentBase):
    """Schema for course enrollment response"""
    id: int
    planning_center_registration_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True
