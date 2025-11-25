"""
Program Participant Pydantic schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ProgramParticipantBase(BaseModel):
    """Base program participant schema"""

    program_id: int = Field(..., gt=0)
    people_id: int = Field(..., gt=0)
    role_name: str = Field(..., min_length=1, max_length=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = Field(
        default="active",
        pattern="^(active|paused|completed|ended)$"
    )
    notes: Optional[str] = None
    progress_percentage: float = Field(default=0.0, ge=0, le=100)
    last_activity_date: Optional[datetime] = None


class ProgramParticipantCreate(ProgramParticipantBase):
    """Schema for creating a program participant"""

    pass


class ProgramParticipantUpdate(BaseModel):
    """Schema for updating a program participant"""

    role_name: Optional[str] = Field(None, min_length=1, max_length=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = Field(
        None,
        pattern="^(active|paused|completed|ended)$"
    )
    notes: Optional[str] = None
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    last_activity_date: Optional[datetime] = None


class ProgramParticipant(ProgramParticipantBase):
    """Schema for program participant response"""

    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True

