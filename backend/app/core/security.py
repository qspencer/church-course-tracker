"""
Security utilities for JWT tokens and password hashing
"""

import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[int]:
    """Verify JWT token and return user ID"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token payload missing 'sub' field")
            return None
        return int(user_id)
    except JWTError as e:
        logger.warning(f"JWT validation error: {type(e).__name__}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error verifying token: {type(e).__name__}: {str(e)}")
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash

    Only supports bcrypt hashes. SHA256 fallback has been removed for security.
    Users with SHA256 hashes must reset their password.
    """
    import logging
    logger = logging.getLogger(__name__)

    # Only accept bcrypt hashes - reject SHA256 and other formats
    if not (hashed_password.startswith("$2b$") or
            hashed_password.startswith("$2a$") or
            hashed_password.startswith("$2y$")):
        # Not a bcrypt hash - log warning and require password reset
        logger.warning("Password hash is not bcrypt format - user must reset password")
        return False

    try:
        # Ensure hashed_password is bytes for bcrypt
        if isinstance(hashed_password, str):
            hashed_password_bytes = hashed_password.encode('utf-8')
        else:
            hashed_password_bytes = hashed_password

        # Truncate password to 72 bytes (bcrypt limitation)
        password_bytes = plain_password.encode('utf-8')[:72]
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)
    except (ValueError, AttributeError, Exception) as e:
        logger.warning(f"Password verification failed: {type(e).__name__}: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    # Truncate password to 72 bytes (bcrypt limitation)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"

    return True, "Password is strong"


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    import secrets

    return secrets.token_urlsafe(length)


def validate_file_type(file_content: bytes, filename: str) -> bool:
    """Validate file type based on content and filename"""
    import mimetypes

    # Get MIME type from filename
    mime_type, _ = mimetypes.guess_type(filename)

    if mime_type not in settings.ALLOWED_FILE_TYPES:
        return False

    # Additional content-based validation could be added here
    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal attacks"""
    import os
    import re

    # Remove path components
    filename = os.path.basename(filename)

    # Remove dangerous characters
    filename = re.sub(r"[^\w\-_\.]", "", filename)

    # Limit length
    filename = filename[:255]

    return filename
