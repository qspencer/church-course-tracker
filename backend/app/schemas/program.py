"""
Program Pydantic schemas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ProgramBase(BaseModel):
    """Base program schema"""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    
    # Flexible role system - JSON array of role definitions
    role_definitions: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="List of role definitions, each with 'name', 'min_participants', 'max_participants', 'is_primary'"
    )
    
    # Relationship configuration - JSON object
    relationship_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Relationship configuration with 'allow_multiple_secondary', 'max_secondary_per_primary', 'require_pairing'"
    )
    
    # Optional attributes (same as courses)
    locations: Optional[List[str]] = Field(
        None,
        description="List of location strings"
    )
    delivery_modes: Optional[List[str]] = Field(
        None,
        description="List of delivery mode strings"
    )
    prerequisites: Optional[List[int]] = Field(
        None,
        description="List of prerequisite program/course IDs"
    )
    
    # Planning Center integration
    planning_center_event_template_id: Optional[str] = Field(None, max_length=50)
    planning_center_event_id: Optional[str] = Field(None, max_length=50)
    planning_center_event_name: Optional[str] = Field(None, max_length=200)

    # Planning Center Custom Tab configuration for flexible field mapping
    planning_center_tab_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Configuration for importing from Planning Center custom tabs with field mappings"
    )

    is_active: bool = True
    
    @field_validator('role_definitions')
    @classmethod
    def validate_role_definitions(cls, v):
        """Validate role definitions structure"""
        if v is None:
            return v
        for role in v:
            if not isinstance(role, dict):
                raise ValueError("Each role definition must be a dictionary")
            # Required field: name
            if 'name' not in role:
                raise ValueError("Role definition missing required field: name")
            if not isinstance(role['name'], str) or len(role['name']) == 0:
                raise ValueError("Role name must be a non-empty string")
            
            # Optional fields with defaults for backward compatibility
            if 'min_participants' not in role:
                role['min_participants'] = 1  # Default to 1
            if 'max_participants' not in role:
                role['max_participants'] = None  # Default to None (unlimited)
            if 'is_primary' not in role:
                role['is_primary'] = False  # Default to False
            
            # Validate types and values
            if not isinstance(role['min_participants'], int) or role['min_participants'] < 0:
                raise ValueError("min_participants must be a non-negative integer")
            if role['max_participants'] is not None:
                if not isinstance(role['max_participants'], int) or role['max_participants'] < role['min_participants']:
                    raise ValueError("max_participants must be an integer >= min_participants or None")
            if not isinstance(role['is_primary'], bool):
                raise ValueError("is_primary must be a boolean")
        return v
    
    @field_validator('relationship_config')
    @classmethod
    def validate_relationship_config(cls, v):
        """Validate relationship configuration"""
        if v is None:
            return v
        if not isinstance(v, dict):
            raise ValueError("relationship_config must be a dictionary")
        if 'allow_multiple_secondary' in v and not isinstance(v['allow_multiple_secondary'], bool):
            raise ValueError("allow_multiple_secondary must be a boolean")
        if 'max_secondary_per_primary' in v and v['max_secondary_per_primary'] is not None:
            if not isinstance(v['max_secondary_per_primary'], int) or v['max_secondary_per_primary'] < 1:
                raise ValueError("max_secondary_per_primary must be a positive integer or None")
        if 'require_pairing' in v and not isinstance(v['require_pairing'], bool):
            raise ValueError("require_pairing must be a boolean")
        return v


class ProgramCreate(ProgramBase):
    """Schema for creating a program"""

    pass


class ProgramUpdate(BaseModel):
    """Schema for updating a program"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    role_definitions: Optional[List[Dict[str, Any]]] = None
    relationship_config: Optional[Dict[str, Any]] = None
    locations: Optional[List[str]] = None
    delivery_modes: Optional[List[str]] = None
    prerequisites: Optional[List[int]] = None
    planning_center_event_template_id: Optional[str] = Field(None, max_length=50)
    planning_center_event_id: Optional[str] = Field(None, max_length=50)
    planning_center_event_name: Optional[str] = Field(None, max_length=200)
    planning_center_tab_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    
    @field_validator('role_definitions')
    @classmethod
    def validate_role_definitions(cls, v):
        """Validate role definitions structure"""
        if v is None:
            return v
        return ProgramBase.validate_role_definitions(v)
    
    @field_validator('relationship_config')
    @classmethod
    def validate_relationship_config(cls, v):
        """Validate relationship configuration"""
        if v is None:
            return v
        return ProgramBase.validate_relationship_config(v)


class Program(ProgramBase):
    """Schema for program response"""

    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_by_user_name: Optional[str] = None
    updated_by_user_name: Optional[str] = None

    class Config:
        from_attributes = True


class BulkImportParticipantsFromPCEventRequest(BaseModel):
    """Schema for bulk import participants from Planning Center event"""
    
    program_id: int = Field(..., description="Program ID to add participants to")
    pc_event_id: str = Field(..., description="Planning Center event ID")
    role_name: str = Field(..., description="Role name for imported participants")
    status_filter: Optional[List[str]] = Field(
        default=['registered', 'confirmed'],
        description="Only import registrations with these statuses"
    )
    update_existing: bool = Field(
        default=True,
        description="Whether to update existing participants"
    )


class BulkImportParticipantsFromPCListRequest(BaseModel):
    """Schema for bulk import participants from Planning Center list"""

    program_id: int = Field(..., description="Program ID to add participants to")
    pc_list_id: str = Field(..., description="Planning Center list ID")
    role_name: str = Field(..., description="Role name for imported participants")
    update_existing: bool = Field(
        default=True,
        description="Whether to update existing participants"
    )


class BulkDeleteProgramsRequest(BaseModel):
    """Schema for bulk deleting programs"""
    program_ids: List[int] = Field(..., min_length=1)


class BulkDeleteProgramsResponse(BaseModel):
    """Schema for bulk delete response"""
    deleted_count: int
    deleted_ids: List[int]
    failed_ids: List[int] = []
    errors: List[dict] = []

