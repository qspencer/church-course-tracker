"""
People Pydantic schemas (from Planning Center)
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date


class PeopleBase(BaseModel):
    """Base people schema"""
    planning_center_id: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=10)
    address1: Optional[str] = Field(None, max_length=255)
    address2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip: Optional[str] = Field(None, max_length=20)
    household_id: Optional[str] = Field(None, max_length=50)
    household_name: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(default="active", max_length=50)
    join_date: Optional[date] = None
    is_active: bool = Field(default=True)


class PeopleCreate(PeopleBase):
    """Schema for creating a person"""
    pass


class PeopleUpdate(BaseModel):
    """Schema for updating a person"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=10)
    address1: Optional[str] = Field(None, max_length=255)
    address2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip: Optional[str] = Field(None, max_length=20)
    household_id: Optional[str] = Field(None, max_length=50)
    household_name: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, max_length=50)
    join_date: Optional[date] = None
    is_active: Optional[bool] = None


class People(PeopleBase):
    """Schema for people response"""
    id: int
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True
