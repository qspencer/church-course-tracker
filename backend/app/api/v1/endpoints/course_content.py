"""
Course Content API Endpoints

This module provides API endpoints for managing course content including
modules, content items, file uploads, and access tracking.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user, get_current_admin_user
from app.services.content_service import ContentService
from app.schemas.course_content import (
    CourseModule, CourseModuleCreate, CourseModuleUpdate,
    CourseContent, CourseContentCreate, CourseContentUpdate,
    ContentAccessLog, ContentAccessLogCreate,
    ContentAuditLog, ContentUploadResponse, ContentDownloadRequest,
    ContentProgressUpdate, CourseContentSummary
)
from app.models.user import User

router = APIRouter()


# Course Module Endpoints

@router.post("/modules/", response_model=CourseModule, status_code=status.HTTP_201_CREATED)
async def create_module(
    module_data: CourseModuleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new course module - Admin and Staff only"""
    # Check if user has permission to create modules
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can create course modules"
        )
    
    content_service = ContentService(db)
    return content_service.create_module(module_data, current_user["id"])


@router.get("/modules/{course_id}", response_model=List[CourseModule])
async def get_course_modules(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get all modules for a course"""
    content_service = ContentService(db)
    return content_service.get_modules(course_id)


@router.get("/modules/single/{module_id}", response_model=CourseModule)
async def get_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific module"""
    content_service = ContentService(db)
    module = content_service.get_module(module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    return module


@router.put("/modules/{module_id}", response_model=CourseModule)
async def update_module(
    module_id: int,
    module_data: CourseModuleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Update a course module - Admin and Staff only"""
    # Check if user has permission to update modules
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can update course modules"
        )
    
    content_service = ContentService(db)
    module = content_service.update_module(module_id, module_data, current_user["id"])
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    return module


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Delete a course module - Admin and Staff only"""
    # Check if user has permission to delete modules
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can delete course modules"
        )
    
    content_service = ContentService(db)
    success = content_service.delete_module(module_id, current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )


# Course Content Endpoints

@router.post("/", response_model=CourseContent, status_code=status.HTTP_201_CREATED)
async def create_content(
    content_data: CourseContentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Create new course content - Admin and Staff only"""
    # Check if user has permission to create content
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can create course content"
        )
    
    content_service = ContentService(db)
    return content_service.create_content(content_data, current_user["id"])


@router.get("/course/{course_id}", response_model=List[CourseContent])
async def get_course_content(
    course_id: int,
    module_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get content for a course, optionally filtered by module"""
    content_service = ContentService(db)
    return content_service.get_content(course_id, module_id)


@router.get("/{content_id}", response_model=CourseContent)
async def get_content_item(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific content item"""
    content_service = ContentService(db)
    content = content_service.get_content_item(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    return content


@router.put("/{content_id}", response_model=CourseContent)
async def update_content(
    content_id: int,
    content_data: CourseContentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Update course content - Admin and Staff only"""
    # Check if user has permission to update content
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can update course content"
        )
    
    content_service = ContentService(db)
    content = content_service.update_content(content_id, content_data, current_user["id"])
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    return content


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Delete course content - Admin and Staff only"""
    # Check if user has permission to delete content
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can delete course content"
        )
    
    content_service = ContentService(db)
    success = content_service.delete_content(content_id, current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )


# File Upload Endpoints

@router.post("/{content_id}/upload", response_model=ContentUploadResponse)
async def upload_file(
    content_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Upload a file for course content - Admin and Staff only"""
    # Check if user has permission to upload files
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can upload files"
        )
    
    content_service = ContentService(db)
    return content_service.upload_file(content_id, file, current_user["id"])


@router.get("/{content_id}/download")
async def download_content(
    content_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Download course content"""
    content_service = ContentService(db)
    
    # Get client IP and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    result = content_service.download_content(
        content_id, 
        current_user["id"], 
        ip_address, 
        user_agent
    )
    
    from fastapi.responses import Response
    return Response(
        content=result["content"],
        media_type=result["mime_type"],
        headers={
            "Content-Disposition": f"attachment; filename={result['filename']}",
            "Content-Length": str(result["file_size"])
        }
    )


# Content Access and Progress Tracking

@router.post("/{content_id}/access", response_model=ContentAccessLog)
async def log_content_access(
    content_id: int,
    access_data: ContentAccessLogCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Log content access (view, download, complete)"""
    # Ensure the access log is for the current user
    access_data.user_id = current_user["id"]
    access_data.content_id = content_id
    
    content_service = ContentService(db)
    return content_service.log_content_access(access_data)


@router.put("/{content_id}/progress")
async def update_content_progress(
    content_id: int,
    progress_data: ContentProgressUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Update content progress (for videos/audio)"""
    content_service = ContentService(db)
    
    # Get client IP and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Log the progress update
    access_data = ContentAccessLogCreate(
        content_id=content_id,
        user_id=current_user["id"],
        access_type="view",
        progress_percentage=progress_data.progress_percentage,
        time_spent=progress_data.time_spent,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return content_service.log_content_access(access_data)


@router.get("/{content_id}/access-logs", response_model=List[ContentAccessLog])
async def get_content_access_logs(
    content_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get access logs for content - Admin and Staff only"""
    # Check if user has permission to view access logs
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can view access logs"
        )
    
    content_service = ContentService(db)
    return content_service.get_content_access_logs(content_id, limit)


@router.get("/user/{user_id}/course/{course_id}/progress")
async def get_user_content_progress(
    user_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get user's content progress for a course"""
    # Users can only view their own progress, admins/staff can view any user's progress
    if current_user["id"] != user_id and current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own progress"
        )
    
    content_service = ContentService(db)
    return content_service.get_user_content_progress(user_id, course_id)


# Audit Trail

@router.get("/{content_id}/audit-logs", response_model=List[ContentAuditLog])
async def get_content_audit_logs(
    content_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get audit logs for content - Admin and Staff only"""
    # Check if user has permission to view audit logs
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can view audit logs"
        )
    
    content_service = ContentService(db)
    return content_service.get_audit_logs(content_id, limit)


# Course Content Summary

@router.get("/course/{course_id}/summary", response_model=CourseContentSummary)
async def get_course_content_summary(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user)
):
    """Get content summary for a course - Admin and Staff only"""
    # Check if user has permission to view content summary
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can view content summary"
        )
    
    content_service = ContentService(db)
    
    # Get content and modules
    content_items = content_service.get_content(course_id)
    modules = content_service.get_modules(course_id)
    
    # Calculate summary statistics
    total_content_items = len(content_items)
    total_modules = len(modules)
    total_file_size = sum(item.file_size or 0 for item in content_items)
    
    # Count content by type
    content_by_type = {}
    for item in content_items:
        content_type = item.content_type.value
        content_by_type[content_type] = content_by_type.get(content_type, 0) + 1
    
    # Get recent uploads (last 10)
    recent_uploads = sorted(content_items, key=lambda x: x.created_at, reverse=True)[:10]
    
    return CourseContentSummary(
        course_id=course_id,
        total_content_items=total_content_items,
        total_modules=total_modules,
        total_file_size=total_file_size,
        content_by_type=content_by_type,
        recent_uploads=recent_uploads
    )


