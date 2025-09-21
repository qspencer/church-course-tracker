"""
Course API endpoints (Maps to Planning Center Events)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.course import Course, CourseCreate, CourseUpdate
from app.services.course_service import CourseService

router = APIRouter()


@router.get("/", response_model=List[Course])
async def get_courses(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all courses with pagination and optional filtering"""
    course_service = CourseService(db)
    return course_service.get_courses(skip=skip, limit=limit, is_active=is_active)


@router.get("/{course_id}", response_model=Course)
async def get_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific course by ID"""
    course_service = CourseService(db)
    course = course_service.get_course(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return course


@router.get("/pc-event/{pc_event_id}", response_model=Course)
async def get_course_by_pc_event_id(
    pc_event_id: str,
    db: Session = Depends(get_db)
):
    """Get a course by Planning Center event ID"""
    course_service = CourseService(db)
    course = course_service.get_course_by_pc_event_id(pc_event_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found for Planning Center event ID"
        )
    return course


@router.post("/", response_model=Course, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db)
):
    """Create a new course"""
    course_service = CourseService(db)
    return course_service.create_course(course)


@router.put("/{course_id}", response_model=Course)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing course"""
    course_service = CourseService(db)
    course = course_service.update_course(course_id, course_update)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db)
):
    """Delete a course"""
    course_service = CourseService(db)
    success = course_service.delete_course(course_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
