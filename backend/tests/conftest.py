"""
Test configuration and fixtures
"""

import pytest
import asyncio
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, date, timezone

# Override database configuration for tests
os.environ["DATABASE_URL"] = "sqlite:///./data/church_course_tracker.db"
os.environ["RATE_LIMIT_ENABLED"] = "false"

# Test database URL - use the migrated database for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/church_course_tracker.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the database engine in the app's database module
import app.core.database as db_module
db_module.engine = engine
db_module.SessionLocal = TestingSessionLocal

# Import after setting environment variables
from app.core.database import Base, get_db
from main import app

# Import all models to ensure they are registered with SQLAlchemy
from app.models import *
# Import all models explicitly to ensure they are registered
from app.models.audit_log import AuditLog
from app.models.campus import Campus
from app.models.certification import Certification
from app.models.certification_progress import CertificationProgress
from app.models.content import Content
from app.models.content_type import ContentType
from app.models.course import Course
from app.models.course_content import CourseContent, CourseModule, ContentAccessLog, ContentAuditLog
from app.models.course_role import CourseRole
from app.models.enrollment import CourseEnrollment
from app.models.member import People
from app.models.people_campus import PeopleCampus
from app.models.people_role import PeopleRole
from app.models.planning_center_events_cache import PlanningCenterEventsCache
from app.models.planning_center_registrations_cache import PlanningCenterRegistrationsCache
from app.models.planning_center_sync_log import PlanningCenterSyncLog
from app.models.planning_center_webhook_events import PlanningCenterWebhookEvents
from app.models.progress import ContentCompletion
from app.models.role import Role
from app.models.user import User

# Disable TrustedHostMiddleware for tests
app.user_middleware = [mw for mw in app.user_middleware if 'TrustedHostMiddleware' not in str(mw)]

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Use the existing migrated database - don't drop/recreate tables
    # Just ensure tables exist (they should from migrations)
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()

    # Yield the session to the test
    yield session

    # Clean up the session after the test
    try:
        session.rollback()
    except Exception:
        pass
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Ensure tables are created for the test client
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app, headers={"host": "testserver"}) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "staff",
        "is_active": True,
        "hashed_password": "hashed_password_123"
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
        "title": "Introduction to Faith",
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
        "validity_months": 12,
        "is_active": True
    }


@pytest.fixture
def sample_enrollment_data():
    """Sample enrollment data for testing."""
    return {
        "people_id": 1,  # Will be set in test
        "course_id": 1,  # Will be set in test
        "enrollment_date": datetime.now(timezone.utc),
        "status": "enrolled",
        "progress_percentage": 0.0,
        "planning_center_synced": False,
        "registration_status": "registered"
    }


@pytest.fixture
def admin_token(db_session):
    """Create a test admin user and return their token."""
    from app.core.security import create_access_token, get_password_hash
    from app.models.user import User
    from datetime import timedelta
    
    # Create admin user in database
    admin_user = User(
        username="admin",
        email="admin@test.com",
        full_name="Admin User",
        role="admin",
        hashed_password=get_password_hash("password"),
        is_active=True
    )
    db_session.add(admin_user)
    db_session.commit()
    db_session.refresh(admin_user)
    
    # Create a token for admin user
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(admin_user.id)}, expires_delta=access_token_expires
    )
    return access_token


@pytest.fixture
def staff_token(db_session):
    """Create a test staff user and return their token."""
    from app.core.security import create_access_token, get_password_hash
    from app.models.user import User
    from datetime import timedelta
    
    # Create staff user in database
    staff_user = User(
        username="staff",
        email="staff@test.com",
        full_name="Staff User",
        role="staff",
        hashed_password=get_password_hash("password"),
        is_active=True
    )
    db_session.add(staff_user)
    db_session.commit()
    db_session.refresh(staff_user)
    
    # Create a token for staff user
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(staff_user.id)}, expires_delta=access_token_expires
    )
    return access_token


@pytest.fixture
def viewer_token(db_session):
    """Create a test viewer user and return their token."""
    from app.core.security import create_access_token, get_password_hash
    from app.models.user import User
    from datetime import timedelta
    
    # Create viewer user in database
    viewer_user = User(
        username="viewer",
        email="viewer@test.com",
        full_name="Viewer User",
        role="viewer",
        hashed_password=get_password_hash("password"),
        is_active=True
    )
    db_session.add(viewer_user)
    db_session.commit()
    db_session.refresh(viewer_user)
    
    # Create a token for viewer user
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(viewer_user.id)}, expires_delta=access_token_expires
    )
    return access_token