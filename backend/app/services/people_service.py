"""
People service layer (from Planning Center)
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.member import People as PeopleModel
from app.schemas.people import PeopleCreate, PeopleUpdate
from app.services.audit_service import AuditService


class PeopleService:
    """Service for people operations - from Planning Center"""

    def __init__(self, db: Session):
        self.db = db

    def get_people(
        self, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
    ) -> List[PeopleModel]:
        """Get all people with pagination and optional filtering"""
        query = self.db.query(PeopleModel)
        if is_active is not None:
            query = query.filter(PeopleModel.is_active == is_active)
        return query.offset(skip).limit(limit).all()

    def get_person(self, person_id: int) -> Optional[PeopleModel]:
        """Get a specific person by ID"""
        return self.db.query(PeopleModel).filter(PeopleModel.id == person_id).first()

    def get_person_by_pc_id(self, pc_id: str) -> Optional[PeopleModel]:
        """Get a person by Planning Center ID"""
        return (
            self.db.query(PeopleModel)
            .filter(PeopleModel.planning_center_id == pc_id)
            .first()
        )

    def search_people(self, search_term: str, limit: int = 50) -> List[PeopleModel]:
        """Search people by name or email"""
        return (
            self.db.query(PeopleModel)
            .filter(
                (PeopleModel.first_name.ilike(f"%{search_term}%"))
                | (PeopleModel.last_name.ilike(f"%{search_term}%"))
                | (PeopleModel.email.ilike(f"%{search_term}%"))
            )
            .limit(limit)
            .all()
        )

    def create_person(
        self, person: PeopleCreate, created_by: Optional[int] = None
    ) -> PeopleModel:
        """Create a new person"""
        person_data = person.dict()
        
        # If planning_center_id is not provided or is empty, generate a unique placeholder
        # This allows manual creation without Planning Center integration
        if not person_data.get('planning_center_id'):
            import uuid
            person_data['planning_center_id'] = f"manual_{uuid.uuid4().hex[:12]}"
        
        db_person = PeopleModel(**person_data)
        db_person.created_at = datetime.utcnow()
        db_person.updated_at = datetime.utcnow()
        db_person.created_by = created_by

        self.db.add(db_person)
        self.db.commit()
        self.db.refresh(db_person)
        AuditService(self.db).log_change(
            table_name=PeopleModel.__tablename__,
            record_id=db_person.id,
            action="insert",
            changed_by=created_by,
            new_values=AuditService.serialize_model(db_person),
        )
        return db_person

    def update_person(
        self,
        person_id: int,
        person_update: PeopleUpdate,
        updated_by: Optional[int] = None,
    ) -> Optional[PeopleModel]:
        """Update an existing person"""
        db_person = self.get_person(person_id)
        if not db_person:
            return None
        old_values = AuditService.serialize_model(db_person)
        update_data = person_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_person, field, value)

        db_person.updated_at = datetime.utcnow()
        db_person.updated_by = updated_by
        self.db.commit()
        self.db.refresh(db_person)
        AuditService(self.db).log_change(
            table_name=PeopleModel.__tablename__,
            record_id=db_person.id,
            action="update",
            changed_by=updated_by,
            old_values=old_values,
            new_values=AuditService.serialize_model(db_person),
        )
        return db_person

    def delete_person(self, person_id: int, deleted_by: Optional[int] = None) -> bool:
        """Delete a person"""
        db_person = self.get_person(person_id)
        if not db_person:
            return False
        old_values = AuditService.serialize_model(db_person)
        record_id = db_person.id

        self.db.delete(db_person)
        self.db.commit()
        AuditService(self.db).log_change(
            table_name=PeopleModel.__tablename__,
            record_id=record_id,
            action="delete",
            changed_by=deleted_by,
            old_values=old_values,
        )
        return True

    def sync_from_planning_center(
        self, pc_person_data: dict, updated_by: Optional[int] = None
    ) -> PeopleModel:
        """Sync person data from Planning Center"""
        pc_id = pc_person_data.get("id")

        # Check if person already exists
        existing_person = self.get_person_by_pc_id(pc_id)

        if existing_person:
            # Update existing person
            existing_person.first_name = pc_person_data.get("first_name", "")
            existing_person.last_name = pc_person_data.get("last_name", "")
            existing_person.email = pc_person_data.get("email")
            existing_person.phone = pc_person_data.get("phone")
            existing_person.date_of_birth = pc_person_data.get("date_of_birth")
            existing_person.gender = pc_person_data.get("gender")
            existing_person.address1 = pc_person_data.get("address1")
            existing_person.address2 = pc_person_data.get("address2")
            existing_person.city = pc_person_data.get("city")
            existing_person.state = pc_person_data.get("state")
            existing_person.zip = pc_person_data.get("zip")
            existing_person.household_id = pc_person_data.get("household_id")
            existing_person.household_name = pc_person_data.get("household_name")
            existing_person.status = pc_person_data.get("status", "active")
            existing_person.join_date = pc_person_data.get("join_date")
            existing_person.last_synced_at = datetime.utcnow()
            existing_person.updated_at = datetime.utcnow()
            existing_person.updated_by = updated_by
            self.db.commit()
            self.db.refresh(existing_person)
            return existing_person
        else:
            # Create new person
            person_data = PeopleCreate(
                planning_center_id=pc_id,
                first_name=pc_person_data.get("first_name", ""),
                last_name=pc_person_data.get("last_name", ""),
                email=pc_person_data.get("email"),
                phone=pc_person_data.get("phone"),
                date_of_birth=pc_person_data.get("date_of_birth"),
                gender=pc_person_data.get("gender"),
                address1=pc_person_data.get("address1"),
                address2=pc_person_data.get("address2"),
                city=pc_person_data.get("city"),
                state=pc_person_data.get("state"),
                zip=pc_person_data.get("zip"),
                household_id=pc_person_data.get("household_id"),
                household_name=pc_person_data.get("household_name"),
                status=pc_person_data.get("status", "active"),
                join_date=pc_person_data.get("join_date"),
            )
            return self.create_person(person_data, created_by=updated_by)
