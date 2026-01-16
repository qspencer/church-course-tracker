"""
System Settings endpoints
"""

from typing import Dict, List, Optional

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_admin_user
from app.core.database import get_db
from app.schemas.system_settings import (
    PlanningCenterConfig,
    SystemSettings,
    SystemSettingsBatchUpdate,
    SystemSettingsCreate,
    SystemSettingsUpdate,
)
from app.services.system_settings_service import SystemSettingsService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=Dict[str, List[SystemSettings]])
@router.get("/", response_model=Dict[str, List[SystemSettings]])
async def get_all_settings(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    """Get all system settings, optionally filtered by category"""
    settings_service = SystemSettingsService(db)
    if category:
        if category not in ("system", "planning_center", "security", "backup"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: system, planning_center, security, backup",
            )
        return {category: settings_service.get_settings_by_category(category)}
    return settings_service.get_all_settings()


@router.get("/{key}", response_model=SystemSettings)
async def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    """Get a specific setting by key"""
    settings_service = SystemSettingsService(db)
    setting = settings_service.get_setting(key)
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Setting '{key}' not found"
        )
    return setting


@router.post("", response_model=SystemSettings)
@router.post("/", response_model=SystemSettings)
async def create_setting(
    setting: SystemSettingsCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    """Create a new system setting"""
    settings_service = SystemSettingsService(db)
    try:
        return settings_service.create_setting(setting, created_by=current_user["id"])
    except Exception as e:
        logger.exception("Error creating setting '%s'", setting.key)
        if "IntegrityError" in str(type(e).__name__):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Setting with key '{setting.key}' already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create setting at this time",
        )


@router.patch("/batch", response_model=List[SystemSettings])
async def update_settings_batch(
    batch_update: SystemSettingsBatchUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    """Update multiple settings in a batch"""
    settings_service = SystemSettingsService(db)
    try:
        updated_settings = settings_service.update_settings_batch(
            batch_update.settings, updated_by=current_user["id"]
        )
        if not updated_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No settings were found or updated",
            )
        return updated_settings
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logger.exception("Error updating settings batch")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update settings at this time",
        )


@router.patch("/{key}", response_model=SystemSettings)
async def update_setting(
    key: str,
    setting_update: SystemSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    """Update a system setting"""
    settings_service = SystemSettingsService(db)
    try:
        setting = settings_service.update_setting_full(
            key, setting_update, updated_by=current_user["id"]
        )
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Setting '{key}' not found"
            )
        return setting
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logger.exception("Error updating setting '%s'", key)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update setting at this time",
        )


@router.get("/planning-center/config", response_model=PlanningCenterConfig)
async def get_planning_center_config(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    """Get Planning Center configuration"""
    settings_service = SystemSettingsService(db)
    try:
        return settings_service.get_planning_center_config()
    except Exception as e:
        logger.exception("Error getting Planning Center config")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve Planning Center configuration",
        )


@router.patch("/planning-center/config", response_model=Dict[str, SystemSettings])
async def update_planning_center_config(
    config: PlanningCenterConfig,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    """Update Planning Center configuration"""
    settings_service = SystemSettingsService(db)
    try:
        updated_settings = settings_service.update_planning_center_config(
            config, updated_by=current_user["id"]
        )
        if not updated_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Planning Center settings not found",
            )
        return updated_settings
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logger.exception("Error updating Planning Center config")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update Planning Center configuration",
        )


@router.post("/sync-to-env")
async def sync_to_environment(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user),
):
    """Sync database settings to environment variables"""
    settings_service = SystemSettingsService(db)
    try:
        settings_service.sync_to_environment()
        return {"message": "Environment sync requested. Settings are read from database at runtime."}
    except Exception as e:
        logger.exception("Error syncing settings to environment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to sync settings to environment",
        )
