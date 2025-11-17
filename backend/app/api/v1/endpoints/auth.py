"""
Authentication endpoints
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.schemas.user import User
from app.services.user_service import UserService
from app.services.failed_login_service import FailedLoginService

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    import logging
    logger = logging.getLogger(__name__)
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        from app.core.security import verify_token
        
        # Log Authorization header for debugging
        auth_header = request.headers.get("Authorization")
        if auth_header:
            auth_preview = auth_header[:30] + "..." if len(auth_header) > 30 else auth_header
            logger.info(f"Authorization header received: {auth_preview} (length: {len(auth_header)})")
        else:
            logger.warning("No Authorization header found in request")
        
        # Log token info for debugging (first 20 chars only for security)
        token_preview = token[:20] + "..." if len(token) > 20 else token
        logger.info(f"Extracted token: {token_preview} (length: {len(token)})")
        
        user_id = verify_token(token)
        if user_id is None:
            logger.warning(f"Token validation failed: user_id is None")
            raise credentials_exception
        logger.info(f"Token validated successfully for user_id: {user_id}")
    except HTTPException:
        # Re-raise HTTP exceptions (like credentials_exception)
        raise
    except Exception as e:
        logger.error(f"Token validation exception: {type(e).__name__}: {str(e)}")
        raise credentials_exception

    user_service = UserService(db)
    user = user_service.get_user(user_id)
    if user is None:
        raise credentials_exception

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
    }


async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Get current active user"""
    if not current_user["is_active"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Dependency to check if user is admin
async def get_current_admin_user(current_user: dict = Depends(get_current_active_user)):
    """Get current admin user"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user


class LoginRequest(BaseModel):
    """Login request model"""

    username: str
    password: str


@router.post("/login")
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint with account lockout protection"""
    user_service = UserService(db)
    failed_login_service = FailedLoginService(db)

    # Check if account is locked
    is_locked, locked_until = failed_login_service.is_locked(login_data.username)
    if is_locked:
        remaining_minutes = int((locked_until - datetime.utcnow()).total_seconds() / 60) + 1
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked due to too many failed login attempts. Please try again in {remaining_minutes} minute(s).",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Try to find user by username first, then by email
    user = user_service.get_user_by_username(login_data.username)
    if not user:
        user = user_service.get_user_by_email(login_data.username)

    # Check if login failed
    if not user or not user_service.verify_password(
        login_data.password, user.hashed_password
    ):
        # Record failed attempt
        failed_login_service.record_failed_attempt(login_data.username)
        remaining_attempts = failed_login_service.get_remaining_attempts(login_data.username)
        
        # Check if account is now locked
        is_locked, locked_until = failed_login_service.is_locked(login_data.username)
        if is_locked:
            remaining_minutes = int((locked_until - datetime.utcnow()).total_seconds() / 60) + 1
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked due to too many failed login attempts. Please try again in {remaining_minutes} minute(s).",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        error_detail = "Incorrect username or password"
        if remaining_attempts > 0:
            error_detail += f". {remaining_attempts} attempt(s) remaining before account lockout."
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Successful login - clear failed attempts
    failed_login_service.clear_failed_attempts(login_data.username)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
        },
    }


@router.post("refresh")
@router.post("/refresh")
async def refresh_token(
    current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Refresh access token"""
    # Get full user info from database
    user_service = UserService(db)
    user = user_service.get_user(current_user["id"])
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
        },
    }
