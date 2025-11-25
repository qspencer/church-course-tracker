"""
Program Pairing Pydantic schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProgramPairingBase(BaseModel):
    """Base program pairing schema"""

    program_id: int = Field(..., gt=0)
    primary_participant_id: int = Field(..., gt=0)
    secondary_participant_id: int = Field(..., gt=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = Field(
        default="active",
        pattern="^(active|paused|completed|ended)$"
    )
    notes: Optional[str] = None


class ProgramPairingCreate(ProgramPairingBase):
    """Schema for creating a program pairing"""

    pass


class ProgramPairingUpdate(BaseModel):
    """Schema for updating a program pairing"""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = Field(
        None,
        pattern="^(active|paused|completed|ended)$"
    )
    notes: Optional[str] = None


class ProgramPairing(ProgramPairingBase):
    """Schema for program pairing response"""

    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True

