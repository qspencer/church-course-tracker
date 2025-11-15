"""
ContentCompletion Pydantic schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, computed_field

from app.schemas.course_content import CourseContent


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
    content: Optional[CourseContent] = None

    class Config:
        from_attributes = True

    @computed_field
    def enrollment_id(self) -> int:
        return self.course_enrollment_id

    @computed_field
    def status(self) -> str:
        if self.completed_at:
            return "completed"
        if any(
            value is not None
            for value in (self.time_spent_minutes, self.score, self.notes)
        ):
            return "in_progress"
        return "not_started"


class EnrollmentContentProgress(BaseModel):
    """Schema for aggregated enrollment content progress"""

    id: Optional[int] = None
    enrollment_id: int
    content_id: int
    status: str
    completed_at: Optional[datetime] = None
    time_spent_minutes: Optional[int] = Field(None, ge=0)
    score: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = Field(None, max_length=500)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    content: Optional[CourseContent] = None

    class Config:
        from_attributes = True
