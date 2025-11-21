"""
CourseInstance Pydantic schemas (Course Offerings)
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CourseInstanceBase(BaseModel):
    """Base course instance schema"""

    course_id: int = Field(..., description="Master Course ID")
    instance_name: str = Field(..., min_length=1, max_length=200, description="Name of the offering")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    schedule: Optional[dict] = Field(
        None, description="Optional schedule JSON: {day_of_week, time, frequency}"
    )
    max_capacity: Optional[int] = Field(None, ge=1)
    planning_center_event_id: Optional[str] = Field(None, max_length=50)
    planning_center_event_name: Optional[str] = Field(None, max_length=200)
    is_active: bool = Field(default=True)
    enrollment_open: bool = Field(default=True)
    enrollment_deadline: Optional[datetime] = None
    campus_id: Optional[int] = Field(None, description="Campus where this offering takes place")


class CourseInstanceCreate(CourseInstanceBase):
    """Schema for creating a course instance"""

    pass


class CourseInstanceUpdate(BaseModel):
    """Schema for updating a course instance"""

    instance_name: Optional[str] = Field(None, min_length=1, max_length=200)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    schedule: Optional[dict] = None
    max_capacity: Optional[int] = Field(None, ge=1)
    planning_center_event_id: Optional[str] = Field(None, max_length=50)
    planning_center_event_name: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None
    enrollment_open: Optional[bool] = None
    enrollment_deadline: Optional[datetime] = None
    campus_id: Optional[int] = None


class CourseInstance(CourseInstanceBase):
    """Schema for course instance response"""

    id: int
    current_enrollments: int = Field(default=0)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class CourseInstanceTeacherBase(BaseModel):
    """Base course instance teacher schema"""

    people_id: int = Field(..., description="Person ID of the teacher")
    role_type: str = Field(
        ..., pattern="^(teacher|mentor|assistant|co-teacher)$", description="Teacher role type"
    )
    assigned_date: date
    is_primary: bool = Field(default=False, description="Primary teacher/mentor")
    max_students: Optional[int] = Field(None, ge=1, description="Max students for 1:1 discipleship")
    is_active: bool = Field(default=True)


class CourseInstanceTeacherCreate(CourseInstanceTeacherBase):
    """Schema for creating a course instance teacher"""

    pass


class CourseInstanceTeacherUpdate(BaseModel):
    """Schema for updating a course instance teacher"""

    role_type: Optional[str] = Field(None, pattern="^(teacher|mentor|assistant|co-teacher)$")
    is_primary: Optional[bool] = None
    max_students: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class CourseInstanceTeacher(CourseInstanceTeacherBase):
    """Schema for course instance teacher response"""

    id: int
    course_instance_id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True

