"""
User service layer
"""

from datetime import datetime
from typing import List, Optional
import logging

from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate, UserProfileUpdate
from app.services.audit_service import AuditService

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


class UserService:
    """Service for user operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        """Get all users with pagination"""
        return self.db.query(UserModel).offset(skip).limit(limit).all()

    def get_user(self, user_id: int) -> Optional[UserModel]:
        """Get a specific user by ID"""
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get a user by email"""
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """Get a user by username"""
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def create_user(
        self, user: UserCreate, created_by: Optional[int] = None
    ) -> UserModel:
        """Create a new user"""
        # Hash the password
        hashed_password = pwd_context.hash(user.password)

        db_user = UserModel(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            AuditService(self.db).log_change(
                table_name=UserModel.__tablename__,
                record_id=db_user.id,
                action="insert",
                changed_by=created_by,
                new_values=AuditService.serialize_model(
                    db_user, exclude={"hashed_password"}
                ),
            )
            return db_user
        except IntegrityError as exc:
            self.db.rollback()
            logger.exception("Integrity error creating user '%s'", user.username)
            raise
        except Exception as exc:
            self.db.rollback()
            logger.exception("Unexpected error creating user '%s'", user.username)
            raise

    def update_user(
        self,
        user_id: int,
        user_update: UserUpdate,
        updated_by: Optional[int] = None,
    ) -> Optional[UserModel]:
        """Update an existing user"""
        db_user = self.get_user(user_id)
        if not db_user:
            return None

        old_values = AuditService.serialize_model(db_user, exclude={"hashed_password"})
        update_data = user_update.dict(exclude_unset=True)

        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = pwd_context.hash(
                update_data.pop("password")
            )

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db_user.updated_at = datetime.utcnow()
        try:
            self.db.commit()
            self.db.refresh(db_user)
            AuditService(self.db).log_change(
                table_name=UserModel.__tablename__,
                record_id=db_user.id,
                action="update",
                changed_by=updated_by,
                old_values=old_values,
                new_values=AuditService.serialize_model(
                    db_user, exclude={"hashed_password"}
                ),
            )
            return db_user
        except IntegrityError as exc:
            self.db.rollback()
            logger.exception("Integrity error updating user id=%s", user_id)
            raise
        except Exception as exc:
            self.db.rollback()
            logger.exception("Unexpected error updating user id=%s", user_id)
            raise

    def delete_user(self, user_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete a user"""
        db_user = self.get_user(user_id)
        if not db_user:
            return False
        old_values = AuditService.serialize_model(db_user, exclude={"hashed_password"})
        record_id = db_user.id

        self.db.delete(db_user)
        self.db.commit()
        AuditService(self.db).log_change(
            table_name=UserModel.__tablename__,
            record_id=record_id,
            action="delete",
            changed_by=deleted_by,
            old_values=old_values,
        )
        return True

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        from app.core.security import verify_password

        return verify_password(plain_password, hashed_password)

    def update_current_user(
        self,
        user_id: int,
        user_update: "UserProfileUpdate",
        updated_by: Optional[int] = None,
    ) -> Optional[UserModel]:
        """Update current user's own profile (excludes role and is_active)"""
        db_user = self.get_user(user_id)
        if not db_user:
            return None

        old_values = AuditService.serialize_model(db_user, exclude={"hashed_password"})
        update_data = user_update.dict(exclude_unset=True)

        # Ensure user can't update role or is_active through this method
        update_data.pop("role", None)
        update_data.pop("is_active", None)

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db_user.updated_at = datetime.utcnow()
        try:
            self.db.commit()
            self.db.refresh(db_user)
            AuditService(self.db).log_change(
                table_name=UserModel.__tablename__,
                record_id=db_user.id,
                action="update",
                changed_by=updated_by or user_id,  # Use user_id if updated_by not provided
                old_values=old_values,
                new_values=AuditService.serialize_model(
                    db_user, exclude={"hashed_password"}
                ),
            )
            return db_user
        except IntegrityError as exc:
            self.db.rollback()
            logger.exception("Integrity error updating user profile id=%s", user_id)
            raise
        except Exception as exc:
            self.db.rollback()
            logger.exception("Unexpected error updating user profile id=%s", user_id)
            raise
