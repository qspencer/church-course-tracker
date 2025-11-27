"""
Custom Attributes API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user
from app.services.custom_attribute_service import CustomAttributeService
from app.schemas.custom_attribute import CustomAttribute, CustomAttributeCreate, CustomAttributeUpdate
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=List[CustomAttribute])
async def get_custom_attributes(
    entity_type: str = Query(..., description="Entity type (person, course, program, enrollment, program_participant)"),
    entity_id: int = Query(..., description="Entity ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get all custom attributes for an entity"""
    custom_attr_service = CustomAttributeService(db)
    custom_attrs = custom_attr_service.get_custom_attributes(entity_type, entity_id)
    return custom_attrs


@router.get("/{attribute_id}", response_model=CustomAttribute)
async def get_custom_attribute(
    attribute_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get a specific custom attribute by ID"""
    custom_attr_service = CustomAttributeService(db)
    custom_attr = custom_attr_service.get_custom_attribute_by_id(attribute_id)
    if not custom_attr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom attribute with ID {attribute_id} not found"
        )
    return custom_attr


@router.post("/", response_model=CustomAttribute, status_code=status.HTTP_201_CREATED)
async def create_custom_attribute(
    custom_attr: CustomAttributeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Create a new custom attribute"""
    # Check if user has permission (admin/staff only)
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can create custom attributes",
        )
    
    custom_attr_service = CustomAttributeService(db)
    return custom_attr_service.create_custom_attribute(
        entity_type=custom_attr.entity_type,
        entity_id=custom_attr.entity_id,
        attribute_name=custom_attr.attribute_name,
        attribute_value=custom_attr.attribute_value,
        pc_attribute_name=custom_attr.pc_attribute_name,
        attribute_type=custom_attr.attribute_type,
        source=custom_attr.source,
        planning_center_source_id=custom_attr.planning_center_source_id,
        created_by=current_user["id"]
    )


@router.put("/{attribute_id}", response_model=CustomAttribute)
async def update_custom_attribute(
    attribute_id: int,
    custom_attr_update: CustomAttributeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Update a custom attribute"""
    # Check if user has permission (admin/staff only)
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can update custom attributes",
        )
    
    custom_attr_service = CustomAttributeService(db)
    custom_attr = custom_attr_service.get_custom_attribute_by_id(attribute_id)
    if not custom_attr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom attribute with ID {attribute_id} not found"
        )
    
    # Get the existing attribute to know entity_type, entity_id, and attribute_name
    existing_attr = custom_attr_service.get_custom_attribute_by_id(attribute_id)
    if not existing_attr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom attribute with ID {attribute_id} not found"
        )
    
    # Update using the service method signature
    updated = custom_attr_service.update_custom_attribute(
        entity_type=existing_attr.entity_type,
        entity_id=existing_attr.entity_id,
        attribute_name=existing_attr.attribute_name,
        attribute_value=custom_attr_update.attribute_value if custom_attr_update.attribute_value is not None else existing_attr.attribute_value,
        updated_by=current_user["id"]
    )
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom attribute not found"
        )
    
    return updated


@router.delete("/{attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_attribute(
    attribute_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Delete a custom attribute"""
    # Check if user has permission (admin/staff only)
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can delete custom attributes",
        )
    
    custom_attr_service = CustomAttributeService(db)
    custom_attr = custom_attr_service.get_custom_attribute_by_id(attribute_id)
    if not custom_attr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom attribute with ID {attribute_id} not found"
        )
    
    # Get the existing attribute to know entity_type, entity_id, and attribute_name
    existing_attr = custom_attr_service.get_custom_attribute_by_id(attribute_id)
    if not existing_attr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom attribute with ID {attribute_id} not found"
        )
    
    deleted = custom_attr_service.delete_custom_attribute(
        entity_type=existing_attr.entity_type,
        entity_id=existing_attr.entity_id,
        attribute_name=existing_attr.attribute_name
    )
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Custom attribute not found"
        )
    
    return None

