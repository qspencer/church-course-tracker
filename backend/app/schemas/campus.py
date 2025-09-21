"""
Campus Pydantic schemas
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class CampusBase(BaseModel):
    """Base campus schema"""
    name: str = Field(..., min_length=1, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    planning_center_location_id: Optional[str] = Field(None, max_length=50)
    is_active: bool = Field(default=True)


class CampusCreate(CampusBase):
    """Schema for creating a campus"""
    pass


class CampusUpdate(BaseModel):
    """Schema for updating a campus"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    planning_center_location_id: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class Campus(CampusBase):
    """Schema for campus response"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True
