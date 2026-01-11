"""
Program Content API Endpoints

This module provides API endpoints for managing program content including
modules (categories) and content items (lessons).
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user, get_current_admin_user
from app.core.database import get_db
from app.schemas.program_content import (
    ProgramContent,
    ProgramContentCreate,
    ProgramContentUpdate,
    ProgramModule,
    ProgramModuleCreate,
    ProgramModuleUpdate,
)
from app.services.program_content_service import ProgramContentService
from app.services.program_service import ProgramService

router = APIRouter()


# Program Module Endpoints (Categories)


@router.post(
    "/modules/", response_model=ProgramModule, status_code=status.HTTP_201_CREATED
)
@router.post(
    "/modules", response_model=ProgramModule, status_code=status.HTTP_201_CREATED
)
async def create_program_module(
    module_data: ProgramModuleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Create a new program module (category) - Program admin or system admin only"""
    # Check if user is program admin or system admin
    program_service = ProgramService(db)
    if not program_service.is_program_admin(module_data.program_id, current_user["id"]):
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can create program modules",
            )

    content_service = ProgramContentService(db)
    return content_service.create_module(module_data, current_user["id"])


@router.get("/modules/{program_id}", response_model=List[ProgramModule])
async def get_program_modules(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get all modules (categories) for a program"""
    # Verify program exists
    program_service = ProgramService(db)
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )

    content_service = ProgramContentService(db)
    return content_service.get_modules(program_id)


@router.get("/modules/single/{module_id}", response_model=ProgramModule)
async def get_program_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get a specific program module"""
    content_service = ProgramContentService(db)
    module = content_service.get_module(module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )
    return module


@router.put("/modules/{module_id}", response_model=ProgramModule)
async def update_program_module(
    module_id: int,
    module_data: ProgramModuleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Update a program module - Program admin or system admin only"""
    content_service = ProgramContentService(db)
    module = content_service.get_module(module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    # Check if user is program admin or system admin
    program_service = ProgramService(db)
    if not program_service.is_program_admin(module.program_id, current_user["id"]):
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can update program modules",
            )

    updated_module = content_service.update_module(module_id, module_data, current_user["id"])
    if not updated_module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )
    return updated_module


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Delete a program module - Program admin or system admin only"""
    content_service = ProgramContentService(db)
    module = content_service.get_module(module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    # Check if user is program admin or system admin
    program_service = ProgramService(db)
    if not program_service.is_program_admin(module.program_id, current_user["id"]):
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can delete program modules",
            )

    success = content_service.delete_module(module_id, current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )


# Program Content Endpoints (Lessons)


@router.post("", response_model=ProgramContent, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ProgramContent, status_code=status.HTTP_201_CREATED)
async def create_program_content(
    content_data: ProgramContentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Create new program content (lesson) - Program admin or system admin only"""
    # Check if user is program admin or system admin
    program_service = ProgramService(db)
    if not program_service.is_program_admin(content_data.program_id, current_user["id"]):
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can create program content",
            )

    content_service = ProgramContentService(db)
    return content_service.create_content(content_data, current_user["id"])


@router.get("/program/{program_id}", response_model=List[ProgramContent])
async def get_program_content(
    program_id: int,
    module_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get content (lessons) for a program, optionally filtered by module (category)"""
    # Verify program exists
    program_service = ProgramService(db)
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )

    content_service = ProgramContentService(db)
    return content_service.get_content(program_id, module_id)


@router.get("/{content_id}", response_model=ProgramContent)
async def get_program_content_item(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get a specific program content item by ID"""
    content_service = ProgramContentService(db)
    content = content_service.get_content_item(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content item with ID {content_id} not found",
        )
    return content


@router.put("/{content_id}", response_model=ProgramContent)
async def update_program_content(
    content_id: int,
    content_data: ProgramContentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Update program content - Program admin or system admin only"""
    content_service = ProgramContentService(db)
    content = content_service.get_content_item(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    # Check if user is program admin or system admin
    program_service = ProgramService(db)
    if not program_service.is_program_admin(content.program_id, current_user["id"]):
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can update program content",
            )

    updated_content = content_service.update_content(
        content_id, content_data, current_user["id"]
    )
    if not updated_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )
    return updated_content


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Delete program content - Program admin or system admin only"""
    content_service = ProgramContentService(db)
    content = content_service.get_content_item(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    # Check if user is program admin or system admin
    program_service = ProgramService(db)
    if not program_service.is_program_admin(content.program_id, current_user["id"]):
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can delete program content",
            )

    success = content_service.delete_content(content_id, current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content item with ID {content_id} not found",
        )


