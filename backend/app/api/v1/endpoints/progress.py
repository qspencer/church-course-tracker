"""
Progress tracking endpoints
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.schemas.progress import (ContentCompletion, ContentCompletionCreate,
                                  ContentCompletionUpdate,
                                  EnrollmentContentProgress)
from app.services.progress_service import ProgressService

router = APIRouter()

# Roles allowed to mutate progress records. Instructors are included because
# they grade content; viewers are not.
_WRITE_ROLES = ("admin", "staff", "instructor")


def _require_write_role(current_user: dict) -> None:
    if current_user.get("role") not in _WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin, staff, or instructor role required",
        )


@router.get("/member/{member_id}", response_model=List[ContentCompletion])
async def get_member_progress(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get progress for a specific member across all courses"""
    progress_service = ProgressService(db)
    return progress_service.get_member_progress(member_id)


@router.get("/course/{course_id}", response_model=List[ContentCompletion])
async def get_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get progress for all members in a specific course"""
    progress_service = ProgressService(db)
    return progress_service.get_course_progress(course_id)


@router.get(
    "/enrollment/{enrollment_id}",
    response_model=List[EnrollmentContentProgress],
)
async def get_enrollment_progress(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get progress for each content item within an enrollment's course"""
    progress_service = ProgressService(db)
    enrollment_progress = progress_service.get_enrollment_progress(enrollment_id)
    if enrollment_progress is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )
    return enrollment_progress


@router.get("/{progress_id}", response_model=ContentCompletion)
async def get_progress(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get a specific progress record by ID"""
    progress_service = ProgressService(db)
    progress = progress_service.get_progress(progress_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Progress record not found"
        )
    return progress


@router.post("", response_model=ContentCompletion)
@router.post("/", response_model=ContentCompletion)
async def create_progress(
    progress: ContentCompletionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Create a new progress record"""
    _require_write_role(current_user)
    progress_service = ProgressService(db)
    return progress_service.create_progress(progress)


@router.put("/{progress_id}", response_model=ContentCompletion)
async def update_progress(
    progress_id: int,
    progress_update: ContentCompletionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Update an existing progress record"""
    _require_write_role(current_user)
    progress_service = ProgressService(db)
    progress = progress_service.update_progress(progress_id, progress_update)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Progress record not found"
        )
    return progress


@router.delete("/{progress_id}")
async def delete_progress(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Delete a progress record"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    progress_service = ProgressService(db)
    success = progress_service.delete_progress(progress_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Progress record not found"
        )
    return {"message": "Progress record deleted successfully"}
