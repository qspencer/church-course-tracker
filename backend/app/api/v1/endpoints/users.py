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
from app.schemas.user import (
    User,
    UserCreate,
    UserUpdate,
    UserProfileUpdate,
    BulkDeleteUsersRequest,
    BulkDeleteUsersResponse,
)
from app.schemas.password import ChangePasswordRequest
from app.schemas.user_preference import UserPreference, UserPreferenceUpdate
from app.services.user_service import UserService
from app.services.user_preference_service import UserPreferenceService
from app.services.planning_center_sync_service import PlanningCenterSyncService
from pydantic import BaseModel

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
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get all users, optionally filtered by role. Requires authentication."""
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit, role=role)


@router.post("/bulk-delete", response_model=BulkDeleteUsersResponse)
async def bulk_delete_users(
    request: BulkDeleteUsersRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Bulk delete users - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can delete users",
        )

    user_service = UserService(db)
    result = user_service.bulk_delete_users(
        request.user_ids, deleted_by=current_user["id"], soft_delete=request.soft_delete
    )
    return BulkDeleteUsersResponse(**result)


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get a specific user by ID. Requires authentication."""
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
    """Create a new user - Admin only"""
    # Authorization: Only admin users can create new users
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create new user accounts",
        )

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
    """Update an existing user - Admin only

    This endpoint allows admins to update any user's information including role.
    Non-admin users should use PATCH /me to update their own profile.
    """
    # Authorization: Only admin users can update other users
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can update user accounts. Use PATCH /me to update your own profile.",
        )

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
    """Delete a user - Admin only"""
    # Authorization: Only admin users can delete users
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can delete user accounts",
        )

    user_service = UserService(db)
    success = user_service.delete_user(user_id, deleted_by=current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"message": "User deleted successfully"}


class ImportUserFromPCRequest(BaseModel):
    planning_center_person_id: str
    role: str = "instructor"


@router.post("/import-from-pc", response_model=User)
async def import_user_from_planning_center(
    request: ImportUserFromPCRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Import a user from Planning Center by person ID"""
    sync_service = PlanningCenterSyncService(db)
    user_service = UserService(db)
    
    try:
        # Fetch the person data from Planning Center with emails and phone numbers included
        import httpx
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"https://api.planningcenteronline.com/people/v2/people/{request.planning_center_person_id}",
                headers=sync_service.headers,
                params={"include": "emails,phone_numbers"}
            )
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Person not found in Planning Center"
                )
            
            response.raise_for_status()
            data = response.json()
            person_data = data.get("data")
            included = data.get("included", [])
            
            if not person_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Person data not found in Planning Center response"
                )
        
        # Process included emails and phone numbers and attach to person_data
        emails_by_id = {}
        phones_by_id = {}
        
        for item in included:
            item_type = item.get("type")
            item_id = item.get("id")
            attrs = item.get("attributes", {})
            
            if item_type == "Email":
                emails_by_id[item_id] = attrs.get("address", "")
            elif item_type == "PhoneNumber":
                phones_by_id[item_id] = attrs.get("number", "")
        
        # Attach emails and phone numbers to person attributes
        relationships = person_data.get("relationships", {})
        person_attrs = person_data.get("attributes", {})
        
        # Get email addresses
        email_data = relationships.get("emails", {}).get("data", [])
        emails = []
        for email_ref in email_data:
            email_id = email_ref.get("id")
            if email_id in emails_by_id:
                emails.append(emails_by_id[email_id])
        
        # Get phone numbers
        phone_data = relationships.get("phone_numbers", {}).get("data", [])
        phone_numbers = []
        for phone_ref in phone_data:
            phone_id = phone_ref.get("id")
            if phone_id in phones_by_id:
                phone_numbers.append(phones_by_id[phone_id])
        
        # Attach to person attributes for create_user_from_planning_center to use
        if emails:
            person_attrs["email"] = emails[0]  # Primary email
            person_attrs["emails"] = emails  # All emails
        if phone_numbers:
            person_attrs["phone_number"] = phone_numbers[0]  # Primary phone
            person_attrs["phone_numbers"] = phone_numbers  # All phone numbers
        
        # Create user from Planning Center person data
        user = user_service.create_user_from_planning_center(
            person_data,
            default_role=request.role,
            created_by=current_user["id"]
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user from Planning Center person"
            )
        
        return user
        
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Planning Center API error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching person from Planning Center: {e.response.status_code}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error importing user from Planning Center: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to import user from Planning Center: {str(e)}"
        )
