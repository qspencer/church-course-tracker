"""
Program Progress Pydantic schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ProgramProgressBase(BaseModel):
    """Base program progress schema"""

    program_id: int = Field(..., gt=0)
    participant_id: int = Field(..., gt=0)
    progress_type: str = Field(
        ...,
        pattern="^(content_completion|session_completion|milestone)$"
    )
    
    # Content completion fields
    content_id: Optional[int] = Field(None, gt=0)
    completion_date: Optional[datetime] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    
    # Session completion fields
    session_id: Optional[int] = Field(None, gt=0)
    
    # Milestone fields
    milestone_name: Optional[str] = Field(None, max_length=200)
    milestone_description: Optional[str] = None
    
    notes: Optional[str] = None
    
    @field_validator('progress_type')
    @classmethod
    def validate_progress_type_fields(cls, v, info):
        """Validate that required fields are provided based on progress_type"""
        data = info.data if hasattr(info, 'data') else {}
        progress_type = v
        
        if progress_type == "content_completion":
            if not data.get("content_id"):
                raise ValueError("content_id is required for content_completion progress type")
        elif progress_type == "session_completion":
            if not data.get("session_id"):
                raise ValueError("session_id is required for session_completion progress type")
        elif progress_type == "milestone":
            if not data.get("milestone_name"):
                raise ValueError("milestone_name is required for milestone progress type")
        
        return v


class ProgramProgressCreate(ProgramProgressBase):
    """Schema for creating program progress"""

    pass


class ProgramProgressUpdate(BaseModel):
    """Schema for updating program progress"""

    progress_type: Optional[str] = Field(
        None,
        pattern="^(content_completion|session_completion|milestone)$"
    )
    content_id: Optional[int] = Field(None, gt=0)
    completion_date: Optional[datetime] = None
    completion_percentage: Optional[int] = Field(None, ge=0, le=100)
    session_id: Optional[int] = Field(None, gt=0)
    milestone_name: Optional[str] = Field(None, max_length=200)
    milestone_description: Optional[str] = None
    notes: Optional[str] = None


class ProgramProgress(ProgramProgressBase):
    """Schema for program progress response"""

    id: int
    created_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

