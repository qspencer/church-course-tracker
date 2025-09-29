"""
Tests for course content file operations (upload/download)
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from io import BytesIO

from main import app
from app.models.course_content import ContentType, StorageType
from app.schemas.course_content import ContentUploadResponse


class TestCourseContentFileOperations:
    """Test course content file upload and download operations"""
    
    def test_upload_file_success(self, client: TestClient, admin_token, db_session):
        """Test successful file upload"""
        # Create a course first
        from app.models.course import Course
        course = Course(
            title="Test Course",
            description="Test Description",
            is_active=True
        )
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)
        
        # Create content item
        from app.models.course_content import CourseContent
        content = CourseContent(
            course_id=course.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1
        )
        db_session.add(content)
        db_session.commit()
        db_session.refresh(content)
        
        # Mock the upload service
        with patch('app.services.content_service.ContentService.upload_file') as mock_upload:
            mock_upload.return_value = ContentUploadResponse(
                content_id=content.id,
                filename="test.pdf",
                file_size=1024,
                file_path="database://test.pdf",
                storage_type="database",
                message="File uploaded successfully"
            )
            
            # Create test file
            test_file = BytesIO(b"test file content")
            files = {"file": ("test.pdf", test_file, "application/pdf")}
            
            response = client.post(
                f"/api/v1/content/{content.id}/upload",
                files=files,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["content_id"] == content.id
            assert data["filename"] == "test.pdf"
            assert data["file_size"] == 1024
            assert data["storage_type"] == "database"
            assert data["message"] == "File uploaded successfully"
    
    def test_upload_file_unauthorized(self, client: TestClient):
        """Test file upload without authentication"""
        test_file = BytesIO(b"test file content")
        files = {"file": ("test.pdf", test_file, "application/pdf")}
        
        response = client.post("/api/v1/content/1/upload", files=files)
        
        assert response.status_code == 401
    
    def test_upload_file_forbidden(self, client: TestClient, viewer_token):
        """Test file upload with insufficient permissions"""
        test_file = BytesIO(b"test file content")
        files = {"file": ("test.pdf", test_file, "application/pdf")}
        
        response = client.post(
            "/api/v1/content/1/upload",
            files=files,
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403
    
    def test_upload_file_invalid_content_id(self, client: TestClient, admin_token):
        """Test file upload with non-existent content ID"""
        test_file = BytesIO(b"test file content")
        files = {"file": ("test.pdf", test_file, "application/pdf")}
        
        response = client.post(
            "/api/v1/content/999/upload",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
    
    def test_upload_file_invalid_file_type(self, client: TestClient, admin_token, db_session):
        """Test file upload with invalid file type"""
        # Create a course and content
        from app.models.course import Course
        from app.models.course_content import CourseContent, ContentType, StorageType
        
        course = Course(title="Test Course", description="Test", is_active=True)
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)
        
        content = CourseContent(
            course_id=course.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1
        )
        db_session.add(content)
        db_session.commit()
        db_session.refresh(content)
        
        # Mock upload service to raise validation error
        with patch('app.services.content_service.ContentService.upload_file') as mock_upload:
            mock_upload.side_effect = ValueError("Invalid file type")
            
            test_file = BytesIO(b"test file content")
            files = {"file": ("test.exe", test_file, "application/octet-stream")}
            
            response = client.post(
                f"/api/v1/content/{content.id}/upload",
                files=files,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == 400
    
    def test_download_content_success(self, client: TestClient, admin_token, db_session):
        """Test successful content download"""
        # Create a course and content
        from app.models.course import Course
        from app.models.course_content import CourseContent, ContentType, StorageType
        
        course = Course(title="Test Course", description="Test", is_active=True)
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)
        
        content = CourseContent(
            course_id=course.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1
        )
        db_session.add(content)
        db_session.commit()
        db_session.refresh(content)
        
        # Mock the download service
        with patch('app.services.content_service.ContentService.download_content') as mock_download:
            mock_download.return_value = {
                "content": b"test file content",
                "filename": "test.pdf",
                "mime_type": "application/pdf",
                "file_size": 1024
            }
            
            response = client.get(
                f"/api/v1/content/{content.id}/download",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
            assert response.headers["content-disposition"] == "attachment; filename=test.pdf"
            assert response.content == b"test file content"
    
    def test_download_content_not_found(self, client: TestClient, admin_token):
        """Test download of non-existent content"""
        with patch('app.services.content_service.ContentService.download_content') as mock_download:
            mock_download.return_value = None
            
            response = client.get(
                "/api/v1/content/999/download",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == 404
    
    def test_download_content_unauthorized(self, client: TestClient):
        """Test content download without authentication"""
        response = client.get("/api/v1/content/1/download")
        
        assert response.status_code == 401


class TestCourseContentProgressTracking:
    """Test course content progress tracking operations"""
    
    def test_update_content_progress_success(self, client: TestClient, admin_token, db_session):
        """Test successful progress update"""
        # Create a course and content
        from app.models.course import Course
        from app.models.course_content import CourseContent, ContentType, StorageType
        
        course = Course(title="Test Course", description="Test", is_active=True)
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)
        
        content = CourseContent(
            course_id=course.id,
            title="Test Content",
            content_type=ContentType.VIDEO,
            storage_type=StorageType.DATABASE,
            order_index=1
        )
        db_session.add(content)
        db_session.commit()
        db_session.refresh(content)
        
        # Mock the progress update service
        with patch('app.services.content_service.ContentService.log_content_access') as mock_log:
            mock_log.return_value = {
                "id": 1,
                "content_id": content.id,
                "user_id": 1,
                "access_type": "view",
                "progress_percentage": 75,
                "time_spent": 300
            }
            
            progress_data = {
                "progress_percentage": 75,
                "time_spent": 300
            }
            
            response = client.put(
                f"/api/v1/content/{content.id}/progress",
                json=progress_data,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["progress_percentage"] == 75
            assert data["time_spent"] == 300
    
    def test_update_progress_invalid_percentage(self, client: TestClient, admin_token):
        """Test progress update with invalid percentage"""
        progress_data = {
            "progress_percentage": 150,  # Invalid: should be 0-100
            "time_spent": 300
        }
        
        response = client.put(
            "/api/v1/content/1/progress",
            json=progress_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 422
    
    def test_update_progress_unauthorized(self, client: TestClient):
        """Test progress update without authentication"""
        progress_data = {
            "progress_percentage": 50,
            "time_spent": 300
        }
        
        response = client.put("/api/v1/content/1/progress", json=progress_data)
        
        assert response.status_code == 401


class TestCourseContentAccessLogs:
    """Test course content access logging operations"""
    
    def test_log_content_access_success(self, client: TestClient, admin_token, db_session):
        """Test successful content access logging"""
        # Create a course and content
        from app.models.course import Course
        from app.models.course_content import CourseContent, ContentType, StorageType
        
        course = Course(title="Test Course", description="Test", is_active=True)
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)
        
        content = CourseContent(
            course_id=course.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1
        )
        db_session.add(content)
        db_session.commit()
        db_session.refresh(content)
        
        # Mock the access logging service
        with patch('app.services.content_service.ContentService.log_content_access') as mock_log:
            mock_log.return_value = {
                "id": 1,
                "content_id": content.id,
                "user_id": 1,
                "access_type": "view",
                "progress_percentage": 0,
                "time_spent": 0
            }
            
            access_data = {
                "access_type": "view",
                "progress_percentage": 0,
                "time_spent": 0
            }
            
            response = client.post(
                f"/api/v1/content/{content.id}/access",
                json=access_data,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["content_id"] == content.id
            assert data["user_id"] == 1
            assert data["access_type"] == "view"
    
    def test_log_access_invalid_data(self, client: TestClient, admin_token):
        """Test access logging with invalid data"""
        invalid_data = {
            "access_type": "invalid_type",
            "progress_percentage": -10
        }
        
        response = client.post(
            "/api/v1/content/1/access",
            json=invalid_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 422
    
    def test_get_content_access_logs_success(self, client: TestClient, admin_token, db_session):
        """Test successful retrieval of access logs"""
        # Create a course and content
        from app.models.course import Course
        from app.models.course_content import CourseContent, ContentType, StorageType
        
        course = Course(title="Test Course", description="Test", is_active=True)
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)
        
        content = CourseContent(
            course_id=course.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1
        )
        db_session.add(content)
        db_session.commit()
        db_session.refresh(content)
        
        # Mock the access logs service
        with patch('app.services.content_service.ContentService.get_content_access_logs') as mock_logs:
            mock_logs.return_value = [
                {
                    "id": 1,
                    "content_id": content.id,
                    "user_id": 1,
                    "access_type": "view",
                    "progress_percentage": 50,
                    "time_spent": 300
                }
            ]
            
            response = client.get(
                f"/api/v1/content/{content.id}/access-logs",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["content_id"] == content.id
    
    def test_get_access_logs_forbidden(self, client: TestClient, viewer_token):
        """Test access logs retrieval with insufficient permissions"""
        response = client.get(
            "/api/v1/content/1/access-logs",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403


class TestCourseContentAuditLogs:
    """Test course content audit logging operations"""
    
    def test_get_content_audit_logs_success(self, client: TestClient, admin_token, db_session):
        """Test successful retrieval of audit logs"""
        # Create a course and content
        from app.models.course import Course
        from app.models.course_content import CourseContent, ContentType, StorageType
        
        course = Course(title="Test Course", description="Test", is_active=True)
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)
        
        content = CourseContent(
            course_id=course.id,
            title="Test Content",
            content_type=ContentType.DOCUMENT,
            storage_type=StorageType.DATABASE,
            order_index=1
        )
        db_session.add(content)
        db_session.commit()
        db_session.refresh(content)
        
        # Mock the audit logs service
        with patch('app.services.content_service.ContentService.get_audit_logs') as mock_audit:
            mock_audit.return_value = [
                {
                    "id": 1,
                    "content_id": content.id,
                    "user_id": 1,
                    "action": "create",
                    "change_timestamp": "2024-01-01T00:00:00Z",
                    "change_summary": "Content created"
                }
            ]
            
            response = client.get(
                f"/api/v1/content/{content.id}/audit-logs",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["content_id"] == content.id
            assert data[0]["action"] == "create"
    
    def test_get_audit_logs_forbidden(self, client: TestClient, viewer_token):
        """Test audit logs retrieval with insufficient permissions"""
        response = client.get(
            "/api/v1/content/1/audit-logs",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403


class TestCourseContentUserProgress:
    """Test course content user progress operations"""
    
    def test_get_user_content_progress_success(self, client: TestClient, admin_token, db_session):
        """Test successful retrieval of user progress"""
        # Create a course
        from app.models.course import Course
        course = Course(title="Test Course", description="Test", is_active=True)
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)
        
        # Mock the user progress service
        with patch('app.services.content_service.ContentService.get_user_content_progress') as mock_progress:
            mock_progress.return_value = {
                "user_id": 1,
                "course_id": course.id,
                "total_content": 5,
                "completed_content": 3,
                "progress_percentage": 60,
                "content_progress": [
                    {"content_id": 1, "progress_percentage": 100},
                    {"content_id": 2, "progress_percentage": 50}
                ]
            }
            
            response = client.get(
                f"/api/v1/content/user/1/course/{course.id}/progress",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == 1
            assert data["course_id"] == course.id
            assert data["progress_percentage"] == 60
    
    def test_get_user_progress_own_data(self, client: TestClient, user_token, db_session):
        """Test user can access their own progress"""
        # Create a course
        from app.models.course import Course
        course = Course(title="Test Course", description="Test", is_active=True)
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)
        
        # Mock the user progress service
        with patch('app.services.content_service.ContentService.get_user_content_progress') as mock_progress:
            mock_progress.return_value = {
                "user_id": 2,  # Same as current user
                "course_id": course.id,
                "total_content": 5,
                "completed_content": 2,
                "progress_percentage": 40
            }
            
            response = client.get(
                f"/api/v1/content/user/2/course/{course.id}/progress",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            
            assert response.status_code == 200
    
    def test_get_user_progress_forbidden(self, client: TestClient, user_token, db_session):
        """Test user cannot access another user's progress"""
        # Create a course
        from app.models.course import Course
        course = Course(title="Test Course", description="Test", is_active=True)
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)
        
        response = client.get(
            f"/api/v1/content/user/999/course/{course.id}/progress",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403


class TestCourseContentSummary:
    """Test course content summary operations"""
    
    def test_get_course_content_summary_success(self, client: TestClient, admin_token, db_session):
        """Test successful retrieval of course content summary"""
        # Create a course
        from app.models.course import Course
        course = Course(title="Test Course", description="Test", is_active=True)
        db_session.add(course)
        db_session.commit()
        db_session.refresh(course)
        
        # Mock the content summary service
        with patch('app.services.content_service.ContentService.get_content') as mock_content, \
             patch('app.services.content_service.ContentService.get_modules') as mock_modules:
            
            mock_content.return_value = [
                {"id": 1, "title": "Content 1", "content_type": "document"},
                {"id": 2, "title": "Content 2", "content_type": "video"}
            ]
            mock_modules.return_value = [
                {"id": 1, "title": "Module 1", "order_index": 1},
                {"id": 2, "title": "Module 2", "order_index": 2}
            ]
            
            response = client.get(
                f"/api/v1/content/course/{course.id}/summary",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "course_id" in data
            assert "modules" in data
            assert "content_items" in data
            assert "total_modules" in data
            assert "total_content" in data
    
    def test_get_content_summary_forbidden(self, client: TestClient, viewer_token):
        """Test content summary retrieval with insufficient permissions"""
        response = client.get(
            "/api/v1/content/course/1/summary",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403
