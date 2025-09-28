"""
User service layer
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from passlib.context import CryptContext

from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User as UserModel

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    
    def create_user(self, user: UserCreate) -> UserModel:
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
            updated_at=datetime.utcnow()
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserModel]:
        """Update an existing user"""
        db_user = self.get_user(user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        db_user = self.get_user(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        from app.core.security import verify_password
        return verify_password(plain_password, hashed_password)
