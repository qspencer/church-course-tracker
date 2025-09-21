"""
CourseRole Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class CourseRoleBase(BaseModel):
    """Base course role schema"""
    people_id: int
    course_id: int
    role_type: str = Field(..., regex="^(teacher|student|assistant|observer)$")
    assigned_date: date
    assigned_by: Optional[int] = None
    is_active: bool = Field(default=True)


class CourseRoleCreate(CourseRoleBase):
    """Schema for creating a course role"""
    pass


class CourseRoleUpdate(BaseModel):
    """Schema for updating a course role"""
    role_type: Optional[str] = Field(None, regex="^(teacher|student|assistant|observer)$")
    assigned_by: Optional[int] = None
    is_active: Optional[bool] = None


class CourseRole(CourseRoleBase):
    """Schema for course role response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
