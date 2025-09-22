"""
Progress tracking endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.progress import ContentCompletion, ContentCompletionCreate, ContentCompletionUpdate
from app.services.progress_service import ProgressService

router = APIRouter()


@router.get("/member/{member_id}", response_model=List[ContentCompletion])
async def get_member_progress(
    member_id: int,
    db: Session = Depends(get_db)
):
    """Get progress for a specific member across all courses"""
    progress_service = ProgressService(db)
    return progress_service.get_member_progress(member_id)


@router.get("/course/{course_id}", response_model=List[ContentCompletion])
async def get_course_progress(
    course_id: int,
    db: Session = Depends(get_db)
):
    """Get progress for all members in a specific course"""
    progress_service = ProgressService(db)
    return progress_service.get_course_progress(course_id)


@router.get("/{progress_id}", response_model=ContentCompletion)
async def get_progress(
    progress_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific progress record by ID"""
    progress_service = ProgressService(db)
    progress = progress_service.get_progress(progress_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress record not found"
        )
    return progress


@router.post("/", response_model=ContentCompletion)
async def create_progress(
    progress: ContentCompletionCreate,
    db: Session = Depends(get_db)
):
    """Create a new progress record"""
    progress_service = ProgressService(db)
    return progress_service.create_progress(progress)


@router.put("/{progress_id}", response_model=ContentCompletion)
async def update_progress(
    progress_id: int,
    progress_update: ContentCompletionUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing progress record"""
    progress_service = ProgressService(db)
    progress = progress_service.update_progress(progress_id, progress_update)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress record not found"
        )
    return progress


@router.delete("/{progress_id}")
async def delete_progress(
    progress_id: int,
    db: Session = Depends(get_db)
):
    """Delete a progress record"""
    progress_service = ProgressService(db)
    success = progress_service.delete_progress(progress_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress record not found"
        )
    return {"message": "Progress record deleted successfully"}
