"""
Tests for ContentService
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from fastapi import HTTPException

from app.services.content_service import ContentService
from app.models.course_content import (
    CourseModule, CourseContent, ContentAccessLog, ContentAuditLog,
    ContentType, StorageType
)
from app.models.course import Course
from app.models.user import User
from app.schemas.course_content import (
    CourseModuleCreate, CourseModuleUpdate,
    CourseContentCreate, CourseContentUpdate,
    ContentAccessLogCreate, ContentAuditLogCreate,
    ContentProgressUpdate
)


class TestContentService:
    """Test ContentService functionality"""
    
    def test_create_module(self, db_session, sample_course_data, sample_user_data):
        """Test creating a course module"""
        # Setup
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        service = ContentService(db_session)
        
        module_data = CourseModuleCreate(
            course_id=course.id,
            title="Introduction Module",
            description="Welcome to the course",
            order_index=1
        )
        
        # Execute
        result = service.create_module(module_data, user.id)
        
        # Verify
        assert result.id is not None
        assert result.course_id == course.id
        assert result.title == "Introduction Module"
        assert result.description == "Welcome to the course"
        assert result.order_index == 1
        assert result.is_active is True
        assert result.created_by == user.id
        assert result.updated_by == user.id
    
    def test_get_course_modules(self, db_session, sample_course_data, sample_user_data):
        """Test getting course modules"""
        # Setup
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        # Create modules
        module1 = CourseModule(
            course_id=course.id,
            title="Module 1",
            order_index=1,
            created_by=user.id
        )
        module2 = CourseModule(
            course_id=course.id,
            title="Module 2",
            order_index=2,
            created_by=user.id
        )
        db_session.add_all([module1, module2])
        db_session.commit()
        
        service = ContentService(db_session)
        
        # Execute
        result = service.get_course_modules(course.id)
        
        # Verify
        assert len(result) == 2
        assert result[0].title == "Module 1"
        assert result[1].title == "Module 2"
        assert result[0].order_index == 1
        assert result[1].order_index == 2
    
    def test_update_module(self, db_session, sample_course_data, sample_user_data):
        """Test updating a course module"""
        # Setup
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        module = CourseModule(
            course_id=course.id,
            title="Original Title",
            order_index=1,
            created_by=user.id
        )
        db_session.add(module)
        db_session.commit()
        
        service = ContentService(db_session)
        
        update_data = CourseModuleUpdate(
            title="Updated Title",
            description="New description",
            order_index=2
        )
        
        # Execute
        result = service.update_module(module.id, update_data, user.id)
        
        # Verify
        assert result.title == "Updated Title"
        assert result.description == "New description"
        assert result.order_index == 2
        assert result.updated_by == user.id
    
    def test_delete_module(self, db_session, sample_course_data, sample_user_data):
        """Test deleting a course module"""
        # Setup
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
        
        service = ContentService(db_session)
        
        # Execute
        service.delete_module(module.id)
        
        # Verify
        deleted_module = db_session.query(CourseModule).filter(
            CourseModule.id == module.id
        ).first()
        assert deleted_module is None
    
    def test_create_content(self, db_session, sample_course_data, sample_user_data):
        """Test creating course content"""
        # Setup
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        service = ContentService(db_session)
        
        content_data = CourseContentCreate(
            course_id=course.id,
            title="Welcome Video",
            description="Introduction video",
            content_type=ContentType.VIDEO,
            storage_type=StorageType.S3,
            file_name="welcome.mp4",
            file_size=1024000,
            duration=300,
            order_index=1
        )
        
        # Execute
        result = service.create_content(content_data, user.id)
        
        # Verify
        assert result.id is not None
        assert result.course_id == course.id
        assert result.title == "Welcome Video"
        assert result.content_type == ContentType.VIDEO
        assert result.storage_type == StorageType.S3
        assert result.file_name == "welcome.mp4"
        assert result.file_size == 1024000
        assert result.duration == 300
        assert result.created_by == user.id
    
    def test_get_course_content(self, db_session, sample_course_data, sample_user_data):
        """Test getting course content"""
        # Setup
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        # Create content items
        content1 = CourseContent(
            course_id=course.id,
            title="Content 1",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1,
            created_by=user.id
        )
        content2 = CourseContent(
            course_id=course.id,
            title="Content 2",
            content_type=ContentType.VIDEO,
            storage_type=StorageType.S3,
            order_index=2,
            created_by=user.id
        )
        db_session.add_all([content1, content2])
        db_session.commit()
        
        service = ContentService(db_session)
        
        # Execute
        result = service.get_course_content(course.id)
        
        # Verify
        assert len(result) == 2
        assert result[0].title == "Content 1"
        assert result[1].title == "Content 2"
    
    def test_update_content(self, db_session, sample_course_data, sample_user_data):
        """Test updating course content"""
        # Setup
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        content = CourseContent(
            course_id=course.id,
            title="Original Title",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1,
            created_by=user.id
        )
        db_session.add(content)
        db_session.commit()
        
        service = ContentService(db_session)
        
        update_data = CourseContentUpdate(
            title="Updated Title",
            description="New description",
            order_index=2
        )
        
        # Execute
        result = service.update_content(content.id, update_data, user.id)
        
        # Verify
        assert result.title == "Updated Title"
        assert result.description == "New description"
        assert result.order_index == 2
        assert result.updated_by == user.id
    
    def test_delete_content(self, db_session, sample_course_data, sample_user_data):
        """Test deleting course content"""
        # Setup
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
        
        service = ContentService(db_session)
        
        # Execute
        service.delete_content(content.id)
        
        # Verify
        deleted_content = db_session.query(CourseContent).filter(
            CourseContent.id == content.id
        ).first()
        assert deleted_content is None
    
    def test_log_content_access(self, db_session, sample_course_data, sample_user_data):
        """Test logging content access"""
        # Setup
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
        
        service = ContentService(db_session)
        
        access_data = ContentAccessLogCreate(
            content_id=content.id,
            user_id=user.id,
            access_type="view",
            progress_percentage=50,
            time_spent=120
        )
        
        # Execute
        result = service.log_content_access(access_data)
        
        # Verify
        assert result.id is not None
        assert result.content_id == content.id
        assert result.user_id == user.id
        assert result.access_type == "view"
        assert result.progress_percentage == 50
        assert result.time_spent == 120
    
    def test_get_audit_logs(self, db_session, sample_course_data, sample_user_data):
        """Test getting audit logs for content"""
        # Setup
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
        
        # Create audit logs
        audit1 = ContentAuditLog(
            content_id=content.id,
            user_id=user.id,
            action="create"
        )
        audit2 = ContentAuditLog(
            content_id=content.id,
            user_id=user.id,
            action="update"
        )
        db_session.add_all([audit1, audit2])
        db_session.commit()
        
        service = ContentService(db_session)
        
        # Execute
        result = service.get_audit_logs(content.id, limit=10)
        
        # Verify
        assert len(result) == 2
        assert result[0].action == "create"
        assert result[1].action == "update"
    
    def test_get_content_summary(self, db_session, sample_course_data, sample_user_data):
        """Test getting course content summary"""
        # Setup
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        # Create modules
        module1 = CourseModule(
            course_id=course.id,
            title="Module 1",
            order_index=1,
            created_by=user.id
        )
        module2 = CourseModule(
            course_id=course.id,
            title="Module 2",
            order_index=2,
            created_by=user.id
        )
        db_session.add_all([module1, module2])
        db_session.commit()
        
        # Create content items
        content1 = CourseContent(
            course_id=course.id,
            module_id=module1.id,
            title="Content 1",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            file_size=1024,
            order_index=1,
            created_by=user.id
        )
        content2 = CourseContent(
            course_id=course.id,
            module_id=module2.id,
            title="Content 2",
            content_type=ContentType.VIDEO,
            storage_type=StorageType.S3,
            file_size=2048,
            order_index=1,
            created_by=user.id
        )
        db_session.add_all([content1, content2])
        db_session.commit()
        
        service = ContentService(db_session)
        
        # Execute
        result = service.get_content_summary(course.id)
        
        # Verify
        assert result.total_modules == 2
        assert result.total_content_items == 2
        assert result.total_file_size == 3072  # 1024 + 2048
        assert "document" in result.content_type_distribution
        assert "video" in result.content_type_distribution
        assert result.content_type_distribution["document"] == 1
        assert result.content_type_distribution["video"] == 1


class TestContentServiceErrorHandling:
    """Test ContentService error handling"""
    
    def test_create_module_nonexistent_course(self, db_session, sample_user_data):
        """Test creating module for nonexistent course"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        service = ContentService(db_session)
        
        module_data = CourseModuleCreate(
            course_id=999,  # Non-existent course
            title="Test Module",
            order_index=1
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_module(module_data, user.id)
        
        assert exc_info.value.status_code == 404
    
    def test_update_nonexistent_module(self, db_session, sample_user_data):
        """Test updating nonexistent module"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        service = ContentService(db_session)
        
        update_data = CourseModuleUpdate(title="Updated Title")
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_module(999, update_data, user.id)  # Non-existent module
        
        assert exc_info.value.status_code == 404
    
    def test_delete_nonexistent_module(self, db_session):
        """Test deleting nonexistent module"""
        service = ContentService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete_module(999)  # Non-existent module
        
        assert exc_info.value.status_code == 404
    
    def test_create_content_nonexistent_course(self, db_session, sample_user_data):
        """Test creating content for nonexistent course"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        service = ContentService(db_session)
        
        content_data = CourseContentCreate(
            course_id=999,  # Non-existent course
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.create_content(content_data, user.id)
        
        assert exc_info.value.status_code == 404
    
    def test_update_nonexistent_content(self, db_session, sample_user_data):
        """Test updating nonexistent content"""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        service = ContentService(db_session)
        
        update_data = CourseContentUpdate(title="Updated Title")
        
        with pytest.raises(HTTPException) as exc_info:
            service.update_content(999, update_data, user.id)  # Non-existent content
        
        assert exc_info.value.status_code == 404
    
    def test_delete_nonexistent_content(self, db_session):
        """Test deleting nonexistent content"""
        service = ContentService(db_session)
        
        with pytest.raises(HTTPException) as exc_info:
            service.delete_content(999)  # Non-existent content
        
        assert exc_info.value.status_code == 404


class TestContentServiceFileOperations:
    """Test ContentService file operations"""
    
    @patch('app.services.content_service.boto3')
    def test_upload_file_to_s3(self, mock_boto3, db_session, sample_course_data, sample_user_data):
        """Test uploading file to S3"""
        # Setup
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        content = CourseContent(
            course_id=course.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.S3,
            order_index=1,
            created_by=user.id
        )
        db_session.add(content)
        db_session.commit()
        
        # Mock S3 client
        mock_s3_client = Mock()
        mock_boto3.client.return_value = mock_s3_client
        
        service = ContentService(db_session)
        
        # Mock file
        mock_file = Mock()
        mock_file.filename = "test.pdf"
        mock_file.size = 1024
        mock_file.content_type = "application/pdf"
        mock_file.read.return_value = b"file content"
        
        # Execute
        result = service.upload_file(content.id, mock_file)
        
        # Verify
        assert result.file_name == "test.pdf"
        assert result.file_size == 1024
        assert result.mime_type == "application/pdf"
        assert "s3://" in result.file_path
        mock_s3_client.upload_fileobj.assert_called_once()
    
    def test_download_file_from_database(self, db_session, sample_course_data, sample_user_data):
        """Test downloading file from database"""
        # Setup
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        content = CourseContent(
            course_id=course.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            file_name="test.pdf",
            file_size=1024,
            mime_type="application/pdf",
            file_path="/path/to/file",
            order_index=1,
            created_by=user.id
        )
        db_session.add(content)
        db_session.commit()
        
        service = ContentService(db_session)
        
        # Execute
        result = service.download_file(content.id)
        
        # Verify
        assert result is not None
        # Note: In a real implementation, this would return file content
        # For now, we're just testing that the method doesn't crash
    
    def test_download_external_file(self, db_session, sample_course_data, sample_user_data):
        """Test downloading external file"""
        # Setup
        course = Course(**sample_course_data)
        user = User(**sample_user_data)
        db_session.add_all([course, user])
        db_session.commit()
        
        content = CourseContent(
            course_id=course.id,
            title="External Content",
            content_type=ContentType.EXTERNAL_LINK,
            storage_type=StorageType.EXTERNAL,
            external_url="https://example.com/file.pdf",
            order_index=1,
            created_by=user.id
        )
        db_session.add(content)
        db_session.commit()
        
        service = ContentService(db_session)
        
        # Execute
        result = service.download_file(content.id)
        
        # Verify
        assert result is not None
        # Note: In a real implementation, this would return the external URL
        # For now, we're just testing that the method doesn't crash


