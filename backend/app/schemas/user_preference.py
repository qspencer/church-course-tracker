"""
User preference schemas
"""

from pydantic import BaseModel
from typing import Optional


class UserPreferenceBase(BaseModel):
    """Base user preference schema"""
    
    email_notifications: bool = True
    course_updates: bool = True
    system_announcements: bool = True


class UserPreferenceUpdate(BaseModel):
    """Schema for updating user preferences"""
    
    email_notifications: Optional[bool] = None
    course_updates: Optional[bool] = None
    system_announcements: Optional[bool] = None


class UserPreference(UserPreferenceBase):
    """Schema for user preference response"""
    
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

