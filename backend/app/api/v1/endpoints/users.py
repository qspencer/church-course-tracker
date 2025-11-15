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
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


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
