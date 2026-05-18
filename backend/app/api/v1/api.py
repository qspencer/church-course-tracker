"""
API v1 router configuration
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (audit, auth, autocomplete_suggestions, course_content, course_instances,
                                  courses, custom_attributes, enrollments, mock_planning_center,
                                  people, planning_center_sync, program_content, programs, progress,
                                  reports, sync, system_settings, users)
from app.core.config import settings

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Core entity endpoints
api_router.include_router(people.router, prefix="/people", tags=["people"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(programs.router, prefix="/programs", tags=["programs"])
api_router.include_router(
    course_instances.router, prefix="/course-instances", tags=["course-instances"]
)
api_router.include_router(
    enrollments.router, prefix="/enrollments", tags=["enrollments"]
)

# Course content endpoints
api_router.include_router(
    course_content.router, prefix="/content", tags=["course-content"]
)

# Program content endpoints
api_router.include_router(
    program_content.router, prefix="/program-content", tags=["program-content"]
)

# Progress and reporting endpoints
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

# User management endpoints
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Planning Center integration endpoints
api_router.include_router(
    planning_center_sync.router, prefix="/planning-center", tags=["planning-center"]
)
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])

# Audit endpoints
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])

# Autocomplete suggestions endpoints
api_router.include_router(
    autocomplete_suggestions.router, prefix="/autocomplete-suggestions", tags=["autocomplete-suggestions"]
)

# Custom attributes endpoints
api_router.include_router(
    custom_attributes.router, prefix="/custom-attributes", tags=["custom-attributes"]
)

# System Settings endpoints
api_router.include_router(
    system_settings.router, prefix="/settings", tags=["system-settings"]
)

# Mock Planning Center endpoints (for development/testing). Mounted only
# when explicitly enabled AND outside of production. The mock module itself
# has no auth gates on its routes - exposing it in production would be an
# unauthenticated write surface. The audit (2026-05-18 §3.1 B9) flagged
# this as a P1 risk; we close it here by gating registration.
if settings.ENVIRONMENT != "production" and settings.USE_MOCK_PLANNING_CENTER:
    api_router.include_router(
        mock_planning_center.router,
        prefix="/mock-planning-center",
        tags=["mock-planning-center"],
    )
