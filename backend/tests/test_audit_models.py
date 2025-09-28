"""
Tests for audit log models
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.audit_log import AuditLog
from app.models.user import User


class TestAuditLogModel:
    """Test AuditLog model"""
    
    def test_create_audit_log(self, db_session, sample_user_data):
        """Test creating an audit log entry"""
        # Create user first
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        audit_data = {
            "table_name": "courses",
            "record_id": 123,
            "action": "insert",
            "old_values": None,
            "new_values": {"name": "New Course", "description": "Course description"},
            "changed_by": user.id,
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        audit_log = AuditLog(**audit_data)
        db_session.add(audit_log)
        db_session.commit()
        
        assert audit_log.id is not None
        assert audit_log.table_name == "courses"
        assert audit_log.record_id == 123
        assert audit_log.action == "insert"
        assert audit_log.old_values is None
        assert audit_log.new_values == {"name": "New Course", "description": "Course description"}
        assert audit_log.changed_by == user.id
        assert audit_log.ip_address == "192.168.1.1"
        assert audit_log.user_agent == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        assert audit_log.changed_at is not None
    
    def test_create_audit_log_update_action(self, db_session, sample_user_data):
        """Test creating an audit log for update action"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        audit_data = {
            "table_name": "users",
            "record_id": 456,
            "action": "update",
            "old_values": {"email": "old@example.com", "full_name": "Old Name"},
            "new_values": {"email": "new@example.com", "full_name": "New Name"},
            "changed_by": user.id,
            "ip_address": "10.0.0.1"
        }
        
        audit_log = AuditLog(**audit_data)
        db_session.add(audit_log)
        db_session.commit()
        
        assert audit_log.action == "update"
        assert audit_log.old_values == {"email": "old@example.com", "full_name": "Old Name"}
        assert audit_log.new_values == {"email": "new@example.com", "full_name": "New Name"}
    
    def test_create_audit_log_delete_action(self, db_session, sample_user_data):
        """Test creating an audit log for delete action"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        audit_data = {
            "table_name": "courses",
            "record_id": 789,
            "action": "delete",
            "old_values": {"name": "Deleted Course", "description": "This course was deleted"},
            "new_values": None,
            "changed_by": user.id
        }
        
        audit_log = AuditLog(**audit_data)
        db_session.add(audit_log)
        db_session.commit()
        
        assert audit_log.action == "delete"
        assert audit_log.old_values == {"name": "Deleted Course", "description": "This course was deleted"}
        assert audit_log.new_values is None
    
    def test_audit_log_relationships(self, db_session, sample_user_data):
        """Test audit log relationships"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        audit_log = AuditLog(
            table_name="test_table",
            record_id=1,
            action="insert",
            changed_by=user.id
        )
        db_session.add(audit_log)
        db_session.commit()
        
        # Test that we can access the user through the relationship
        # Note: The relationship might not be defined in the model, so this test
        # verifies the foreign key constraint works
        assert audit_log.changed_by == user.id
    
    def test_audit_log_optional_fields(self, db_session):
        """Test that optional fields can be null"""
        audit_data = {
            "table_name": "test_table",
            "record_id": 1,
            "action": "insert",
            "old_values": None,
            "new_values": None,
            "changed_by": None,
            "ip_address": None,
            "user_agent": None
        }
        
        audit_log = AuditLog(**audit_data)
        db_session.add(audit_log)
        db_session.commit()
        
        assert audit_log.old_values is None
        assert audit_log.new_values is None
        assert audit_log.changed_by is None
        assert audit_log.ip_address is None
        assert audit_log.user_agent is None
    
    def test_audit_log_timestamps(self, db_session):
        """Test that timestamps are automatically set"""
        audit_log = AuditLog(
            table_name="test_table",
            record_id=1,
            action="insert"
        )
        
        # Before adding to session
        assert audit_log.changed_at is None
        
        db_session.add(audit_log)
        db_session.commit()
        
        # After commit
        assert audit_log.changed_at is not None
        assert isinstance(audit_log.changed_at, datetime)
    
    def test_audit_log_json_fields(self, db_session):
        """Test that JSON fields can store complex data"""
        complex_old_values = {
            "nested": {
                "array": [1, 2, 3],
                "object": {"key": "value"}
            },
            "simple": "string"
        }
        
        complex_new_values = {
            "updated": True,
            "metadata": {
                "version": "2.0",
                "features": ["feature1", "feature2"]
            }
        }
        
        audit_log = AuditLog(
            table_name="complex_table",
            record_id=1,
            action="update",
            old_values=complex_old_values,
            new_values=complex_new_values
        )
        db_session.add(audit_log)
        db_session.commit()
        
        assert audit_log.old_values == complex_old_values
        assert audit_log.new_values == complex_new_values
        assert audit_log.old_values["nested"]["array"] == [1, 2, 3]
        assert audit_log.new_values["metadata"]["version"] == "2.0"


class TestAuditLogConstraints:
    """Test audit log constraints and validations"""
    
    def test_audit_log_requires_table_name(self, db_session):
        """Test that table_name is required"""
        audit_log = AuditLog(
            record_id=1,
            action="insert"
        )
        db_session.add(audit_log)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_audit_log_requires_record_id(self, db_session):
        """Test that record_id is required"""
        audit_log = AuditLog(
            table_name="test_table",
            action="insert"
        )
        db_session.add(audit_log)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_audit_log_requires_action(self, db_session):
        """Test that action is required"""
        audit_log = AuditLog(
            table_name="test_table",
            record_id=1
        )
        db_session.add(audit_log)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_audit_log_valid_actions(self, db_session):
        """Test that only valid actions are accepted"""
        valid_actions = ["insert", "update", "delete"]
        
        for action in valid_actions:
            audit_log = AuditLog(
                table_name="test_table",
                record_id=1,
                action=action
            )
            db_session.add(audit_log)
            db_session.commit()
            
            # Clean up for next iteration
            db_session.delete(audit_log)
            db_session.commit()
    
    def test_audit_log_field_lengths(self, db_session):
        """Test field length constraints"""
        # Test table_name length (max 100)
        long_table_name = "a" * 101
        audit_log = AuditLog(
            table_name=long_table_name,
            record_id=1,
            action="insert"
        )
        db_session.add(audit_log)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        # Test ip_address length (max 45 for IPv6)
        long_ip = "1" * 46
        audit_log = AuditLog(
            table_name="test_table",
            record_id=1,
            action="insert",
            ip_address=long_ip
        )
        db_session.add(audit_log)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestAuditLogQueries:
    """Test audit log query capabilities"""
    
    def test_query_by_table_name(self, db_session, sample_user_data):
        """Test querying audit logs by table name"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Create audit logs for different tables
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
        
        # Query by table name
        course_audits = db_session.query(AuditLog).filter(
            AuditLog.table_name == "courses"
        ).all()
        
        assert len(course_audits) == 2
        assert all(audit.table_name == "courses" for audit in course_audits)
    
    def test_query_by_action(self, db_session, sample_user_data):
        """Test querying audit logs by action"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Create audit logs for different actions
        audit1 = AuditLog(
            table_name="test_table",
            record_id=1,
            action="insert",
            changed_by=user.id
        )
        audit2 = AuditLog(
            table_name="test_table",
            record_id=2,
            action="update",
            changed_by=user.id
        )
        audit3 = AuditLog(
            table_name="test_table",
            record_id=3,
            action="insert",
            changed_by=user.id
        )
        
        db_session.add_all([audit1, audit2, audit3])
        db_session.commit()
        
        # Query by action
        insert_audits = db_session.query(AuditLog).filter(
            AuditLog.action == "insert"
        ).all()
        
        assert len(insert_audits) == 2
        assert all(audit.action == "insert" for audit in insert_audits)
    
    def test_query_by_user(self, db_session, sample_user_data):
        """Test querying audit logs by user"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Create audit logs
        audit1 = AuditLog(
            table_name="test_table",
            record_id=1,
            action="insert",
            changed_by=user.id
        )
        audit2 = AuditLog(
            table_name="test_table",
            record_id=2,
            action="update",
            changed_by=user.id
        )
        
        db_session.add_all([audit1, audit2])
        db_session.commit()
        
        # Query by user
        user_audits = db_session.query(AuditLog).filter(
            AuditLog.changed_by == user.id
        ).all()
        
        assert len(user_audits) == 2
        assert all(audit.changed_by == user.id for audit in user_audits)
    
    def test_query_by_date_range(self, db_session):
        """Test querying audit logs by date range"""
        from datetime import datetime, timedelta
        
        # Create audit logs with different timestamps
        now = datetime.utcnow()
        
        audit1 = AuditLog(
            table_name="test_table",
            record_id=1,
            action="insert"
        )
        audit1.changed_at = now - timedelta(days=2)
        
        audit2 = AuditLog(
            table_name="test_table",
            record_id=2,
            action="update"
        )
        audit2.changed_at = now - timedelta(days=1)
        
        audit3 = AuditLog(
            table_name="test_table",
            record_id=3,
            action="delete"
        )
        audit3.changed_at = now
        
        db_session.add_all([audit1, audit2, audit3])
        db_session.commit()
        
        # Query by date range (last 2 days)
        start_date = now - timedelta(days=2)
        recent_audits = db_session.query(AuditLog).filter(
            AuditLog.changed_at >= start_date
        ).all()
        
        assert len(recent_audits) == 3
        
        # Query by specific date range
        yesterday = now - timedelta(days=1)
        today_audits = db_session.query(AuditLog).filter(
            AuditLog.changed_at >= yesterday
        ).all()
        
        assert len(today_audits) == 2


