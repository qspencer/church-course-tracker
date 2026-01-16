"""
AuditLog Pydantic schemas
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AuditLogBase(BaseModel):
    """Base audit log schema"""

    table_name: str = Field(..., min_length=1, max_length=100)
    record_id: int = Field(..., ge=1)
    action: str = Field(..., pattern="^(insert|update|delete)$")
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changed_by: Optional[int] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating audit log"""

    pass


class AuditLog(AuditLogBase):
    """Full schema for audit log (response model)"""

    id: int
    changed_at: datetime
    changed_by_user_name: Optional[str] = None  # User name for display

    class Config:
        from_attributes = True
