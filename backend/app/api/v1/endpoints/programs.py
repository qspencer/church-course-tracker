"""
Program API endpoints
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user, get_current_admin_user
from app.core.database import get_db
from app.schemas.program import (
    Program,
    ProgramCreate,
    ProgramUpdate,
    BulkImportParticipantsFromPCEventRequest,
    BulkImportParticipantsFromPCListRequest,
    BulkDeleteProgramsRequest,
    BulkDeleteProgramsResponse,
)
from app.schemas.program_admin import ProgramAdmin, ProgramAdminCreate, ProgramAdminUpdate
from app.schemas.program_participant import (
    ProgramParticipant,
    ProgramParticipantCreate,
    ProgramParticipantUpdate,
)
from app.schemas.program_pairing import (
    ProgramPairing,
    ProgramPairingCreate,
    ProgramPairingUpdate,
)
from app.schemas.program_session import (
    ProgramSession,
    ProgramSessionCreate,
    ProgramSessionUpdate,
)
from app.schemas.program_progress import (
    ProgramProgress,
    ProgramProgressCreate,
    ProgramProgressUpdate,
)
from app.services.program_service import ProgramService

router = APIRouter()


def program_to_schema(program_model) -> Program:
    """Convert Program model to Program schema with user names populated"""
    program_dict = {
        "id": program_model.id,
        "title": program_model.title,
        "description": program_model.description,
        "role_definitions": program_model.role_definitions,
        "relationship_config": program_model.relationship_config,
        "locations": program_model.locations,
        "delivery_modes": program_model.delivery_modes,
        "prerequisites": program_model.prerequisites,
        "planning_center_event_template_id": program_model.planning_center_event_template_id,
        "planning_center_event_id": program_model.planning_center_event_id,
        "planning_center_event_name": program_model.planning_center_event_name,
        "is_active": program_model.is_active,
        "created_at": program_model.created_at,
        "updated_at": program_model.updated_at,
        "created_by": program_model.created_by,
        "updated_by": program_model.updated_by,
        "created_by_user_name": None,
        "updated_by_user_name": None,
    }
    
    # Populate user names from relationships
    if program_model.created_by_user:
        program_dict["created_by_user_name"] = (
            program_model.created_by_user.full_name 
            or program_model.created_by_user.username 
            or program_model.created_by_user.email
        )
    if program_model.updated_by_user:
        program_dict["updated_by_user_name"] = (
            program_model.updated_by_user.full_name 
            or program_model.updated_by_user.username 
            or program_model.updated_by_user.email
        )
    if not program_dict["updated_by_user_name"] and program_dict["created_by_user_name"]:
        program_dict["updated_by_user_name"] = program_dict["created_by_user_name"]
    
    return Program(**program_dict)


@router.get("", response_model=List[Program])
@router.get("/", response_model=List[Program])
async def get_programs(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get all programs with pagination and optional filtering"""
    program_service = ProgramService(db)
    programs = program_service.get_programs(skip=skip, limit=limit, is_active=is_active)
    try:
        return [program_to_schema(program) for program in programs]
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error serializing programs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing programs: {str(e)}"
        )


@router.post("/bulk-delete", response_model=BulkDeleteProgramsResponse)
async def bulk_delete_programs(
    request: BulkDeleteProgramsRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Bulk delete programs (soft delete) - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can bulk delete programs",
        )

    program_service = ProgramService(db)
    result = program_service.bulk_delete_programs(
        request.program_ids, deleted_by=current_user["id"]
    )
    return BulkDeleteProgramsResponse(**result)


@router.get("/{program_id}", response_model=Program)
async def get_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get a specific program by ID"""
    program_service = ProgramService(db)
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    return program_to_schema(program)


@router.post("", response_model=Program, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=Program, status_code=status.HTTP_201_CREATED)
async def create_program(
    program_data: ProgramCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Create a new program"""
    try:
        program_service = ProgramService(db)
        program = program_service.create_program(program_data, created_by=current_user["id"])
        return program_to_schema(program)
    except HTTPException:
        # Re-raise HTTP exceptions (they already have proper status codes)
        raise
    except Exception as e:
        # Log the error and return a proper HTTP exception
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating program: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create program: {str(e)}"
        )


@router.put("/{program_id}", response_model=Program)
async def update_program(
    program_id: int,
    program_data: ProgramUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Update an existing program"""
    program_service = ProgramService(db)
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(program_id, current_user["id"]):
        # Check if user is system admin
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can update programs",
            )
    
    program = program_service.update_program(
        program_id, program_data, updated_by=current_user["id"]
    )
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    return program_to_schema(program)


@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Delete a program (soft delete)"""
    program_service = ProgramService(db)
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(program_id, current_user["id"]):
        # Check if user is system admin
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can delete programs",
            )
    
    success = program_service.delete_program(program_id, deleted_by=current_user["id"])
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )


# Program Admin endpoints
@router.get("/{program_id}/admins", response_model=List[ProgramAdmin])
async def get_program_admins(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get all admins for a program"""
    program_service = ProgramService(db)
    
    # Check if program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can view program admins",
            )
    
    admins = program_service.get_program_admins(program_id)
    return admins


@router.post("/{program_id}/admins", response_model=ProgramAdmin, status_code=status.HTTP_201_CREATED)
async def add_program_admin(
    program_id: int,
    admin_data: ProgramAdminCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Add an admin to a program"""
    program_service = ProgramService(db)
    
    # Check if program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can add program admins",
            )
    
    # Ensure program_id matches
    admin_data.program_id = program_id
    admin = program_service.add_program_admin(admin_data, created_by=current_user["id"])
    return admin


@router.put("/admins/{admin_id}", response_model=ProgramAdmin)
async def update_program_admin(
    admin_id: int,
    admin_data: ProgramAdminUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Update program admin permissions"""
    program_service = ProgramService(db)
    
    # Get admin to find program_id
    from app.models.program import ProgramAdmin as ProgramAdminModel
    admin = db.query(ProgramAdminModel).filter(ProgramAdminModel.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program admin with ID {admin_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(admin.program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can update program admins",
            )
    
    updated_admin = program_service.update_program_admin(admin_id, admin_data)
    if not updated_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program admin with ID {admin_id} not found",
        )
    return updated_admin


@router.delete("/admins/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_program_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Remove an admin from a program"""
    program_service = ProgramService(db)
    
    # Get admin to find program_id
    from app.models.program import ProgramAdmin as ProgramAdminModel
    admin = db.query(ProgramAdminModel).filter(ProgramAdminModel.id == admin_id).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program admin with ID {admin_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(admin.program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can remove program admins",
            )
    
    success = program_service.remove_program_admin(admin_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program admin with ID {admin_id} not found",
        )


# Program Participant endpoints
# NOTE: All /participants routes must come BEFORE /{program_id}/participants to avoid route conflicts
# Using explicit path without trailing slash to ensure correct matching
@router.get("/participants", response_model=List[ProgramParticipant], name="get_all_program_participants")
async def get_all_program_participants(
    status: Optional[str] = Query(None, description="Filter by status (active, paused, completed, ended)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get all participants across all programs"""
    program_service = ProgramService(db)
    participants = program_service.get_all_participants(status=status, skip=skip, limit=limit)
    # Explicitly convert to schemas to ensure proper serialization
    return [ProgramParticipant.model_validate(p) for p in participants]


@router.post(
    "/participants/bulk-from-pc-event",
    response_model=List[ProgramParticipant],
    status_code=status.HTTP_201_CREATED
)
async def bulk_import_participants_from_pc_event(
    import_data: BulkImportParticipantsFromPCEventRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Bulk import participants from a Planning Center Registration event"""
    # Check if user has permission (admin/staff only)
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can bulk import from Planning Center events",
        )
    
    program_service = ProgramService(db)
    try:
        participants = program_service.bulk_import_participants_from_pc_event(
            program_id=import_data.program_id,
            pc_event_id=import_data.pc_event_id,
            role_name=import_data.role_name,
            created_by=current_user["id"],
            status_filter=import_data.status_filter,
            update_existing=import_data.update_existing,
        )
        return participants
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk import from Planning Center event: {str(e)}"
        )


@router.post(
    "/participants/bulk-from-pc-list",
    response_model=List[ProgramParticipant],
    status_code=status.HTTP_201_CREATED
)
async def bulk_import_participants_from_pc_list(
    import_data: BulkImportParticipantsFromPCListRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Bulk import participants from a Planning Center List"""
    # Check if user has permission (admin/staff only)
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can bulk import from Planning Center lists",
        )
    
    program_service = ProgramService(db)
    try:
        participants = program_service.bulk_import_participants_from_pc_list(
            program_id=import_data.program_id,
            pc_list_id=import_data.pc_list_id,
            role_name=import_data.role_name,
            created_by=current_user["id"],
            update_existing=import_data.update_existing,
        )
        return participants
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk import from Planning Center list: {str(e)}"
        )


@router.get("/{program_id}/participants", response_model=List[ProgramParticipant])
async def get_program_participants(
    program_id: int,
    status: Optional[str] = Query(None, description="Filter by status (active, paused, completed, ended)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search by first name or last name (starts with, case-insensitive)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get participants for a program with pagination and search"""
    program_service = ProgramService(db)
    
    # Check if program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    
    participants = program_service.get_program_participants(
        program_id, status=status, skip=skip, limit=limit, search=search
    )
    return participants


@router.get("/{program_id}/participants/count")
async def get_program_participants_count(
    program_id: int,
    status: Optional[str] = Query(None, description="Filter by status (active, paused, completed, ended)"),
    search: Optional[str] = Query(None, description="Search by first name or last name (starts with, case-insensitive)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get total count of participants for a program"""
    program_service = ProgramService(db)
    
    # Check if program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    
    count = program_service.get_program_participants_count(program_id, status=status, search=search)
    return {"count": count}


@router.post("/{program_id}/participants", response_model=ProgramParticipant, status_code=status.HTTP_201_CREATED)
async def add_program_participant(
    program_id: int,
    participant_data: ProgramParticipantCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Add a participant to a program"""
    program_service = ProgramService(db)
    
    # Check if program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can add participants",
            )
    
    # Ensure program_id matches
    participant_data.program_id = program_id
    participant, error = program_service.add_participant(
        participant_data, created_by=current_user["id"]
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    return participant


@router.put("/participants/{participant_id}", response_model=ProgramParticipant)
async def update_program_participant(
    participant_id: int,
    participant_data: ProgramParticipantUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Update a program participant"""
    program_service = ProgramService(db)
    
    # Get participant to find program_id
    participant = program_service.get_participant(participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program participant with ID {participant_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(participant.program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can update participants",
            )
    
    updated_participant = program_service.update_participant(
        participant_id, participant_data, updated_by=current_user["id"]
    )
    if not updated_participant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update participant. Check role name is valid.",
        )
    return updated_participant


@router.delete("/participants/{participant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_program_participant(
    participant_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Remove a participant from a program"""
    program_service = ProgramService(db)
    
    # Get participant to find program_id
    participant = program_service.get_participant(participant_id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program participant with ID {participant_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(participant.program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can remove participants",
            )
    
    success = program_service.remove_participant(participant_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program participant with ID {participant_id} not found",
        )


# Program Pairing endpoints
@router.get("/{program_id}/pairings/count", response_model=dict)
async def get_pairing_count_for_primary(
    program_id: int,
    primary_participant_id: int = Query(..., description="Primary participant ID"),
    status: Optional[str] = Query("active", description="Filter by status (default: active)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get count of active pairings for a primary participant"""
    program_service = ProgramService(db)
    
    # Check if program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can view pairing counts",
            )
    
    count = program_service.get_pairing_count_for_primary(
        program_id,
        primary_participant_id,
        status=status
    )
    return {
        "program_id": program_id,
        "primary_participant_id": primary_participant_id,
        "count": count
    }


@router.get("/{program_id}/pairings", response_model=List[ProgramPairing])
async def get_program_pairings(
    program_id: int,
    status: Optional[str] = None,
    primary_participant_id: Optional[int] = Query(None, description="Filter by primary participant ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get all pairings for a program"""
    program_service = ProgramService(db)
    
    # Check if program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    
    pairings = program_service.get_program_pairings(
        program_id, 
        status=status,
        primary_participant_id=primary_participant_id
    )
    return pairings


@router.post("/{program_id}/pairings", response_model=ProgramPairing, status_code=status.HTTP_201_CREATED)
async def create_program_pairing(
    program_id: int,
    pairing_data: ProgramPairingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Create a pairing between participants"""
    program_service = ProgramService(db)
    
    # Check if program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can create pairings",
            )
    
    # Ensure program_id matches
    pairing_data.program_id = program_id
    pairing, error = program_service.create_pairing(
        pairing_data, created_by=current_user["id"]
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    return pairing


@router.put("/pairings/{pairing_id}", response_model=ProgramPairing)
async def update_program_pairing(
    pairing_id: int,
    pairing_data: ProgramPairingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Update a program pairing"""
    program_service = ProgramService(db)
    
    # Get pairing to find program_id
    pairing = program_service.get_pairing(pairing_id)
    if not pairing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program pairing with ID {pairing_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(pairing.program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can update pairings",
            )
    
    updated_pairing = program_service.update_pairing(
        pairing_id, pairing_data, updated_by=current_user["id"]
    )
    if not updated_pairing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program pairing with ID {pairing_id} not found",
        )
    return updated_pairing


@router.delete("/pairings/{pairing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_program_pairing(
    pairing_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Remove a program pairing"""
    program_service = ProgramService(db)
    
    # Get pairing to find program_id
    pairing = program_service.get_pairing(pairing_id)
    if not pairing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program pairing with ID {pairing_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(pairing.program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can remove pairings",
            )
    
    success = program_service.remove_pairing(pairing_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program pairing with ID {pairing_id} not found",
        )


# Program Session endpoints
@router.get("/{program_id}/sessions", response_model=List[ProgramSession])
async def get_program_sessions(
    program_id: int,
    pairing_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get all sessions for a program"""
    program_service = ProgramService(db)
    
    # Check if program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    
    sessions = program_service.get_program_sessions(program_id, pairing_id=pairing_id)
    return sessions


@router.post("/{program_id}/sessions", response_model=ProgramSession, status_code=status.HTTP_201_CREATED)
async def create_program_session(
    program_id: int,
    session_data: ProgramSessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Create a new program session"""
    program_service = ProgramService(db)
    
    # Check if program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can create sessions",
            )
    
    # Ensure program_id matches
    session_data.program_id = program_id
    session = program_service.create_session(session_data, created_by=current_user["id"])
    return session


@router.put("/sessions/{session_id}", response_model=ProgramSession)
async def update_program_session(
    session_id: int,
    session_data: ProgramSessionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Update a program session"""
    program_service = ProgramService(db)
    
    # Get session to find program_id
    session = program_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program session with ID {session_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(session.program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can update sessions",
            )
    
    updated_session = program_service.update_session(session_id, session_data)
    if not updated_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program session with ID {session_id} not found",
        )
    return updated_session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Delete a program session"""
    program_service = ProgramService(db)
    
    # Get session to find program_id
    session = program_service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program session with ID {session_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(session.program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can delete sessions",
            )
    
    success = program_service.delete_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program session with ID {session_id} not found",
        )


# Program Progress endpoints
@router.get("/{program_id}/progress", response_model=List[ProgramProgress])
async def get_program_progress(
    program_id: int,
    participant_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get progress records for a program"""
    program_service = ProgramService(db)
    
    # Check if program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    
    progress_records = program_service.get_program_progress(
        program_id, participant_id=participant_id
    )
    return progress_records


@router.post("/{program_id}/progress", response_model=ProgramProgress, status_code=status.HTTP_201_CREATED)
async def create_program_progress(
    program_id: int,
    progress_data: ProgramProgressCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Create a new progress record"""
    program_service = ProgramService(db)
    
    # Check if program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can create progress records",
            )
    
    # Ensure program_id matches
    progress_data.program_id = program_id
    progress, error = program_service.create_progress(
        progress_data, created_by=current_user["id"]
    )
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    return progress


@router.put("/progress/{progress_id}", response_model=ProgramProgress)
async def update_program_progress(
    progress_id: int,
    progress_data: ProgramProgressUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Update a progress record"""
    program_service = ProgramService(db)
    
    # Get progress to find program_id
    progress = program_service.get_progress(progress_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program progress with ID {progress_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(progress.program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can update progress records",
            )
    
    updated_progress = program_service.update_progress(progress_id, progress_data)
    if not updated_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program progress with ID {progress_id} not found",
        )
    return updated_progress


@router.delete("/progress/{progress_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program_progress(
    progress_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Delete a progress record"""
    program_service = ProgramService(db)
    
    # Get progress to find program_id
    progress = program_service.get_progress(progress_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program progress with ID {progress_id} not found",
        )
    
    # Check if user is program admin or system admin
    if not program_service.is_program_admin(progress.program_id, current_user["id"]):
        from app.api.v1.endpoints.auth import get_current_admin_user
        try:
            await get_current_admin_user(current_user=current_user)
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only program admins or system admins can delete progress records",
            )
    
    success = program_service.delete_progress(progress_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program progress with ID {progress_id} not found",
        )


# ============================================================================
# Planning Center Custom Tab Endpoints
# ============================================================================

@router.get("/planning-center/tabs/{person_id}", response_model=List[dict])
def get_planning_center_tabs(
    person_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get available Planning Center custom tabs for a person
    (Used for configuration UI to discover available tabs)
    """
    from app.services.planning_center_sync_service import PlanningCenterSyncService
    
    pc_service = PlanningCenterSyncService(db)
    try:
        tabs = pc_service.get_person_tabs(person_id)
        return tabs
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tabs: {str(e)}"
        )


@router.get("/planning-center/tabs/{tab_id}/fields", response_model=List[dict])
def get_tab_field_definitions(
    tab_id: str,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get field definitions for a custom tab
    (Used for mapping configuration UI to discover available fields)
    """
    from app.services.planning_center_sync_service import PlanningCenterSyncService
    
    pc_service = PlanningCenterSyncService(db)
    try:
        fields = pc_service.get_tab_field_definitions(tab_id)
        return fields
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch field definitions: {str(e)}"
        )


@router.post("/{program_id}/participants/bulk-from-pc-list-with-tabs")
def bulk_import_participants_from_pc_list_with_tabs(
    program_id: int,
    request: BulkImportParticipantsFromPCListRequest,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Import participants from Planning Center list using custom tab field mappings
    
    This endpoint:
    1. Validates program has tab configuration
    2. Fetches people from Planning Center list
    3. Gets custom tab data for each person
    4. Applies field mappings to determine role, status, etc.
    5. Creates participants in the program
    
    Requires program.planning_center_tab_config to be configured.
    """
    from app.services.planning_center_sync_service import PlanningCenterSyncService
    from app.services.people_service import PeopleService
    
    program_service = ProgramService(db)
    pc_service = PlanningCenterSyncService(db)
    people_service = PeopleService(db)
    
    # Validate program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found"
        )
    
    # Check user has permission
    is_admin = hasattr(current_user, 'role') and current_user.role == 'admin'
    is_program_admin = program_service.is_program_admin(program_id, current_user.id)
    
    if not is_admin and not is_program_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only program admins or system admins can import participants"
        )
    
    # Validate tab configuration exists
    if not program.planning_center_tab_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Program does not have Planning Center tab configuration. Please configure tab mappings first."
        )
    
    tab_config = program.planning_center_tab_config
    if not tab_config.get("enabled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tab import is not enabled for this program"
        )
    
    tab_slug = tab_config.get("tab_slug")
    if not tab_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tab configuration is missing tab_slug"
        )
    
    try:
        # Get people with tab data from Planning Center
        people_with_tabs = pc_service.get_list_people_with_tab_data(
            request.pc_list_id,
            tab_slug
        )
        
        imported = []
        errors = []
        
        for person in people_with_tabs:
            try:
                # Apply field mappings to get participant data
                mapped_data = pc_service.apply_tab_field_mappings(
                    person,
                    tab_config
                )
                
                # Validate role was mapped
                if "role_name" not in mapped_data:
                    errors.append({
                        "person_id": person.get("id"),
                        "name": f"{person.get('attributes', {}).get('first_name')} {person.get('attributes', {}).get('last_name')}",
                        "error": "No role could be determined from tab data"
                    })
                    continue
                
                # Sync person to local database if configured
                if tab_config.get("sync_on_import", True):
                    local_person = people_service.sync_person_from_pc(person)
                    people_id = local_person.id
                else:
                    # Try to find existing person by PC ID
                    pc_person_id = person.get("id")
                    local_person = people_service.get_by_pc_person_id(pc_person_id)
                    if not local_person:
                        errors.append({
                            "person_id": pc_person_id,
                            "name": f"{person.get('attributes', {}).get('first_name')} {person.get('attributes', {}).get('last_name')}",
                            "error": "Person not found locally and sync_on_import is disabled"
                        })
                        continue
                    people_id = local_person.id
                
                # Create participant with mapped data
                participant_data = {
                    "program_id": program_id,
                    "people_id": people_id,
                    **mapped_data
                }
                
                # Check if should update existing
                update_existing = request.update_existing if hasattr(request, 'update_existing') else tab_config.get("update_existing", False)
                
                participant, error = program_service.add_participant(
                    participant_data,
                    current_user.id
                )
                
                if participant:
                    imported.append({
                        "participant_id": participant.id,
                        "people_id": people_id,
                        "name": f"{person.get('attributes', {}).get('first_name')} {person.get('attributes', {}).get('last_name')}",
                        "role": mapped_data.get("role_name"),
                        "status": mapped_data.get("status")
                    })
                else:
                    errors.append({
                        "person_id": person.get("id"),
                        "name": f"{person.get('attributes', {}).get('first_name')} {person.get('attributes', {}).get('last_name')}",
                        "error": error or "Failed to create participant"
                    })
            
            except Exception as e:
                errors.append({
                    "person_id": person.get("id"),
                    "name": f"{person.get('attributes', {}).get('first_name', 'Unknown')} {person.get('attributes', {}).get('last_name', '')}",
                    "error": str(e)
                })
        
        return {
            "imported_count": len(imported),
            "error_count": len(errors),
            "imported": imported,
            "errors": errors
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )
