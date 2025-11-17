"""
Course service layer (Maps to Planning Center Events)
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.course import Course as CourseModel
from app.models.enrollment import CourseEnrollment as EnrollmentModel
from app.schemas.course import CourseCreate, CourseUpdate
from app.services.audit_service import AuditService


class CourseService:
    """Service for course operations - Maps to Planning Center Events"""

    def __init__(self, db: Session):
        self.db = db

    def get_courses(
        self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
    ) -> List[CourseModel]:
        """Get all courses with pagination and optional filtering"""
        try:
            query = self.db.query(CourseModel)
            if is_active is not None:
                query = query.filter(CourseModel.is_active == is_active)
            # Use options to prevent eager loading of relationships that might cause issues
            # But load user relationships for created_by and updated_by
            from sqlalchemy.orm import noload, joinedload

            return (
                query.options(
                    joinedload(CourseModel.created_by_user),
                    joinedload(CourseModel.updated_by_user),
                    noload(CourseModel.course_enrollments),
                    noload(CourseModel.content),
                    noload(CourseModel.course_content),
                    noload(CourseModel.modules),
                    noload(CourseModel.course_role),
                    noload(CourseModel.certification_courses),
                )
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            # Log the error and return empty list if there's a database issue
            import logging

            logging.error(f"Error fetching courses: {e}")
            return []

    def get_course(self, course_id: int) -> Optional[CourseModel]:
        """Get a specific course by ID"""
        from sqlalchemy.orm import joinedload
        return (
            self.db.query(CourseModel)
            .options(
                joinedload(CourseModel.created_by_user),
                joinedload(CourseModel.updated_by_user),
            )
            .filter(CourseModel.id == course_id)
            .first()
        )

    def get_course_by_pc_event_id(self, pc_event_id: str) -> Optional[CourseModel]:
        """Get a course by Planning Center event ID"""
        from sqlalchemy.orm import joinedload
        return (
            self.db.query(CourseModel)
            .options(
                joinedload(CourseModel.created_by_user),
                joinedload(CourseModel.updated_by_user),
            )
            .filter(CourseModel.planning_center_event_id == pc_event_id)
            .first()
        )

    def _validate_prerequisites(
        self, prerequisites: Optional[List[int]], course_id: Optional[int] = None
    ) -> None:
        """Validate prerequisites: check they exist and prevent circular dependencies"""
        if not prerequisites:
            return

        # Remove duplicates
        prerequisites = list(set(prerequisites))

        # Check that all prerequisite courses exist
        existing_courses = (
            self.db.query(CourseModel.id)
            .filter(CourseModel.id.in_(prerequisites))
            .all()
        )
        existing_ids = {course.id for course in existing_courses}
        missing_ids = set(prerequisites) - existing_ids

        if missing_ids:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Prerequisite courses not found: {list(missing_ids)}",
            )

        # Prevent self-reference
        if course_id and course_id in prerequisites:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A course cannot be a prerequisite for itself",
            )

        # Check for circular dependencies (if updating)
        if course_id:
            self._check_circular_dependencies(course_id, prerequisites)

    def _check_circular_dependencies(
        self, course_id: int, prerequisites: List[int]
    ) -> None:
        """Check for circular dependencies in prerequisites"""
        visited = set()
        to_check = list(prerequisites)

        while to_check:
            prereq_id = to_check.pop()
            if prereq_id in visited:
                continue
            visited.add(prereq_id)

            # If this prerequisite course has the current course as a prerequisite, it's circular
            if prereq_id == course_id:
                from fastapi import HTTPException, status

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Circular dependency detected in prerequisites",
                )

            # Check if this prerequisite course has prerequisites
            prereq_course = self.get_course(prereq_id)
            if prereq_course and prereq_course.prerequisites:
                # Add this course's prerequisites to check list
                if isinstance(prereq_course.prerequisites, list):
                    to_check.extend(prereq_course.prerequisites)

    def create_course(
        self, course: CourseCreate, created_by: Optional[int] = None
    ) -> CourseModel:
        """Create a new course"""
        # Validate prerequisites
        self._validate_prerequisites(course.prerequisites)

        db_course = CourseModel(**course.model_dump())
        db_course.created_at = datetime.now(timezone.utc)
        db_course.updated_at = datetime.now(timezone.utc)
        db_course.created_by = created_by

        self.db.add(db_course)
        self.db.commit()
        self.db.refresh(db_course)
        AuditService(self.db).log_change(
            table_name=CourseModel.__tablename__,
            record_id=db_course.id,
            action="insert",
            changed_by=created_by,
            new_values=AuditService.serialize_model(db_course),
        )
        
        # Query again with user relationships to ensure they're loaded
        from sqlalchemy.orm import joinedload
        return self.get_course(db_course.id)

    def update_course(
        self,
        course_id: int,
        course_update: CourseUpdate,
        updated_by: Optional[int] = None,
    ) -> Optional[CourseModel]:
        """Update an existing course"""
        db_course = self.get_course(course_id)
        if not db_course:
            return None

        # Validate prerequisites if they're being updated
        if "prerequisites" in course_update.model_dump(exclude_unset=True):
            self._validate_prerequisites(course_update.prerequisites, course_id)

        old_values = AuditService.serialize_model(db_course)
        update_data = course_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_course, field, value)

        db_course.updated_at = datetime.now(timezone.utc)
        db_course.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_course)
        AuditService(self.db).log_change(
            table_name=CourseModel.__tablename__,
            record_id=db_course.id,
            action="update",
            changed_by=updated_by,
            old_values=old_values,
            new_values=AuditService.serialize_model(db_course),
        )
        
        # Query again with user relationships to ensure they're loaded
        return self.get_course(course_id)

    def delete_course(self, course_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete a course"""
        db_course = self.get_course(course_id)
        if not db_course:
            return False
        old_values = AuditService.serialize_model(db_course)
        record_id = db_course.id

        self.db.delete(db_course)
        self.db.commit()
        AuditService(self.db).log_change(
            table_name=CourseModel.__tablename__,
            record_id=record_id,
            action="delete",
            changed_by=deleted_by,
            old_values=old_values,
        )
        return True

    def sync_from_planning_center(
        self, pc_event_data: dict, updated_by: Optional[int] = None
    ) -> CourseModel:
        """Sync course data from Planning Center event"""
        pc_event_id = pc_event_data.get("id")

        # Check if course already exists
        existing_course = self.get_course_by_pc_event_id(pc_event_id)

        if existing_course:
            # Update existing course
            existing_course.title = pc_event_data.get(
                "title", pc_event_data.get("name", existing_course.title)
            )
            existing_course.description = pc_event_data.get(
                "description", existing_course.description
            )
            existing_course.planning_center_event_name = pc_event_data.get("name")
            existing_course.event_start_date = pc_event_data.get("start_date")
            existing_course.event_end_date = pc_event_data.get("end_date")
            existing_course.max_capacity = pc_event_data.get("max_capacity")
            existing_course.current_registrations = pc_event_data.get(
                "current_registrations", 0
            )
            existing_course.updated_at = datetime.now(timezone.utc)
            existing_course.updated_by = updated_by
            self.db.commit()
            self.db.refresh(existing_course)
            return existing_course
        else:
            # Create new course
            course_data = CourseCreate(
                title=pc_event_data.get(
                    "title", pc_event_data.get("name", "Unknown Course")
                ),
                description=pc_event_data.get("description"),
                planning_center_event_id=pc_event_id,
                planning_center_event_name=pc_event_data.get("name"),
                event_start_date=pc_event_data.get("start_date"),
                event_end_date=pc_event_data.get("end_date"),
                max_capacity=pc_event_data.get("max_capacity"),
                current_registrations=pc_event_data.get("current_registrations", 0),
            )
            return self.create_course(course_data, created_by=updated_by)

    def get_registration_counts(
        self, course_ids: Optional[List[int]] = None
    ) -> Dict[int, int]:
        """Return enrollment counts per course."""
        query = self.db.query(
            EnrollmentModel.course_id, func.count(EnrollmentModel.id)
        )
        if course_ids:
            query = query.filter(EnrollmentModel.course_id.in_(course_ids))

        counts = query.group_by(EnrollmentModel.course_id).all()
        return {
            int(course_id): int(count) if count is not None else 0
            for course_id, count in counts
            if course_id is not None
        }
