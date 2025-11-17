"""
Failed login attempt model for account lockout
"""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


class FailedLoginAttempt(Base):
    """Model for tracking failed login attempts"""

    __tablename__ = "failed_login_attempts"

    id = Column(Integer, primary_key=True, index=True)
    username_or_email = Column(String(255), nullable=False, index=True)
    attempt_count = Column(Integer, default=1, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    last_attempt_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

