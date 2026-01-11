"""
CourseEnrollment service layer (Maps to Planning Center Registrations)
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session, selectinload, defer

from app.models.enrollment import CourseEnrollment as CourseEnrollmentModel
from app.schemas.enrollment import (CourseEnrollmentCreate,
                                    CourseEnrollmentUpdate)
from app.services.audit_service import AuditService
from app.services.people_service import PeopleService
from app.services.course_service import CourseService
from fastapi import HTTPException, status


class CourseEnrollmentService:
    """Service for course enrollment operations - Maps to Planning Center Registrations"""

    def __init__(self, db: Session):
        self.db = db

    def get_enrollments(
        self,
        skip: int = 0,
        limit: int = 100,
        course_id: Optional[int] = None,
        people_id: Optional[int] = None,
        status: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = "asc",
    ) -> List[CourseEnrollmentModel]:
        """Get enrollments with optional filtering and sorting"""
        from sqlalchemy import desc, asc
        
        # Only load relationships that exist - avoid course_instance if column doesn't exist
        query = (
            self.db.query(CourseEnrollmentModel)
            .options(
                selectinload(CourseEnrollmentModel.people),
                selectinload(CourseEnrollmentModel.course),  # Uses course_id which exists
            )
        )

        if course_id:
            query = query.filter(CourseEnrollmentModel.course_id == course_id)
        if people_id:
            query = query.filter(CourseEnrollmentModel.people_id == people_id)
        if status:
            query = query.filter(CourseEnrollmentModel.status == status)

        # Handle sorting
        if sort:
            # Map frontend field names to model column names
            sort_mapping = {
                "enrolled_at": CourseEnrollmentModel.enrollment_date,
                "enrollment_date": CourseEnrollmentModel.enrollment_date,
                "created_at": CourseEnrollmentModel.created_at,
                "updated_at": CourseEnrollmentModel.updated_at,
                "status": CourseEnrollmentModel.status,
            }
            
            sort_column = sort_mapping.get(sort.lower())
            if sort_column:
                if order and order.lower() == "desc":
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))
            else:
                # Default to enrollment_date desc if sort field not recognized
                query = query.order_by(desc(CourseEnrollmentModel.enrollment_date))
        else:
            # Default sorting by enrollment_date desc
            query = query.order_by(desc(CourseEnrollmentModel.enrollment_date))

        return query.offset(skip).limit(limit).all()

    def get_enrollment(self, enrollment_id: int) -> Optional[CourseEnrollmentModel]:
        """Get a specific enrollment by ID"""
        return (
            self.db.query(CourseEnrollmentModel)
            .options(
                selectinload(CourseEnrollmentModel.people),
                selectinload(CourseEnrollmentModel.course),
            )
            .filter(CourseEnrollmentModel.id == enrollment_id)
            .first()
        )

    def get_enrollment_by_pc_registration_id(
        self, pc_registration_id: str
    ) -> Optional[CourseEnrollmentModel]:
        """Get enrollment by Planning Center registration ID"""
        return (
            self.db.query(CourseEnrollmentModel)
            .options(
                selectinload(CourseEnrollmentModel.people),
                selectinload(CourseEnrollmentModel.course),
            )
            .filter(
                CourseEnrollmentModel.planning_center_registration_id
                == pc_registration_id
            )
            .first()
        )

    def create_enrollment(
        self, enrollment: CourseEnrollmentCreate, created_by: Optional[int] = None
    ) -> CourseEnrollmentModel:
        """Create a new enrollment"""
        enrollment_dict = enrollment.dict()
        # Remove person_id if present (we use people_id in the model)
        enrollment_dict.pop('person_id', None)
        # Ensure people_id is set
        if not enrollment_dict.get('people_id'):
            raise ValueError("people_id is required")
        
        db_enrollment = CourseEnrollmentModel(**enrollment_dict)
        db_enrollment.created_at = datetime.utcnow()
        db_enrollment.updated_at = datetime.utcnow()
        db_enrollment.created_by = created_by

        self.db.add(db_enrollment)
        self.db.commit()
        self.db.refresh(db_enrollment)
        AuditService(self.db).log_change(
            table_name=CourseEnrollmentModel.__tablename__,
            record_id=db_enrollment.id,
            action="insert",
            changed_by=created_by,
            new_values=AuditService.serialize_model(db_enrollment),
        )
        return db_enrollment

    def bulk_enroll(
        self, course_id: int, people_ids: List[int], created_by: Optional[int] = None
    ) -> List[CourseEnrollmentModel]:
        """Bulk enroll multiple people in a course"""
        enrollments = []
        for people_id in people_ids:
            enrollment_data = CourseEnrollmentCreate(
                course_id=course_id,
                people_id=people_id,
                enrollment_date=datetime.utcnow(),
            )
            enrollment = self.create_enrollment(enrollment_data, created_by=created_by)
            enrollments.append(enrollment)
        return enrollments

    def update_enrollment(
        self,
        enrollment_id: int,
        enrollment_update: CourseEnrollmentUpdate,
        updated_by: Optional[int] = None,
    ) -> Optional[CourseEnrollmentModel]:
        """Update an existing enrollment"""
        db_enrollment = self.get_enrollment(enrollment_id)
        if not db_enrollment:
            return None

        old_values = AuditService.serialize_model(db_enrollment)
        update_data = enrollment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_enrollment, field, value)

        db_enrollment.updated_at = datetime.utcnow()
        db_enrollment.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_enrollment)
        AuditService(self.db).log_change(
            table_name=CourseEnrollmentModel.__tablename__,
            record_id=db_enrollment.id,
            action="update",
            changed_by=updated_by,
            old_values=old_values,
            new_values=AuditService.serialize_model(db_enrollment),
        )
        return db_enrollment

    def delete_enrollment(
        self, enrollment_id: int, deleted_by: Optional[int] = None
    ) -> bool:
        """Delete an enrollment"""
        db_enrollment = self.get_enrollment(enrollment_id)
        if not db_enrollment:
            return False
        old_values = AuditService.serialize_model(db_enrollment)
        record_id = db_enrollment.id

        self.db.delete(db_enrollment)
        self.db.commit()
        AuditService(self.db).log_change(
            table_name=CourseEnrollmentModel.__tablename__,
            record_id=record_id,
            action="delete",
            changed_by=deleted_by,
            old_values=old_values,
        )
        return True

    def sync_from_planning_center(
        self, pc_registration_data: dict, updated_by: Optional[int] = None
    ) -> CourseEnrollmentModel:
        """Sync enrollment data from Planning Center registration"""
        pc_registration_id = pc_registration_data.get("id")

        # Check if enrollment already exists
        existing_enrollment = self.get_enrollment_by_pc_registration_id(
            pc_registration_id
        )

        if existing_enrollment:
            # Update existing enrollment
            existing_enrollment.registration_status = pc_registration_data.get("status")
            existing_enrollment.registration_notes = pc_registration_data.get("notes")
            existing_enrollment.updated_at = datetime.utcnow()
            existing_enrollment.updated_by = updated_by
            self.db.commit()
            self.db.refresh(existing_enrollment)
            return existing_enrollment
        else:
            # Create new enrollment (requires people_id and course_id to be resolved)
            # This would typically be called after people and courses are synced
            enrollment_data = CourseEnrollmentCreate(
                people_id=0,  # This would need to be resolved from PC person ID
                course_id=0,  # This would need to be resolved from PC event ID
                planning_center_registration_id=pc_registration_id,
                registration_status=pc_registration_data.get("status"),
                registration_notes=pc_registration_data.get("notes"),
                enrollment_date=pc_registration_data.get(
                    "created_at", datetime.utcnow()
                ),
            )
            return self.create_enrollment(enrollment_data, created_by=updated_by)

    def update_progress(
        self,
        enrollment_id: int,
        progress_percentage: float,
        updated_by: Optional[int] = None,
    ) -> Optional[CourseEnrollmentModel]:
        """Update enrollment progress percentage"""
        db_enrollment = self.get_enrollment(enrollment_id)
        if not db_enrollment:
            return None

        old_values = AuditService.serialize_model(db_enrollment)
        db_enrollment.progress_percentage = progress_percentage
        if progress_percentage >= 100.0:
            db_enrollment.status = "completed"
            db_enrollment.completion_date = datetime.utcnow()
        elif progress_percentage > 0.0:
            db_enrollment.status = "in_progress"

        db_enrollment.updated_at = datetime.utcnow()
        db_enrollment.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_enrollment)
        AuditService(self.db).log_change(
            table_name=CourseEnrollmentModel.__tablename__,
            record_id=db_enrollment.id,
            action="update",
            changed_by=updated_by,
            old_values=old_values,
            new_values=AuditService.serialize_model(db_enrollment),
        )
        return db_enrollment

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

    def _map_pc_status_to_enrollment_status(self, pc_status: str) -> str:
        """Map Planning Center registration status to enrollment status"""
        status_mapping = {
            "registered": "enrolled",
            "confirmed": "enrolled",
            "waitlisted": "enrolled",  # Could be a separate status, but using enrolled for now
            "cancelled": "dropped",
            "declined": "dropped",
        }
        return status_mapping.get(pc_status.lower(), "enrolled")

    def bulk_enroll_from_pc_event(
        self,
        course_id: int,
        pc_event_id: str,
        created_by: Optional[int] = None,
        status_filter: Optional[List[str]] = None,
        update_existing: bool = True,
    ) -> List[CourseEnrollmentModel]:
        """
        Bulk enroll people based on Planning Center Registration event
        
        Args:
            course_id: The course to enroll people in
            pc_event_id: Planning Center event ID to get registrations from
            created_by: User creating the enrollments
            status_filter: Only enroll registrations with these statuses (default: ['registered', 'confirmed'])
            update_existing: Whether to update existing enrollments (default: True)
        
        Returns:
            List of created/updated enrollments
        """
        from app.services.planning_center_sync_service import PlanningCenterSyncService
        
        # Validate course exists
        course_service = CourseService(self.db)
        course = course_service.get_course(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with ID {course_id} not found"
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

        enrollments = []
        errors = []
        
        for reg in registrations:
            try:
                # Extract registration data
                # Handle both JSON API format (with attributes/relationships) and flat format
                if 'attributes' in reg or 'relationships' in reg:
                    # JSON API format
                    reg_id = reg.get('id')
                    reg_attributes = reg.get('attributes', {})
                    # Try relationships first, then fallback to direct person_id
                    pc_person_id = (
                        reg.get('relationships', {}).get('person', {}).get('data', {}).get('id')
                        or reg_attributes.get('person_id')
                        or reg.get('person_id')
                    )
                else:
                    # Flat format (after transformation)
                    reg_id = reg.get('id')
                    reg_attributes = reg
                    pc_person_id = reg.get('person_id')
                
                if not reg_id:
                    errors.append(f"Registration missing ID: {reg}")
                    continue
                    
                if not pc_person_id:
                    errors.append(f"Registration {reg_id}: Missing person ID")
                    continue

                # Get local people_id
                try:
                    people_id = self._get_people_id_from_pc_person_id(pc_person_id)
                except HTTPException:
                    errors.append(f"Registration {reg_id}: Person {pc_person_id} not found locally")
                    continue

                # Check if enrollment already exists
                existing = self.get_enrollment_by_pc_registration_id(reg_id) if reg_id else None
                
                if existing:
                    if update_existing:
                        # Update existing enrollment
                        # Get status from attributes or direct field
                        pc_status = (
                            reg_attributes.get('status', '')
                            if isinstance(reg_attributes, dict)
                            else reg.get('status', 'registered')
                        ) or 'registered'
                        enrollment_update = CourseEnrollmentUpdate(
                            status=self._map_pc_status_to_enrollment_status(pc_status),
                            registration_status=pc_status,
                            registration_notes=reg_attributes.get('notes') if isinstance(reg_attributes, dict) else reg.get('notes'),
                            planning_center_synced=True,
                        )
                        updated = self.update_enrollment(existing.id, enrollment_update, updated_by=created_by)
                        if updated:
                            enrollments.append(updated)
                    # If not updating existing, skip
                else:
                    # Create new enrollment
                    # Get status and date from attributes or direct field
                    pc_status = (
                        reg_attributes.get('status', '')
                        if isinstance(reg_attributes, dict)
                        else reg.get('status', 'registered')
                    ) or 'registered'
                    registration_date = (
                        reg_attributes.get('created_at')
                        if isinstance(reg_attributes, dict)
                        else reg.get('created_at')
                    )
                    if registration_date:
                        try:
                            from dateutil.parser import parse as parse_date
                            registration_date = parse_date(registration_date)
                        except:
                            registration_date = datetime.utcnow()
                    else:
                        registration_date = datetime.utcnow()

                    enrollment_data = CourseEnrollmentCreate(
                        people_id=people_id,
                        course_id=course_id,
                        planning_center_registration_id=reg_id,
                        enrollment_date=registration_date,
                        status=self._map_pc_status_to_enrollment_status(pc_status),
                        registration_status=pc_status,
                        registration_notes=reg_attributes.get('notes') if isinstance(reg_attributes, dict) else reg.get('notes'),
                        data_source='api',
                        planning_center_synced=True,
                    )
                    enrollment = self.create_enrollment(enrollment_data, created_by=created_by)
                    enrollments.append(enrollment)
            except Exception as e:
                errors.append(f"Registration {reg.get('id', 'unknown')}: {str(e)}")
                continue

        if errors:
            # Log errors but still return successful enrollments
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Bulk enrollment from PC event had {len(errors)} errors: {errors}")

        return enrollments

    def bulk_enroll_from_pc_list(
        self,
        course_id: int,
        pc_list_id: str,
        created_by: Optional[int] = None,
        update_existing: bool = True,
    ) -> List[CourseEnrollmentModel]:
        """
        Bulk enroll people based on Planning Center List
        
        Args:
            course_id: The course to enroll people in
            pc_list_id: Planning Center list ID to get people from
            created_by: User creating the enrollments
            update_existing: Whether to update existing enrollments (default: True)
        
        Returns:
            List of created/updated enrollments
        """
        from app.services.planning_center_sync_service import PlanningCenterSyncService
        
        # Validate course exists
        course_service = CourseService(self.db)
        course = course_service.get_course(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with ID {course_id} not found"
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

        enrollments = []
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

                # Check if enrollment already exists
                # For lists, we don't have a registration ID, so we check by course_id + people_id
                existing_enrollment = (
                    self.db.query(CourseEnrollmentModel)
                    .filter(
                        CourseEnrollmentModel.course_id == course_id,
                        CourseEnrollmentModel.people_id == people_id
                    )
                    .first()
                )
                
                if existing_enrollment:
                    if update_existing:
                        # Update existing enrollment
                        enrollment_update = CourseEnrollmentUpdate(
                            status="enrolled", # Default to enrolled since they are on the list
                            planning_center_synced=True,
                        )
                        updated = self.update_enrollment(existing_enrollment.id, enrollment_update, updated_by=created_by)
                        if updated:
                            enrollments.append(updated)
                    # If not updating existing, skip
                else:
                    # Create new enrollment
                    enrollment_data = CourseEnrollmentCreate(
                        people_id=people_id,
                        course_id=course_id,
                        enrollment_date=datetime.utcnow(),
                        status="enrolled",
                        planning_center_synced=True,
                    )
                    enrollment = self.create_enrollment(enrollment_data, created_by=created_by)
                    enrollments.append(enrollment)
            except Exception as e:
                errors.append(f"Person {pc_person.get('id', 'unknown')}: {str(e)}")
                continue

        if errors:
            # Log errors but still return successful enrollments
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Bulk enrollment from PC list had {len(errors)} errors: {errors}")

        return enrollments

    def import_registrations(
        self,
        course_id: int,
        registration_ids: List[str],
        event_id: str,
        created_by: Optional[int] = None,
        update_existing: bool = True,
    ) -> List[CourseEnrollmentModel]:
        """
        Import selected registrations from a Planning Center event as enrollments.
        Automatically syncs people from Planning Center if they don't exist locally.
        
        Args:
            course_id: The course to enroll people in
            registration_ids: List of Planning Center registration IDs to import
            event_id: Planning Center event ID (used to fetch full registration data)
            created_by: User creating the enrollments
            update_existing: Whether to update existing enrollments (default: True)
        
        Returns:
            List of created/updated enrollments
        """
        from app.services.planning_center_sync_service import PlanningCenterSyncService
        
        # Validate course exists
        course_service = CourseService(self.db)
        course = course_service.get_course(course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with ID {course_id} not found"
            )

        # Get all registrations from the event
        pc_service = PlanningCenterSyncService(self.db)
        try:
            all_registrations = pc_service.get_event_registrations(event_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch registrations from Planning Center: {str(e)}"
            )

        # Filter to only the selected registration IDs
        selected_registrations = [
            reg for reg in all_registrations
            if reg.get('id') in registration_ids
        ]

        if not selected_registrations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"None of the specified registration IDs were found in the event"
            )

        enrollments = []
        errors = []
        people_service = PeopleService(self.db)
        
        for reg in selected_registrations:
            try:
                # Extract registration data
                reg_id = reg.get('id')
                reg_attributes = reg.get('attributes', {})
                
                # Get person ID from registration
                pc_person_id = (
                    reg.get('relationships', {}).get('person', {}).get('data', {}).get('id')
                    or reg_attributes.get('person_id')
                )
                
                if not pc_person_id:
                    errors.append(f"Registration {reg_id}: Missing person ID")
                    continue

                # Get or create person locally
                person = people_service.get_person_by_pc_id(pc_person_id)
                if not person:
                    # Person doesn't exist - sync from Planning Center
                    try:
                        # Fetch full person data from Planning Center
                        import httpx
                        with httpx.Client(timeout=30.0) as client:
                            response = client.get(
                                f"{pc_service.base_url}/people/v2/people/{pc_person_id}",
                                headers=pc_service.headers,
                                params={"include": "emails,phone_numbers"}
                            )
                            
                            if response.status_code == 404:
                                errors.append(f"Registration {reg_id}: Person {pc_person_id} not found in Planning Center")
                                continue
                            
                            response.raise_for_status()
                            data = response.json()
                            pc_person_data = data.get("data")
                            included = data.get("included", [])
                            
                            if not pc_person_data:
                                errors.append(f"Registration {reg_id}: Person data not found in Planning Center response")
                                continue
                            
                            # Attach included data (emails, phone numbers)
                            pc_person_data = pc_service._attach_included_data([pc_person_data], included)[0]
                            
                            # Sync person from Planning Center
                            person = people_service.sync_from_planning_center(
                                pc_person_data, updated_by=created_by
                            )
                    except Exception as e:
                        errors.append(f"Registration {reg_id}: Failed to sync person {pc_person_id} from Planning Center: {str(e)}")
                        continue

                people_id = person.id

                # Check if enrollment already exists
                existing = self.get_enrollment_by_pc_registration_id(reg_id) if reg_id else None
                
                if existing:
                    if update_existing:
                        # Update existing enrollment
                        pc_status = reg_attributes.get('status', 'registered') or 'registered'
                        enrollment_update = CourseEnrollmentUpdate(
                            status=self._map_pc_status_to_enrollment_status(pc_status),
                            registration_status=pc_status,
                            registration_notes=reg_attributes.get('notes'),
                            planning_center_synced=True,
                        )
                        updated = self.update_enrollment(existing.id, enrollment_update, updated_by=created_by)
                        if updated:
                            enrollments.append(updated)
                else:
                    # Create new enrollment
                    pc_status = reg_attributes.get('status', 'registered') or 'registered'
                    
                    # Parse registration date
                    registration_date = reg_attributes.get('created_at') or reg_attributes.get('registration_date')
                    if registration_date:
                        try:
                            from dateutil.parser import parse as parse_date
                            registration_date = parse_date(registration_date)
                        except:
                            registration_date = datetime.utcnow()
                    else:
                        registration_date = datetime.utcnow()

                    enrollment_data = CourseEnrollmentCreate(
                        people_id=people_id,
                        course_id=course_id,
                        planning_center_registration_id=reg_id,
                        enrollment_date=registration_date,
                        status=self._map_pc_status_to_enrollment_status(pc_status),
                        registration_status=pc_status,
                        registration_notes=reg_attributes.get('notes'),
                        data_source='api',
                        planning_center_synced=True,
                    )
                    enrollment = self.create_enrollment(enrollment_data, created_by=created_by)
                    enrollments.append(enrollment)
                    
            except Exception as e:
                errors.append(f"Registration {reg.get('id', 'unknown')}: {str(e)}")
                continue

        if errors:
            # Log errors but still return successful enrollments
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Import registrations had {len(errors)} errors: {errors}")

        return enrollments
