"""
User service layer
"""

from datetime import datetime, timezone
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

    def get_users(self, skip: int = 0, limit: int = 100, role: Optional[str] = None) -> List[UserModel]:
        """Get all users with pagination and optional role filtering"""
        query = self.db.query(UserModel)
        if role:
            query = query.filter(UserModel.role == role)
        return query.offset(skip).limit(limit).all()
    
    def get_instructors(self) -> List[UserModel]:
        """Get all users with instructor role"""
        return self.get_users(role="instructor", limit=1000)

    def get_user(self, user_id: int) -> Optional[UserModel]:
        """Get a specific user by ID"""
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get a user by email"""
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """Get a user by username"""
        return self.db.query(UserModel).filter(UserModel.username == username).first()
    
    def get_user_by_pc_person_id(self, pc_person_id: str) -> Optional[UserModel]:
        """Get a user by Planning Center person ID"""
        return (
            self.db.query(UserModel)
            .filter(UserModel.planning_center_person_id == pc_person_id)
            .first()
        )
    
    def create_user_from_planning_center(
        self, person_data: dict, default_role: str = "instructor", created_by: Optional[int] = None
    ) -> Optional[UserModel]:
        """
        Create a user from Planning Center person data
        
        Args:
            person_data: Planning Center person data dictionary
            default_role: Default role to assign (default: "instructor")
            created_by: User ID who created this
            
        Returns:
            Created UserModel or None if user already exists or creation failed
        """
        import secrets
        
        pc_person_id = person_data.get("id")
        if not pc_person_id:
            return None
        
        # Check if user already exists by PC person ID
        existing_user = self.get_user_by_pc_person_id(pc_person_id)
        if existing_user:
            # Update existing user with latest info
            attrs = person_data.get("attributes", {})
            existing_user.full_name = f"{attrs.get('first_name', '')} {attrs.get('last_name', '')}".strip()
            existing_user.email = attrs.get("email") or existing_user.email
            existing_user.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(existing_user)
            return existing_user
        
        # Extract person attributes
        attrs = person_data.get("attributes", {})
        email = attrs.get("email")
        first_name = attrs.get("first_name", "")
        last_name = attrs.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()
        
        if not email:
            # Skip people without email
            return None
        
        # Check if user exists by email
        existing_user = self.get_user_by_email(email)
        if existing_user:
            # Link PC person ID to existing user
            existing_user.planning_center_person_id = pc_person_id
            if not existing_user.full_name or existing_user.full_name == "":
                existing_user.full_name = full_name
            existing_user.updated_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(existing_user)
            return existing_user
        
        # Generate a random password (user will need to reset it)
        # Use token_urlsafe(32) which generates 32 random bytes = ~43 chars when base64 encoded
        # This is well under bcrypt's 72-byte limit
        random_password = secrets.token_urlsafe(32)
        
        # Truncate to 72 bytes if needed (safety check)
        password_bytes = random_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            random_password = password_bytes.decode('utf-8', errors='ignore')
        
        # Use direct bcrypt to avoid passlib compatibility issues
        import bcrypt
        hashed_password = bcrypt.hashpw(random_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create username from email if not provided
        username = email.split("@")[0] if email else None
        
        # Create new user
        db_user = UserModel(
            username=username,
            email=email,
            full_name=full_name,
            role=default_role,
            is_active=True,
            hashed_password=hashed_password,
            planning_center_person_id=pc_person_id,
            data_source="planning_center",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        try:
            self.db.add(db_user)
            self.db.flush()  # Get ID without committing

            # Log audit in same transaction
            AuditService(self.db).log_change(
                table_name=UserModel.__tablename__,
                record_id=db_user.id,
                action="insert",
                changed_by=created_by,
                new_values=AuditService.serialize_model(
                    db_user, exclude={"hashed_password"}
                ),
            )

            self.db.commit()  # Commit both together
            self.db.refresh(db_user)
            return db_user
        except IntegrityError as exc:
            self.db.rollback()
            logger.exception("Integrity error creating user from PC person '%s'", pc_person_id)
            return None
        except Exception as exc:
            self.db.rollback()
            logger.exception("Unexpected error creating user from PC person '%s'", pc_person_id)
            return None

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
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
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
            # Use direct bcrypt to avoid passlib compatibility issues
            import bcrypt
            password = update_data.pop("password")
            # Truncate password to 72 bytes (bcrypt limit) if needed
            if isinstance(password, str):
                password_bytes = password.encode('utf-8')
                if len(password_bytes) > 72:
                    password_bytes = password_bytes[:72]
                    password = password_bytes.decode('utf-8', errors='ignore')
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            update_data["hashed_password"] = hashed

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db_user.updated_at = datetime.now(timezone.utc)
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

        db_user.updated_at = datetime.now(timezone.utc)
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
