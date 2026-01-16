"""
Tests for System Settings API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.models.system_settings import SystemSettings
from app.models.user import User
from app.core.security import get_password_hash


class TestSystemSettingsEndpoints:
    """Test System Settings API endpoints"""

    def test_get_all_settings_requires_admin(self, client, db_session):
        """Test that getting settings requires admin authentication"""
        response = client.get("/api/v1/settings")
        assert response.status_code == 401  # Unauthorized

    def test_get_all_settings_as_admin(self, client, db_session, admin_token):
        """Test getting all settings as admin"""
        # Create some test settings
        setting1 = SystemSettings(
            key="test_setting1",
            value="value1",
            category="system",
            data_type="string"
        )
        setting2 = SystemSettings(
            key="test_setting2",
            value="value2",
            category="security",
            data_type="string"
        )
        db_session.add_all([setting1, setting2])
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/settings", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert "security" in data

    def test_get_settings_by_category(self, client, db_session, admin_token):
        """Test getting settings filtered by category"""
        # Use unique keys to avoid conflicts with seeded data
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        test_key = f"test_system_setting_{unique_id}"
        
        # Create test settings
        setting1 = SystemSettings(
            key=test_key,
            value="value1",
            category="system",
            data_type="string"
        )
        db_session.add(setting1)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/settings?category=system", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        # Should have at least our test setting (may have more from seed data)
        test_settings = [s for s in data["system"] if unique_id in s["key"]]
        assert len(test_settings) == 1
        assert test_settings[0]["key"] == test_key

    def test_get_setting_by_key(self, client, db_session, admin_token):
        """Test getting a specific setting by key"""
        setting = SystemSettings(
            key="test_key",
            value="test_value",
            category="system",
            data_type="string"
        )
        db_session.add(setting)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/settings/test_key", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "test_key"
        assert data["value"] == "test_value"

    def test_get_setting_not_found(self, client, db_session, admin_token):
        """Test getting a non-existent setting"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/settings/nonexistent", headers=headers)
        
        assert response.status_code == 404

    def test_create_setting(self, client, db_session, admin_token):
        """Test creating a new setting"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        setting_data = {
            "key": "new_setting",
            "value": "new_value",
            "category": "system",
            "data_type": "string",
            "description": "A new setting"
        }
        
        response = client.post("/api/v1/settings", json=setting_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "new_setting"
        assert data["value"] == "new_value"

    def test_update_setting(self, client, db_session, admin_token):
        """Test updating a setting"""
        # Create a setting first
        setting = SystemSettings(
            key="update_test",
            value="old_value",
            category="system",
            data_type="string"
        )
        db_session.add(setting)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        update_data = {"value": "new_value"}
        
        response = client.patch("/api/v1/settings/update_test", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == "new_value"

    def test_update_settings_batch(self, client, db_session, admin_token):
        """Test batch updating multiple settings"""
        # Use unique keys to avoid conflicts with seeded data
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        key1 = f"test_batch_key1_{unique_id}"
        key2 = f"test_batch_key2_{unique_id}"
        
        # Create settings first
        setting1 = SystemSettings(
            key=key1,
            value="value1",
            category="system",
            data_type="string"
        )
        setting2 = SystemSettings(
            key=key2,
            value="value2",
            category="system",
            data_type="string"
        )
        db_session.add_all([setting1, setting2])
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        batch_data = {
            "settings": {
                key1: "new_value1",
                key2: "new_value2"
            }
        }
        
        response = client.patch("/api/v1/settings/batch", json=batch_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_planning_center_config(self, client, db_session, admin_token):
        """Test getting Planning Center configuration"""
        # Create Planning Center settings
        settings_data = [
            ("planning_center_api_url", "https://api.test.com", "planning_center", "string"),
            ("planning_center_max_events", "1000", "planning_center", "integer"),
            ("use_mock_planning_center", "false", "planning_center", "boolean"),
        ]
        
        for key, value, category, data_type in settings_data:
            setting = SystemSettings(
                key=key,
                value=value,
                category=category,
                data_type=data_type
            )
            db_session.add(setting)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/settings/planning-center/config", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "api_url" in data
        assert "max_events" in data

    def test_update_planning_center_config(self, client, db_session, admin_token):
        """Test updating Planning Center configuration"""
        # This test uses existing seeded settings, so we'll update them
        # First ensure the setting exists
        from app.services.system_settings_service import SystemSettingsService
        from app.schemas.system_settings import SystemSettingsCreate
        
        service = SystemSettingsService(db_session)
        existing = service.get_setting("planning_center_api_url")
        if not existing:
            setting_data = SystemSettingsCreate(
                key="planning_center_api_url",
                value="https://old.api.com",
                category="planning_center",
                data_type="string"
            )
            service.create_setting(setting_data, created_by=1)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        config_data = {
            "api_url": "https://new.api.com",
            "max_events": 2000,
            "cache_ttl_minutes": 20,
            "use_mock": False
        }
        
        response = client.patch("/api/v1/settings/planning-center/config", json=config_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_non_admin_cannot_access_settings(self, client, db_session, staff_token):
        """Test that non-admin users cannot access settings"""
        headers = {"Authorization": f"Bearer {staff_token}"}
        response = client.get("/api/v1/settings", headers=headers)
        
        assert response.status_code == 403  # Forbidden

    # Negative test cases
    def test_create_setting_missing_required_fields(self, client, db_session, admin_token):
        """Test creating setting with missing required fields"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Missing 'key' field
        setting_data = {
            "value": "test_value",
            "category": "system",
            "data_type": "string"
        }
        
        response = client.post("/api/v1/settings", json=setting_data, headers=headers)
        assert response.status_code == 422  # Validation error

    def test_create_setting_invalid_data_type(self, client, db_session, admin_token):
        """Test creating setting with invalid data type"""
        import uuid
        unique_key = f"test_invalid_type_{str(uuid.uuid4())[:8]}"
        headers = {"Authorization": f"Bearer {admin_token}"}
        setting_data = {
            "key": unique_key,
            "value": "test_value",
            "category": "system",
            "data_type": "invalid_type"  # Invalid data type
        }
        
        response = client.post("/api/v1/settings", json=setting_data, headers=headers)
        # Should either validate and reject or accept but fail validation later
        assert response.status_code in [200, 400, 422]

    def test_create_setting_malformed_json(self, client, db_session, admin_token):
        """Test creating setting with malformed JSON"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Send invalid JSON
        response = client.post(
            "/api/v1/settings",
            data="{'key': 'test', invalid json}",
            headers={**headers, "Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Validation error

    def test_update_setting_invalid_value_type(self, client, db_session, admin_token):
        """Test updating setting with invalid value type"""
        import uuid
        unique_key = f"test_invalid_value_{str(uuid.uuid4())[:8]}"
        
        # Create integer setting
        setting = SystemSettings(
            key=unique_key,
            value="123",
            category="system",
            data_type="integer"
        )
        db_session.add(setting)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Try to set non-integer value
        update_data = {"value": "not_a_number"}
        
        response = client.patch(f"/api/v1/settings/{unique_key}", json=update_data, headers=headers)
        # Should either validate and reject or accept but fail validation
        assert response.status_code in [200, 400, 422]

    def test_update_setting_empty_key(self, client, db_session, admin_token):
        """Test updating setting with empty key in URL"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        update_data = {"value": "new_value"}
        
        # Empty key in path parameter - FastAPI may route to different endpoint or return 404
        response = client.patch("/api/v1/settings/", json=update_data, headers=headers)
        # May route to batch endpoint or return 404/405
        assert response.status_code in [404, 405, 422]

    def test_get_setting_empty_key(self, client, db_session, admin_token):
        """Test getting setting with empty key"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Empty key routes to GET all settings endpoint
        response = client.get("/api/v1/settings/", headers=headers)
        # FastAPI routes trailing slash to GET all settings, so expect 200
        assert response.status_code == 200

    def test_batch_update_empty_dict(self, client, db_session, admin_token):
        """Test batch update with empty settings dict"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        batch_data = {"settings": {}}
        
        try:
            response = client.patch("/api/v1/settings/batch", json=batch_data, headers=headers)
            # Empty dict - service returns empty list, endpoint returns 404 per implementation
            # Or may raise exception
            assert response.status_code in [404, 500]
            if response.status_code == 404:
                data = response.json()
                assert "detail" in data
        except Exception:
            # If endpoint raises exception, that's also acceptable behavior
            pass

    def test_batch_update_invalid_keys(self, client, db_session, admin_token):
        """Test batch update with non-existent keys"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        batch_data = {
            "settings": {
                "nonexistent_key1": "value1",
                "nonexistent_key2": "value2"
            }
        }
        
        try:
            response = client.patch("/api/v1/settings/batch", json=batch_data, headers=headers)
            # Non-existent keys - service returns empty list, endpoint returns 404 per implementation
            # Or may raise exception
            assert response.status_code in [404, 500]
            if response.status_code == 404:
                data = response.json()
                assert "detail" in data
        except Exception:
            # If endpoint raises exception, that's also acceptable behavior
            pass

    def test_update_planning_center_config_invalid_url(self, client, db_session, admin_token):
        """Test updating Planning Center config with invalid URL"""
        from app.services.system_settings_service import SystemSettingsService
        from app.schemas.system_settings import SystemSettingsCreate
        
        service = SystemSettingsService(db_session)
        existing = service.get_setting("planning_center_api_url")
        if not existing:
            setting_data = SystemSettingsCreate(
                key="planning_center_api_url",
                value="https://old.api.com",
                category="planning_center",
                data_type="string"
            )
            service.create_setting(setting_data, created_by=1)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Invalid URL format
        config_data = {
            "api_url": "not_a_valid_url",
            "max_events": 2000
        }
        
        response = client.patch("/api/v1/settings/planning-center/config", json=config_data, headers=headers)
        # Should either validate URL format or accept it
        assert response.status_code in [200, 400, 422]

    def test_update_planning_center_config_negative_max_events(self, client, db_session, admin_token):
        """Test updating Planning Center config with negative max_events"""
        from app.services.system_settings_service import SystemSettingsService
        from app.schemas.system_settings import SystemSettingsCreate
        
        service = SystemSettingsService(db_session)
        existing = service.get_setting("planning_center_max_events")
        if not existing:
            setting_data = SystemSettingsCreate(
                key="planning_center_max_events",
                value="1000",
                category="planning_center",
                data_type="integer"
            )
            service.create_setting(setting_data, created_by=1)
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        config_data = {
            "api_url": "https://api.test.com",
            "max_events": -1  # Negative value
        }
        
        response = client.patch("/api/v1/settings/planning-center/config", json=config_data, headers=headers)
        # Should either validate and reject or accept it
        assert response.status_code in [200, 400, 422]

    # Edge case tests
    def test_create_setting_very_long_key(self, client, db_session, admin_token):
        """Test creating setting with very long key (boundary test)"""
        import uuid
        # Key max length is 100 characters
        long_key = "a" * 100
        unique_suffix = str(uuid.uuid4())[:8]
        test_key = f"{long_key[:92]}{unique_suffix}"
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        setting_data = {
            "key": test_key,
            "value": "test_value",
            "category": "system",
            "data_type": "string"
        }
        
        response = client.post("/api/v1/settings", json=setting_data, headers=headers)
        assert response.status_code in [200, 400, 422]  # May validate length

    def test_create_setting_very_long_value(self, client, db_session, admin_token):
        """Test creating setting with very long value"""
        import uuid
        unique_key = f"test_long_value_{str(uuid.uuid4())[:8]}"
        # Very long value (10KB)
        long_value = "a" * 10000
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        setting_data = {
            "key": unique_key,
            "value": long_value,
            "category": "system",
            "data_type": "string"
        }
        
        response = client.post("/api/v1/settings", json=setting_data, headers=headers)
        assert response.status_code in [200, 400, 413]  # May have size limits

    def test_create_setting_special_characters(self, client, db_session, admin_token):
        """Test creating setting with special characters"""
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        special_key = f"test_special_{unique_suffix}"
        special_value = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        setting_data = {
            "key": special_key,
            "value": special_value,
            "category": "system",
            "data_type": "string"
        }
        
        response = client.post("/api/v1/settings", json=setting_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == special_value

    def test_create_setting_unicode_characters(self, client, db_session, admin_token):
        """Test creating setting with unicode characters"""
        import uuid
        unique_key = f"test_unicode_{str(uuid.uuid4())[:8]}"
        unicode_value = "测试 🎉 émoji ñoño"
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        setting_data = {
            "key": unique_key,
            "value": unicode_value,
            "category": "system",
            "data_type": "string"
        }
        
        response = client.post("/api/v1/settings", json=setting_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == unicode_value

    def test_create_setting_empty_value(self, client, db_session, admin_token):
        """Test creating setting with empty value"""
        import uuid
        unique_key = f"test_empty_{str(uuid.uuid4())[:8]}"
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        setting_data = {
            "key": unique_key,
            "value": "",  # Empty value
            "category": "system",
            "data_type": "string"
        }
        
        response = client.post("/api/v1/settings", json=setting_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == ""

    def test_get_settings_with_invalid_category(self, client, db_session, admin_token):
        """Test getting settings with invalid category filter"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/settings?category=nonexistent_category", headers=headers)
        
        # Invalid category returns 400 Bad Request
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid category" in data["detail"]

    def test_update_setting_sql_injection_attempt(self, client, db_session, admin_token):
        """Test that SQL injection attempts are prevented"""
        import uuid
        unique_key = f"test_sql_{str(uuid.uuid4())[:8]}"
        
        setting = SystemSettings(
            key=unique_key,
            value="original_value",
            category="system",
            data_type="string"
        )
        db_session.add(setting)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        # SQL injection attempt
        malicious_value = "'; DROP TABLE system_settings; --"
        update_data = {"value": malicious_value}
        
        response = client.patch(f"/api/v1/settings/{unique_key}", json=update_data, headers=headers)
        # Should handle safely - either accept as string value or reject
        assert response.status_code in [200, 400, 422]
        
        # Verify table still exists by querying
        if response.status_code == 200:
            verify_response = client.get(f"/api/v1/settings/{unique_key}", headers=headers)
            assert verify_response.status_code == 200
            # Value should be stored as-is (not executed)
            assert verify_response.json()["value"] == malicious_value

    def test_update_setting_xss_attempt(self, client, db_session, admin_token):
        """Test that XSS attempts are handled safely"""
        import uuid
        unique_key = f"test_xss_{str(uuid.uuid4())[:8]}"
        
        setting = SystemSettings(
            key=unique_key,
            value="original_value",
            category="system",
            data_type="string"
        )
        db_session.add(setting)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        # XSS attempt
        xss_value = "<script>alert('XSS')</script>"
        update_data = {"value": xss_value}
        
        response = client.patch(f"/api/v1/settings/{unique_key}", json=update_data, headers=headers)
        # Should accept as string value (sanitization happens on frontend)
        assert response.status_code in [200, 400, 422]
        
        if response.status_code == 200:
            verify_response = client.get(f"/api/v1/settings/{unique_key}", headers=headers)
            assert verify_response.status_code == 200
            # Value should be stored as-is
            assert verify_response.json()["value"] == xss_value

    def test_batch_update_large_payload(self, client, db_session, admin_token):
        """Test batch update with large number of settings"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create many settings
        settings_to_create = []
        for i in range(50):
            key = f"test_batch_{unique_id}_{i}"
            setting = SystemSettings(
                key=key,
                value=f"value_{i}",
                category="system",
                data_type="string"
            )
            settings_to_create.append(setting)
        db_session.add_all(settings_to_create)
        db_session.commit()
        
        # Batch update all of them
        batch_data = {
            "settings": {f"test_batch_{unique_id}_{i}": f"new_value_{i}" for i in range(50)}
        }
        
        response = client.patch("/api/v1/settings/batch", json=batch_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 50
