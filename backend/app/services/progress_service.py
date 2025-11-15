"""
Progress service layer
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from app.models.course_content import CourseContent as CourseContentModel
from app.models.enrollment import CourseEnrollment as CourseEnrollmentModel
from app.models.progress import ContentCompletion as ProgressModel
from app.schemas.progress import (ContentCompletionCreate,
                                  ContentCompletionUpdate)


class ProgressService:
    """Service for progress operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_member_progress(self, member_id: int) -> List[ProgressModel]:
        """Get progress for a specific member across all courses"""
        return (
            self.db.query(ProgressModel)
            .join(ProgressModel.course_enrollment)
            .filter(ProgressModel.course_enrollment.has(people_id=member_id))
            .all()
        )

    def get_course_progress(self, course_id: int) -> List[ProgressModel]:
        """Get progress for all members in a specific course"""
        return (
            self.db.query(ProgressModel)
            .join(ProgressModel.course_enrollment)
            .filter(ProgressModel.course_enrollment.has(course_id=course_id))
            .all()
        )

    def get_progress(self, progress_id: int) -> Optional[ProgressModel]:
        """Get a specific progress record by ID"""
        return (
            self.db.query(ProgressModel).filter(ProgressModel.id == progress_id).first()
        )

    def create_progress(self, progress: ContentCompletionCreate) -> ProgressModel:
        """Create a new progress record"""
        db_progress = ProgressModel(**progress.dict())
        db_progress.created_at = datetime.utcnow()
        db_progress.updated_at = datetime.utcnow()

        self.db.add(db_progress)
        self.db.commit()
        self.db.refresh(db_progress)
        return db_progress

    def update_progress(
        self, progress_id: int, progress_update: ContentCompletionUpdate
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

    def get_enrollment_progress(self, enrollment_id: int):
        """Return progress entries (and placeholders) for a specific enrollment"""
        enrollment = (
            self.db.query(CourseEnrollmentModel)
            .filter(CourseEnrollmentModel.id == enrollment_id)
            .first()
        )
        if not enrollment:
            return None

        contents = (
            self.db.query(CourseContentModel)
            .filter(CourseContentModel.course_id == enrollment.course_id)
            .order_by(CourseContentModel.order_index, CourseContentModel.id)
            .all()
        )

        content_map = {content.id: content for content in contents}

        try:
            completions = (
                self.db.query(ProgressModel)
                .filter(ProgressModel.course_enrollment_id == enrollment_id)
                .all()
            )
        except ProgrammingError as exc:
            # Older production schema uses the "progress" table instead of "content_completion"
            # Treat missing table as "no completion records" so the UI still shows placeholders.
            if "content_completion" in str(exc.orig):
                completions = []
                self.db.rollback()
            else:
                raise

        completions_by_content = {
            completion.content_id: completion for completion in completions
        }

        progress_items = []
        for content in contents:
            completion = completions_by_content.get(content.id)
            status = "not_started"
            if completion:
                if completion.completed_at:
                    status = "completed"
                elif any(
                    value is not None
                    for value in (
                        completion.time_spent_minutes,
                        completion.score,
                        completion.notes,
                    )
                ):
                    status = "in_progress"
                else:
                    status = "in_progress"

            progress_items.append(
                {
                    "id": completion.id if completion else None,
                    "enrollment_id": enrollment.id,
                    "content_id": content.id,
                    "status": status,
                    "completed_at": completion.completed_at if completion else None,
                    "time_spent_minutes": (
                        completion.time_spent_minutes if completion else None
                    ),
                    "score": completion.score if completion else None,
                    "notes": completion.notes if completion else None,
                    "created_at": completion.created_at if completion else None,
                    "updated_at": completion.updated_at if completion else None,
                    "content": content_map.get(content.id),
                }
            )

        return progress_items
