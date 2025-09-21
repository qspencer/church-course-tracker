"""
Progress service layer
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.schemas.progress import ProgressCreate, ProgressUpdate
from app.models.progress import Progress as ProgressModel


class ProgressService:
    """Service for progress operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_member_progress(self, member_id: int) -> List[ProgressModel]:
        """Get progress for a specific member across all courses"""
        return self.db.query(ProgressModel).join(
            ProgressModel.enrollment
        ).filter(
            ProgressModel.enrollment.has(member_id=member_id)
        ).all()
    
    def get_course_progress(self, course_id: int) -> List[ProgressModel]:
        """Get progress for all members in a specific course"""
        return self.db.query(ProgressModel).join(
            ProgressModel.enrollment
        ).filter(
            ProgressModel.enrollment.has(course_id=course_id)
        ).all()
    
    def get_progress(self, progress_id: int) -> Optional[ProgressModel]:
        """Get a specific progress record by ID"""
        return self.db.query(ProgressModel).filter(
            ProgressModel.id == progress_id
        ).first()
    
    def create_progress(self, progress: ProgressCreate) -> ProgressModel:
        """Create a new progress record"""
        db_progress = ProgressModel(**progress.dict())
        db_progress.created_at = datetime.utcnow()
        db_progress.updated_at = datetime.utcnow()
        
        self.db.add(db_progress)
        self.db.commit()
        self.db.refresh(db_progress)
        return db_progress
    
    def update_progress(
        self, 
        progress_id: int, 
        progress_update: ProgressUpdate
    ) -> Optional[ProgressModel]:
        """Update an existing progress record"""
        db_progress = self.get_progress(progress_id)
        if not db_progress:
            return None
        
        update_data = progress_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_progress, field, value)
        
        db_progress.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_progress)
        return db_progress
    
    def delete_progress(self, progress_id: int) -> bool:
        """Delete a progress record"""
        db_progress = self.get_progress(progress_id)
        if not db_progress:
            return False
        
        self.db.delete(db_progress)
        self.db.commit()
        return True
