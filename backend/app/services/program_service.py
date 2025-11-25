"""
Program service layer for managing programs, participants, pairings, and related operations
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.program import (
    Program as ProgramModel,
    ProgramAdmin as ProgramAdminModel,
    ProgramParticipant as ProgramParticipantModel,
    ProgramPairing as ProgramPairingModel,
)
from app.models.program_progress import (
    ProgramSession as ProgramSessionModel,
    ProgramProgress as ProgramProgressModel,
)
from app.schemas.program import ProgramCreate, ProgramUpdate
from app.schemas.program_admin import ProgramAdminCreate, ProgramAdminUpdate
from app.schemas.program_participant import (
    ProgramParticipantCreate,
    ProgramParticipantUpdate,
)
from app.schemas.program_pairing import ProgramPairingCreate, ProgramPairingUpdate
from app.schemas.program_session import (
    ProgramSessionCreate,
    ProgramSessionUpdate,
)
from app.schemas.program_progress import (
    ProgramProgressCreate,
    ProgramProgressUpdate,
)
from app.services.audit_service import AuditService
from app.services.people_service import PeopleService
from fastapi import HTTPException, status


class ProgramService:
    """Service for program operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_programs(
        self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
    ) -> List[ProgramModel]:
        """Get all programs with pagination and optional filtering"""
        try:
            query = self.db.query(ProgramModel)
            if is_active is not None:
                query = query.filter(ProgramModel.is_active == is_active)
            
            from sqlalchemy.orm import noload, joinedload
            
            return (
                query.options(
                    joinedload(ProgramModel.created_by_user),
                    joinedload(ProgramModel.updated_by_user),
                    noload(ProgramModel.program_admins),
                    noload(ProgramModel.program_participants),
                    noload(ProgramModel.program_content),
                    noload(ProgramModel.program_pairings),
                    noload(ProgramModel.program_sessions),
                )
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            import logging
            logging.error(f"Error fetching programs: {e}")
            return []

    def get_program(self, program_id: int) -> Optional[ProgramModel]:
        """Get a specific program by ID"""
        from sqlalchemy.orm import joinedload
        return (
            self.db.query(ProgramModel)
            .options(
                joinedload(ProgramModel.created_by_user),
                joinedload(ProgramModel.updated_by_user),
            )
            .filter(ProgramModel.id == program_id)
            .first()
        )

    def create_program(
        self, program_data: ProgramCreate, created_by: Optional[int] = None
    ) -> ProgramModel:
        """Create a new program"""
        program_dict = program_data.model_dump()
        program_dict["created_by"] = created_by
        program_dict["updated_by"] = created_by
        
        program = ProgramModel(**program_dict)
        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)
        
        # Eagerly load relationships for response
        from sqlalchemy.orm import joinedload
        program = (
            self.db.query(ProgramModel)
            .options(
                joinedload(ProgramModel.created_by_user),
                joinedload(ProgramModel.updated_by_user),
            )
            .filter(ProgramModel.id == program.id)
            .first()
        )
        
        # Create audit log
        if created_by:
            AuditService(self.db).log_change(
                table_name="programs",
                record_id=program.id,
                action="insert",
                changed_by=created_by,
                new_values={"title": program.title},
            )
        
        return program

    def update_program(
        self, program_id: int, program_data: ProgramUpdate, updated_by: Optional[int] = None
    ) -> Optional[ProgramModel]:
        """Update an existing program"""
        program = self.get_program(program_id)
        if not program:
            return None
        
        update_dict = program_data.model_dump(exclude_unset=True)
        update_dict["updated_by"] = updated_by
        
        for key, value in update_dict.items():
            setattr(program, key, value)
        
        self.db.commit()
        self.db.refresh(program)
        
        # Create audit log
        if updated_by:
            AuditService(self.db).log_change(
                table_name="programs",
                record_id=program.id,
                action="update",
                changed_by=updated_by,
                new_values={"title": program.title},
            )
        
        return program

    def delete_program(self, program_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete a program (soft delete by setting is_active=False)"""
        program = self.get_program(program_id)
        if not program:
            return False
        
        program.is_active = False
        program.updated_by = deleted_by
        self.db.commit()
        
        # Create audit log
        if deleted_by:
            AuditService(self.db).log_change(
                table_name="programs",
                record_id=program.id,
                action="delete",
                changed_by=deleted_by,
                old_values={"title": program.title, "is_active": True},
                new_values={"is_active": False},
            )
        
        return True

    def validate_role_name(self, program_id: int, role_name: str) -> bool:
        """Validate that a role name exists in the program's role definitions"""
        program = self.get_program(program_id)
        if not program or not program.role_definitions:
            return False
        
        role_names = [role.get("name") for role in program.role_definitions]
        return role_name in role_names

    def validate_pairing_constraints(
        self, program_id: int, primary_participant_id: int
    ) -> tuple[bool, Optional[str]]:
        """Validate pairing constraints based on relationship_config"""
        program = self.get_program(program_id)
        if not program or not program.relationship_config:
            return True, None
        
        config = program.relationship_config
        
        # Check if multiple secondary participants are allowed
        if not config.get("allow_multiple_secondary", True):
            # Count existing active pairings for this primary participant
            existing_pairings = (
                self.db.query(ProgramPairingModel)
                .filter(
                    ProgramPairingModel.program_id == program_id,
                    ProgramPairingModel.primary_participant_id == primary_participant_id,
                    ProgramPairingModel.status == "active",
                )
                .count()
            )
            if existing_pairings > 0:
                return False, "Multiple secondary participants not allowed for this program"
        
        # Check max secondary per primary
        max_secondary = config.get("max_secondary_per_primary")
        if max_secondary is not None:
            existing_pairings = (
                self.db.query(ProgramPairingModel)
                .filter(
                    ProgramPairingModel.program_id == program_id,
                    ProgramPairingModel.primary_participant_id == primary_participant_id,
                    ProgramPairingModel.status == "active",
                )
                .count()
            )
            if existing_pairings >= max_secondary:
                return (
                    False,
                    f"Maximum of {max_secondary} secondary participants per primary participant",
                )
        
        return True, None

    # Program Admin methods
    def get_program_admins(self, program_id: int) -> List[ProgramAdminModel]:
        """Get all admins for a program"""
        return (
            self.db.query(ProgramAdminModel)
            .filter(ProgramAdminModel.program_id == program_id)
            .all()
        )

    def is_program_admin(self, program_id: int, user_id: int) -> bool:
        """Check if a user is an admin of a program"""
        try:
            return (
                self.db.query(ProgramAdminModel)
                .filter(
                    ProgramAdminModel.program_id == program_id,
                    ProgramAdminModel.user_id == user_id,
                )
                .first()
                is not None
            )
        except Exception:
            # If program_admins table doesn't exist, return False
            # System admins can still access via the admin check in the endpoint
            return False

    def add_program_admin(
        self, admin_data: ProgramAdminCreate, created_by: Optional[int] = None
    ) -> ProgramAdminModel:
        """Add an admin to a program"""
        admin_dict = admin_data.model_dump()
        admin_dict["created_by"] = created_by
        
        admin = ProgramAdminModel(**admin_dict)
        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)
        return admin

    def update_program_admin(
        self, admin_id: int, admin_data: ProgramAdminUpdate
    ) -> Optional[ProgramAdminModel]:
        """Update program admin permissions"""
        admin = (
            self.db.query(ProgramAdminModel)
            .filter(ProgramAdminModel.id == admin_id)
            .first()
        )
        if not admin:
            return None
        
        update_dict = admin_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(admin, key, value)
        
        self.db.commit()
        self.db.refresh(admin)
        return admin

    def remove_program_admin(self, admin_id: int) -> bool:
        """Remove an admin from a program"""
        admin = (
            self.db.query(ProgramAdminModel)
            .filter(ProgramAdminModel.id == admin_id)
            .first()
        )
        if not admin:
            return False
        
        self.db.delete(admin)
        self.db.commit()
        return True

    # Program Participant methods
    def get_program_participants(
        self, program_id: int, status: Optional[str] = None
    ) -> List[ProgramParticipantModel]:
        """Get all participants for a program"""
        query = self.db.query(ProgramParticipantModel).filter(
            ProgramParticipantModel.program_id == program_id
        )
        if status:
            query = query.filter(ProgramParticipantModel.status == status)
        return query.all()

    def get_all_participants(
        self, status: Optional[str] = None, skip: int = 0, limit: int = 100
    ) -> List[ProgramParticipantModel]:
        """Get all participants across all programs"""
        query = self.db.query(ProgramParticipantModel)
        if status:
            query = query.filter(ProgramParticipantModel.status == status)
        return query.offset(skip).limit(limit).all()

    def get_participant(self, participant_id: int) -> Optional[ProgramParticipantModel]:
        """Get a specific participant by ID"""
        return (
            self.db.query(ProgramParticipantModel)
            .filter(ProgramParticipantModel.id == participant_id)
            .first()
        )

    def add_participant(
        self,
        participant_data: ProgramParticipantCreate,
        created_by: Optional[int] = None,
    ) -> tuple[Optional[ProgramParticipantModel], Optional[str]]:
        """Add a participant to a program with validation"""
        # Validate role name
        if not self.validate_role_name(
            participant_data.program_id, participant_data.role_name
        ):
            return None, f"Invalid role name: {participant_data.role_name}"
        
        # Check if participant already exists
        existing = (
            self.db.query(ProgramParticipantModel)
            .filter(
                ProgramParticipantModel.program_id == participant_data.program_id,
                ProgramParticipantModel.people_id == participant_data.people_id,
                ProgramParticipantModel.status == "active",
            )
            .first()
        )
        if existing:
            return None, "Participant already exists in this program"
        
        participant_dict = participant_data.model_dump()
        participant_dict["created_by"] = created_by
        participant_dict["updated_by"] = created_by
        
        participant = ProgramParticipantModel(**participant_dict)
        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)
        return participant, None

    def update_participant(
        self,
        participant_id: int,
        participant_data: ProgramParticipantUpdate,
        updated_by: Optional[int] = None,
    ) -> Optional[ProgramParticipantModel]:
        """Update a participant"""
        participant = self.get_participant(participant_id)
        if not participant:
            return None
        
        update_dict = participant_data.model_dump(exclude_unset=True)
        
        # Validate role name if being updated
        if "role_name" in update_dict:
            if not self.validate_role_name(participant.program_id, update_dict["role_name"]):
                return None
        
        update_dict["updated_by"] = updated_by
        for key, value in update_dict.items():
            setattr(participant, key, value)
        
        self.db.commit()
        self.db.refresh(participant)
        return participant

    def remove_participant(self, participant_id: int) -> bool:
        """Remove a participant (soft delete by setting status to 'ended')"""
        participant = self.get_participant(participant_id)
        if not participant:
            return False
        
        participant.status = "ended"
        participant.end_date = datetime.now(timezone.utc)
        self.db.commit()
        return True

    # Program Pairing methods
    def get_program_pairings(
        self, program_id: int, status: Optional[str] = None
    ) -> List[ProgramPairingModel]:
        """Get all pairings for a program"""
        query = self.db.query(ProgramPairingModel).filter(
            ProgramPairingModel.program_id == program_id
        )
        if status:
            query = query.filter(ProgramPairingModel.status == status)
        return query.all()

    def get_pairing(self, pairing_id: int) -> Optional[ProgramPairingModel]:
        """Get a specific pairing by ID"""
        return (
            self.db.query(ProgramPairingModel)
            .filter(ProgramPairingModel.id == pairing_id)
            .first()
        )

    def create_pairing(
        self,
        pairing_data: ProgramPairingCreate,
        created_by: Optional[int] = None,
    ) -> tuple[Optional[ProgramPairingModel], Optional[str]]:
        """Create a pairing with validation"""
        # Validate participants exist and are in the program
        primary = self.get_participant(pairing_data.primary_participant_id)
        secondary = self.get_participant(pairing_data.secondary_participant_id)
        
        if not primary or primary.program_id != pairing_data.program_id:
            return None, "Primary participant not found or not in program"
        if not secondary or secondary.program_id != pairing_data.program_id:
            return None, "Secondary participant not found or not in program"
        
        # Validate pairing constraints
        is_valid, error_msg = self.validate_pairing_constraints(
            pairing_data.program_id, pairing_data.primary_participant_id
        )
        if not is_valid:
            return None, error_msg
        
        pairing_dict = pairing_data.model_dump()
        pairing_dict["created_by"] = created_by
        pairing_dict["updated_by"] = created_by
        
        pairing = ProgramPairingModel(**pairing_dict)
        self.db.add(pairing)
        self.db.commit()
        self.db.refresh(pairing)
        return pairing, None

    def update_pairing(
        self,
        pairing_id: int,
        pairing_data: ProgramPairingUpdate,
        updated_by: Optional[int] = None,
    ) -> Optional[ProgramPairingModel]:
        """Update a pairing"""
        pairing = self.get_pairing(pairing_id)
        if not pairing:
            return None
        
        update_dict = pairing_data.model_dump(exclude_unset=True)
        update_dict["updated_by"] = updated_by
        
        for key, value in update_dict.items():
            setattr(pairing, key, value)
        
        self.db.commit()
        self.db.refresh(pairing)
        return pairing

    def remove_pairing(self, pairing_id: int) -> bool:
        """Remove a pairing (soft delete by setting status to 'ended')"""
        pairing = self.get_pairing(pairing_id)
        if not pairing:
            return False
        
        pairing.status = "ended"
        pairing.end_date = datetime.now(timezone.utc)
        self.db.commit()
        return True

    # Program Session methods
    def get_program_sessions(
        self, program_id: int, pairing_id: Optional[int] = None
    ) -> List[ProgramSessionModel]:
        """Get all sessions for a program"""
        query = self.db.query(ProgramSessionModel).filter(
            ProgramSessionModel.program_id == program_id
        )
        if pairing_id:
            query = query.filter(ProgramSessionModel.pairing_id == pairing_id)
        return query.order_by(ProgramSessionModel.session_date.desc()).all()

    def get_session(self, session_id: int) -> Optional[ProgramSessionModel]:
        """Get a specific session by ID"""
        return (
            self.db.query(ProgramSessionModel)
            .filter(ProgramSessionModel.id == session_id)
            .first()
        )

    def create_session(
        self,
        session_data: ProgramSessionCreate,
        created_by: Optional[int] = None,
    ) -> ProgramSessionModel:
        """Create a new session"""
        session_dict = session_data.model_dump()
        session_dict["created_by"] = created_by
        
        session = ProgramSessionModel(**session_dict)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def update_session(
        self,
        session_id: int,
        session_data: ProgramSessionUpdate,
    ) -> Optional[ProgramSessionModel]:
        """Update a session"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        update_dict = session_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(session, key, value)
        
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete_session(self, session_id: int) -> bool:
        """Delete a session"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        return True

    # Program Progress methods
    def get_program_progress(
        self, program_id: int, participant_id: Optional[int] = None
    ) -> List[ProgramProgressModel]:
        """Get progress records for a program"""
        query = self.db.query(ProgramProgressModel).filter(
            ProgramProgressModel.program_id == program_id
        )
        if participant_id:
            query = query.filter(ProgramProgressModel.participant_id == participant_id)
        return query.order_by(ProgramProgressModel.created_at.desc()).all()

    def get_progress(self, progress_id: int) -> Optional[ProgramProgressModel]:
        """Get a specific progress record by ID"""
        return (
            self.db.query(ProgramProgressModel)
            .filter(ProgramProgressModel.id == progress_id)
            .first()
        )

    def create_progress(
        self,
        progress_data: ProgramProgressCreate,
        created_by: Optional[int] = None,
    ) -> tuple[Optional[ProgramProgressModel], Optional[str]]:
        """Create a new progress record"""
        # Validate participant exists and is in the program
        participant = self.get_participant(progress_data.participant_id)
        if not participant or participant.program_id != progress_data.program_id:
            return None, "Participant not found or not in program"
        
        progress_dict = progress_data.model_dump()
        progress_dict["created_by"] = created_by
        
        progress = ProgramProgressModel(**progress_dict)
        self.db.add(progress)
        
        # Update participant's progress percentage if needed
        if progress_data.progress_type == "content_completion":
            # Could calculate overall progress here
            pass
        
        self.db.commit()
        self.db.refresh(progress)
        return progress, None

    def update_progress(
        self,
        progress_id: int,
        progress_data: ProgramProgressUpdate,
    ) -> Optional[ProgramProgressModel]:
        """Update a progress record"""
        progress = self.get_progress(progress_id)
        if not progress:
            return None
        
        update_dict = progress_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(progress, key, value)
        
        self.db.commit()
        self.db.refresh(progress)
        return progress

    def delete_progress(self, progress_id: int) -> bool:
        """Delete a progress record"""
        progress = self.get_progress(progress_id)
        if not progress:
            return False
        
        self.db.delete(progress)
        self.db.commit()
        return True

    def _get_people_id_from_pc_person_id(self, pc_person_id: str) -> int:
        """Get local people_id from Planning Center person ID"""
        people_service = PeopleService(self.db)
        person = people_service.get_person_by_pc_id(pc_person_id)
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person with Planning Center ID '{pc_person_id}' not found locally. Please sync people from Planning Center first."
            )
        return person.id

    def bulk_import_participants_from_pc_event(
        self,
        program_id: int,
        pc_event_id: str,
        role_name: str,
        created_by: Optional[int] = None,
        status_filter: Optional[List[str]] = None,
        update_existing: bool = True,
    ) -> List[ProgramParticipantModel]:
        """
        Bulk import participants from a Planning Center Registration event
        
        Args:
            program_id: The program to add participants to
            pc_event_id: Planning Center event ID to get registrations from
            role_name: The role name for imported participants
            created_by: User creating the participants
            status_filter: Only import registrations with these statuses (default: ['registered', 'confirmed'])
            update_existing: Whether to update existing participants (default: True)
        
        Returns:
            List of created/updated participants
        """
        from app.services.planning_center_sync_service import PlanningCenterSyncService
        
        # Validate program exists
        program = self.get_program(program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found"
            )

        # Validate role name
        if not self.validate_role_name(program_id, role_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role name '{role_name}' for this program"
            )

        # Get registrations from Planning Center
        pc_service = PlanningCenterSyncService(self.db)
        try:
            registrations = pc_service.get_event_registrations(pc_event_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch registrations from Planning Center: {str(e)}"
            )

        if not registrations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No registrations found for Planning Center event '{pc_event_id}'"
            )

        # Filter by status if specified
        if status_filter is None:
            status_filter = ['registered', 'confirmed']
        
        # Filter registrations by status (handle both JSON API and flat formats)
        filtered_registrations = []
        for reg in registrations:
            # Handle both JSON API format and flat format
            if 'attributes' in reg:
                reg_status = reg.get('attributes', {}).get('status', '')
            else:
                reg_status = reg.get('status', '')
            
            if reg_status.lower() in [s.lower() for s in status_filter]:
                filtered_registrations.append(reg)
        
        registrations = filtered_registrations

        if not registrations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No registrations found with status in {status_filter}"
            )

        participants = []
        errors = []
        
        for reg in registrations:
            try:
                # Extract registration data
                # Handle both JSON API format (with attributes/relationships) and flat format
                if 'attributes' in reg or 'relationships' in reg:
                    # JSON API format
                    reg_attributes = reg.get('attributes', {})
                    # Try relationships first, then fallback to direct person_id
                    pc_person_id = (
                        reg.get('relationships', {}).get('person', {}).get('data', {}).get('id')
                        or reg_attributes.get('person_id')
                        or reg.get('person_id')
                    )
                else:
                    # Flat format (after transformation)
                    reg_attributes = reg
                    pc_person_id = reg.get('person_id')
                
                if not pc_person_id:
                    errors.append(f"Registration missing person ID: {reg}")
                    continue

                # Get local people_id
                try:
                    people_id = self._get_people_id_from_pc_person_id(pc_person_id)
                except HTTPException:
                    errors.append(f"Person {pc_person_id} not found locally")
                    continue

                # Check if participant already exists
                existing = (
                    self.db.query(ProgramParticipantModel)
                    .filter(
                        ProgramParticipantModel.program_id == program_id,
                        ProgramParticipantModel.people_id == people_id,
                        ProgramParticipantModel.status == "active",
                    )
                    .first()
                )
                
                if existing:
                    if update_existing:
                        # Update existing participant's role if different
                        if existing.role_name != role_name:
                            existing.role_name = role_name
                            existing.updated_by = created_by
                            self.db.commit()
                            self.db.refresh(existing)
                        participants.append(existing)
                    # If not updating existing, skip
                else:
                    # Create new participant
                    participant_data = ProgramParticipantCreate(
                        program_id=program_id,
                        people_id=people_id,
                        role_name=role_name,
                        start_date=datetime.now(timezone.utc),
                        status="active",
                    )
                    participant, error = self.add_participant(participant_data, created_by=created_by)
                    if participant:
                        participants.append(participant)
                    elif error:
                        errors.append(f"Person {pc_person_id}: {error}")
            except Exception as e:
                errors.append(f"Registration {reg.get('id', 'unknown')}: {str(e)}")
                continue

        if errors:
            # Log errors but still return successful participants
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Bulk import from PC event had {len(errors)} errors: {errors}")

        return participants

    def bulk_import_participants_from_pc_list(
        self,
        program_id: int,
        pc_list_id: str,
        role_name: str,
        created_by: Optional[int] = None,
        update_existing: bool = True,
    ) -> List[ProgramParticipantModel]:
        """
        Bulk import participants from a Planning Center List
        
        Args:
            program_id: The program to add participants to
            pc_list_id: Planning Center list ID to get people from
            role_name: The role name for imported participants
            created_by: User creating the participants
            update_existing: Whether to update existing participants (default: True)
        
        Returns:
            List of created/updated participants
        """
        from app.services.planning_center_sync_service import PlanningCenterSyncService
        
        # Validate program exists
        program = self.get_program(program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found"
            )

        # Validate role name
        if not self.validate_role_name(program_id, role_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role name '{role_name}' for this program"
            )

        # Get list members from Planning Center
        pc_service = PlanningCenterSyncService(self.db)
        try:
            pc_people = pc_service.get_list_people(pc_list_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch people from Planning Center list: {str(e)}"
            )

        if not pc_people:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No people found in Planning Center list '{pc_list_id}'"
            )

        participants = []
        errors = []
        
        for pc_person in pc_people:
            try:
                pc_person_id = pc_person.get('id')
                if not pc_person_id:
                    continue

                # Get local people_id
                try:
                    people_id = self._get_people_id_from_pc_person_id(pc_person_id)
                except HTTPException:
                    # If person not found locally, sync them first
                    try:
                        people_service = PeopleService(self.db)
                        people_service.sync_from_planning_center(pc_person, updated_by=created_by)
                        people_id = self._get_people_id_from_pc_person_id(pc_person_id)
                    except Exception as sync_error:
                        errors.append(f"Person {pc_person_id}: Failed to sync - {str(sync_error)}")
                        continue

                # Check if participant already exists
                existing = (
                    self.db.query(ProgramParticipantModel)
                    .filter(
                        ProgramParticipantModel.program_id == program_id,
                        ProgramParticipantModel.people_id == people_id,
                        ProgramParticipantModel.status == "active",
                    )
                    .first()
                )
                
                if existing:
                    if update_existing:
                        # Update existing participant's role if different
                        if existing.role_name != role_name:
                            existing.role_name = role_name
                            existing.updated_by = created_by
                            self.db.commit()
                            self.db.refresh(existing)
                        participants.append(existing)
                    # If not updating existing, skip
                else:
                    # Create new participant
                    participant_data = ProgramParticipantCreate(
                        program_id=program_id,
                        people_id=people_id,
                        role_name=role_name,
                        start_date=datetime.now(timezone.utc),
                        status="active",
                    )
                    participant, error = self.add_participant(participant_data, created_by=created_by)
                    if participant:
                        participants.append(participant)
                    elif error:
                        errors.append(f"Person {pc_person_id}: {error}")
            except Exception as e:
                errors.append(f"Person {pc_person.get('id', 'unknown')}: {str(e)}")
                continue

        if errors:
            # Log errors but still return successful participants
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Bulk import from PC list had {len(errors)} errors: {errors}")

        return participants

