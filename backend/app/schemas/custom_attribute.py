"""
Custom Attribute Pydantic schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CustomAttributeBase(BaseModel):
    """Base custom attribute schema"""
    
    entity_type: str = Field(..., description="Entity type (person, course, program, enrollment, program_participant)")
    entity_id: int = Field(..., description="Entity ID")
    attribute_name: str = Field(..., max_length=200, description="Custom attribute name")
    pc_attribute_name: Optional[str] = Field(None, max_length=200, description="Original Planning Center attribute name")
    attribute_value: Optional[str] = Field(None, description="Attribute value (stored as text)")
    attribute_type: Optional[str] = Field(None, max_length=50, description="Attribute type (string, number, boolean, date, json)")
    source: str = Field(default='planning_center', max_length=50, description="Source of the attribute")
    planning_center_source_id: Optional[str] = Field(None, max_length=50, description="Planning Center source ID")


class CustomAttributeCreate(CustomAttributeBase):
    """Schema for creating a custom attribute"""
    pass


class CustomAttributeUpdate(BaseModel):
    """Schema for updating a custom attribute"""
    
    attribute_value: Optional[str] = None
    attribute_type: Optional[str] = Field(None, max_length=50)


class CustomAttribute(CustomAttributeBase):
    """Schema for custom attribute response"""
    
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    
    class Config:
        from_attributes = True

