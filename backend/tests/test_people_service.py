"""
Tests for PeopleService that would catch import errors like missing 'timezone'
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from app.services.people_service import PeopleService
from app.schemas.people import PeopleCreate


def test_sync_from_planning_center_uses_timezone_correctly(db_session):
    """Test that sync_from_planning_center correctly uses timezone.utc
    
    This test would have caught the missing 'timezone' import error.
    """
    service = PeopleService(db_session)
    
    # Mock Planning Center person data
    pc_person_data = {
        "id": "12345",
        "attributes": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "555-1234",
            "status": "active"
        }
    }
    
    # This should not raise NameError: name 'timezone' is not defined
    try:
        person = service.sync_from_planning_center(pc_person_data, updated_by=1)
        
        # Verify person was created
        assert person is not None
        assert person.first_name == "John"
        assert person.last_name == "Doe"
        assert person.email == "john.doe@example.com"
        
        # The key test: if timezone wasn't imported, this would raise NameError
        # The fact that we got here means timezone was imported correctly
        assert person.updated_at is not None
        # Note: SQLite may store naive datetimes, but the code should use timezone.utc
        
    except NameError as e:
        if "timezone" in str(e):
            pytest.fail(f"Missing 'timezone' import detected: {e}")
        raise


def test_create_person_uses_timezone_correctly(db_session):
    """Test that create_person correctly uses timezone.utc
    
    This test would have caught the missing 'timezone' import error.
    """
    service = PeopleService(db_session)
    
    person_data = PeopleCreate(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        phone="555-5678"
    )
    
    # This should not raise NameError: name 'timezone' is not defined
    try:
        person = service.create_person(person_data, created_by=1)
        
        # Verify person was created
        assert person is not None
        assert person.first_name == "Jane"
        assert person.last_name == "Smith"
        
        # The key test: if timezone wasn't imported, this would raise NameError
        # The fact that we got here means timezone was imported correctly
        assert person.created_at is not None
        assert person.updated_at is not None
        
    except NameError as e:
        if "timezone" in str(e):
            pytest.fail(f"Missing 'timezone' import detected: {e}")
        raise


def test_update_person_uses_timezone_correctly(db_session):
    """Test that update_person correctly uses timezone.utc
    
    This test would have caught the missing 'timezone' import error.
    """
    service = PeopleService(db_session)
    
    # First create a person
    person_data = PeopleCreate(
        first_name="Bob",
        last_name="Johnson",
        email="bob.johnson@example.com"
    )
    person = service.create_person(person_data, created_by=1)
    
    # Now update the person - need to use proper schema
    from app.schemas.people import PeopleUpdate
    update_data = PeopleUpdate(phone="555-9999")
    
    # This should not raise NameError: name 'timezone' is not defined
    try:
        updated_person = service.update_person(person.id, update_data, updated_by=1)
        
        # Verify person was updated
        assert updated_person.phone == "555-9999"
        
        # The key test: if timezone wasn't imported, this would raise NameError
        # The fact that we got here means timezone was imported correctly
        assert updated_person.updated_at is not None
        
    except NameError as e:
        if "timezone" in str(e):
            pytest.fail(f"Missing 'timezone' import detected: {e}")
        raise


def test_bulk_import_participants_from_pc_list_handles_sync_errors(db_session):
    """Test that bulk import handles people sync errors gracefully
    
    This test would have caught the issue where all people failed to sync
    due to missing 'timezone' import, but the endpoint still returned success.
    """
    from app.services.program_service import ProgramService
    from app.schemas.program import ProgramCreate
    
    # Create a test program using proper schema
    program_service = ProgramService(db_session)
    program_data = ProgramCreate(
        title="Test Program",
        description="Test",
        is_active=True,
        role_definitions=[{"name": "Mentor", "min_participants": 1, "max_participants": 1, "is_primary": True}],
        relationship_config={"allow_multiple_secondary": True, "max_secondary_per_primary": None, "require_pairing": True, "progress_calculation": "content_based"},
        locations=[],
        delivery_modes=[],
        prerequisites=[]
    )
    program = program_service.create_program(program_data, created_by=1)
    
    # Mock Planning Center list with people
    mock_pc_people = [
        {
            "id": "12345",
            "attributes": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com"
            }
        },
        {
            "id": "67890",
            "attributes": {
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@example.com"
            }
        }
    ]
    
    # Mock the Planning Center sync service - patch where it's imported inside the method
    with patch('app.services.planning_center_sync_service.PlanningCenterSyncService') as mock_pc_service:
        mock_instance = mock_pc_service.return_value
        mock_instance.get_list_people.return_value = mock_pc_people
        
        # This should succeed and create participants
        # If timezone import is missing, this would fail with NameError
        try:
            participants = program_service.bulk_import_participants_from_pc_list(
                program_id=program.id,
                pc_list_id="test_list_id",
                role_name="Mentor",
                created_by=1
            )
            
            # Verify participants were created
            assert len(participants) == 2, f"Expected 2 participants, got {len(participants)}"
            
            # Verify people were created in database
            from app.models.member import People
            people_count = db_session.query(People).count()
            assert people_count >= 2, f"Expected at least 2 people, got {people_count}"
            
        except NameError as e:
            if "timezone" in str(e):
                pytest.fail(f"Missing 'timezone' import detected in bulk import: {e}")
            raise
