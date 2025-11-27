"""
Autocomplete Suggestion Pydantic schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AutocompleteSuggestionBase(BaseModel):
    """Base schema for autocomplete suggestions"""
    field_type: str = Field(..., max_length=50, description="Type of field (e.g., 'location', 'delivery_mode')")
    value: str = Field(..., max_length=200, description="The suggestion value")


class AutocompleteSuggestionCreate(AutocompleteSuggestionBase):
    """Schema for creating an autocomplete suggestion"""
    pass


class AutocompleteSuggestionUpdate(BaseModel):
    """Schema for updating an autocomplete suggestion"""
    usage_count: Optional[int] = Field(None, ge=0, description="Increment usage count")


class AutocompleteSuggestion(AutocompleteSuggestionBase):
    """Schema for autocomplete suggestion response"""
    id: int
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

