"""
CourseEnrollment API endpoints (Maps to Planning Center Registrations)
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.schemas.enrollment import (
    BulkEnrollFromPCEventRequest,
    BulkEnrollFromPCListRequest,
    ImportRegistrationsRequest,
    CourseEnrollment,
    CourseEnrollmentCreate,
    CourseEnrollmentUpdate,
    BulkDeleteEnrollmentsRequest,
    BulkDeleteEnrollmentsResponse,
)
from app.services.enrollment_service import CourseEnrollmentService

router = APIRouter()


@router.get("", response_model=List[CourseEnrollment])
@router.get("/", response_model=List[CourseEnrollment])
async def get_enrollments(
    skip: int = 0,
    limit: int = 100,
    course_id: Optional[int] = None,
    people_id: Optional[int] = None,
    status: Optional[str] = None,
    sort: Optional[str] = None,
    order: Optional[str] = "asc",
    db: Session = Depends(get_db),
):
    """Get enrollments with optional filtering and sorting"""
    enrollment_service = CourseEnrollmentService(db)
    return enrollment_service.get_enrollments(
        skip=skip, limit=limit, course_id=course_id, people_id=people_id, status=status,
        sort=sort, order=order
    )


@router.post("/bulk-delete", response_model=BulkDeleteEnrollmentsResponse)
async def bulk_delete_enrollments(
    request: BulkDeleteEnrollmentsRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Bulk delete enrollments - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can bulk delete enrollments",
        )

    enrollment_service = CourseEnrollmentService(db)
    result = enrollment_service.bulk_delete_enrollments(
        request.enrollment_ids, deleted_by=current_user["id"]
    )
    return BulkDeleteEnrollmentsResponse(**result)


@router.get("/{enrollment_id}", response_model=CourseEnrollment)
async def get_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    """Get a specific enrollment by ID"""
    enrollment_service = CourseEnrollmentService(db)
    enrollment = enrollment_service.get_enrollment(enrollment_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )
    return enrollment


@router.get("/pc-registration/{pc_registration_id}", response_model=CourseEnrollment)
async def get_enrollment_by_pc_registration_id(
    pc_registration_id: str, db: Session = Depends(get_db)
):
    """Get enrollment by Planning Center registration ID"""
    enrollment_service = CourseEnrollmentService(db)
    enrollment = enrollment_service.get_enrollment_by_pc_registration_id(
        pc_registration_id
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found for Planning Center registration ID",
        )
    return enrollment


@router.post("", response_model=CourseEnrollment, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=CourseEnrollment, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    enrollment: CourseEnrollmentCreate, db: Session = Depends(get_db)
):
    """Create a new enrollment"""
    enrollment_service = CourseEnrollmentService(db)
    return enrollment_service.create_enrollment(enrollment)


@router.post(
    "/bulk", response_model=List[CourseEnrollment], status_code=status.HTTP_201_CREATED
)
async def bulk_enroll(
    course_id: int = Query(..., description="Course ID"),
    people_ids: List[int] = Query(..., description="List of people IDs to enroll"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Bulk enroll multiple people in a course"""
    enrollment_service = CourseEnrollmentService(db)
    return enrollment_service.bulk_enroll(
        course_id, people_ids, created_by=current_user["id"]
    )


@router.post(
    "/bulk-from-pc-event",
    response_model=List[CourseEnrollment],
    status_code=status.HTTP_201_CREATED
)
async def bulk_enroll_from_pc_event(
    enrollment_data: BulkEnrollFromPCEventRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Bulk enroll people from a Planning Center Registration event"""
    # Check if user has permission (admin/staff only)
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can bulk enroll from Planning Center events",
        )
    
    enrollment_service = CourseEnrollmentService(db)
    try:
        enrollments = enrollment_service.bulk_enroll_from_pc_event(
            course_id=enrollment_data.course_id,
            pc_event_id=enrollment_data.pc_event_id,
            created_by=current_user["id"],
            status_filter=enrollment_data.status_filter,
            update_existing=enrollment_data.update_existing,
        )
        return enrollments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk enroll from Planning Center event: {str(e)}"
        )


@router.post(
    "/bulk-from-pc-list",
    response_model=List[CourseEnrollment],
    status_code=status.HTTP_201_CREATED
)
async def bulk_enroll_from_pc_list(
    enrollment_data: BulkEnrollFromPCListRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Bulk enroll people from a Planning Center List"""
    # Check if user has permission (admin/staff only)
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can bulk enroll from Planning Center lists",
        )
    
    enrollment_service = CourseEnrollmentService(db)
    try:
        enrollments = enrollment_service.bulk_enroll_from_pc_list(
            course_id=enrollment_data.course_id,
            pc_list_id=enrollment_data.pc_list_id,
            created_by=current_user["id"],
            update_existing=enrollment_data.update_existing,
        )
        return enrollments
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk enroll from Planning Center list: {str(e)}"
        )


@router.put("/{enrollment_id}", response_model=CourseEnrollment)
async def update_enrollment(
    enrollment_id: int,
    enrollment_update: CourseEnrollmentUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing enrollment"""
    enrollment_service = CourseEnrollmentService(db)
    enrollment = enrollment_service.update_enrollment(enrollment_id, enrollment_update)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )
    return enrollment


@router.put("/{enrollment_id}/progress", response_model=CourseEnrollment)
async def update_progress(
    enrollment_id: int, progress_percentage: float, db: Session = Depends(get_db)
):
    """Update enrollment progress percentage"""
    enrollment_service = CourseEnrollmentService(db)
    enrollment = enrollment_service.update_progress(enrollment_id, progress_percentage)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )
    return enrollment


@router.post(
    "/import-registrations",
    response_model=List[CourseEnrollment],
    status_code=status.HTTP_201_CREATED
)
async def import_registrations(
    request: ImportRegistrationsRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """
    Import selected registrations from a Planning Center event as enrollments.
    Automatically syncs people from Planning Center if they don't exist locally.
    Requires admin or staff role.
    """
    if not current_user or current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can import registrations",
        )
    
    enrollment_service = CourseEnrollmentService(db)
    try:
        enrollments = enrollment_service.import_registrations(
            course_id=request.course_id,
            registration_ids=request.registration_ids,
            event_id=request.event_id,
            created_by=current_user["id"],
            update_existing=request.update_existing,
        )
        return enrollments
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Error importing registrations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import registrations: {str(e)}"
        )


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    """Delete an enrollment"""
    enrollment_service = CourseEnrollmentService(db)
    success = enrollment_service.delete_enrollment(enrollment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )
