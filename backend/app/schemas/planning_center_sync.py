"""
Planning Center Sync Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class PlanningCenterSyncLogBase(BaseModel):
    """Base sync log schema"""
    sync_type: str = Field(..., regex="^(people|events|registrations|custom_fields)$")
    sync_direction: str = Field(..., regex="^(from_pc|to_pc)$")
    records_processed: int = Field(default=0, ge=0)
    records_successful: int = Field(default=0, ge=0)
    records_failed: int = Field(default=0, ge=0)
    error_details: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_by: Optional[int] = None


class PlanningCenterSyncLogCreate(PlanningCenterSyncLogBase):
    """Schema for creating sync log"""
    pass


class PlanningCenterSyncLog(PlanningCenterSyncLogBase):
    """Schema for sync log response"""
    id: int
    
    class Config:
        from_attributes = True


class PlanningCenterWebhookEventBase(BaseModel):
    """Base webhook event schema"""
    event_type: str = Field(..., min_length=1, max_length=100)
    planning_center_id: str = Field(..., min_length=1, max_length=50)
    payload: Dict[str, Any]
    processed: bool = Field(default=False)
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class PlanningCenterWebhookEventCreate(PlanningCenterWebhookEventBase):
    """Schema for creating webhook event"""
    pass


class PlanningCenterWebhookEventUpdate(BaseModel):
    """Schema for updating webhook event"""
    processed: Optional[bool] = None
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class PlanningCenterWebhookEvent(PlanningCenterWebhookEventBase):
    """Schema for webhook event response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PlanningCenterEventsCacheBase(BaseModel):
    """Base events cache schema"""
    planning_center_event_id: str = Field(..., min_length=1, max_length=50)
    event_name: str = Field(..., min_length=1, max_length=200)
    event_description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_capacity: Optional[int] = Field(None, ge=0)
    current_registrations_count: int = Field(default=0, ge=0)
    registration_deadline: Optional[datetime] = None
    event_status: Optional[str] = Field(None, max_length=50)
    last_synced_at: Optional[datetime] = None


class PlanningCenterEventsCacheCreate(PlanningCenterEventsCacheBase):
    """Schema for creating events cache"""
    pass


class PlanningCenterEventsCacheUpdate(BaseModel):
    """Schema for updating events cache"""
    event_name: Optional[str] = Field(None, min_length=1, max_length=200)
    event_description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    max_capacity: Optional[int] = Field(None, ge=0)
    current_registrations_count: Optional[int] = Field(None, ge=0)
    registration_deadline: Optional[datetime] = None
    event_status: Optional[str] = Field(None, max_length=50)
    last_synced_at: Optional[datetime] = None


class PlanningCenterEventsCache(PlanningCenterEventsCacheBase):
    """Schema for events cache response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PlanningCenterRegistrationsCacheBase(BaseModel):
    """Base registrations cache schema"""
    planning_center_registration_id: str = Field(..., min_length=1, max_length=50)
    planning_center_event_id: str = Field(..., min_length=1, max_length=50)
    planning_center_person_id: str = Field(..., min_length=1, max_length=50)
    registration_status: Optional[str] = Field(None, max_length=50)
    registration_date: Optional[datetime] = None
    registration_notes: Optional[str] = None
    custom_field_responses: Optional[Dict[str, Any]] = None
    last_synced_at: Optional[datetime] = None


class PlanningCenterRegistrationsCacheCreate(PlanningCenterRegistrationsCacheBase):
    """Schema for creating registrations cache"""
    pass


class PlanningCenterRegistrationsCacheUpdate(BaseModel):
    """Schema for updating registrations cache"""
    registration_status: Optional[str] = Field(None, max_length=50)
    registration_date: Optional[datetime] = None
    registration_notes: Optional[str] = None
    custom_field_responses: Optional[Dict[str, Any]] = None
    last_synced_at: Optional[datetime] = None


class PlanningCenterRegistrationsCache(PlanningCenterRegistrationsCacheBase):
    """Schema for registrations cache response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
