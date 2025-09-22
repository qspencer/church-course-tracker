"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.config import settings
from app.schemas.user import User
from app.services.user_service import UserService
from app.core.security import create_access_token, verify_password

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        from app.core.security import verify_token
        user_id = verify_token(token)
        if user_id is None:
            raise credentials_exception
    except Exception:
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
        "is_active": user.is_active
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
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


@router.post("/login")
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login endpoint"""
    user_service = UserService(db)
    
    # Try to find user by username first, then by email
    user = user_service.get_user_by_username(login_data.username)
    if not user:
        user = user_service.get_user_by_email(login_data.username)
    
    if not user or not user_service.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
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
            "is_active": user.is_active
        }
    }


@router.post("/refresh")
async def refresh_token(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user["id"])}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
