"""
Tests for AuditService
"""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from app.services.audit_service import AuditService
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogCreate


class TestAuditService:
    """Test AuditService functionality"""
    
    def test_create_audit_log(self, db_session, sample_user_data):
        """Test creating an audit log entry"""
        # Setup
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        service = AuditService(db_session)
        
        audit_data = AuditLogCreate(
            table_name="courses",
            record_id=123,
            action="insert",
            old_values=None,
            new_values={"name": "New Course", "description": "Course description"},
            changed_by=user.id,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0..."
        )
        
        # Execute
        result = service.create_audit_log(audit_data)
        
        # Verify
        assert result.id is not None
        assert result.table_name == "courses"
        assert result.record_id == 123
        assert result.action == "insert"
        assert result.old_values is None
        assert result.new_values == {"name": "New Course", "description": "Course description"}
        assert result.changed_by == user.id
        assert result.ip_address == "192.168.1.1"
        assert result.user_agent == "Mozilla/5.0..."
        assert result.changed_at is not None
    
    def test_get_audit_logs(self, db_session, sample_user_data):
        """Test getting audit logs with filters"""
        # Setup
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Create audit logs
        audit1 = AuditLog(
            table_name="courses",
            record_id=1,
            action="insert",
            changed_by=user.id
        )
        audit2 = AuditLog(
            table_name="users",
            record_id=1,
            action="update",
            changed_by=user.id
        )
        audit3 = AuditLog(
            table_name="courses",
            record_id=2,
            action="delete",
            changed_by=user.id
        )
        db_session.add_all([audit1, audit2, audit3])
        db_session.commit()
        
        service = AuditService(db_session)
        
        # Execute - get all audit logs
        result = service.get_audit_logs()
        
        # Verify
        assert len(result) == 3
        
        # Execute - filter by table name
        result = service.get_audit_logs(table_name="courses")
        
        # Verify
        assert len(result) == 2
        assert all(log.table_name == "courses" for log in result)
        
        # Execute - filter by action
        result = service.get_audit_logs(action="insert")
        
        # Verify
        assert len(result) == 1
        assert result[0].action == "insert"
        
        # Execute - filter by user
        result = service.get_audit_logs(changed_by=user.id)
        
        # Verify
        assert len(result) == 3
        assert all(log.changed_by == user.id for log in result)
    
    def test_get_audit_logs_with_date_range(self, db_session, sample_user_data):
        """Test getting audit logs with date range"""
        # Setup
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Create audit logs with different timestamps
        now = datetime.now(timezone.utc)
        
        audit1 = AuditLog(
            table_name="test_table",
            record_id=1,
            action="insert",
            changed_by=user.id
        )
        audit1.changed_at = now - timedelta(days=3)
        
        audit2 = AuditLog(
            table_name="test_table",
            record_id=2,
            action="update",
            changed_by=user.id
        )
        audit2.changed_at = now - timedelta(days=1)
        
        audit3 = AuditLog(
            table_name="test_table",
            record_id=3,
            action="delete",
            changed_by=user.id
        )
        audit3.changed_at = now
        
        db_session.add_all([audit1, audit2, audit3])
        db_session.commit()
        
        service = AuditService(db_session)
        
        # Execute - filter by date range (last 2 days)
        start_date = now - timedelta(days=2)
        result = service.get_audit_logs(start_date=start_date)
        
        # Verify
        assert len(result) == 2
        assert all(log.changed_at >= start_date for log in result)
        
        # Execute - filter by date range with end date
        end_date = now - timedelta(days=1)
        result = service.get_audit_logs(start_date=start_date, end_date=end_date)
        
        # Verify
        assert len(result) == 1
        assert result[0].changed_at >= start_date
        assert result[0].changed_at <= end_date
    
    def test_get_audit_logs_with_pagination(self, db_session, sample_user_data):
        """Test getting audit logs with pagination"""
        # Setup
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Create multiple audit logs
        audits = []
        for i in range(10):
            audit = AuditLog(
                table_name="test_table",
                record_id=i,
                action="insert",
                changed_by=user.id
            )
            audits.append(audit)
        
        db_session.add_all(audits)
        db_session.commit()
        
        service = AuditService(db_session)
        
        # Execute - get first page
        result = service.get_audit_logs(limit=5, skip=0)
        
        # Verify
        assert len(result) == 5
        
        # Execute - get second page
        result = service.get_audit_logs(limit=5, skip=5)
        
        # Verify
        assert len(result) == 5
        
        # Execute - get remaining items
        result = service.get_audit_logs(limit=5, skip=10)
        
        # Verify
        assert len(result) == 0
    
    def test_get_audit_summary(self, db_session, sample_user_data):
        """Test getting audit summary"""
        # Setup
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Create audit logs for different tables and actions
        audit1 = AuditLog(
            table_name="courses",
            record_id=1,
            action="insert",
            changed_by=user.id
        )
        audit2 = AuditLog(
            table_name="courses",
            record_id=2,
            action="update",
            changed_by=user.id
        )
        audit3 = AuditLog(
            table_name="users",
            record_id=1,
            action="insert",
            changed_by=user.id
        )
        audit4 = AuditLog(
            table_name="users",
            record_id=2,
            action="delete",
            changed_by=user.id
        )
        db_session.add_all([audit1, audit2, audit3, audit4])
        db_session.commit()
        
        service = AuditService(db_session)
        
        # Execute
        result = service.get_audit_summary()
        
        # Verify
        assert result["total_logs"] == 4
        assert len(result["table_breakdown"]) == 2
        assert len(result["action_breakdown"]) == 3  # insert, update, delete
        assert "courses" in result["table_breakdown"]
        assert "users" in result["table_breakdown"]
        assert result["table_breakdown"]["courses"] == 2
        assert result["table_breakdown"]["users"] == 2
        assert "insert" in result["action_breakdown"]
        assert "update" in result["action_breakdown"]
        assert "delete" in result["action_breakdown"]
        assert result["action_breakdown"]["insert"] == 2
        assert result["action_breakdown"]["update"] == 1
        assert result["action_breakdown"]["delete"] == 1
    
    def test_get_audit_summary_with_filters(self, db_session, sample_user_data):
        """Test getting audit summary with filters"""
        # Setup
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Create audit logs
        audit1 = AuditLog(
            table_name="courses",
            record_id=1,
            action="insert",
            changed_by=user.id
        )
        audit2 = AuditLog(
            table_name="courses",
            record_id=2,
            action="update",
            changed_by=user.id
        )
        audit3 = AuditLog(
            table_name="users",
            record_id=1,
            action="insert",
            changed_by=user.id
        )
        db_session.add_all([audit1, audit2, audit3])
        db_session.commit()
        
        service = AuditService(db_session)
        
        # Execute - filter by date range
        from datetime import date
        today = date.today()
        result = service.get_audit_summary(start_date=today, end_date=today)
        
        # Verify
        assert result["total_logs"] == 3
        assert len(result["table_breakdown"]) == 2
        assert "courses" in result["table_breakdown"]
        assert "users" in result["table_breakdown"]
        assert result["table_breakdown"]["courses"] == 2
        assert result["table_breakdown"]["users"] == 1
    
    def test_get_table_audit_logs(self, db_session, sample_user_data):
        """Test getting audit logs for a specific table"""
        # Setup
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Create audit logs for different records
        audit1 = AuditLog(
            table_name="courses",
            record_id=123,
            action="insert",
            changed_by=user.id
        )
        audit2 = AuditLog(
            table_name="courses",
            record_id=123,
            action="update",
            changed_by=user.id
        )
        audit3 = AuditLog(
            table_name="courses",
            record_id=456,
            action="insert",
            changed_by=user.id
        )
        db_session.add_all([audit1, audit2, audit3])
        db_session.commit()
        
        service = AuditService(db_session)
        
        # Execute - get all logs for courses table
        result = service.get_table_audit_logs("courses")
        
        # Verify
        assert len(result) == 3
        assert all(log.table_name == "courses" for log in result)
        
        # Execute - get logs for specific record
        result = service.get_table_audit_logs("courses", record_id=123)
        
        # Verify
        assert len(result) == 2
        assert all(log.record_id == 123 for log in result)
        assert result[0].action == "insert"
        assert result[1].action == "update"
    
    def test_get_user_audit_logs(self, db_session, sample_user_data):
        """Test getting audit logs for a specific user"""
        # Setup
        user1 = User(**sample_user_data)
        user2 = User(
            username="user2",
            email="user2@example.com",
            full_name="User Two",
            hashed_password="hashed_password",
            role="staff",
            is_active=True
        )
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Create audit logs for different users
        audit1 = AuditLog(
            table_name="courses",
            record_id=1,
            action="insert",
            changed_by=user1.id
        )
        audit2 = AuditLog(
            table_name="courses",
            record_id=2,
            action="update",
            changed_by=user1.id
        )
        audit3 = AuditLog(
            table_name="courses",
            record_id=3,
            action="insert",
            changed_by=user2.id
        )
        db_session.add_all([audit1, audit2, audit3])
        db_session.commit()
        
        service = AuditService(db_session)
        
        # Execute
        result = service.get_user_audit_logs(user1.id)
        
        # Verify
        assert len(result) == 2
        assert all(log.changed_by == user1.id for log in result)
        assert result[0].action == "insert"
        assert result[1].action == "update"
    
    def test_get_recent_audit_logs(self, db_session, sample_user_data):
        """Test getting recent audit logs"""
        # Setup
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Create audit logs with different timestamps
        now = datetime.now(timezone.utc)
        
        audit1 = AuditLog(
            table_name="test_table",
            record_id=1,
            action="insert",
            changed_by=user.id,
            changed_at=now - timedelta(minutes=30)  # 30 minutes ago
        )
        
        audit2 = AuditLog(
            table_name="test_table",
            record_id=2,
            action="update",
            changed_by=user.id,
            changed_at=now - timedelta(minutes=90)  # 90 minutes ago
        )
        
        audit3 = AuditLog(
            table_name="test_table",
            record_id=3,
            action="delete",
            changed_by=user.id,
            changed_at=now - timedelta(hours=3)  # 3 hours ago
        )
        
        db_session.add_all([audit1, audit2, audit3])
        db_session.commit()
        
        service = AuditService(db_session)
        
        # Execute - get recent logs (last 2 hours)
        result = service.get_recent_audit_logs(hours=2)
        
        # Verify - should get 2 logs (30 min and 90 min ago)
        assert len(result) == 2
        assert all(log.changed_at >= now - timedelta(hours=2) for log in result)
        
        # Execute - get recent logs (last 1 hour)
        result = service.get_recent_audit_logs(hours=1)
        
        # Verify - should get 1 log (30 min ago)
        assert len(result) == 1
        assert result[0].changed_at >= now - timedelta(hours=1)


class TestAuditServiceErrorHandling:
    """Test AuditService error handling"""
    
    def test_get_table_audit_logs_nonexistent(self, db_session):
        """Test getting audit logs for nonexistent record"""
        service = AuditService(db_session)
        
        # Execute
        result = service.get_table_audit_logs("nonexistent_table", record_id=999)
        
        # Verify
        assert len(result) == 0
    
    def test_get_user_audit_logs_nonexistent(self, db_session):
        """Test getting audit logs for nonexistent user"""
        service = AuditService(db_session)
        
        # Execute
        result = service.get_user_audit_logs(999)
        
        # Verify
        assert len(result) == 0
    
    def test_get_audit_summary_empty_database(self, db_session):
        """Test getting audit summary from empty database"""
        service = AuditService(db_session)
        
        # Execute
        result = service.get_audit_summary()
        
        # Verify
        assert result["total_logs"] == 0
        assert len(result["action_breakdown"]) == 0
        assert len(result["table_breakdown"]) == 0
        assert len(result["user_breakdown"]) == 0
    
    def test_get_recent_audit_logs_empty_database(self, db_session):
        """Test getting recent audit logs from empty database"""
        service = AuditService(db_session)
        
        # Execute
        result = service.get_recent_audit_logs(hours=24)
        
        # Verify
        assert len(result) == 0


class TestAuditServiceComplexQueries:
    """Test AuditService complex query scenarios"""
    
    def test_get_audit_logs_multiple_filters(self, db_session, sample_user_data):
        """Test getting audit logs with multiple filters"""
        # Setup
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Create audit logs
        audit1 = AuditLog(
            table_name="courses",
            record_id=1,
            action="insert",
            changed_by=user.id
        )
        audit2 = AuditLog(
            table_name="courses",
            record_id=2,
            action="update",
            changed_by=user.id
        )
        audit3 = AuditLog(
            table_name="users",
            record_id=1,
            action="insert",
            changed_by=user.id
        )
        db_session.add_all([audit1, audit2, audit3])
        db_session.commit()
        
        service = AuditService(db_session)
        
        # Execute - filter by table name and action
        result = service.get_audit_logs(table_name="courses", action="insert")
        
        # Verify
        assert len(result) == 1
        assert result[0].table_name == "courses"
        assert result[0].action == "insert"
        
        # Execute - filter by table name and user
        result = service.get_audit_logs(table_name="courses", changed_by=user.id)
        
        # Verify
        assert len(result) == 2
        assert all(log.table_name == "courses" for log in result)
        assert all(log.changed_by == user.id for log in result)
    
    def test_get_audit_logs_with_sorting(self, db_session, sample_user_data):
        """Test getting audit logs with sorting"""
        # Setup
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Create audit logs with different timestamps
        now = datetime.now(timezone.utc)
        
        audit1 = AuditLog(
            table_name="test_table",
            record_id=1,
            action="insert",
            changed_by=user.id
        )
        audit1.changed_at = now - timedelta(hours=1)
        
        audit2 = AuditLog(
            table_name="test_table",
            record_id=2,
            action="update",
            changed_by=user.id
        )
        audit2.changed_at = now - timedelta(hours=2)
        
        audit3 = AuditLog(
            table_name="test_table",
            record_id=3,
            action="delete",
            changed_by=user.id
        )
        audit3.changed_at = now - timedelta(hours=3)
        
        db_session.add_all([audit1, audit2, audit3])
        db_session.commit()
        
        service = AuditService(db_session)
        
        # Execute - get logs (already sorted by changed_at desc by default)
        result = service.get_audit_logs()
        
        # Verify
        assert len(result) == 3
        # Results should be ordered by changed_at descending (newest first)
        assert result[0].changed_at >= result[1].changed_at
        assert result[1].changed_at >= result[2].changed_at


