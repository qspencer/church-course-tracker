"""
Audit service for managing system-wide audit trails
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
import csv
import json
import io

from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogCreate
from app.models.user import User


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def create_audit_log(self, audit_data: AuditLogCreate) -> AuditLog:
        """Create a new audit log entry"""
        audit_log = AuditLog(**audit_data.dict())
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log

    def get_audit_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        table_name: Optional[str] = None,
        action: Optional[str] = None,
        changed_by: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[AuditLog]:
        """Get audit logs with filtering options"""
        query = self.db.query(AuditLog)
        
        # Apply filters
        if table_name:
            query = query.filter(AuditLog.table_name == table_name)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if changed_by:
            query = query.filter(AuditLog.changed_by == changed_by)
        
        if start_date:
            query = query.filter(func.date(AuditLog.changed_at) >= start_date)
        
        if end_date:
            query = query.filter(func.date(AuditLog.changed_at) <= end_date)
        
        # Order by most recent first
        query = query.order_by(desc(AuditLog.changed_at))
        
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    def get_audit_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get audit log summary statistics"""
        query = self.db.query(AuditLog)
        
        # Apply date filters
        if start_date:
            query = query.filter(func.date(AuditLog.changed_at) >= start_date)
        
        if end_date:
            query = query.filter(func.date(AuditLog.changed_at) <= end_date)
        
        # Get total count
        total_logs = query.count()
        
        # Get action breakdown
        action_breakdown = (
            query.with_entities(AuditLog.action, func.count(AuditLog.id))
            .group_by(AuditLog.action)
            .all()
        )
        
        # Get table breakdown
        table_breakdown = (
            query.with_entities(AuditLog.table_name, func.count(AuditLog.id))
            .group_by(AuditLog.table_name)
            .all()
        )
        
        # Get user breakdown
        user_breakdown = (
            query.join(User, AuditLog.changed_by == User.id)
            .with_entities(User.full_name, func.count(AuditLog.id))
            .group_by(User.full_name)
            .all()
        )
        
        # Get recent activity (last 7 days)
        # For SQLite compatibility, use datetime arithmetic instead of interval
        from datetime import timedelta
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        recent_activity = (
            query.filter(
                AuditLog.changed_at >= seven_days_ago
            )
            .with_entities(
                func.date(AuditLog.changed_at).label('date'),
                func.count(AuditLog.id).label('count')
            )
            .group_by(func.date(AuditLog.changed_at))
            .order_by(desc('date'))
            .all()
        )
        
        return {
            "total_logs": total_logs,
            "action_breakdown": {action: count for action, count in action_breakdown},
            "table_breakdown": {table: count for table, count in table_breakdown},
            "user_breakdown": {user: count for user, count in user_breakdown},
            "recent_activity": [
                {"date": str(date), "count": count} 
                for date, count in recent_activity
            ]
        }

    def get_table_audit_logs(
        self,
        table_name: str,
        record_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs for a specific table"""
        query = self.db.query(AuditLog).filter(AuditLog.table_name == table_name)
        
        if record_id:
            query = query.filter(AuditLog.record_id == record_id)
        
        return (
            query.order_by(desc(AuditLog.changed_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_audit_logs(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs for a specific user"""
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.changed_by == user_id)
            .order_by(desc(AuditLog.changed_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def export_audit_logs(
        self,
        format: str = "csv",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        table_name: Optional[str] = None
    ) -> StreamingResponse:
        """Export audit logs in specified format"""
        query = self.db.query(AuditLog)
        
        # Apply filters
        if start_date:
            query = query.filter(func.date(AuditLog.changed_at) >= start_date)
        
        if end_date:
            query = query.filter(func.date(AuditLog.changed_at) <= end_date)
        
        if table_name:
            query = query.filter(AuditLog.table_name == table_name)
        
        # Get all matching records
        audit_logs = query.order_by(desc(AuditLog.changed_at)).all()
        
        if format.lower() == "csv":
            return self._export_csv(audit_logs)
        elif format.lower() == "json":
            return self._export_json(audit_logs)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported export format. Use 'csv' or 'json'"
            )

    def _export_csv(self, audit_logs: List[AuditLog]) -> StreamingResponse:
        """Export audit logs as CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Table Name', 'Record ID', 'Action', 'Changed By',
            'Changed At', 'IP Address', 'User Agent', 'Old Values', 'New Values'
        ])
        
        # Write data
        for log in audit_logs:
            writer.writerow([
                log.id,
                log.table_name,
                log.record_id,
                log.action,
                log.changed_by,
                log.changed_at.isoformat() if log.changed_at else '',
                log.ip_address or '',
                log.user_agent or '',
                json.dumps(log.old_values) if log.old_values else '',
                json.dumps(log.new_values) if log.new_values else ''
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=audit_logs.csv"}
        )

    def _export_json(self, audit_logs: List[AuditLog]) -> StreamingResponse:
        """Export audit logs as JSON"""
        data = []
        for log in audit_logs:
            data.append({
                'id': log.id,
                'table_name': log.table_name,
                'record_id': log.record_id,
                'action': log.action,
                'changed_by': log.changed_by,
                'changed_at': log.changed_at.isoformat() if log.changed_at else None,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
                'old_values': log.old_values,
                'new_values': log.new_values
            })
        
        json_data = json.dumps(data, indent=2, default=str)
        
        return StreamingResponse(
            io.BytesIO(json_data.encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=audit_logs.json"}
        )

    def get_recent_audit_logs(self, hours: int = 24, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get recent audit logs within the specified number of hours"""
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return self.db.query(AuditLog).filter(
            AuditLog.changed_at >= cutoff_time
        ).order_by(desc(AuditLog.changed_at)).offset(skip).limit(limit).all()
