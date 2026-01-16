"""
System Settings service layer
"""

import json
import logging
from typing import Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.system_settings import SystemSettings
from app.schemas.system_settings import (
    PlanningCenterConfig,
    SystemSettingsCreate,
    SystemSettingsUpdate,
)
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class SystemSettingsService:
    """Service for system settings operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_setting(self, key: str) -> Optional[SystemSettings]:
        """Get a specific setting by key"""
        return self.db.query(SystemSettings).filter(SystemSettings.key == key).first()

    def get_settings_by_category(self, category: str) -> List[SystemSettings]:
        """Get all settings for a specific category"""
        return (
            self.db.query(SystemSettings)
            .filter(SystemSettings.category == category)
            .order_by(SystemSettings.key)
            .all()
        )

    def get_all_settings(self) -> Dict[str, List[SystemSettings]]:
        """Get all settings grouped by category"""
        all_settings = self.db.query(SystemSettings).order_by(SystemSettings.category, SystemSettings.key).all()
        result: Dict[str, List[SystemSettings]] = {}
        for setting in all_settings:
            if setting.category not in result:
                result[setting.category] = []
            result[setting.category].append(setting)
        return result

    def create_setting(
        self, setting: SystemSettingsCreate, created_by: Optional[int] = None
    ) -> SystemSettings:
        """Create a new system setting"""
        db_setting = SystemSettings(**setting.model_dump())
        db_setting.updated_by = created_by
        try:
            self.db.add(db_setting)
            self.db.commit()
            self.db.refresh(db_setting)
            AuditService(self.db).log_change(
                table_name=SystemSettings.__tablename__,
                record_id=db_setting.id,
                action="insert",
                changed_by=created_by,
                new_values=AuditService.serialize_model(db_setting),
            )
            return db_setting
        except IntegrityError:
            self.db.rollback()
            logger.exception("Integrity error creating setting '%s'", setting.key)
            raise
        except Exception:
            self.db.rollback()
            logger.exception("Unexpected error creating setting '%s'", setting.key)
            raise

    def update_setting(
        self, key: str, value: str, updated_by: Optional[int] = None
    ) -> Optional[SystemSettings]:
        """Update a system setting's value"""
        db_setting = self.get_setting(key)
        if not db_setting:
            return None

        old_values = AuditService.serialize_model(db_setting)
        old_value = db_setting.value

        # Validate value based on data_type
        if not self.validate_setting_value(key, value):
            raise ValueError(f"Invalid value for setting '{key}' with data_type '{db_setting.data_type}'")

        db_setting.value = value
        db_setting.updated_by = updated_by

        try:
            self.db.commit()
            self.db.refresh(db_setting)
            AuditService(self.db).log_change(
                table_name=SystemSettings.__tablename__,
                record_id=db_setting.id,
                action="update",
                changed_by=updated_by,
                old_values=old_values,
                new_values=AuditService.serialize_model(db_setting),
            )
            return db_setting
        except IntegrityError:
            self.db.rollback()
            logger.exception("Integrity error updating setting '%s'", key)
            raise
        except Exception:
            self.db.rollback()
            logger.exception("Unexpected error updating setting '%s'", key)
            raise

    def update_setting_full(
        self,
        key: str,
        setting_update: SystemSettingsUpdate,
        updated_by: Optional[int] = None,
    ) -> Optional[SystemSettings]:
        """Update a system setting (value and/or description)"""
        db_setting = self.get_setting(key)
        if not db_setting:
            return None

        old_values = AuditService.serialize_model(db_setting)
        update_data = setting_update.model_dump(exclude_unset=True)

        if "value" in update_data:
            value = update_data["value"]
            if value is not None and not self.validate_setting_value(key, value):
                raise ValueError(
                    f"Invalid value for setting '{key}' with data_type '{db_setting.data_type}'"
                )
            db_setting.value = value

        if "description" in update_data:
            db_setting.description = update_data["description"]

        db_setting.updated_by = updated_by

        try:
            self.db.commit()
            self.db.refresh(db_setting)
            AuditService(self.db).log_change(
                table_name=SystemSettings.__tablename__,
                record_id=db_setting.id,
                action="update",
                changed_by=updated_by,
                old_values=old_values,
                new_values=AuditService.serialize_model(db_setting),
            )
            return db_setting
        except IntegrityError:
            self.db.rollback()
            logger.exception("Integrity error updating setting '%s'", key)
            raise
        except Exception:
            self.db.rollback()
            logger.exception("Unexpected error updating setting '%s'", key)
            raise

    def update_settings_batch(
        self, settings: Dict[str, str], updated_by: Optional[int] = None
    ) -> List[SystemSettings]:
        """Update multiple settings in a batch"""
        updated_settings = []
        for key, value in settings.items():
            setting = self.update_setting(key, value, updated_by)
            if setting:
                updated_settings.append(setting)
        return updated_settings

    def validate_setting_value(self, key: str, value: str) -> bool:
        """Validate a setting value based on its data_type"""
        if value is None:
            return True  # None/null values are allowed

        db_setting = self.get_setting(key)
        if not db_setting:
            return False

        try:
            if db_setting.data_type == "integer":
                int(value)
            elif db_setting.data_type == "boolean":
                if value.lower() not in ("true", "false", "1", "0", "yes", "no"):
                    return False
            elif db_setting.data_type == "json":
                json.loads(value)
            # string type accepts any value
        except (ValueError, json.JSONDecodeError):
            return False

        return True

    def get_planning_center_config(self) -> PlanningCenterConfig:
        """Get Planning Center configuration as a structured object"""
        settings = self.get_settings_by_category("planning_center")
        config_dict: Dict[str, any] = {
            "api_url": "https://api.planningcenteronline.com",
            "max_events": 2000,
            "cache_ttl_minutes": 10,
            "use_mock": False,
        }

        for setting in settings:
            key = setting.key
            if key == "planning_center_api_url":
                config_dict["api_url"] = setting.value or config_dict["api_url"]
            elif key == "planning_center_app_id":
                config_dict["app_id"] = setting.value
            elif key == "planning_center_secret":
                config_dict["secret"] = setting.value
            elif key == "planning_center_access_token":
                config_dict["access_token"] = setting.value
            elif key == "planning_center_max_events":
                config_dict["max_events"] = int(setting.value) if setting.value else 2000
            elif key == "planning_center_cache_ttl_minutes":
                config_dict["cache_ttl_minutes"] = int(setting.value) if setting.value else 10
            elif key == "use_mock_planning_center":
                config_dict["use_mock"] = (
                    setting.value.lower() in ("true", "1", "yes") if setting.value else False
                )

        return PlanningCenterConfig(**config_dict)

    def update_planning_center_config(
        self, config: PlanningCenterConfig, updated_by: Optional[int] = None
    ) -> Dict[str, SystemSettings]:
        """Update Planning Center configuration"""
        updates = {
            "planning_center_api_url": config.api_url,
            "planning_center_app_id": config.app_id or "",
            "planning_center_secret": config.secret or "",
            "planning_center_access_token": config.access_token or "",
            "planning_center_max_events": str(config.max_events),
            "planning_center_cache_ttl_minutes": str(config.cache_ttl_minutes),
            "use_mock_planning_center": "true" if config.use_mock else "false",
        }

        updated_settings = {}
        for key, value in updates.items():
            setting = self.update_setting(key, value, updated_by)
            if setting:
                updated_settings[key] = setting

        return updated_settings

    def sync_to_environment(self) -> None:
        """
        Sync database settings to environment variables (one-way: DB -> Env)
        Note: This is a placeholder - actual environment variable updates would
        require process restart or external configuration management
        """
        # This would typically update environment variables or a config file
        # For now, we'll just log that sync was requested
        logger.info("Environment sync requested - settings are read from database at runtime")
