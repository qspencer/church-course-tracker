"""
Test configuration and fixtures
"""

import pytest
import asyncio
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, date

# Override database configuration for tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Test database URL - use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import after setting environment variables
from app.core.database import Base
from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[app.dependency_overrides.get("get_db", None)] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False
    }


@pytest.fixture
def sample_people_data():
    """Sample people data for testing."""
    return {
        "planning_center_id": "pc_12345",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "555-1234",
        "date_of_birth": date(1990, 1, 1),
        "gender": "Male",
        "address1": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "zip": "12345",
        "household_id": "hh_123",
        "household_name": "Doe Family",
        "status": "active",
        "join_date": date(2020, 1, 1),
        "is_active": True
    }


@pytest.fixture
def sample_campus_data():
    """Sample campus data for testing."""
    return {
        "name": "Main Campus",
        "address": "123 Church St",
        "phone": "555-5678",
        "email": "main@church.com",
        "planning_center_location_id": "loc_123",
        "is_active": True
    }


@pytest.fixture
def sample_role_data():
    """Sample role data for testing."""
    return {
        "name": "Teacher",
        "description": "Course instructor",
        "permissions": ["teach", "grade"],
        "is_active": True
    }


@pytest.fixture
def sample_course_data():
    """Sample course data for testing."""
    return {
        "name": "Introduction to Faith",
        "description": "Basic course on Christian faith",
        "planning_center_event_id": "evt_123",
        "planning_center_event_name": "Introduction to Faith",
        "event_start_date": datetime(2024, 2, 1, 9, 0),
        "event_end_date": datetime(2024, 2, 1, 12, 0),
        "max_capacity": 50,
        "current_registrations": 0,
        "is_active": True
    }


@pytest.fixture
def sample_content_type_data():
    """Sample content type data for testing."""
    return {
        "name": "Video",
        "description": "Video content",
        "icon_class": "fas fa-video",
        "is_active": True
    }


@pytest.fixture
def sample_content_data():
    """Sample content data for testing."""
    return {
        "title": "Welcome Video",
        "content_type_id": 1,  # Will be set in test
        "order_sequence": 1,
        "file_path": "/videos/welcome.mp4",
        "duration_minutes": 15,
        "is_required": True,
        "is_active": True
    }


@pytest.fixture
def sample_certification_data():
    """Sample certification data for testing."""
    return {
        "name": "Basic Christian Education",
        "description": "Complete basic Christian education program",
        "required_courses": [1, 2, 3],  # Will be set in test
        "validity_months": 12,
        "is_active": True
    }


@pytest.fixture
def sample_enrollment_data():
    """Sample enrollment data for testing."""
    return {
        "people_id": 1,  # Will be set in test
        "course_id": 1,  # Will be set in test
        "enrollment_date": datetime.utcnow(),
        "status": "enrolled",
        "progress_percentage": 0.0,
        "planning_center_synced": False,
        "registration_status": "registered"
    }