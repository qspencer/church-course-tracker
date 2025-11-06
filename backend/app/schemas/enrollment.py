"""
CourseEnrollment Pydantic schemas (Maps to Planning Center Registrations)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator


class CourseEnrollmentBase(BaseModel):
    """Base course enrollment schema"""

    people_id: Optional[int] = None
    course_id: int
    
    @model_validator(mode='before')
    @classmethod
    def map_person_id_to_people_id(cls, data):
        """Map person_id to people_id if provided (for frontend compatibility)"""
        if isinstance(data, dict):
            if 'person_id' in data and 'people_id' not in data:
                data['people_id'] = data['person_id']
            elif 'person_id' in data and 'people_id' in data:
                # If both are provided, prefer people_id
                data.pop('person_id', None)
        return data
    
    @model_validator(mode='after')
    def validate_people_id(self):
        """Ensure people_id is set"""
        if self.people_id is None:
            raise ValueError("Either people_id or person_id must be provided")
        return self
    enrollment_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(
        default="enrolled", pattern="^(enrolled|in_progress|completed|dropped)$"
    )
    progress_percentage: float = Field(default=0.0, ge=0, le=100)
    completion_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    dependency_override: bool = Field(default=False)
    dependency_override_by: Optional[int] = None
    planning_center_synced: bool = Field(default=False)
    registration_status: Optional[str] = Field(
        None, pattern="^(registered|cancelled|waitlisted)$"
    )
    registration_notes: Optional[str] = Field(None, max_length=500)


class CourseEnrollmentCreate(CourseEnrollmentBase):
    """Schema for creating a course enrollment"""

    pass


class CourseEnrollmentUpdate(BaseModel):
    """Schema for updating a course enrollment"""

    status: Optional[str] = Field(
        None, pattern="^(enrolled|in_progress|completed|dropped)$"
    )
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    completion_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)
    dependency_override: Optional[bool] = None
    dependency_override_by: Optional[int] = None
    planning_center_synced: Optional[bool] = None
    registration_status: Optional[str] = Field(
        None, pattern="^(registered|cancelled|waitlisted)$"
    )
    registration_notes: Optional[str] = Field(None, max_length=500)


class CourseEnrollment(CourseEnrollmentBase):
    """Schema for course enrollment response"""

    id: int
    planning_center_registration_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    @computed_field
    @property
    def person_id(self) -> Optional[int]:
        """Map people_id to person_id for frontend compatibility"""
        return self.people_id

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both people_id and person_id
