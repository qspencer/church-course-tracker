"""
API v1 router configuration
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, courses, enrollments, progress, reports, users, sync,
    people, planning_center_sync
)

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Core entity endpoints
api_router.include_router(people.router, prefix="/people", tags=["people"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])

# Progress and reporting endpoints
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

# User management endpoints
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Planning Center integration endpoints
api_router.include_router(planning_center_sync.router, prefix="/planning-center", tags=["planning-center"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
