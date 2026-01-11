"""
Test configuration and fixtures
"""

import pytest
import asyncio
import os
import subprocess
import pathlib
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, date, timezone

# Override database configuration for tests
os.environ["RATE_LIMIT_ENABLED"] = "false"

# Mock Planning Center credentials for tests
os.environ["PLANNING_CENTER_APP_ID"] = "test_app_id"
os.environ["PLANNING_CENTER_SECRET"] = "test_secret"
os.environ["PLANNING_CENTER_ACCESS_TOKEN"] = "test_token"

# Test database URL - will be set below after determining backend directory

# Ensure data directory exists
# Get the backend directory (where this file is located)
backend_dir = pathlib.Path(__file__).parent.parent
data_dir = backend_dir / "data"
data_dir.mkdir(exist_ok=True)

# Update database path to be relative to backend directory
SQLALCHEMY_DATABASE_URL = f"sqlite:///{data_dir}/church_course_tracker.db"
os.environ["DATABASE_URL"] = SQLALCHEMY_DATABASE_URL

# Remove existing test database to ensure clean state
db_file = data_dir / "church_course_tracker.db"
if db_file.exists():
    try:
        os.remove(db_file)
        print("🗑️  Removed existing test database")
    except Exception as e:
        print(f"⚠️  Could not remove test database: {e}")

# Run migrations on the test database before tests
print("🔄 Running migrations on test database...")
try:
    # Run from backend directory (where alembic.ini is located)
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=str(backend_dir),
        check=True,
        capture_output=True,
        text=True
    )
    print("✅ Migrations completed")
except Exception as e:
    print(f"⚠️  Migration failed: {e}")
    if hasattr(e, 'stdout'):
        print("STDOUT:", e.stdout)
    if hasattr(e, 'stderr'):
        print("STDERR:", e.stderr)
    # Try alternative approach - create tables directly
    print("⚠️  Attempting to create tables directly...")

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
from app.models.custom_attribute import CustomAttribute
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
    
    # Ensure new columns exist (in case migrations didn't apply)
    # This is a safety check for columns added after initial migration
    try:
        with engine.connect() as conn:
            # Check if instructors column exists, if not add it
            result = conn.execute(text("PRAGMA table_info(courses)"))
            columns = [row[1] for row in result]
            if 'instructors' not in columns:
                conn.execute(text("ALTER TABLE courses ADD COLUMN instructors JSON"))
            if 'locations' not in columns:
                conn.execute(text("ALTER TABLE courses ADD COLUMN locations JSON"))
            if 'delivery_modes' not in columns:
                conn.execute(text("ALTER TABLE courses ADD COLUMN delivery_modes JSON"))
            
            # Check if shared_content_id column exists in course_content table
            result = conn.execute(text("PRAGMA table_info(course_content)"))
            course_content_columns = [row[1] for row in result]
            if 'shared_content_id' not in course_content_columns:
                # Check if shared_content table exists first
                tables_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='shared_content'"))
                if tables_result.fetchone():
                    conn.execute(text("ALTER TABLE course_content ADD COLUMN shared_content_id INTEGER"))
                    # Create index if it doesn't exist
                    try:
                        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_course_content_shared_content_id ON course_content(shared_content_id)"))
                    except:
                        pass  # Index might already exist
            
            # Check if planning_center_person_id column exists in users table
            result = conn.execute(text("PRAGMA table_info(users)"))
            users_columns = [row[1] for row in result]
            if 'planning_center_person_id' not in users_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN planning_center_person_id VARCHAR(50)"))
                # Create index if it doesn't exist
                try:
                    conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_planning_center_person_id ON users(planning_center_person_id)"))
                except:
                    pass  # Index might already exist
            
            conn.commit()
    except Exception as e:
        # If columns already exist or other error, that's okay
        pass
    
    session = TestingSessionLocal()

    # Clean up test data before each test
    try:
        # Delete test data in reverse order of dependencies
        session.execute(text("DELETE FROM content_access_logs"))
        session.execute(text("DELETE FROM content_audit_logs"))
        session.execute(text("DELETE FROM content_completion"))
        session.execute(text("DELETE FROM course_content"))
        session.execute(text("DELETE FROM course_modules"))
        session.execute(text("DELETE FROM course_enrollment"))
        session.execute(text("DELETE FROM course_instance_teachers"))  # Added
        session.execute(text("DELETE FROM course_instances"))          # Added
        session.execute(text("DELETE FROM certification_progress"))
        session.execute(text("DELETE FROM certification"))
        session.execute(text("DELETE FROM courses"))
        # Clean up program-related tables (in reverse dependency order)
        session.execute(text("DELETE FROM program_progress"))
        session.execute(text("DELETE FROM program_sessions"))
        session.execute(text("DELETE FROM program_pairings"))
        session.execute(text("DELETE FROM program_participants"))
        session.execute(text("DELETE FROM program_admins"))
        session.execute(text("DELETE FROM programs"))
        session.execute(text("DELETE FROM failed_login_attempts"))  # Clear lockout state
        session.execute(text("DELETE FROM content_type"))
        session.execute(text("DELETE FROM content"))
        session.execute(text("DELETE FROM planning_center_events_cache"))
        session.execute(text("DELETE FROM planning_center_registrations_cache"))
        session.execute(text("DELETE FROM planning_center_sync_log"))
        session.execute(text("DELETE FROM planning_center_webhook_events"))
        session.execute(text("DELETE FROM failed_login_attempts"))  # Clear lockout state
        session.execute(text("DELETE FROM audit_log"))
        session.execute(text("DELETE FROM custom_attributes"))
        session.execute(text("DELETE FROM people_campus"))
        session.execute(text("DELETE FROM people_role"))
        session.execute(text("DELETE FROM people"))
        session.execute(text("DELETE FROM campus"))
        session.execute(text("DELETE FROM role"))
        session.execute(text("DELETE FROM users WHERE email != 'course.tracker.admin@eastgate.church'"))
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Warning: Could not clean test data: {e}")

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
        hashed_password="test_hash",  # Use a simple hash for tests
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
        hashed_password="test_hash",  # Use a simple hash for tests
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
        hashed_password="test_hash",  # Use a simple hash for tests
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


@pytest.fixture
def user_token(db_session):
    """Create a test regular user and return their token."""
    from app.core.security import create_access_token, get_password_hash
    from app.models.user import User
    from datetime import timedelta
    
    # Create regular user in database
    user = User(
        username="user",
        email="user@test.com",
        full_name="Regular User",
        role="user",
        hashed_password="test_hash",  # Use a simple hash for tests
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create a token for regular user
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return access_token