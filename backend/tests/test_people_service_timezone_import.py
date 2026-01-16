"""
Simple test that would have caught the missing 'timezone' import error.

This test directly exercises the code path that uses timezone.utc,
which would fail with NameError if timezone wasn't imported.
"""
import pytest
from app.services.people_service import PeopleService
from app.schemas.people import PeopleCreate


def test_people_service_imports_timezone(db_session):
    """Test that PeopleService can use timezone.utc without NameError
    
    This test would have immediately caught the missing 'timezone' import.
    The error would be: NameError: name 'timezone' is not defined
    """
    service = PeopleService(db_session)
    
    # Create a person - this calls create_person which uses datetime.now(timezone.utc)
    person_data = PeopleCreate(
        first_name="Test",
        last_name="User",
        email="test@example.com"
    )
    
    # If timezone wasn't imported, this line would raise:
    # NameError: name 'timezone' is not defined
    person = service.create_person(person_data, created_by=1)
    
    # If we get here, timezone was imported correctly
    assert person is not None
    assert person.first_name == "Test"
    assert person.email == "test@example.com"


def test_sync_from_pc_uses_timezone(db_session):
    """Test that sync_from_planning_center can use timezone.utc without NameError
    
    This test would have caught the missing 'timezone' import in the sync method.
    """
    service = PeopleService(db_session)
    
    # Mock Planning Center person data
    pc_person_data = {
        "id": "test_pc_id",
        "attributes": {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com"
        }
    }
    
    # If timezone wasn't imported, this line would raise:
    # NameError: name 'timezone' is not defined
    person = service.sync_from_planning_center(pc_person_data, updated_by=1)
    
    # If we get here, timezone was imported correctly
    assert person is not None
    assert person.first_name == "Jane"
    assert person.planning_center_id == "test_pc_id"
