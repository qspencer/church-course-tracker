"""
Certification Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CertificationBase(BaseModel):
    """Base certification schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    required_courses: Optional[List[int]] = None  # Array of course IDs
    validity_months: Optional[int] = Field(None, ge=1)
    is_active: bool = Field(default=True)


class CertificationCreate(CertificationBase):
    """Schema for creating a certification"""
    pass


class CertificationUpdate(BaseModel):
    """Schema for updating a certification"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    required_courses: Optional[List[int]] = None
    validity_months: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class Certification(CertificationBase):
    """Schema for certification response"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True
