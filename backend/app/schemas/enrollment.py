"""
CourseEnrollment Pydantic schemas (Maps to Planning Center Registrations)
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

from app.schemas.course import Course as CourseSchema
from app.schemas.people import People as PeopleSchema


class CourseEnrollmentBase(BaseModel):
    """Base course enrollment schema"""

    people_id: Optional[int] = None
    course_id: Optional[int] = None  # Legacy field - deprecated, use course_instance_id
    course_instance_id: Optional[int] = None  # New field - links to CourseInstance
    assigned_teacher_id: Optional[int] = None  # Links to CourseInstanceTeacher
    
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
    course: Optional[CourseSchema] = None
    people: Optional[PeopleSchema] = None

    @computed_field
    @property
    def person_id(self) -> Optional[int]:
        """Map people_id to person_id for frontend compatibility"""
        return self.people_id

    @computed_field
    @property
    def person(self) -> Optional[PeopleSchema]:
        """Expose related person data as `person`"""
        return getattr(self, "people", None)

    @computed_field
    @property
    def enrolled_at(self) -> Optional[datetime]:
        """Expose enrollment_date as enrolled_at for frontend compatibility"""
        return self.enrollment_date

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both people_id and person_id


class BulkEnrollFromPCEventRequest(BaseModel):
    """Schema for bulk enrollment from Planning Center event"""
    
    course_id: int = Field(..., description="Course ID to enroll people in")
    pc_event_id: str = Field(..., description="Planning Center event ID")
    status_filter: Optional[List[str]] = Field(
        default=['registered', 'confirmed'],
        description="Only enroll registrations with these statuses"
    )
    update_existing: bool = Field(
        default=True,
        description="Whether to update existing enrollments"
    )


class BulkEnrollFromPCListRequest(BaseModel):
    """Schema for bulk enrollment from Planning Center list"""
    
    course_id: int = Field(..., description="Course ID to enroll people in")
    pc_list_id: str = Field(..., description="Planning Center list ID")
    update_existing: bool = Field(
        default=True,
        description="Whether to update existing enrollments"
    )


class ImportRegistrationsRequest(BaseModel):
    """Schema for importing selected registrations from Planning Center event"""

    course_id: int = Field(..., description="Course ID to enroll people in")
    event_id: str = Field(..., description="Planning Center event ID")
    registration_ids: List[str] = Field(..., description="List of Planning Center registration IDs to import")
    update_existing: bool = Field(
        default=True,
        description="Whether to update existing enrollments"
    )


class BulkDeleteEnrollmentsRequest(BaseModel):
    """Schema for bulk deleting enrollments"""
    enrollment_ids: List[int] = Field(..., min_length=1)
    soft_delete: bool = Field(
        default=False,
        description="If true, sets status to 'dropped' instead of deleting"
    )


class BulkDeleteEnrollmentsResponse(BaseModel):
    """Schema for bulk delete response"""
    deleted_count: int
    deleted_ids: List[int]
    failed_ids: List[int] = []
    errors: List[dict] = []
