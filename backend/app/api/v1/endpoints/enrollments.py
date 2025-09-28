"""
CourseEnrollment API endpoints (Maps to Planning Center Registrations)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.enrollment import CourseEnrollment, CourseEnrollmentCreate, CourseEnrollmentUpdate
from app.services.enrollment_service import CourseEnrollmentService

router = APIRouter()


@router.get("/", response_model=List[CourseEnrollment])
async def get_enrollments(
    skip: int = 0,
    limit: int = 100,
    course_id: Optional[int] = None,
    people_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get enrollments with optional filtering"""
    enrollment_service = CourseEnrollmentService(db)
    return enrollment_service.get_enrollments(
        skip=skip, 
        limit=limit, 
        course_id=course_id, 
        people_id=people_id,
        status=status
    )


@router.get("/{enrollment_id}", response_model=CourseEnrollment)
async def get_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific enrollment by ID"""
    enrollment_service = CourseEnrollmentService(db)
    enrollment = enrollment_service.get_enrollment(enrollment_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    return enrollment


@router.get("/pc-registration/{pc_registration_id}", response_model=CourseEnrollment)
async def get_enrollment_by_pc_registration_id(
    pc_registration_id: str,
    db: Session = Depends(get_db)
):
    """Get enrollment by Planning Center registration ID"""
    enrollment_service = CourseEnrollmentService(db)
    enrollment = enrollment_service.get_enrollment_by_pc_registration_id(pc_registration_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found for Planning Center registration ID"
        )
    return enrollment


@router.post("/", response_model=CourseEnrollment, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    enrollment: CourseEnrollmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new enrollment"""
    enrollment_service = CourseEnrollmentService(db)
    return enrollment_service.create_enrollment(enrollment)


@router.post("/bulk", response_model=List[CourseEnrollment], status_code=status.HTTP_201_CREATED)
async def bulk_enroll(
    course_id: int = Query(..., description="Course ID"),
    people_ids: List[int] = Query(..., description="List of people IDs to enroll"),
    db: Session = Depends(get_db)
):
    """Bulk enroll multiple people in a course"""
    enrollment_service = CourseEnrollmentService(db)
    return enrollment_service.bulk_enroll(course_id, people_ids)


@router.put("/{enrollment_id}", response_model=CourseEnrollment)
async def update_enrollment(
    enrollment_id: int,
    enrollment_update: CourseEnrollmentUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing enrollment"""
    enrollment_service = CourseEnrollmentService(db)
    enrollment = enrollment_service.update_enrollment(enrollment_id, enrollment_update)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    return enrollment


@router.put("/{enrollment_id}/progress", response_model=CourseEnrollment)
async def update_progress(
    enrollment_id: int,
    progress_percentage: float,
    db: Session = Depends(get_db)
):
    """Update enrollment progress percentage"""
    enrollment_service = CourseEnrollmentService(db)
    enrollment = enrollment_service.update_progress(enrollment_id, progress_percentage)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    return enrollment


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db)
):
    """Delete an enrollment"""
    enrollment_service = CourseEnrollmentService(db)
    success = enrollment_service.delete_enrollment(enrollment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )