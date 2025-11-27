"""
Tests for Attribute Mapping API Endpoints
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from app.models.course import Course
from app.models.program import Program
from app.models.member import People


class TestAttributeMappingEndpoints:
    """Test attribute mapping API endpoints"""
    
    def test_get_attribute_mappings_for_event(self, client, db_session, admin_token):
        """Test GET /planning-center/attribute-mappings for event"""
        # Create a course with minimal fields
        course = Course(
            title="Test Course",
            description="Test Description",
            planning_center_event_id="pc_event_123",
            is_active=True
        )
        db_session.add(course)
        db_session.flush()  # Flush to get ID without committing
        course_id = course.id
        
        # Mock Planning Center service
        mock_event_data = {
            "id": "pc_event_123",
            "attributes": {
                "name": "Test Event",
                "start_date": "2024-01-15",
                "end_date": "2024-01-20",
                "max_capacity": 50,
                "custom_field_1": "Custom Value"
            }
        }
        
        # Patch the service instantiation to return a mock
        with patch('app.api.v1.endpoints.planning_center_sync.PlanningCenterSyncService') as MockService:
            mock_service_instance = Mock()
            mock_service_instance.get_events.return_value = [mock_event_data]
            MockService.return_value = mock_service_instance
            
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = client.get(
                "/api/v1/planning-center/attribute-mappings",
                params={
                    "source_type": "event",
                    "source_id": "pc_event_123",
                    "target_type": "course",
                    "target_id": course_id
                },
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["source_type"] == "event"
            assert data["source_id"] == "pc_event_123"
            assert data["target_type"] == "course"
            assert data["target_id"] == course_id
            assert "matches" in data
            assert len(data["matches"]) > 0
    
    def test_get_attribute_mappings_for_list(self, client, db_session, admin_token):
        """Test GET /planning-center/attribute-mappings for list"""
        # Create a program with minimal fields
        program = Program(
            title="Test Program",
            description="Test Description",
            is_active=True
        )
        db_session.add(program)
        db_session.flush()  # Flush to get ID without committing
        program_id = program.id
        
        # Mock Planning Center service
        mock_person_data = {
            "id": "pc_person_123",
            "attributes": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "Discipler Name": "Jane Smith",
                "Testimony Entered?": "Yes"
            }
        }
        
        # Patch the service instantiation to return a mock
        with patch('app.api.v1.endpoints.planning_center_sync.PlanningCenterSyncService') as MockService:
            mock_service_instance = Mock()
            mock_service_instance.get_list_people.return_value = [mock_person_data]
            MockService.return_value = mock_service_instance
            
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = client.get(
                "/api/v1/planning-center/attribute-mappings",
                params={
                    "source_type": "list",
                    "source_id": "pc_list_123",
                    "target_type": "program",
                    "target_id": program_id
                },
                headers=headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["source_type"] == "list"
            assert data["source_id"] == "pc_list_123"
            assert data["target_type"] == "program"
            assert data["target_id"] == program_id
            assert "matches" in data
            assert len(data["matches"]) > 0
            assert "matches" in data
            assert len(data["matches"]) > 0
    
    def test_save_attribute_mapping_decisions(self, client, db_session, admin_token):
        """Test POST /planning-center/attribute-mappings/decisions"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        decisions_data = {
            "source_type": "event",
            "source_id": "pc_event_123",
            "target_type": "course",
            "target_id": 1,
            "decisions": [
                {
                    "pc_attribute": "name",
                    "action": "accept",
                    "local_attribute": "title"
                },
                {
                    "pc_attribute": "custom_field_1",
                    "action": "custom",
                    "custom_attribute_name": "custom_field_1"
                },
                {
                    "pc_attribute": "unused_field",
                    "action": "ignore"
                }
            ]
        }
        
        response = client.post(
            "/api/v1/planning-center/attribute-mappings/decisions",
            json=decisions_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "decisions" in data
    
    def test_save_attribute_mapping_decisions_validation(self, client, db_session, admin_token):
        """Test validation of attribute mapping decisions"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Missing local_attribute for accept action
        decisions_data = {
            "source_type": "event",
            "source_id": "pc_event_123",
            "target_type": "course",
            "target_id": 1,
            "decisions": [
                {
                    "pc_attribute": "name",
                    "action": "accept"
                    # Missing local_attribute
                }
            ]
        }
        
        response = client.post(
            "/api/v1/planning-center/attribute-mappings/decisions",
            json=decisions_data,
            headers=headers
        )
        
        assert response.status_code == 400
    
    def test_get_attribute_mappings_event_not_found(self, client, db_session, admin_token):
        """Test GET /planning-center/attribute-mappings with non-existent event"""
        # Create a course with minimal fields
        course = Course(
            title="Test Course",
            description="Test Description",
            is_active=True
        )
        db_session.add(course)
        db_session.flush()  # Flush to get ID without committing
        course_id = course.id
        
        # Patch the service instantiation to return a mock
        with patch('app.api.v1.endpoints.planning_center_sync.PlanningCenterSyncService') as MockService:
            mock_service_instance = Mock()
            mock_service_instance.get_events.return_value = []
            MockService.return_value = mock_service_instance
            
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = client.get(
                "/api/v1/planning-center/attribute-mappings",
                params={
                    "source_type": "event",
                    "source_id": "nonexistent_event",
                    "target_type": "course",
                    "target_id": course_id
                },
                headers=headers
            )
            
            assert response.status_code == 404

