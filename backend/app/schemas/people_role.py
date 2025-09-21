"""
PeopleRole Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class PeopleRoleBase(BaseModel):
    """Base people role schema"""
    people_id: int
    role_id: int
    assigned_date: date
    assigned_by: Optional[int] = None
    is_active: bool = Field(default=True)


class PeopleRoleCreate(PeopleRoleBase):
    """Schema for creating a people role relationship"""
    pass


class PeopleRoleUpdate(BaseModel):
    """Schema for updating a people role relationship"""
    assigned_by: Optional[int] = None
    is_active: Optional[bool] = None


class PeopleRole(PeopleRoleBase):
    """Schema for people role response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
