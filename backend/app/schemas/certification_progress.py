"""
CertificationProgress Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class CertificationProgressBase(BaseModel):
    """Base certification progress schema"""
    people_id: int
    certification_id: int
    started_date: date
    completed_date: Optional[date] = None
    status: str = Field(default="in_progress", pattern="^(in_progress|completed|expired)$")
    expires_date: Optional[date] = None


class CertificationProgressCreate(CertificationProgressBase):
    """Schema for creating certification progress"""
    pass


class CertificationProgressUpdate(BaseModel):
    """Schema for updating certification progress"""
    completed_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(in_progress|completed|expired)$")
    expires_date: Optional[date] = None


class CertificationProgress(CertificationProgressBase):
    """Schema for certification progress response"""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True
