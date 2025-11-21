"""
Course Instance API endpoints (Course Offerings)
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user
from app.core.database import get_db
from app.schemas.course_instance import (
    CourseInstance,
    CourseInstanceCreate,
    CourseInstanceTeacher,
    CourseInstanceTeacherCreate,
    CourseInstanceUpdate,
)
from app.services.course_instance_service import CourseInstanceService

router = APIRouter()


@router.get("", response_model=List[CourseInstance], status_code=status.HTTP_200_OK)
async def get_course_instances(
    course_id: Optional[int] = Query(None, description="Filter by master course ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all course instances (course offerings)"""
    instance_service = CourseInstanceService(db)
    instances = instance_service.get_course_instances(
        course_id=course_id, skip=skip, limit=limit, is_active=is_active
    )
    return instances


@router.get(
    "/{instance_id}",
    response_model=CourseInstance,
    status_code=status.HTTP_200_OK,
)
async def get_course_instance(
    instance_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific course instance by ID"""
    instance_service = CourseInstanceService(db)
    instance = instance_service.get_course_instance(instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course instance with ID {instance_id} not found",
        )
    return instance


@router.post(
    "",
    response_model=CourseInstance,
    status_code=status.HTTP_201_CREATED,
)
async def create_course_instance(
    instance_data: CourseInstanceCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new course instance (course offering)"""
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can create course instances",
        )

    instance_service = CourseInstanceService(db)
    instance = instance_service.create_course_instance(
        instance_data, created_by=current_user["id"]
    )
    return instance


@router.patch(
    "/{instance_id}",
    response_model=CourseInstance,
    status_code=status.HTTP_200_OK,
)
async def update_course_instance(
    instance_id: int,
    instance_update: CourseInstanceUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update an existing course instance"""
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can update course instances",
        )

    instance_service = CourseInstanceService(db)
    instance = instance_service.update_course_instance(
        instance_id, instance_update, updated_by=current_user["id"]
    )
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course instance with ID {instance_id} not found",
        )
    return instance


@router.delete(
    "/{instance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_course_instance(
    instance_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a course instance"""
    if current_user["role"] not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can delete course instances",
        )

    instance_service = CourseInstanceService(db)
    success = instance_service.delete_course_instance(
        instance_id, deleted_by=current_user["id"]
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course instance with ID {instance_id} not found",
        )
    return None


@router.get(
    "/{instance_id}/teachers",
    response_model=List[CourseInstanceTeacher],
    status_code=status.HTTP_200_OK,
)
async def get_instance_teachers(
    instance_id: int,
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all teachers for a course instance"""
    instance_service = CourseInstanceService(db)
    instance = instance_service.get_course_instance(instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course instance with ID {instance_id} not found",
        )

    teachers = instance_service.get_instance_teachers(
        instance_id, is_active=is_active
    )
    return teachers


@router.post(
    "/{instance_id}/teachers",
    response_model=CourseInstanceTeacher,
    status_code=status.HTTP_201_CREATED,
)
async def add_instance_teacher(
    instance_id: int,
    teacher_data: CourseInstanceTeacherCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Add a teacher to a course instance"""
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can add teachers",
        )

    instance_service = CourseInstanceService(db)
    instance = instance_service.get_course_instance(instance_id)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course instance with ID {instance_id} not found",
        )

    teacher = instance_service.add_teacher(
        instance_id, teacher_data, created_by=current_user["id"]
    )
    return teacher


@router.delete(
    "/{instance_id}/teachers/{teacher_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_instance_teacher(
    instance_id: int,
    teacher_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove a teacher from a course instance"""
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can remove teachers",
        )

    instance_service = CourseInstanceService(db)
    success = instance_service.remove_teacher(
        teacher_id, deleted_by=current_user["id"]
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with ID {teacher_id} not found",
        )
    return None


@router.post(
    "/enrollments/{enrollment_id}/assign-teacher",
    status_code=status.HTTP_200_OK,
)
async def assign_student_to_teacher(
    enrollment_id: int,
    teacher_id: int = Query(..., description="Teacher ID to assign"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Assign a student (enrollment) to a specific teacher for discipleship tracking"""
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can assign students to teachers",
        )

    instance_service = CourseInstanceService(db)
    success = instance_service.assign_student_to_teacher(
        enrollment_id, teacher_id, updated_by=current_user["id"]
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to assign student to teacher. Enrollment or teacher may not exist.",
        )
    return {"message": "Student assigned to teacher successfully"}

