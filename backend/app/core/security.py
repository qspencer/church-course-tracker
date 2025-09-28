"""
Security utilities for JWT tokens and password hashing
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[int]:
    """Verify JWT token and return user ID"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Handle both bcrypt and simple SHA256 hashes
    try:
        # Try bcrypt first (for regular users)
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, AttributeError, Exception):
        # Fall back to simple SHA256 for admin user
        import hashlib
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)
