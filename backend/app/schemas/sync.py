"""
Sync Pydantic schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SyncStatus(BaseModel):
    """Sync status schema"""

    last_sync: Optional[datetime] = None
    status: str = Field(..., pattern="^(idle|syncing|error)$")
    records_synced: int = 0
    error_message: Optional[str] = None


class SyncResponse(BaseModel):
    """Sync response schema"""

    success: bool
    records_synced: int
    message: str
    sync_time: datetime
