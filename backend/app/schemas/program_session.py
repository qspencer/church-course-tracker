"""
Program Session Pydantic schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProgramSessionBase(BaseModel):
    """Base program session schema"""

    program_id: int = Field(..., gt=0)
    pairing_id: Optional[int] = Field(None, gt=0)
    session_date: datetime
    duration_minutes: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=255)
    session_type: Optional[str] = Field(
        None,
        max_length=50,
        description="e.g., 'in_person', 'online', 'phone', 'video_call'"
    )
    participant_ids: Optional[List[int]] = Field(
        None,
        description="List of ProgramParticipant IDs who attended"
    )
    topics_covered: Optional[str] = None
    notes: Optional[str] = None
    content_completed: Optional[List[int]] = Field(
        None,
        description="List of ProgramContent IDs completed in this session"
    )
    milestones_achieved: Optional[List[str]] = Field(
        None,
        description="List of milestone names/IDs achieved"
    )


class ProgramSessionCreate(ProgramSessionBase):
    """Schema for creating a program session"""

    pass


class ProgramSessionUpdate(BaseModel):
    """Schema for updating a program session"""

    session_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    location: Optional[str] = Field(None, max_length=255)
    session_type: Optional[str] = Field(None, max_length=50)
    participant_ids: Optional[List[int]] = None
    topics_covered: Optional[str] = None
    notes: Optional[str] = None
    content_completed: Optional[List[int]] = None
    milestones_achieved: Optional[List[str]] = None


class ProgramSession(ProgramSessionBase):
    """Schema for program session response"""

    id: int
    created_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

