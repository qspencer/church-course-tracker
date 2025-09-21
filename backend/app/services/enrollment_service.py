"""
CourseEnrollment service layer (Maps to Planning Center Registrations)
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.schemas.enrollment import CourseEnrollmentCreate, CourseEnrollmentUpdate
from app.models.enrollment import CourseEnrollment as CourseEnrollmentModel


class CourseEnrollmentService:
    """Service for course enrollment operations - Maps to Planning Center Registrations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_enrollments(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        course_id: Optional[int] = None,
        people_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[CourseEnrollmentModel]:
        """Get enrollments with optional filtering"""
        query = self.db.query(CourseEnrollmentModel)
        
        if course_id:
            query = query.filter(CourseEnrollmentModel.course_id == course_id)
        if people_id:
            query = query.filter(CourseEnrollmentModel.people_id == people_id)
        if status:
            query = query.filter(CourseEnrollmentModel.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    def get_enrollment(self, enrollment_id: int) -> Optional[CourseEnrollmentModel]:
        """Get a specific enrollment by ID"""
        return self.db.query(CourseEnrollmentModel).filter(
            CourseEnrollmentModel.id == enrollment_id
        ).first()
    
    def get_enrollment_by_pc_registration_id(self, pc_registration_id: str) -> Optional[CourseEnrollmentModel]:
        """Get enrollment by Planning Center registration ID"""
        return self.db.query(CourseEnrollmentModel).filter(
            CourseEnrollmentModel.planning_center_registration_id == pc_registration_id
        ).first()
    
    def create_enrollment(self, enrollment: CourseEnrollmentCreate, created_by: Optional[int] = None) -> CourseEnrollmentModel:
        """Create a new enrollment"""
        db_enrollment = CourseEnrollmentModel(**enrollment.dict())
        db_enrollment.created_at = datetime.utcnow()
        db_enrollment.updated_at = datetime.utcnow()
        db_enrollment.created_by = created_by
        
        self.db.add(db_enrollment)
        self.db.commit()
        self.db.refresh(db_enrollment)
        return db_enrollment
    
    def bulk_enroll(self, course_id: int, people_ids: List[int], created_by: Optional[int] = None) -> List[CourseEnrollmentModel]:
        """Bulk enroll multiple people in a course"""
        enrollments = []
        for people_id in people_ids:
            enrollment_data = CourseEnrollmentCreate(
                course_id=course_id,
                people_id=people_id,
                enrollment_date=datetime.utcnow()
            )
            enrollment = self.create_enrollment(enrollment_data, created_by=created_by)
            enrollments.append(enrollment)
        return enrollments
    
    def update_enrollment(
        self, 
        enrollment_id: int, 
        enrollment_update: CourseEnrollmentUpdate,
        updated_by: Optional[int] = None
    ) -> Optional[CourseEnrollmentModel]:
        """Update an existing enrollment"""
        db_enrollment = self.get_enrollment(enrollment_id)
        if not db_enrollment:
            return None
        
        update_data = enrollment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_enrollment, field, value)
        
        db_enrollment.updated_at = datetime.utcnow()
        db_enrollment.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_enrollment)
        return db_enrollment
    
    def delete_enrollment(self, enrollment_id: int) -> bool:
        """Delete an enrollment"""
        db_enrollment = self.get_enrollment(enrollment_id)
        if not db_enrollment:
            return False
        
        self.db.delete(db_enrollment)
        self.db.commit()
        return True
    
    def sync_from_planning_center(self, pc_registration_data: dict, updated_by: Optional[int] = None) -> CourseEnrollmentModel:
        """Sync enrollment data from Planning Center registration"""
        pc_registration_id = pc_registration_data.get("id")
        
        # Check if enrollment already exists
        existing_enrollment = self.get_enrollment_by_pc_registration_id(pc_registration_id)
        
        if existing_enrollment:
            # Update existing enrollment
            existing_enrollment.registration_status = pc_registration_data.get("status")
            existing_enrollment.registration_notes = pc_registration_data.get("notes")
            existing_enrollment.updated_at = datetime.utcnow()
            existing_enrollment.updated_by = updated_by
            self.db.commit()
            self.db.refresh(existing_enrollment)
            return existing_enrollment
        else:
            # Create new enrollment (requires people_id and course_id to be resolved)
            # This would typically be called after people and courses are synced
            enrollment_data = CourseEnrollmentCreate(
                people_id=0,  # This would need to be resolved from PC person ID
                course_id=0,  # This would need to be resolved from PC event ID
                planning_center_registration_id=pc_registration_id,
                registration_status=pc_registration_data.get("status"),
                registration_notes=pc_registration_data.get("notes"),
                enrollment_date=pc_registration_data.get("created_at", datetime.utcnow())
            )
            return self.create_enrollment(enrollment_data, created_by=updated_by)
    
    def update_progress(self, enrollment_id: int, progress_percentage: float, updated_by: Optional[int] = None) -> Optional[CourseEnrollmentModel]:
        """Update enrollment progress percentage"""
        db_enrollment = self.get_enrollment(enrollment_id)
        if not db_enrollment:
            return None
        
        db_enrollment.progress_percentage = progress_percentage
        if progress_percentage >= 100.0:
            db_enrollment.status = "completed"
            db_enrollment.completion_date = datetime.utcnow()
        
        db_enrollment.updated_at = datetime.utcnow()
        db_enrollment.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_enrollment)
        return db_enrollment
