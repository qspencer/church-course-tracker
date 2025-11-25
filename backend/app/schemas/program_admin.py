"""
Program Admin Pydantic schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProgramAdminBase(BaseModel):
    """Base program admin schema"""

    program_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    can_manage_participants: bool = True
    can_manage_pairings: bool = True
    can_manage_content: bool = True


class ProgramAdminCreate(ProgramAdminBase):
    """Schema for creating a program admin"""

    pass


class ProgramAdminUpdate(BaseModel):
    """Schema for updating a program admin"""

    can_manage_participants: Optional[bool] = None
    can_manage_pairings: Optional[bool] = None
    can_manage_content: Optional[bool] = None


class ProgramAdmin(ProgramAdminBase):
    """Schema for program admin response"""

    id: int
    created_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

