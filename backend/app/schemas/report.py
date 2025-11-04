"""
Report Pydantic schemas
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReportType(str, Enum):
    """Report type enumeration"""

    ENROLLMENT = "enrollment"
    COMPLETION = "completion"
    MEMBER_PROGRESS = "member_progress"


class ReportData(BaseModel):
    """Report data structure"""

    headers: List[str]
    rows: List[List[Any]]
    summary: Dict[str, Any]


class ReportResponse(BaseModel):
    """Report response schema"""

    report_type: ReportType
    generated_at: datetime
    filters: Dict[str, Any]
    data: ReportData
    total_records: int


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
