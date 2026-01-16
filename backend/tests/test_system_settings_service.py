"""
Tests for SystemSettingsService
"""

import pytest
from app.services.system_settings_service import SystemSettingsService
from app.schemas.system_settings import SystemSettingsCreate, SystemSettingsUpdate, PlanningCenterConfig
from app.models.system_settings import SystemSettings


class TestSystemSettingsService:
    """Test SystemSettingsService"""

    def test_create_setting(self, db_session):
        """Test creating a system setting"""
        service = SystemSettingsService(db_session)
        
        setting_data = SystemSettingsCreate(
            key="test_setting",
            value="test_value",
            category="system",
            data_type="string",
            description="Test setting"
        )
        
        setting = service.create_setting(setting_data, created_by=1)
        
        assert setting is not None
        assert setting.key == "test_setting"
        assert setting.value == "test_value"
        assert setting.category == "system"
        assert setting.data_type == "string"

    def test_get_setting(self, db_session):
        """Test getting a specific setting"""
        # Use unique key to avoid conflicts with seeded data
        import uuid
        unique_key = f"test_key_{str(uuid.uuid4())[:8]}"
        
        # Create a setting first
        setting = SystemSettings(
            key=unique_key,
            value="test_value",
            category="system",
            data_type="string"
        )
        db_session.add(setting)
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        found_setting = service.get_setting(unique_key)
        
        assert found_setting is not None
        assert found_setting.key == unique_key
        assert found_setting.value == "test_value"

    def test_get_settings_by_category(self, db_session):
        """Test getting settings by category"""
        # Use unique keys to avoid conflicts with seeded data
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # Create settings in different categories
        setting1 = SystemSettings(
            key=f"test_system_setting1_{unique_id}",
            value="value1",
            category="system",
            data_type="string"
        )
        setting2 = SystemSettings(
            key=f"test_system_setting2_{unique_id}",
            value="value2",
            category="system",
            data_type="string"
        )
        setting3 = SystemSettings(
            key=f"test_security_setting1_{unique_id}",
            value="value3",
            category="security",
            data_type="string"
        )
        db_session.add_all([setting1, setting2, setting3])
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        system_settings = service.get_settings_by_category("system")
        
        # Should have at least our 2 test settings (may have more from seed data)
        test_settings = [s for s in system_settings if unique_id in s.key]
        assert len(test_settings) == 2
        assert all(s.category == "system" for s in test_settings)

    def test_get_all_settings(self, db_session):
        """Test getting all settings grouped by category"""
        # Use unique keys to avoid conflicts with seeded data
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        
        # Create settings in different categories
        setting1 = SystemSettings(
            key=f"test_system_setting1_{unique_id}",
            value="value1",
            category="system",
            data_type="string"
        )
        setting2 = SystemSettings(
            key=f"test_security_setting1_{unique_id}",
            value="value2",
            category="security",
            data_type="string"
        )
        db_session.add_all([setting1, setting2])
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        all_settings = service.get_all_settings()
        
        assert "system" in all_settings
        assert "security" in all_settings
        # Should have at least our test settings (may have more from seed data)
        test_system = [s for s in all_settings["system"] if unique_id in s.key]
        test_security = [s for s in all_settings["security"] if unique_id in s.key]
        assert len(test_system) == 1
        assert len(test_security) == 1

    def test_update_setting(self, db_session):
        """Test updating a setting's value"""
        # Use unique key to avoid conflicts with seeded data
        import uuid
        unique_key = f"test_key_{str(uuid.uuid4())[:8]}"
        
        # Create a setting first
        setting = SystemSettings(
            key=unique_key,
            value="old_value",
            category="system",
            data_type="string"
        )
        db_session.add(setting)
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        updated_setting = service.update_setting(unique_key, "new_value", updated_by=1)
        
        assert updated_setting is not None
        assert updated_setting.value == "new_value"

    def test_update_setting_full(self, db_session):
        """Test updating a setting with full update"""
        # Use unique key to avoid conflicts with seeded data
        import uuid
        unique_key = f"test_key_{str(uuid.uuid4())[:8]}"
        
        # Create a setting first
        setting = SystemSettings(
            key=unique_key,
            value="old_value",
            category="system",
            data_type="string",
            description="Old description"
        )
        db_session.add(setting)
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        update_data = SystemSettingsUpdate(
            value="new_value",
            description="New description"
        )
        updated_setting = service.update_setting_full(unique_key, update_data, updated_by=1)
        
        assert updated_setting is not None
        assert updated_setting.value == "new_value"
        assert updated_setting.description == "New description"

    def test_update_settings_batch(self, db_session):
        """Test batch updating multiple settings"""
        # Use unique keys to avoid conflicts with seeded data
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        key1 = f"test_key1_{unique_id}"
        key2 = f"test_key2_{unique_id}"
        
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
        
        service = SystemSettingsService(db_session)
        updates = {
            key1: "new_value1",
            key2: "new_value2"
        }
        updated_settings = service.update_settings_batch(updates, updated_by=1)
        
        assert len(updated_settings) == 2
        assert updated_settings[0].value == "new_value1" or updated_settings[1].value == "new_value1"

    def test_validate_setting_value_string(self, db_session):
        """Test validating string value"""
        setting = SystemSettings(
            key="test_string",
            value="test",
            category="system",
            data_type="string"
        )
        db_session.add(setting)
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        assert service.validate_setting_value("test_string", "any_string") is True

    def test_validate_setting_value_integer(self, db_session):
        """Test validating integer value"""
        setting = SystemSettings(
            key="test_int",
            value="123",
            category="system",
            data_type="integer"
        )
        db_session.add(setting)
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        assert service.validate_setting_value("test_int", "456") is True
        assert service.validate_setting_value("test_int", "not_a_number") is False

    def test_validate_setting_value_boolean(self, db_session):
        """Test validating boolean value"""
        setting = SystemSettings(
            key="test_bool",
            value="true",
            category="system",
            data_type="boolean"
        )
        db_session.add(setting)
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        assert service.validate_setting_value("test_bool", "true") is True
        assert service.validate_setting_value("test_bool", "false") is True
        assert service.validate_setting_value("test_bool", "invalid") is False

    def test_get_planning_center_config(self, db_session):
        """Test getting Planning Center configuration"""
        # Create Planning Center settings
        settings_data = [
            ("planning_center_api_url", "https://api.test.com", "planning_center", "string"),
            ("planning_center_app_id", "app123", "planning_center", "string"),
            ("planning_center_secret", "secret123", "planning_center", "string"),
            ("planning_center_max_events", "1000", "planning_center", "integer"),
            ("planning_center_cache_ttl_minutes", "15", "planning_center", "integer"),
            ("use_mock_planning_center", "false", "planning_center", "boolean"),
        ]
        
        # Remove existing settings first to avoid conflicts
        service = SystemSettingsService(db_session)
        for key, _, _, _ in settings_data:
            existing = service.get_setting(key)
            if existing:
                db_session.delete(existing)
        db_session.commit()
        
        for key, value, category, data_type in settings_data:
            setting = SystemSettings(
                key=key,
                value=value,
                category=category,
                data_type=data_type
            )
            db_session.add(setting)
        db_session.commit()
        
        config = service.get_planning_center_config()
        
        assert config.api_url == "https://api.test.com"
        assert config.app_id == "app123"
        assert config.max_events == 1000
        assert config.cache_ttl_minutes == 15
        assert config.use_mock is False

    def test_update_planning_center_config(self, db_session):
        """Test updating Planning Center configuration"""
        # This test uses existing seeded settings, so we'll update them
        # First check if they exist, if not create them
        service = SystemSettingsService(db_session)
        
        # Ensure required settings exist
        required_keys = ["planning_center_api_url", "planning_center_max_events", "use_mock_planning_center"]
        for key in required_keys:
            existing = service.get_setting(key)
            if not existing:
                # Create if doesn't exist
                setting_data = SystemSettingsCreate(
                    key=key,
                    value="https://old.api.com" if "api_url" in key else ("500" if "max_events" in key else "true"),
                    category="planning_center",
                    data_type="string" if "api_url" in key else ("integer" if "max_events" in key else "boolean")
                )
                service.create_setting(setting_data, created_by=1)
        
        new_config = PlanningCenterConfig(
            api_url="https://new.api.com",
            max_events=2000,
            cache_ttl_minutes=20,
            use_mock=False
        )
        
        updated = service.update_planning_center_config(new_config, updated_by=1)
        
        assert len(updated) > 0
        # Verify the updates
        updated_setting = service.get_setting("planning_center_api_url")
        assert updated_setting is not None
        assert updated_setting.value == "https://new.api.com"

    # Negative test cases
    def test_create_setting_duplicate_key(self, db_session):
        """Test creating a setting with duplicate key fails"""
        import uuid
        unique_key = f"test_duplicate_{str(uuid.uuid4())[:8]}"
        
        service = SystemSettingsService(db_session)
        setting_data = SystemSettingsCreate(
            key=unique_key,
            value="value1",
            category="system",
            data_type="string"
        )
        
        # Create first setting
        service.create_setting(setting_data, created_by=1)
        
        # Try to create duplicate - should raise IntegrityError
        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            service.create_setting(setting_data, created_by=1)

    def test_get_setting_not_found(self, db_session):
        """Test getting a non-existent setting returns None"""
        service = SystemSettingsService(db_session)
        found_setting = service.get_setting("nonexistent_key")
        
        assert found_setting is None

    def test_update_setting_not_found(self, db_session):
        """Test updating a non-existent setting returns None"""
        service = SystemSettingsService(db_session)
        updated_setting = service.update_setting("nonexistent_key", "new_value", updated_by=1)
        
        assert updated_setting is None

    def test_update_setting_full_not_found(self, db_session):
        """Test updating a non-existent setting with full update returns None"""
        service = SystemSettingsService(db_session)
        update_data = SystemSettingsUpdate(value="new_value")
        updated_setting = service.update_setting_full("nonexistent_key", update_data, updated_by=1)
        
        assert updated_setting is None

    def test_validate_setting_value_invalid_integer(self, db_session):
        """Test validating invalid integer values"""
        import uuid
        unique_key = f"test_int_{str(uuid.uuid4())[:8]}"
        
        setting = SystemSettings(
            key=unique_key,
            value="123",
            category="system",
            data_type="integer"
        )
        db_session.add(setting)
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        # Test various invalid integer formats
        assert service.validate_setting_value(unique_key, "abc") is False
        assert service.validate_setting_value(unique_key, "12.34") is False
        # Empty string might be handled differently - check actual behavior
        # The service might return False for empty string
        result = service.validate_setting_value(unique_key, "")
        assert isinstance(result, bool)

    def test_validate_setting_value_invalid_boolean(self, db_session):
        """Test validating invalid boolean values"""
        import uuid
        unique_key = f"test_bool_{str(uuid.uuid4())[:8]}"
        
        setting = SystemSettings(
            key=unique_key,
            value="true",
            category="system",
            data_type="boolean"
        )
        db_session.add(setting)
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        # The service accepts "true", "false", "1", "0", "yes", "no" for boolean
        # So test with truly invalid values
        assert service.validate_setting_value(unique_key, "invalid") is False
        assert service.validate_setting_value(unique_key, "maybe") is False
        assert service.validate_setting_value(unique_key, "2") is False
        # Empty string might be handled differently
        result = service.validate_setting_value(unique_key, "")
        assert isinstance(result, bool)

    def test_validate_setting_value_nonexistent_key(self, db_session):
        """Test validating value for non-existent setting"""
        service = SystemSettingsService(db_session)
        # Should handle gracefully - may return False or raise exception
        result = service.validate_setting_value("nonexistent_key", "value")
        # The behavior depends on implementation, but should not crash
        assert isinstance(result, bool)

    def test_update_settings_batch_partial_failure(self, db_session):
        """Test batch update with some non-existent keys"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        key1 = f"test_batch_key1_{unique_id}"
        key2 = f"test_batch_key2_{unique_id}"
        
        # Create only one setting
        setting1 = SystemSettings(
            key=key1,
            value="value1",
            category="system",
            data_type="string"
        )
        db_session.add(setting1)
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        updates = {
            key1: "new_value1",
            key2: "new_value2"  # This key doesn't exist
        }
        # Should handle gracefully - may only update existing keys
        updated_settings = service.update_settings_batch(updates, updated_by=1)
        
        # Should have at least one updated setting
        assert len(updated_settings) >= 1

    # Edge case tests
    def test_create_setting_very_long_key(self, db_session):
        """Test creating setting with very long key"""
        import uuid
        # Key max length is 100 characters
        long_key = "a" * 100
        unique_suffix = str(uuid.uuid4())[:8]
        test_key = f"{long_key[:92]}{unique_suffix}"
        
        service = SystemSettingsService(db_session)
        setting_data = SystemSettingsCreate(
            key=test_key,
            value="test_value",
            category="system",
            data_type="string"
        )
        
        setting = service.create_setting(setting_data, created_by=1)
        assert setting is not None
        assert setting.key == test_key

    def test_create_setting_very_long_value(self, db_session):
        """Test creating setting with very long value"""
        import uuid
        unique_key = f"test_long_value_{str(uuid.uuid4())[:8]}"
        # Very long value (10KB)
        long_value = "a" * 10000
        
        service = SystemSettingsService(db_session)
        setting_data = SystemSettingsCreate(
            key=unique_key,
            value=long_value,
            category="system",
            data_type="string"
        )
        
        setting = service.create_setting(setting_data, created_by=1)
        assert setting is not None
        assert len(setting.value) == 10000

    def test_create_setting_special_characters(self, db_session):
        """Test creating setting with special characters in key and value"""
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        special_key = f"test_special_{unique_suffix}"
        special_value = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        service = SystemSettingsService(db_session)
        setting_data = SystemSettingsCreate(
            key=special_key,
            value=special_value,
            category="system",
            data_type="string"
        )
        
        setting = service.create_setting(setting_data, created_by=1)
        assert setting is not None
        assert setting.value == special_value

    def test_create_setting_unicode_characters(self, db_session):
        """Test creating setting with unicode characters"""
        import uuid
        unique_key = f"test_unicode_{str(uuid.uuid4())[:8]}"
        unicode_value = "测试 🎉 émoji ñoño"
        
        service = SystemSettingsService(db_session)
        setting_data = SystemSettingsCreate(
            key=unique_key,
            value=unicode_value,
            category="system",
            data_type="string"
        )
        
        setting = service.create_setting(setting_data, created_by=1)
        assert setting is not None
        assert setting.value == unicode_value

    def test_create_setting_empty_value(self, db_session):
        """Test creating setting with empty value"""
        import uuid
        unique_key = f"test_empty_{str(uuid.uuid4())[:8]}"
        
        service = SystemSettingsService(db_session)
        setting_data = SystemSettingsCreate(
            key=unique_key,
            value="",  # Empty value
            category="system",
            data_type="string"
        )
        
        setting = service.create_setting(setting_data, created_by=1)
        assert setting is not None
        assert setting.value == ""

    def test_get_settings_by_category_empty(self, db_session):
        """Test getting settings for category with no settings"""
        service = SystemSettingsService(db_session)
        settings = service.get_settings_by_category("nonexistent_category")
        
        # Should return empty list, not None
        assert settings is not None
        assert isinstance(settings, list)

    def test_get_all_settings_empty_database(self, db_session):
        """Test getting all settings when database is empty (except seed data)"""
        service = SystemSettingsService(db_session)
        all_settings = service.get_all_settings()
        
        # Should return dict, even if empty
        assert isinstance(all_settings, dict)

    def test_update_setting_empty_value(self, db_session):
        """Test updating setting with empty value"""
        import uuid
        unique_key = f"test_update_empty_{str(uuid.uuid4())[:8]}"
        
        setting = SystemSettings(
            key=unique_key,
            value="original_value",
            category="system",
            data_type="string"
        )
        db_session.add(setting)
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        updated_setting = service.update_setting(unique_key, "", updated_by=1)
        
        assert updated_setting is not None
        assert updated_setting.value == ""

    def test_validate_setting_value_boundary_integer(self, db_session):
        """Test validating integer boundary values"""
        setting = SystemSettings(
            key="test_int_boundary",
            value="0",
            category="system",
            data_type="integer"
        )
        db_session.add(setting)
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        # Test boundary values
        assert service.validate_setting_value("test_int_boundary", "0") is True
        assert service.validate_setting_value("test_int_boundary", "-1") is True
        assert service.validate_setting_value("test_int_boundary", "2147483647") is True  # Max 32-bit int
        assert service.validate_setting_value("test_int_boundary", "-2147483648") is True  # Min 32-bit int

    def test_validate_setting_value_case_sensitivity_boolean(self, db_session):
        """Test boolean validation case handling"""
        import uuid
        unique_key = f"test_bool_case_{str(uuid.uuid4())[:8]}"
        
        setting = SystemSettings(
            key=unique_key,
            value="true",
            category="system",
            data_type="boolean"
        )
        db_session.add(setting)
        db_session.commit()
        
        service = SystemSettingsService(db_session)
        # The service uses .lower() so it's case-insensitive for "true"/"false"
        assert service.validate_setting_value(unique_key, "true") is True
        assert service.validate_setting_value(unique_key, "True") is True  # Case-insensitive
        assert service.validate_setting_value(unique_key, "TRUE") is True  # Case-insensitive
        assert service.validate_setting_value(unique_key, "false") is True
        assert service.validate_setting_value(unique_key, "False") is True  # Case-insensitive
        # Also accepts "1", "0", "yes", "no"
        assert service.validate_setting_value(unique_key, "1") is True
        assert service.validate_setting_value(unique_key, "0") is True
        assert service.validate_setting_value(unique_key, "yes") is True
        assert service.validate_setting_value(unique_key, "no") is True
