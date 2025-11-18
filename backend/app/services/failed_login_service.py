"""
Service for managing failed login attempts and account lockout
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

from sqlalchemy.orm import Session

from app.models.failed_login_attempt import FailedLoginAttempt as FailedLoginAttemptModel

logger = logging.getLogger(__name__)

# Lockout configuration
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


class FailedLoginService:
    """Service for managing failed login attempts"""

    def __init__(self, db: Session):
        self.db = db

    def record_failed_attempt(self, username_or_email: str) -> Optional[FailedLoginAttemptModel]:
        """Record a failed login attempt"""
        try:
            attempt = (
                self.db.query(FailedLoginAttemptModel)
                .filter(FailedLoginAttemptModel.username_or_email == username_or_email)
                .first()
            )

            if attempt:
                # Update existing attempt
                attempt.attempt_count += 1
                attempt.last_attempt_time = datetime.utcnow()
                attempt.updated_at = datetime.utcnow()

                # Lock account if max attempts reached
                if attempt.attempt_count >= MAX_FAILED_ATTEMPTS:
                    attempt.locked_until = datetime.utcnow() + timedelta(
                        minutes=LOCKOUT_DURATION_MINUTES
                    )
                    logger.warning(
                        f"Account locked for {username_or_email} after {attempt.attempt_count} failed attempts"
                    )
            else:
                # Create new attempt record
                attempt = FailedLoginAttemptModel(
                    username_or_email=username_or_email,
                    attempt_count=1,
                    last_attempt_time=datetime.utcnow(),
                )
                self.db.add(attempt)

            self.db.commit()
            self.db.refresh(attempt)
            return attempt
        except Exception as e:
            # If there's a database error (e.g., table doesn't exist), log it and return None
            # This allows the login endpoint to still return 401 instead of 500
            logger.warning(f"Error recording failed login attempt for {username_or_email}: {e}", exc_info=True)
            self.db.rollback()
            return None

    def clear_failed_attempts(self, username_or_email: str) -> None:
        """Clear failed login attempts after successful login"""
        attempt = (
            self.db.query(FailedLoginAttemptModel)
            .filter(FailedLoginAttemptModel.username_or_email == username_or_email)
            .first()
        )

        if attempt:
            self.db.delete(attempt)
            self.db.commit()

    def is_locked(self, username_or_email: str) -> Tuple[bool, Optional[datetime]]:
        """
        Check if account is locked
        Returns: (is_locked, locked_until)
        """
        try:
            attempt = (
                self.db.query(FailedLoginAttemptModel)
                .filter(FailedLoginAttemptModel.username_or_email == username_or_email)
                .first()
            )

            if not attempt or not attempt.locked_until:
                return False, None

            # Check if lockout has expired
            if attempt.locked_until <= datetime.utcnow():
                # Lockout expired, clear it
                try:
                    self.db.delete(attempt)
                    self.db.commit()
                except Exception as e:
                    logger.warning(f"Error clearing expired lockout: {e}", exc_info=True)
                    self.db.rollback()
                return False, None

            return True, attempt.locked_until
        except Exception as e:
            # If there's a database error, assume account is not locked
            logger.warning(f"Error checking lockout status for {username_or_email}: {e}", exc_info=True)
            return False, None

    def get_remaining_attempts(self, username_or_email: str) -> int:
        """Get remaining login attempts before lockout"""
        try:
            attempt = (
                self.db.query(FailedLoginAttemptModel)
                .filter(FailedLoginAttemptModel.username_or_email == username_or_email)
                .first()
            )

            if not attempt:
                return MAX_FAILED_ATTEMPTS

            if attempt.locked_until and attempt.locked_until > datetime.utcnow():
                return 0  # Account is locked

            return max(0, MAX_FAILED_ATTEMPTS - attempt.attempt_count)
        except Exception as e:
            # If there's a database error, return max attempts (assume no lockout)
            logger.warning(f"Error getting remaining attempts for {username_or_email}: {e}", exc_info=True)
            return MAX_FAILED_ATTEMPTS

