"""
Password change schemas
"""

from pydantic import BaseModel, Field


class ChangePasswordRequest(BaseModel):
    """Schema for changing password"""

    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)

