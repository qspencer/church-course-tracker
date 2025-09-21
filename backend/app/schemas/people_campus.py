"""
PeopleCampus Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class PeopleCampusBase(BaseModel):
    """Base people campus schema"""
    people_id: int
    campus_id: int
    assigned_date: date
    is_primary: bool = Field(default=False)
    is_active: bool = Field(default=True)


class PeopleCampusCreate(PeopleCampusBase):
    """Schema for creating a people campus relationship"""
    pass


class PeopleCampusUpdate(BaseModel):
    """Schema for updating a people campus relationship"""
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None


class PeopleCampus(PeopleCampusBase):
    """Schema for people campus response"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True
