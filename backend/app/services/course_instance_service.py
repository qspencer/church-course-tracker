"""
CourseInstance service layer (Course Offerings)
Manages Course Instances and Course Instance Teachers
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.course_instance import CourseInstance as CourseInstanceModel
from app.models.course_instance import CourseInstanceTeacher as CourseInstanceTeacherModel
from app.schemas.course_instance import (
    CourseInstanceCreate,
    CourseInstanceUpdate,
    CourseInstanceTeacherCreate,
    CourseInstanceTeacherUpdate,
)
from app.services.audit_service import AuditService


class CourseInstanceService:
    """Service for course instance operations (Course Offerings)"""

    def __init__(self, db: Session):
        self.db = db

    def get_course_instances(
        self,
        course_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[CourseInstanceModel]:
        """Get course instances with optional filtering"""
        query = self.db.query(CourseInstanceModel).options(
            joinedload(CourseInstanceModel.course),
            joinedload(CourseInstanceModel.campus),
            joinedload(CourseInstanceModel.created_by_user),
            joinedload(CourseInstanceModel.updated_by_user),
        )

        if course_id:
            query = query.filter(CourseInstanceModel.course_id == course_id)
        if is_active is not None:
            query = query.filter(CourseInstanceModel.is_active == is_active)

        return query.offset(skip).limit(limit).all()

    def get_course_instance(self, instance_id: int) -> Optional[CourseInstanceModel]:
        """Get a specific course instance by ID"""
        return (
            self.db.query(CourseInstanceModel)
            .options(
                joinedload(CourseInstanceModel.course),
                joinedload(CourseInstanceModel.campus),
                joinedload(CourseInstanceModel.teachers).joinedload(
                    CourseInstanceTeacherModel.people
                ),
                joinedload(CourseInstanceModel.created_by_user),
                joinedload(CourseInstanceModel.updated_by_user),
            )
            .filter(CourseInstanceModel.id == instance_id)
            .first()
        )

    def get_course_instance_by_pc_event_id(
        self, pc_event_id: str
    ) -> Optional[CourseInstanceModel]:
        """Get a course instance by Planning Center event ID"""
        return (
            self.db.query(CourseInstanceModel)
            .options(
                joinedload(CourseInstanceModel.course),
                joinedload(CourseInstanceModel.campus),
            )
            .filter(CourseInstanceModel.planning_center_event_id == pc_event_id)
            .first()
        )

    def create_course_instance(
        self, instance: CourseInstanceCreate, created_by: Optional[int] = None
    ) -> CourseInstanceModel:
        """Create a new course instance (Course Offering)"""
        db_instance = CourseInstanceModel(**instance.model_dump())
        db_instance.created_at = datetime.now(timezone.utc)
        db_instance.updated_at = datetime.now(timezone.utc)
        db_instance.created_by = created_by

        self.db.add(db_instance)
        self.db.commit()
        self.db.refresh(db_instance)
        AuditService(self.db).log_change(
            table_name=CourseInstanceModel.__tablename__,
            record_id=db_instance.id,
            action="insert",
            changed_by=created_by,
            new_values=AuditService.serialize_model(db_instance),
        )

        # Query again with relationships
        return self.get_course_instance(db_instance.id)

    def update_course_instance(
        self,
        instance_id: int,
        instance_update: CourseInstanceUpdate,
        updated_by: Optional[int] = None,
    ) -> Optional[CourseInstanceModel]:
        """Update an existing course instance"""
        db_instance = self.get_course_instance(instance_id)
        if not db_instance:
            return None

        old_values = AuditService.serialize_model(db_instance)
        update_data = instance_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_instance, field, value)

        db_instance.updated_at = datetime.now(timezone.utc)
        db_instance.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_instance)
        AuditService(self.db).log_change(
            table_name=CourseInstanceModel.__tablename__,
            record_id=db_instance.id,
            action="update",
            changed_by=updated_by,
            old_values=old_values,
            new_values=AuditService.serialize_model(db_instance),
        )

        return self.get_course_instance(instance_id)

    def delete_course_instance(
        self, instance_id: int, deleted_by: Optional[int] = None
    ) -> bool:
        """Delete a course instance"""
        db_instance = self.get_course_instance(instance_id)
        if not db_instance:
            return False

        old_values = AuditService.serialize_model(db_instance)
        record_id = db_instance.id

        self.db.delete(db_instance)
        self.db.commit()
        AuditService(self.db).log_change(
            table_name=CourseInstanceModel.__tablename__,
            record_id=record_id,
            action="delete",
            changed_by=deleted_by,
            old_values=old_values,
        )
        return True

    def add_teacher(
        self,
        instance_id: int,
        teacher: CourseInstanceTeacherCreate,
        created_by: Optional[int] = None,
    ) -> CourseInstanceTeacherModel:
        """Add a teacher to a course instance"""
        db_teacher = CourseInstanceTeacherModel(**teacher.model_dump())
        db_teacher.course_instance_id = instance_id
        db_teacher.created_at = datetime.now(timezone.utc)
        db_teacher.updated_at = datetime.now(timezone.utc)
        db_teacher.created_by = created_by

        self.db.add(db_teacher)
        self.db.commit()
        self.db.refresh(db_teacher)
        AuditService(self.db).log_change(
            table_name=CourseInstanceTeacherModel.__tablename__,
            record_id=db_teacher.id,
            action="insert",
            changed_by=created_by,
            new_values=AuditService.serialize_model(db_teacher),
        )
        return db_teacher

    def remove_teacher(
        self, teacher_id: int, deleted_by: Optional[int] = None
    ) -> bool:
        """Remove a teacher from a course instance"""
        db_teacher = (
            self.db.query(CourseInstanceTeacherModel)
            .filter(CourseInstanceTeacherModel.id == teacher_id)
            .first()
        )
        if not db_teacher:
            return False

        old_values = AuditService.serialize_model(db_teacher)
        record_id = db_teacher.id

        self.db.delete(db_teacher)
        self.db.commit()
        AuditService(self.db).log_change(
            table_name=CourseInstanceTeacherModel.__tablename__,
            record_id=record_id,
            action="delete",
            changed_by=deleted_by,
            old_values=old_values,
        )
        return True

    def get_instance_teachers(
        self, instance_id: int, is_active: Optional[bool] = None
    ) -> List[CourseInstanceTeacherModel]:
        """Get all teachers for a course instance"""
        query = (
            self.db.query(CourseInstanceTeacherModel)
            .options(joinedload(CourseInstanceTeacherModel.people))
            .filter(CourseInstanceTeacherModel.course_instance_id == instance_id)
        )

        if is_active is not None:
            query = query.filter(CourseInstanceTeacherModel.is_active == is_active)

        return query.all()

    def assign_student_to_teacher(
        self, enrollment_id: int, teacher_id: int, updated_by: Optional[int] = None
    ) -> bool:
        """Assign a student (enrollment) to a specific teacher for discipleship tracking"""
        from app.models.enrollment import CourseEnrollment as CourseEnrollmentModel

        enrollment = (
            self.db.query(CourseEnrollmentModel)
            .filter(CourseEnrollmentModel.id == enrollment_id)
            .first()
        )
        if not enrollment:
            return False

        # Verify teacher exists and is for the same course instance
        teacher = (
            self.db.query(CourseInstanceTeacherModel)
            .filter(
                CourseInstanceTeacherModel.id == teacher_id,
                CourseInstanceTeacherModel.course_instance_id == enrollment.course_instance_id,
                CourseInstanceTeacherModel.is_active == True,
            )
            .first()
        )
        if not teacher:
            return False

        enrollment.assigned_teacher_id = teacher_id
        enrollment.updated_at = datetime.now(timezone.utc)
        enrollment.updated_by = updated_by
        self.db.commit()

        AuditService(self.db).log_change(
            table_name=CourseEnrollmentModel.__tablename__,
            record_id=enrollment_id,
            action="update",
            changed_by=updated_by,
            old_values={"assigned_teacher_id": None},
            new_values={"assigned_teacher_id": teacher_id},
        )
        return True

