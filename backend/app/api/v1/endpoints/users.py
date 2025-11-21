"""
User management endpoints
"""

from typing import List

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate, UserProfileUpdate
from app.schemas.password import ChangePasswordRequest
from app.schemas.user_preference import UserPreference, UserPreferenceUpdate
from app.services.user_service import UserService
from app.services.user_preference_service import UserPreferenceService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.patch("/me", response_model=User)
async def update_current_user_profile(
    user_update: UserProfileUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update current user's own profile"""
    user_service = UserService(db)
    try:
        user = user_service.update_current_user(
            current_user["id"], user_update, updated_by=current_user["id"]
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
    except IntegrityError:
        logger.warning("Duplicate detected updating user profile id=%s", current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Updating the profile would violate a uniqueness constraint.",
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error updating user profile id=%s", current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update profile at this time.",
        )


@router.patch("/me/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change current user's password"""
    user_service = UserService(db)
    user = user_service.get_user(current_user["id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    
    # Verify current password
    if not user_service.verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    # Validate new password is different from current
    if user_service.verify_password(password_data.new_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )
    
    # Update password
    try:
        from app.schemas.user import UserUpdate
        user_update = UserUpdate(password=password_data.new_password)
        updated_user = user_service.update_user(
            current_user["id"], user_update, updated_by=current_user["id"]
        )
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password",
            )
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error changing password for user id=%s", current_user["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to change password at this time.",
        )


@router.get("/me/preferences", response_model=UserPreference)
async def get_user_preferences(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get current user's notification preferences"""
    preference_service = UserPreferenceService(db)
    preferences = preference_service.get_user_preferences(current_user["id"])
    return preferences


@router.patch("/me/preferences", response_model=UserPreference)
async def update_user_preferences(
    preferences_update: UserPreferenceUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update current user's notification preferences"""
    preference_service = UserPreferenceService(db)
    preferences = preference_service.update_user_preferences(
        current_user["id"], preferences_update
    )
    return preferences


@router.get("", response_model=List[User])
@router.get("/", response_model=List[User])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all users"""
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID"""
    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post("", response_model=User)
@router.post("/", response_model=User)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Create a new user"""
    user_service = UserService(db)
    try:
        return user_service.create_user(user, created_by=current_user["id"])
    except IntegrityError:
        logger.warning("Attempt to create duplicate user (username=%s, email=%s)", user.username, user.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with that username or email already exists.",
        )
    except Exception:
        logger.exception("Unexpected error creating user (username=%s)", user.username)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create user at this time.",
        )


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Update an existing user"""
    user_service = UserService(db)
    try:
        user = user_service.update_user(
            user_id, user_update, updated_by=current_user["id"]
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
    except IntegrityError:
        logger.warning("Duplicate detected updating user id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Updating the user would violate a uniqueness constraint.",
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error updating user id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update user at this time.",
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Delete a user"""
    user_service = UserService(db)
    success = user_service.delete_user(user_id, deleted_by=current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"message": "User deleted successfully"}
