"""
Report Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


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
