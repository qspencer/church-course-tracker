"""
Program API endpoints
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import get_current_active_user, get_current_admin_user
from app.core.database import get_db
from app.schemas.program import Program, ProgramCreate, ProgramUpdate
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
    return [program_to_schema(program) for program in programs]


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
    program_service = ProgramService(db)
    program = program_service.create_program(program_data, created_by=current_user["id"])
    return program_to_schema(program)


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
    if not program_service.is_program_admin(admin.program_id, current_user.id):
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
    if not program_service.is_program_admin(admin.program_id, current_user.id):
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
@router.get("/{program_id}/participants", response_model=List[ProgramParticipant])
async def get_program_participants(
    program_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get all participants for a program"""
    program_service = ProgramService(db)
    
    # Check if program exists
    program = program_service.get_program(program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found",
        )
    
    participants = program_service.get_program_participants(program_id, status=status)
    return participants


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
    if not program_service.is_program_admin(participant.program_id, current_user.id):
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
    if not program_service.is_program_admin(participant.program_id, current_user.id):
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
@router.get("/{program_id}/pairings", response_model=List[ProgramPairing])
async def get_program_pairings(
    program_id: int,
    status: Optional[str] = None,
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
    
    pairings = program_service.get_program_pairings(program_id, status=status)
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
    if not program_service.is_program_admin(pairing.program_id, current_user.id):
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
    if not program_service.is_program_admin(pairing.program_id, current_user.id):
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
    if not program_service.is_program_admin(session.program_id, current_user.id):
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
    if not program_service.is_program_admin(session.program_id, current_user.id):
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
    if not program_service.is_program_admin(progress.program_id, current_user.id):
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
    if not program_service.is_program_admin(progress.program_id, current_user.id):
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

