"""
Tests for audit API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from main import app


class TestAuditEndpoints:
    """Test audit API endpoints"""
    
    def test_get_audit_logs_success(self, client: TestClient, admin_token):
        """Test getting audit logs successfully"""
        response = client.get(
            "/api/v1/audit/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_logs_unauthorized(self, client: TestClient):
        """Test getting audit logs without authentication"""
        response = client.get("/api/v1/audit/")
        
        assert response.status_code == 401
    
    def test_get_audit_logs_forbidden(self, client: TestClient, viewer_token):
        """Test getting audit logs with insufficient permissions"""
        response = client.get(
            "/api/v1/audit/",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403
    
    def test_get_audit_logs_with_filters(self, client: TestClient, admin_token):
        """Test getting audit logs with filters"""
        params = {
            "table_name": "courses",
            "action": "insert",
            "limit": 10,
            "offset": 0
        }
        
        response = client.get(
            "/api/v1/audit/",
            params=params,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_logs_with_date_range(self, client: TestClient, admin_token):
        """Test getting audit logs with date range"""
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        response = client.get(
            "/api/v1/audit/",
            params=params,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_summary_success(self, client: TestClient, admin_token):
        """Test getting audit summary successfully"""
        response = client.get(
            "/api/v1/audit/summary",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_logs" in data
        assert "tables_affected" in data
        assert "actions_performed" in data
        assert "table_breakdown" in data
        assert "action_breakdown" in data
    
    def test_get_audit_summary_unauthorized(self, client: TestClient):
        """Test getting audit summary without authentication"""
        response = client.get("/api/v1/audit/summary")
        
        assert response.status_code == 401
    
    def test_get_audit_summary_forbidden(self, client: TestClient, viewer_token):
        """Test getting audit summary with insufficient permissions"""
        response = client.get(
            "/api/v1/audit/summary",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403
    
    def test_get_audit_summary_with_filters(self, client: TestClient, admin_token):
        """Test getting audit summary with filters"""
        params = {
            "table_name": "courses",
            "action": "insert"
        }
        
        response = client.get(
            "/api/v1/audit/summary",
            params=params,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_logs" in data
        assert "tables_affected" in data
        assert "actions_performed" in data
    
    def test_get_audit_logs_by_table(self, client: TestClient, admin_token):
        """Test getting audit logs by table"""
        response = client.get(
            "/api/v1/audit/table/courses",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_logs_by_table_unauthorized(self, client: TestClient):
        """Test getting audit logs by table without authentication"""
        response = client.get("/api/v1/audit/table/courses")
        
        assert response.status_code == 401
    
    def test_get_audit_logs_by_table_forbidden(self, client: TestClient, viewer_token):
        """Test getting audit logs by table with insufficient permissions"""
        response = client.get(
            "/api/v1/audit/table/courses",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403
    
    def test_get_audit_logs_by_record(self, client: TestClient, admin_token):
        """Test getting audit logs by record"""
        response = client.get(
            "/api/v1/audit/table/courses/records/123",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_logs_by_record_unauthorized(self, client: TestClient):
        """Test getting audit logs by record without authentication"""
        response = client.get("/api/v1/audit/table/courses/records/123")
        
        assert response.status_code == 401
    
    def test_get_audit_logs_by_record_forbidden(self, client: TestClient, viewer_token):
        """Test getting audit logs by record with insufficient permissions"""
        response = client.get(
            "/api/v1/audit/table/courses/records/123",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403
    
    def test_get_audit_logs_by_user(self, client: TestClient, admin_token):
        """Test getting audit logs by user"""
        response = client.get(
            "/api/v1/audit/user/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_logs_by_user_unauthorized(self, client: TestClient):
        """Test getting audit logs by user without authentication"""
        response = client.get("/api/v1/audit/user/1")
        
        assert response.status_code == 401
    
    def test_get_audit_logs_by_user_forbidden(self, client: TestClient, viewer_token):
        """Test getting audit logs by user with insufficient permissions"""
        response = client.get(
            "/api/v1/audit/user/1",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403
    
    def test_get_recent_audit_logs(self, client: TestClient, admin_token):
        """Test getting recent audit logs"""
        response = client.get(
            "/api/v1/audit/recent",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_recent_audit_logs_with_hours(self, client: TestClient, admin_token):
        """Test getting recent audit logs with specific hours"""
        params = {"hours": 24}
        
        response = client.get(
            "/api/v1/audit/recent",
            params=params,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_recent_audit_logs_unauthorized(self, client: TestClient):
        """Test getting recent audit logs without authentication"""
        response = client.get("/api/v1/audit/recent")
        
        assert response.status_code == 401
    
    def test_get_recent_audit_logs_forbidden(self, client: TestClient, viewer_token):
        """Test getting recent audit logs with insufficient permissions"""
        response = client.get(
            "/api/v1/audit/recent",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        assert response.status_code == 403


class TestAuditEndpointsValidation:
    """Test audit endpoint validation"""
    
    def test_get_audit_logs_invalid_limit(self, client: TestClient, admin_token):
        """Test getting audit logs with invalid limit"""
        params = {"limit": -1}
        
        response = client.get(
            "/api/v1/audit/",
            params=params,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 422
    
    def test_get_audit_logs_invalid_offset(self, client: TestClient, admin_token):
        """Test getting audit logs with invalid offset"""
        params = {"offset": -1}
        
        response = client.get(
            "/api/v1/audit/",
            params=params,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 422
    
    def test_get_audit_logs_invalid_date_format(self, client: TestClient, admin_token):
        """Test getting audit logs with invalid date format"""
        params = {"start_date": "invalid-date"}
        
        response = client.get(
            "/api/v1/audit/",
            params=params,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 422
    
    def test_get_recent_audit_logs_invalid_hours(self, client: TestClient, admin_token):
        """Test getting recent audit logs with invalid hours"""
        params = {"hours": -1}
        
        response = client.get(
            "/api/v1/audit/recent",
            params=params,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 422
    
    def test_get_audit_logs_by_user_invalid_user_id(self, client: TestClient, admin_token):
        """Test getting audit logs by user with invalid user ID"""
        response = client.get(
            "/api/v1/audit/user/invalid",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 422
    
    def test_get_audit_logs_by_record_invalid_record_id(self, client: TestClient, admin_token):
        """Test getting audit logs by record with invalid record ID"""
        response = client.get(
            "/api/v1/audit/table/courses/records/invalid",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 422


class TestAuditEndpointsErrorHandling:
    """Test audit endpoint error handling"""
    
    def test_get_audit_logs_by_nonexistent_table(self, client: TestClient, admin_token):
        """Test getting audit logs by nonexistent table"""
        response = client.get(
            "/api/v1/audit/table/nonexistent_table",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_audit_logs_by_nonexistent_record(self, client: TestClient, admin_token):
        """Test getting audit logs by nonexistent record"""
        response = client.get(
            "/api/v1/audit/table/courses/records/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_audit_logs_by_nonexistent_user(self, client: TestClient, admin_token):
        """Test getting audit logs by nonexistent user"""
        response = client.get(
            "/api/v1/audit/user/999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestAuditEndpointsStaffAccess:
    """Test audit endpoint access for staff users"""
    
    def test_get_audit_logs_staff_access(self, client: TestClient, staff_token):
        """Test that staff users can access audit logs"""
        response = client.get(
            "/api/v1/audit/",
            headers={"Authorization": f"Bearer {staff_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_summary_staff_access(self, client: TestClient, staff_token):
        """Test that staff users can access audit summary"""
        response = client.get(
            "/api/v1/audit/summary",
            headers={"Authorization": f"Bearer {staff_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_logs" in data
        assert "tables_affected" in data
        assert "actions_performed" in data
    
    def test_get_audit_logs_by_table_staff_access(self, client: TestClient, staff_token):
        """Test that staff users can access audit logs by table"""
        response = client.get(
            "/api/v1/audit/table/courses",
            headers={"Authorization": f"Bearer {staff_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_logs_by_record_staff_access(self, client: TestClient, staff_token):
        """Test that staff users can access audit logs by record"""
        response = client.get(
            "/api/v1/audit/table/courses/records/123",
            headers={"Authorization": f"Bearer {staff_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_logs_by_user_staff_access(self, client: TestClient, staff_token):
        """Test that staff users can access audit logs by user"""
        response = client.get(
            "/api/v1/audit/user/1",
            headers={"Authorization": f"Bearer {staff_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_recent_audit_logs_staff_access(self, client: TestClient, staff_token):
        """Test that staff users can access recent audit logs"""
        response = client.get(
            "/api/v1/audit/recent",
            headers={"Authorization": f"Bearer {staff_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAuditEndpointsComplexQueries:
    """Test audit endpoint complex query scenarios"""
    
    def test_get_audit_logs_multiple_filters(self, client: TestClient, admin_token):
        """Test getting audit logs with multiple filters"""
        params = {
            "table_name": "courses",
            "action": "insert",
            "user_id": 1,
            "limit": 5,
            "offset": 0
        }
        
        response = client.get(
            "/api/v1/audit/",
            params=params,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_logs_with_sorting(self, client: TestClient, admin_token):
        """Test getting audit logs with sorting"""
        params = {
            "sort_by": "changed_at",
            "sort_order": "desc",
            "limit": 10
        }
        
        response = client.get(
            "/api/v1/audit/",
            params=params,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_audit_summary_multiple_filters(self, client: TestClient, admin_token):
        """Test getting audit summary with multiple filters"""
        params = {
            "table_name": "courses",
            "action": "insert",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        
        response = client.get(
            "/api/v1/audit/summary",
            params=params,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_logs" in data
        assert "tables_affected" in data
        assert "actions_performed" in data
