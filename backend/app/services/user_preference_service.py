"""
Service for managing user preferences
"""

from datetime import datetime, timezone
from typing import Optional
import logging

from sqlalchemy.orm import Session

from app.models.user_preference import UserPreference as UserPreferenceModel
from app.schemas.user_preference import UserPreferenceUpdate

logger = logging.getLogger(__name__)


class UserPreferenceService:
    """Service for managing user preferences"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_preferences(self, user_id: int) -> Optional[UserPreferenceModel]:
        """Get user preferences, creating default if they don't exist"""
        preferences = (
            self.db.query(UserPreferenceModel)
            .filter(UserPreferenceModel.user_id == user_id)
            .first()
        )
        
        if not preferences:
            # Create default preferences
            preferences = UserPreferenceModel(
                user_id=user_id,
                email_notifications=True,
                course_updates=True,
                system_announcements=True,
            )
            self.db.add(preferences)
            self.db.commit()
            self.db.refresh(preferences)
        
        return preferences

    def update_user_preferences(
        self, user_id: int, preferences_update: UserPreferenceUpdate
    ) -> UserPreferenceModel:
        """Update user preferences"""
        preferences = self.get_user_preferences(user_id)
        
        update_data = preferences_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preferences, field, value)
        
        preferences.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(preferences)
        
        return preferences

