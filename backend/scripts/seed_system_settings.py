"""
Seed script for system settings
Populates the system_settings table with initial values from config.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.config import settings
from app.models.system_settings import SystemSettings
from app.services.system_settings_service import SystemSettingsService


def seed_system_settings(db: Session):
    """Seed system settings from current configuration"""
    settings_service = SystemSettingsService(db)

    # System Configuration
    system_settings = [
        {
            "key": "app_name",
            "value": settings.APP_NAME,
            "category": "system",
            "data_type": "string",
            "description": "Application name",
            "is_sensitive": False,
        },
        {
            "key": "app_version",
            "value": settings.VERSION,
            "category": "system",
            "data_type": "string",
            "description": "Application version",
            "is_sensitive": False,
        },
        {
            "key": "environment",
            "value": settings.ENVIRONMENT,
            "category": "system",
            "data_type": "string",
            "description": "Application environment (development, staging, production)",
            "is_sensitive": False,
        },
        {
            "key": "debug_mode",
            "value": str(settings.DEBUG).lower(),
            "category": "system",
            "data_type": "boolean",
            "description": "Enable debug mode",
            "is_sensitive": False,
        },
        {
            "key": "session_timeout_minutes",
            "value": str(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "category": "system",
            "data_type": "integer",
            "description": "Session timeout in minutes",
            "is_sensitive": False,
        },
        {
            "key": "max_upload_size_mb",
            "value": str(settings.MAX_FILE_SIZE // (1024 * 1024)),
            "category": "system",
            "data_type": "integer",
            "description": "Maximum file upload size in MB",
            "is_sensitive": False,
        },
        {
            "key": "log_level",
            "value": settings.LOG_LEVEL,
            "category": "system",
            "data_type": "string",
            "description": "Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
            "is_sensitive": False,
        },
    ]

    # Planning Center Configuration
    planning_center_settings = [
        {
            "key": "planning_center_api_url",
            "value": settings.PLANNING_CENTER_API_URL,
            "category": "planning_center",
            "data_type": "string",
            "description": "Planning Center API base URL",
            "is_sensitive": False,
        },
        {
            "key": "planning_center_app_id",
            "value": settings.PLANNING_CENTER_APP_ID or "",
            "category": "planning_center",
            "data_type": "string",
            "description": "Planning Center Application ID",
            "is_sensitive": True,
        },
        {
            "key": "planning_center_secret",
            "value": settings.PLANNING_CENTER_SECRET or "",
            "category": "planning_center",
            "data_type": "string",
            "description": "Planning Center Application Secret",
            "is_sensitive": True,
        },
        {
            "key": "planning_center_access_token",
            "value": settings.PLANNING_CENTER_ACCESS_TOKEN or "",
            "category": "planning_center",
            "data_type": "string",
            "description": "Planning Center Access Token",
            "is_sensitive": True,
        },
        {
            "key": "planning_center_max_events",
            "value": str(settings.PLANNING_CENTER_MAX_EVENTS),
            "category": "planning_center",
            "data_type": "integer",
            "description": "Maximum number of events to fetch from Planning Center",
            "is_sensitive": False,
        },
        {
            "key": "planning_center_cache_ttl_minutes",
            "value": str(settings.PLANNING_CENTER_CACHE_TTL_MINUTES),
            "category": "planning_center",
            "data_type": "integer",
            "description": "Cache TTL in minutes for Planning Center data (0 = disabled)",
            "is_sensitive": False,
        },
        {
            "key": "use_mock_planning_center",
            "value": str(settings.USE_MOCK_PLANNING_CENTER).lower(),
            "category": "planning_center",
            "data_type": "boolean",
            "description": "Use mock Planning Center API for development/testing",
            "is_sensitive": False,
        },
    ]

    # Security Settings
    security_settings = [
        {
            "key": "password_min_length",
            "value": "8",
            "category": "security",
            "data_type": "integer",
            "description": "Minimum password length",
            "is_sensitive": False,
        },
        {
            "key": "password_require_uppercase",
            "value": "false",
            "category": "security",
            "data_type": "boolean",
            "description": "Require uppercase letters in passwords",
            "is_sensitive": False,
        },
        {
            "key": "password_require_lowercase",
            "value": "false",
            "category": "security",
            "data_type": "boolean",
            "description": "Require lowercase letters in passwords",
            "is_sensitive": False,
        },
        {
            "key": "password_require_numbers",
            "value": "false",
            "category": "security",
            "data_type": "boolean",
            "description": "Require numbers in passwords",
            "is_sensitive": False,
        },
        {
            "key": "password_require_special",
            "value": "false",
            "category": "security",
            "data_type": "boolean",
            "description": "Require special characters in passwords",
            "is_sensitive": False,
        },
        {
            "key": "account_lockout_attempts",
            "value": "5",
            "category": "security",
            "data_type": "integer",
            "description": "Number of failed login attempts before account lockout",
            "is_sensitive": False,
        },
        {
            "key": "account_lockout_duration_minutes",
            "value": "30",
            "category": "security",
            "data_type": "integer",
            "description": "Account lockout duration in minutes",
            "is_sensitive": False,
        },
        {
            "key": "session_idle_timeout_minutes",
            "value": "60",
            "category": "security",
            "data_type": "integer",
            "description": "Session idle timeout in minutes",
            "is_sensitive": False,
        },
        {
            "key": "rate_limit_enabled",
            "value": str(settings.RATE_LIMIT_ENABLED).lower(),
            "category": "security",
            "data_type": "boolean",
            "description": "Enable rate limiting",
            "is_sensitive": False,
        },
        {
            "key": "rate_limit_requests",
            "value": str(settings.RATE_LIMIT_REQUESTS),
            "category": "security",
            "data_type": "integer",
            "description": "Maximum requests per rate limit window",
            "is_sensitive": False,
        },
        {
            "key": "rate_limit_window_seconds",
            "value": str(settings.RATE_LIMIT_WINDOW),
            "category": "security",
            "data_type": "integer",
            "description": "Rate limit window in seconds",
            "is_sensitive": False,
        },
    ]

    # Backup & Maintenance Settings
    backup_settings = [
        {
            "key": "backup_enabled",
            "value": "false",
            "category": "backup",
            "data_type": "boolean",
            "description": "Enable automated backups",
            "is_sensitive": False,
        },
        {
            "key": "backup_frequency_days",
            "value": "7",
            "category": "backup",
            "data_type": "integer",
            "description": "Backup frequency in days",
            "is_sensitive": False,
        },
        {
            "key": "backup_retention_days",
            "value": "30",
            "category": "backup",
            "data_type": "integer",
            "description": "Backup retention period in days",
            "is_sensitive": False,
        },
        {
            "key": "maintenance_window_start",
            "value": "02:00",
            "category": "backup",
            "data_type": "string",
            "description": "Maintenance window start time (HH:MM format)",
            "is_sensitive": False,
        },
        {
            "key": "maintenance_window_end",
            "value": "04:00",
            "category": "backup",
            "data_type": "string",
            "description": "Maintenance window end time (HH:MM format)",
            "is_sensitive": False,
        },
    ]

    all_settings = system_settings + planning_center_settings + security_settings + backup_settings

    created_count = 0
    skipped_count = 0

    for setting_data in all_settings:
        # Check if setting already exists
        existing = settings_service.get_setting(setting_data["key"])
        if existing:
            print(f"Setting '{setting_data['key']}' already exists, skipping...")
            skipped_count += 1
            continue

        try:
            from app.schemas.system_settings import SystemSettingsCreate

            setting_create = SystemSettingsCreate(**setting_data)
            settings_service.create_setting(setting_create, created_by=None)
            print(f"Created setting: {setting_data['key']}")
            created_count += 1
        except Exception as e:
            print(f"Error creating setting '{setting_data['key']}': {e}")
            skipped_count += 1

    print(f"\nSeed complete: {created_count} created, {skipped_count} skipped")


def main():
    """Main entry point"""
    db: Session = SessionLocal()
    try:
        seed_system_settings(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
