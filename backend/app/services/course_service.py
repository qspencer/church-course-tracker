"""
Course service layer (Maps to Planning Center Events)
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.schemas.course import CourseCreate, CourseUpdate
from app.models.course import Course as CourseModel


class CourseService:
    """Service for course operations - Maps to Planning Center Events"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_courses(self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[CourseModel]:
        """Get all courses with pagination and optional filtering"""
        query = self.db.query(CourseModel)
        if is_active is not None:
            query = query.filter(CourseModel.is_active == is_active)
        return query.offset(skip).limit(limit).all()
    
    def get_course(self, course_id: int) -> Optional[CourseModel]:
        """Get a specific course by ID"""
        return self.db.query(CourseModel).filter(CourseModel.id == course_id).first()
    
    def get_course_by_pc_event_id(self, pc_event_id: str) -> Optional[CourseModel]:
        """Get a course by Planning Center event ID"""
        return self.db.query(CourseModel).filter(
            CourseModel.planning_center_event_id == pc_event_id
        ).first()
    
    def create_course(self, course: CourseCreate, created_by: Optional[int] = None) -> CourseModel:
        """Create a new course"""
        db_course = CourseModel(**course.dict())
        db_course.created_at = datetime.utcnow()
        db_course.updated_at = datetime.utcnow()
        db_course.created_by = created_by
        
        self.db.add(db_course)
        self.db.commit()
        self.db.refresh(db_course)
        return db_course
    
    def update_course(self, course_id: int, course_update: CourseUpdate, updated_by: Optional[int] = None) -> Optional[CourseModel]:
        """Update an existing course"""
        db_course = self.get_course(course_id)
        if not db_course:
            return None
        
        update_data = course_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_course, field, value)
        
        db_course.updated_at = datetime.utcnow()
        db_course.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_course)
        return db_course
    
    def delete_course(self, course_id: int) -> bool:
        """Delete a course"""
        db_course = self.get_course(course_id)
        if not db_course:
            return False
        
        self.db.delete(db_course)
        self.db.commit()
        return True
    
    def sync_from_planning_center(self, pc_event_data: dict, updated_by: Optional[int] = None) -> CourseModel:
        """Sync course data from Planning Center event"""
        pc_event_id = pc_event_data.get("id")
        
        # Check if course already exists
        existing_course = self.get_course_by_pc_event_id(pc_event_id)
        
        if existing_course:
            # Update existing course
            existing_course.planning_center_event_name = pc_event_data.get("name")
            existing_course.event_start_date = pc_event_data.get("start_date")
            existing_course.event_end_date = pc_event_data.get("end_date")
            existing_course.max_capacity = pc_event_data.get("max_capacity")
            existing_course.current_registrations = pc_event_data.get("current_registrations", 0)
            existing_course.updated_at = datetime.utcnow()
            existing_course.updated_by = updated_by
            self.db.commit()
            self.db.refresh(existing_course)
            return existing_course
        else:
            # Create new course
            course_data = CourseCreate(
                name=pc_event_data.get("name", "Unknown Course"),
                description=pc_event_data.get("description"),
                planning_center_event_id=pc_event_id,
                planning_center_event_name=pc_event_data.get("name"),
                event_start_date=pc_event_data.get("start_date"),
                event_end_date=pc_event_data.get("end_date"),
                max_capacity=pc_event_data.get("max_capacity"),
                current_registrations=pc_event_data.get("current_registrations", 0)
            )
            return self.create_course(course_data, created_by=updated_by)
