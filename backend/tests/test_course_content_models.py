"""
Tests for course content management models
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.course_content import (
    CourseModule, CourseContent, ContentAccessLog, ContentAuditLog,
    ContentType, StorageType
)
from app.models.course import Course
from app.models.user import User


class TestCourseModuleModel:
    """Test CourseModule model"""
    
    def test_create_course_module(self, db_session, sample_course_data, sample_user_data):
        """Test creating a course module"""
        # Create course and user first
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        module_data = {
            "course_id": course.id,
            "title": "Introduction Module",
            "description": "Welcome to the course",
            "order_index": 1,
            "is_active": True,
            "created_by": user.id,
            "updated_by": user.id
        }
        
        module = CourseModule(**module_data)
        db_session.add(module)
        db_session.commit()
        
        assert module.id is not None
        assert module.course_id == course.id
        assert module.title == "Introduction Module"
        assert module.description == "Welcome to the course"
        assert module.order_index == 1
        assert module.is_active is True
        assert module.created_by == user.id
        assert module.updated_by == user.id
        assert module.created_at is not None
        assert module.updated_at is not None
    
    def test_course_module_relationships(self, db_session, sample_course_data, sample_user_data):
        """Test course module relationships"""
        # Create course and user
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        # Create module
        module = CourseModule(
            course_id=course.id,
            title="Test Module",
            order_index=1,
            created_by=user.id
        )
        db_session.add(module)
        db_session.commit()
        
        # Create content item
        content = CourseContent(
            course_id=course.id,
            module_id=module.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1,
            created_by=user.id
        )
        db_session.add(content)
        db_session.commit()
        
        # Test relationships
        assert module.course == course
        assert len(module.content_items) == 1
        assert module.content_items[0] == content
        assert module.created_by_user == user
        assert module.updated_by_user == user


class TestCourseContentModel:
    """Test CourseContent model"""
    
    def test_create_course_content(self, db_session, sample_course_data, sample_user_data):
        """Test creating course content"""
        # Create course and user
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        content_data = {
            "course_id": course.id,
            "title": "Welcome Video",
            "description": "Introduction to the course",
            "content_type": ContentType.VIDEO,
            "storage_type": StorageType.S3,
            "file_name": "welcome.mp4",
            "file_size": 1024000,  # 1MB
            "file_path": "courses/1/welcome.mp4",
            "mime_type": "video/mp4",
            "duration": 300,  # 5 minutes
            "order_index": 1,
            "is_active": True,
            "created_by": user.id,
            "updated_by": user.id
        }
        
        content = CourseContent(**content_data)
        db_session.add(content)
        db_session.commit()
        
        assert content.id is not None
        assert content.course_id == course.id
        assert content.title == "Welcome Video"
        assert content.content_type == ContentType.VIDEO
        assert content.storage_type == StorageType.S3
        assert content.file_name == "welcome.mp4"
        assert content.file_size == 1024000
        assert content.duration == 300
        assert content.download_count == 0
        assert content.view_count == 0
        assert content.created_by == user.id
    
    def test_course_content_relationships(self, db_session, sample_course_data, sample_user_data):
        """Test course content relationships"""
        # Create course, user, and module
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        module = CourseModule(
            course_id=course.id,
            title="Test Module",
            order_index=1,
            created_by=user.id
        )
        db_session.add(module)
        db_session.commit()
        
        # Create content
        content = CourseContent(
            course_id=course.id,
            module_id=module.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1,
            created_by=user.id
        )
        db_session.add(content)
        db_session.commit()
        
        # Test relationships
        assert content.course == course
        assert content.module == module
        assert content.created_by_user == user
        assert content.updated_by_user == user
    
    def test_course_content_with_external_link(self, db_session, sample_course_data, sample_user_data):
        """Test creating content with external link"""
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        content = CourseContent(
            course_id=course.id,
            title="External Resource",
            content_type=ContentType.EXTERNAL_LINK,
            storage_type=StorageType.EXTERNAL,
            external_url="https://example.com/resource",
            order_index=1,
            created_by=user.id
        )
        db_session.add(content)
        db_session.commit()
        
        assert content.content_type == ContentType.EXTERNAL_LINK
        assert content.storage_type == StorageType.EXTERNAL
        assert content.external_url == "https://example.com/resource"
        assert content.file_name is None
        assert content.file_size is None
    
    def test_course_content_with_embedded_content(self, db_session, sample_course_data, sample_user_data):
        """Test creating content with embedded content"""
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        embedded_html = "<iframe src='https://example.com/embed'></iframe>"
        content = CourseContent(
            course_id=course.id,
            title="Embedded Video",
            content_type=ContentType.EMBEDDED,
            storage_type=StorageType.DATABASE,
            embedded_content=embedded_html,
            order_index=1,
            created_by=user.id
        )
        db_session.add(content)
        db_session.commit()
        
        assert content.content_type == ContentType.EMBEDDED
        assert content.embedded_content == embedded_html


class TestContentAccessLogModel:
    """Test ContentAccessLog model"""
    
    def test_create_content_access_log(self, db_session, sample_course_data, sample_user_data):
        """Test creating content access log"""
        # Create course, user, and content
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        content = CourseContent(
            course_id=course.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1,
            created_by=user.id
        )
        db_session.add(content)
        db_session.commit()
        
        access_log_data = {
            "content_id": content.id,
            "user_id": user.id,
            "access_type": "view",
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0...",
            "session_id": "session_123",
            "progress_percentage": 50,
            "time_spent": 120
        }
        
        access_log = ContentAccessLog(**access_log_data)
        db_session.add(access_log)
        db_session.commit()
        
        assert access_log.id is not None
        assert access_log.content_id == content.id
        assert access_log.user_id == user.id
        assert access_log.access_type == "view"
        assert access_log.ip_address == "192.168.1.1"
        assert access_log.progress_percentage == 50
        assert access_log.time_spent == 120
        assert access_log.access_timestamp is not None
    
    def test_content_access_log_relationships(self, db_session, sample_course_data, sample_user_data):
        """Test content access log relationships"""
        # Create course, user, and content
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        content = CourseContent(
            course_id=course.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1,
            created_by=user.id
        )
        db_session.add(content)
        db_session.commit()
        
        # Create access log
        access_log = ContentAccessLog(
            content_id=content.id,
            user_id=user.id,
            access_type="download"
        )
        db_session.add(access_log)
        db_session.commit()
        
        # Test relationships
        assert access_log.content == content
        assert access_log.user == user


class TestContentAuditLogModel:
    """Test ContentAuditLog model"""
    
    def test_create_content_audit_log(self, db_session, sample_course_data, sample_user_data):
        """Test creating content audit log"""
        # Create course, user, and content
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        content = CourseContent(
            course_id=course.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1,
            created_by=user.id
        )
        db_session.add(content)
        db_session.commit()
        
        audit_log_data = {
            "content_id": content.id,
            "user_id": user.id,
            "action": "update",
            "old_values": {"title": "Old Title"},
            "new_values": {"title": "New Title"},
            "change_summary": "Updated content title",
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0..."
        }
        
        audit_log = ContentAuditLog(**audit_log_data)
        db_session.add(audit_log)
        db_session.commit()
        
        assert audit_log.id is not None
        assert audit_log.content_id == content.id
        assert audit_log.user_id == user.id
        assert audit_log.action == "update"
        assert audit_log.old_values == {"title": "Old Title"}
        assert audit_log.new_values == {"title": "New Title"}
        assert audit_log.change_summary == "Updated content title"
        assert audit_log.change_timestamp is not None
    
    def test_content_audit_log_relationships(self, db_session, sample_course_data, sample_user_data):
        """Test content audit log relationships"""
        # Create course, user, and content
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        content = CourseContent(
            course_id=course.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1,
            created_by=user.id
        )
        db_session.add(content)
        db_session.commit()
        
        # Create audit log
        audit_log = ContentAuditLog(
            content_id=content.id,
            user_id=user.id,
            action="create"
        )
        db_session.add(audit_log)
        db_session.commit()
        
        # Test relationships
        assert audit_log.content == content
        assert audit_log.user == user


class TestContentTypeEnum:
    """Test ContentType enum"""
    
    def test_content_type_values(self):
        """Test ContentType enum values"""
        assert ContentType.DOCUMENT.value == "document"
        assert ContentType.VIDEO.value == "video"
        assert ContentType.AUDIO.value == "audio"
        assert ContentType.IMAGE.value == "image"
        assert ContentType.EXTERNAL_LINK.value == "external_link"
        assert ContentType.EMBEDDED.value == "embedded"


class TestStorageTypeEnum:
    """Test StorageType enum"""
    
    def test_storage_type_values(self):
        """Test StorageType enum values"""
        assert StorageType.DATABASE.value == "database"
        assert StorageType.S3.value == "s3"
        assert StorageType.EXTERNAL.value == "external"


class TestModelConstraints:
    """Test model constraints and validations"""
    
    def test_course_module_requires_course(self, db_session, sample_user_data):
        """Test that course module requires a valid course"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        module = CourseModule(
            course_id=999,  # Non-existent course
            title="Test Module",
            order_index=1,
            created_by=user.id
        )
        db_session.add(module)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_course_content_requires_course(self, db_session, sample_user_data):
        """Test that course content requires a valid course"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        content = CourseContent(
            course_id=999,  # Non-existent course
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1,
            created_by=user.id
        )
        db_session.add(content)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_content_access_log_requires_content(self, db_session, sample_user_data):
        """Test that access log requires valid content"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        access_log = ContentAccessLog(
            content_id=999,  # Non-existent content
            user_id=user.id,
            access_type="view"
        )
        db_session.add(access_log)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_content_audit_log_requires_content(self, db_session, sample_user_data):
        """Test that audit log requires valid content"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        audit_log = ContentAuditLog(
            content_id=999,  # Non-existent content
            user_id=user.id,
            action="create"
        )
        db_session.add(audit_log)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


