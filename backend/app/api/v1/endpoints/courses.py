"""
Course API endpoints (Maps to Planning Center Events)
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import (get_current_active_user,
                                       get_current_admin_user)
from app.core.database import get_db
from app.schemas.course import Course, CourseCreate, CourseUpdate
from app.services.course_service import CourseService

router = APIRouter()


def course_to_schema(course_model, current_registrations: Optional[int] = None) -> Course:
    """Convert Course model to Course schema with user names populated"""
    course_dict = {
        "id": course_model.id,
        "title": course_model.title,
        "description": course_model.description,
        "duration_weeks": course_model.duration_weeks,
        "prerequisites": course_model.prerequisites,
        "planning_center_event_id": course_model.planning_center_event_id,
        "planning_center_event_name": course_model.planning_center_event_name,
        "event_start_date": course_model.event_start_date,
        "event_end_date": course_model.event_end_date,
        "max_capacity": course_model.max_capacity,
        "current_registrations": (
            current_registrations
            if current_registrations is not None
            else course_model.current_registrations
        ),
        "is_active": course_model.is_active,
        "content_unlock_mode": course_model.content_unlock_mode,
        "max_file_size_mb": course_model.max_file_size_mb,
        "created_at": course_model.created_at,
        "updated_at": course_model.updated_at,
        "created_by": course_model.created_by,
        "updated_by": course_model.updated_by,
        "created_by_user_name": None,
        "updated_by_user_name": None,
    }
    
    # Populate user names from relationships
    if course_model.created_by_user:
        course_dict["created_by_user_name"] = (
            course_model.created_by_user.full_name 
            or course_model.created_by_user.username 
            or course_model.created_by_user.email
        )
    if course_model.updated_by_user:
        course_dict["updated_by_user_name"] = (
            course_model.updated_by_user.full_name 
            or course_model.updated_by_user.username 
            or course_model.updated_by_user.email
        )
    if not course_dict["updated_by_user_name"] and course_dict["created_by_user_name"]:
        course_dict["updated_by_user_name"] = course_dict["created_by_user_name"]
    
    return Course(**course_dict)


@router.get("", response_model=List[Course])
@router.get("/", response_model=List[Course])
async def get_courses(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """Get all courses with pagination and optional filtering"""
    course_service = CourseService(db)
    courses = course_service.get_courses(skip=skip, limit=limit, is_active=is_active)
    course_ids = [course.id for course in courses]
    registration_counts = (
        course_service.get_registration_counts(course_ids) if course_ids else {}
    )
    return [
        course_to_schema(course, registration_counts.get(course.id)) for course in courses
    ]


@router.get("/{course_id}", response_model=Course)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get a specific course by ID"""
    course_service = CourseService(db)
    course = course_service.get_course(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found",
        )
    registration_counts = course_service.get_registration_counts([course.id])
    return course_to_schema(course, registration_counts.get(course.id))


@router.get("/prerequisites/available")
async def get_available_prerequisites(
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get list of courses available as prerequisites (excludes current course if provided)"""
    course_service = CourseService(db)
    courses = course_service.get_courses(skip=0, limit=1000, is_active=True)
    
    # Filter out the current course if provided
    if course_id:
        courses = [c for c in courses if c.id != course_id]
    
    # Return simplified course list for prerequisite selection
    return [
        {
            "id": course.id,
            "title": course.title,
            "description": course.description,
        }
        for course in courses
    ]


@router.get("/pc-event/{pc_event_id}", response_model=Course)
async def get_course_by_pc_event_id(pc_event_id: str, db: Session = Depends(get_db)):
    """Get a course by Planning Center event ID"""
    course_service = CourseService(db)
    course = course_service.get_course_by_pc_event_id(pc_event_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found for Planning Center event ID",
        )
    return course_to_schema(course)


@router.post("", response_model=Course, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=Course, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Create a new course - Admin and Staff only"""
    # Check if user has permission to create courses
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can create courses",
        )

    course_service = CourseService(db)
    created_course = course_service.create_course(course, created_by=current_user["id"])
    return course_to_schema(created_course)


@router.put("/{course_id}", response_model=Course)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Update an existing course - Admin and Staff only"""
    # Check if user has permission to update courses
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can update courses",
        )

    course_service = CourseService(db)
    course = course_service.update_course(
        course_id, course_update, updated_by=current_user["id"]
    )
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    return course_to_schema(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Delete a course - Admin only"""
    # Check if user has permission to delete courses
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can delete courses",
        )

    course_service = CourseService(db)
    success = course_service.delete_course(course_id, deleted_by=current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
