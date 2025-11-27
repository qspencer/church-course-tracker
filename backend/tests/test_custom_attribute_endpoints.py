"""
Tests for Custom Attributes API Endpoints
"""

import pytest
from fastapi.testclient import TestClient

from app.models.member import People
from app.models.custom_attribute import CustomAttribute


class TestCustomAttributeEndpoints:
    """Test custom attributes API endpoints"""
    
    def test_get_custom_attributes(self, client, db_session, admin_token):
        """Test GET /custom-attributes/"""
        # Create a person
        person = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(person)
        db_session.commit()
        
        # Create custom attributes
        attr1 = CustomAttribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="discipler_name",
            attribute_value="Jane Smith",
            pc_attribute_name="Discipler Name"
        )
        attr2 = CustomAttribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="testimony_entered",
            attribute_value="true",
            attribute_type="boolean"
        )
        db_session.add_all([attr1, attr2])
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get(
            "/api/v1/custom-attributes/",
            params={
                "entity_type": "person",
                "entity_id": person.id
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(attr["attribute_name"] == "discipler_name" for attr in data)
        assert any(attr["attribute_name"] == "testimony_entered" for attr in data)
    
    def test_get_custom_attribute_by_id(self, client, db_session, admin_token):
        """Test GET /custom-attributes/{attribute_id}"""
        person = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(person)
        db_session.commit()
        
        attr = CustomAttribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="discipler_name",
            attribute_value="Jane Smith"
        )
        db_session.add(attr)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get(
            f"/api/v1/custom-attributes/{attr.id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == attr.id
        assert data["attribute_name"] == "discipler_name"
        assert data["attribute_value"] == "Jane Smith"
    
    def test_create_custom_attribute(self, client, db_session, admin_token):
        """Test POST /custom-attributes/"""
        person = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(person)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post(
            "/api/v1/custom-attributes/",
            json={
                "entity_type": "person",
                "entity_id": person.id,
                "attribute_name": "discipler_name",
                "attribute_value": "Jane Smith",
                "pc_attribute_name": "Discipler Name",
                "attribute_type": "string"
            },
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["attribute_name"] == "discipler_name"
        assert data["attribute_value"] == "Jane Smith"
        assert data["entity_type"] == "person"
        assert data["entity_id"] == person.id
    
    def test_update_custom_attribute(self, client, db_session, admin_token):
        """Test PUT /custom-attributes/{attribute_id}"""
        person = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(person)
        db_session.commit()
        
        attr = CustomAttribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="discipler_name",
            attribute_value="Jane Smith"
        )
        db_session.add(attr)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.put(
            f"/api/v1/custom-attributes/{attr.id}",
            json={
                "attribute_value": "John Doe",
                "attribute_type": "string"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["attribute_value"] == "John Doe"
    
    def test_delete_custom_attribute(self, client, db_session, admin_token):
        """Test DELETE /custom-attributes/{attribute_id}"""
        person = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(person)
        db_session.commit()
        
        attr = CustomAttribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="discipler_name",
            attribute_value="Jane Smith"
        )
        db_session.add(attr)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete(
            f"/api/v1/custom-attributes/{attr.id}",
            headers=headers
        )
        
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(
            f"/api/v1/custom-attributes/{attr.id}",
            headers=headers
        )
        assert response.status_code == 404
    
    def test_custom_attribute_permissions(self, client, db_session):
        """Test that non-admin users cannot create/update/delete custom attributes"""
        from app.models.user import User
        from app.core.security import create_access_token
        
        # Create a regular user (not admin)
        regular_user = User(
            email="regular@example.com",
            full_name="Regular User",
            hashed_password="hashed",
            role="user",
            is_active=True
        )
        db_session.add(regular_user)
        db_session.commit()
        
        # Create token for regular user - match the format expected by get_current_active_user
        from datetime import timedelta
        regular_token = create_access_token(
            data={"sub": str(regular_user.id)},
            expires_delta=timedelta(minutes=30)
        )
        
        person = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(person)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {regular_token}"}
        
        # Try to create
        response = client.post(
            "/api/v1/custom-attributes/",
            json={
                "entity_type": "person",
                "entity_id": person.id,
                "attribute_name": "test",
                "attribute_value": "value"
            },
            headers=headers
        )
        assert response.status_code == 403

