"""
Tests for course content API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from main import app
from app.models.course_content import ContentType, StorageType
from app.schemas.course_content import (
    CourseModuleCreate, CourseContentCreate, ContentAccessLogCreate
)


class TestCourseContentEndpoints:
    """Test course content API endpoints"""
    
    def test_create_course_module_success(self, client: TestClient, admin_token, db_session):
        """Test creating a course module successfully"""
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
        
        # Setup
        module_data = {
            "course_id": course.id,
            "title": "Introduction Module",
            "description": "Welcome to the course",
            "order_index": 1
        }
        
        # Execute
        response = client.post(
            "/api/v1/content/modules/",
            json=module_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Verify
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Introduction Module"
        assert data["description"] == "Welcome to the course"
        assert data["order_index"] == 1
        assert data["is_active"] is True
    
    def test_create_course_module_unauthorized(self, client: TestClient):
        """Test creating a course module without authentication"""
        module_data = {
            "course_id": 1,
            "title": "Introduction Module",
            "order_index": 1
        }
        
        response = client.post("/api/v1/content/modules", json=module_data)
        
        assert response.status_code == 401
    
    def test_create_course_module_forbidden(self, client: TestClient, viewer_token):
        """Test creating a course module with insufficient permissions"""
        module_data = {
            "course_id": 1,
            "title": "Introduction Module",
            "order_index": 1
        }
        
        response = client.post(
            "/api/v1/content/modules",
            json=module_data,
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403
    
    def test_get_course_modules(self, client: TestClient, admin_token):
        """Test getting course modules"""
        response = client.get(
            "/api/v1/content/courses/1/modules",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_course_module(self, client: TestClient, admin_token):
        """Test getting a specific course module"""
        response = client.get(
            "/api/v1/content/modules/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # This might return 404 if module doesn't exist, which is expected
        assert response.status_code in [200, 404]
    
    def test_update_course_module(self, client: TestClient, admin_token):
        """Test updating a course module"""
        update_data = {
            "title": "Updated Module Title",
            "description": "Updated description"
        }
        
        response = client.put(
            "/api/v1/content/modules/1",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # This might return 404 if module doesn't exist, which is expected
        assert response.status_code in [200, 404]
    
    def test_delete_course_module(self, client: TestClient, admin_token):
        """Test deleting a course module"""
        response = client.delete(
            "/api/v1/content/modules/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # This might return 404 if module doesn't exist, which is expected
        assert response.status_code in [200, 404]
    
    def test_create_course_content(self, client: TestClient, admin_token):
        """Test creating course content"""
        content_data = {
            "course_id": 1,
            "title": "Welcome Video",
            "description": "Introduction video",
            "content_type": "video",
            "storage_type": "s3",
            "file_name": "welcome.mp4",
            "file_size": 1024000,
            "duration": 300,
            "order_index": 1
        }
        
        response = client.post(
            "/api/v1/content/courses/1/upload",
            json=content_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Welcome Video"
        assert data["content_type"] == "video"
        assert data["storage_type"] == "s3"
    
    def test_create_external_link_content(self, client: TestClient, admin_token):
        """Test creating external link content"""
        content_data = {
            "course_id": 1,
            "title": "External Resource",
            "description": "Link to external resource",
            "content_type": "external_link",
            "storage_type": "external",
            "external_url": "https://example.com/resource",
            "order_index": 1
        }
        
        response = client.post(
            "/api/v1/content/courses/1/link",
            json=content_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "External Resource"
        assert data["content_type"] == "external_link"
        assert data["external_url"] == "https://example.com/resource"
    
    def test_create_embedded_content(self, client: TestClient, admin_token):
        """Test creating embedded content"""
        content_data = {
            "course_id": 1,
            "title": "Embedded Video",
            "description": "Embedded video content",
            "content_type": "embedded",
            "storage_type": "database",
            "embedded_content": "<iframe src='https://example.com/embed'></iframe>",
            "order_index": 1
        }
        
        response = client.post(
            "/api/v1/content/courses/1/embed",
            json=content_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Embedded Video"
        assert data["content_type"] == "embedded"
        assert "iframe" in data["embedded_content"]
    
    def test_get_course_content(self, client: TestClient, admin_token):
        """Test getting course content"""
        response = client.get(
            "/api/v1/content/courses/1/content",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_content_item(self, client: TestClient, admin_token):
        """Test getting a specific content item"""
        response = client.get(
            "/api/v1/content/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # This might return 404 if content doesn't exist, which is expected
        assert response.status_code in [200, 404]
    
    def test_update_content_item(self, client: TestClient, admin_token):
        """Test updating a content item"""
        update_data = {
            "title": "Updated Content Title",
            "description": "Updated description"
        }
        
        response = client.put(
            "/api/v1/content/1",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # This might return 404 if content doesn't exist, which is expected
        assert response.status_code in [200, 404]
    
    def test_delete_content_item(self, client: TestClient, admin_token):
        """Test deleting a content item"""
        response = client.delete(
            "/api/v1/content/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # This might return 404 if content doesn't exist, which is expected
        assert response.status_code in [200, 404]
    
    def test_download_content(self, client: TestClient, admin_token):
        """Test downloading content"""
        response = client.get(
            "/api/v1/content/1/download",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # This might return 404 if content doesn't exist, which is expected
        assert response.status_code in [200, 404]
    
    def test_get_content_summary(self, client: TestClient, admin_token):
        """Test getting course content summary"""
        response = client.get(
            "/api/v1/content/courses/1/summary",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_modules" in data
        assert "total_content_items" in data
        assert "total_file_size" in data
        assert "content_by_type" in data
    
    def test_log_content_access(self, client: TestClient, admin_token):
        """Test logging content access"""
        access_data = {
            "content_id": 1,
            "user_id": 1,
            "access_type": "view",
            "progress_percentage": 50,
            "time_spent": 120
        }
        
        response = client.post(
            "/api/v1/content/1/access-log",
            json=access_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["access_type"] == "view"
        assert data["progress_percentage"] == 50
        assert data["time_spent"] == 120
    
    def test_get_content_audit_logs(self, client: TestClient, admin_token):
        """Test getting content audit logs"""
        response = client.get(
            "/api/v1/content/1/audit-logs",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_content_audit_logs_forbidden(self, client: TestClient, viewer_token):
        """Test getting content audit logs with insufficient permissions"""
        response = client.get(
            "/api/v1/content/1/audit-logs",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403
    
    def test_get_user_content_progress(self, client: TestClient, admin_token):
        """Test getting user content progress"""
        response = client.get(
            "/api/v1/content/user/1/course/1/progress",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


class TestCourseContentEndpointsFileUpload:
    """Test course content file upload endpoints"""
    
    @patch('app.services.content_service.ContentService.upload_file')
    def test_upload_file_success(self, mock_upload, client: TestClient, admin_token):
        """Test successful file upload"""
        # Mock the upload service
        mock_upload.return_value = {
            "file_name": "test.pdf",
            "file_size": 1024,
            "file_path": "s3://bucket/test.pdf",
            "mime_type": "application/pdf",
            "message": "File uploaded successfully"
        }
        
        # Create a mock file
        files = {"file": ("test.pdf", b"file content", "application/pdf")}
        
        response = client.post(
            "/api/v1/content/courses/1/upload",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["file_name"] == "test.pdf"
        assert data["file_size"] == 1024
        assert data["mime_type"] == "application/pdf"
    
    def test_upload_file_unauthorized(self, client: TestClient):
        """Test file upload without authentication"""
        files = {"file": ("test.pdf", b"file content", "application/pdf")}
        
        response = client.post(
            "/api/v1/content/courses/1/upload",
            files=files
        )
        
        assert response.status_code == 401
    
    def test_upload_file_forbidden(self, client: TestClient, viewer_token):
        """Test file upload with insufficient permissions"""
        files = {"file": ("test.pdf", b"file content", "application/pdf")}
        
        response = client.post(
            "/api/v1/content/courses/1/upload",
            files=files,
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403


class TestCourseContentEndpointsValidation:
    """Test course content endpoint validation"""
    
    def test_create_module_invalid_data(self, client: TestClient, admin_token):
        """Test creating module with invalid data"""
        invalid_data = {
            "course_id": "invalid",  # Should be integer
            "title": "",  # Should not be empty
            "order_index": -1  # Should be non-negative
        }
        
        response = client.post(
            "/api/v1/content/modules",
            json=invalid_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 422
    
    def test_create_content_invalid_content_type(self, client: TestClient, admin_token):
        """Test creating content with invalid content type"""
        invalid_data = {
            "course_id": 1,
            "title": "Test Content",
            "content_type": "invalid_type",  # Invalid enum value
            "storage_type": "database",
            "order_index": 1
        }
        
        response = client.post(
            "/api/v1/content/courses/1/upload",
            json=invalid_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 422
    
    def test_create_content_invalid_storage_type(self, client: TestClient, admin_token):
        """Test creating content with invalid storage type"""
        invalid_data = {
            "course_id": 1,
            "title": "Test Content",
            "content_type": "document",
            "storage_type": "invalid_storage",  # Invalid enum value
            "order_index": 1
        }
        
        response = client.post(
            "/api/v1/content/courses/1/upload",
            json=invalid_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 422
    
    def test_log_access_invalid_access_type(self, client: TestClient, admin_token):
        """Test logging access with invalid access type"""
        invalid_data = {
            "content_id": 1,
            "user_id": 1,
            "access_type": "invalid_access",  # Invalid enum value
            "progress_percentage": 50
        }
        
        response = client.post(
            "/api/v1/content/1/access-log",
            json=invalid_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 422
    
    def test_log_access_invalid_progress(self, client: TestClient, admin_token):
        """Test logging access with invalid progress percentage"""
        invalid_data = {
            "content_id": 1,
            "user_id": 1,
            "access_type": "view",
            "progress_percentage": 150  # Should be 0-100
        }
        
        response = client.post(
            "/api/v1/content/1/access-log",
            json=invalid_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 422


class TestCourseContentEndpointsErrorHandling:
    """Test course content endpoint error handling"""
    
    def test_get_nonexistent_module(self, client: TestClient, admin_token):
        """Test getting nonexistent module"""
        response = client.get(
            "/api/v1/content/modules/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
    
    def test_update_nonexistent_module(self, client: TestClient, admin_token):
        """Test updating nonexistent module"""
        update_data = {"title": "Updated Title"}
        
        response = client.put(
            "/api/v1/content/modules/999",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
    
    def test_delete_nonexistent_module(self, client: TestClient, admin_token):
        """Test deleting nonexistent module"""
        response = client.delete(
            "/api/v1/content/modules/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
    
    def test_get_nonexistent_content(self, client: TestClient, admin_token):
        """Test getting nonexistent content"""
        response = client.get(
            "/api/v1/content/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
    
    def test_update_nonexistent_content(self, client: TestClient, admin_token):
        """Test updating nonexistent content"""
        update_data = {"title": "Updated Title"}
        
        response = client.put(
            "/api/v1/content/999",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
    
    def test_delete_nonexistent_content(self, client: TestClient, admin_token):
        """Test deleting nonexistent content"""
        response = client.delete(
            "/api/v1/content/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
    
    def test_download_nonexistent_content(self, client: TestClient, admin_token):
        """Test downloading nonexistent content"""
        response = client.get(
            "/api/v1/content/999/download",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
