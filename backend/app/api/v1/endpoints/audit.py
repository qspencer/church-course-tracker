"""
Audit log endpoints for system-wide audit trail management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user
from app.schemas.audit_log import AuditLog, AuditLogCreate
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("/", response_model=List[AuditLog])
async def get_audit_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    action: Optional[str] = Query(None, description="Filter by action (insert, update, delete)"),
    changed_by: Optional[int] = Query(None, description="Filter by user ID who made the change"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get system-wide audit logs - Admin only"""
    # Check if user has permission to view audit logs
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can view system audit logs"
        )
    
    audit_service = AuditService(db)
    return audit_service.get_audit_logs(
        skip=skip,
        limit=limit,
        table_name=table_name,
        action=action,
        changed_by=changed_by,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/summary", response_model=Dict[str, Any])
async def get_audit_summary(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get audit log summary statistics - Admin only"""
    # Check if user has permission to view audit logs
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can view audit summaries"
        )
    
    audit_service = AuditService(db)
    return audit_service.get_audit_summary(start_date=start_date, end_date=end_date)


@router.get("/table/{table_name}", response_model=List[AuditLog])
async def get_table_audit_logs(
    table_name: str,
    record_id: Optional[int] = Query(None, description="Filter by specific record ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get audit logs for a specific table - Admin only"""
    # Check if user has permission to view audit logs
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can view table audit logs"
        )
    
    audit_service = AuditService(db)
    return audit_service.get_table_audit_logs(
        table_name=table_name,
        record_id=record_id,
        skip=skip,
        limit=limit
    )


@router.get("/user/{user_id}", response_model=List[AuditLog])
async def get_user_audit_logs(
    user_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get audit logs for a specific user - Admin only"""
    # Check if user has permission to view audit logs
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can view user audit logs"
        )
    
    audit_service = AuditService(db)
    return audit_service.get_user_audit_logs(
        user_id=user_id,
        skip=skip,
        limit=limit
    )


@router.get("/recent")
async def get_recent_audit_logs(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get recent audit logs - Admin only"""
    # Check if user has permission to view audit logs
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can view audit logs"
        )
    
    audit_service = AuditService(db)
    return audit_service.get_recent_audit_logs(
        hours=hours,
        skip=skip,
        limit=limit
    )


@router.get("/export")
async def export_audit_logs(
    format: str = Query("csv", description="Export format (csv, json)"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Export audit logs - Admin only"""
    # Check if user has permission to export audit logs
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can export audit logs"
        )
    
    audit_service = AuditService(db)
    return audit_service.export_audit_logs(
        format=format,
        start_date=start_date,
        end_date=end_date,
        table_name=table_name
    )
