"""
User preferences model
"""

from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserPreference(Base):
    """Model for user notification preferences"""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True, nullable=False)
    course_updates = Column(Boolean, default=True, nullable=False)
    system_announcements = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

