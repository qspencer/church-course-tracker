"""
System Settings Pydantic schemas
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class SystemSettingsBase(BaseModel):
    """Base system settings schema"""

    key: str = Field(..., min_length=1, max_length=100)
    value: Optional[str] = None
    category: str = Field(..., pattern="^(system|planning_center|security|backup)$")
    data_type: str = Field(..., pattern="^(string|integer|boolean|json)$")
    description: Optional[str] = None
    is_sensitive: bool = False


class SystemSettingsCreate(SystemSettingsBase):
    """Schema for creating a system setting"""

    pass


class SystemSettingsUpdate(BaseModel):
    """Schema for updating a system setting"""

    value: Optional[str] = None
    description: Optional[str] = None

    @field_validator("value")
    @classmethod
    def validate_value(cls, v):
        """Allow empty string for clearing values"""
        if v is None:
            return None
        return str(v)


class SystemSettings(SystemSettingsBase):
    """Schema for system settings response"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class SystemSettingsCategory(BaseModel):
    """Schema for settings grouped by category"""

    category: str
    settings: List[SystemSettings]


class SystemSettingsBatchUpdate(BaseModel):
    """Schema for batch updating multiple settings"""

    settings: Dict[str, str] = Field(..., description="Dictionary of key-value pairs to update")

    @field_validator("settings")
    @classmethod
    def validate_settings(cls, v):
        """Ensure settings dictionary is not empty"""
        if not v:
            raise ValueError("Settings dictionary cannot be empty")
        return v


class PlanningCenterConfig(BaseModel):
    """Schema for Planning Center configuration"""

    api_url: str
    app_id: Optional[str] = None
    secret: Optional[str] = None
    access_token: Optional[str] = None
    max_events: int = Field(default=2000, ge=1, le=10000)
    cache_ttl_minutes: int = Field(default=10, ge=0, le=1440)
    use_mock: bool = False
