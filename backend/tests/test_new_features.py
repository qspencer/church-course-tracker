"""
Tests for new features: account lockout, profile update, password change, preferences, prerequisites, activity logs
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.models.user import User
from app.models.course import Course

client = TestClient(app)


@pytest.fixture
def admin_user(db_session: Session):
    """Create an admin user for testing"""
    # Use a pre-hashed password to avoid bcrypt compatibility issues in tests
    # This hash corresponds to "testpass123" and will work with verify_password
    import bcrypt
    password = "testpass123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user = User(
        username="testadmin",
        email="testadmin@example.com",
        full_name="Test Admin",
        hashed_password=hashed,
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_course(db_session: Session):
    """Create a test course"""
    course = Course(
        title="Test Course",
        description="Test Description",
        is_active=True,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


def get_auth_token(username: str = "testadmin", password: str = "testpass123"):
    """Helper to get auth token"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


class TestAccountLockout:
    """Test account lockout functionality"""

    def test_account_lockout_after_failed_attempts(self, db_session: Session, admin_user):
        """Test that account gets locked after 5 failed attempts"""
        # Try wrong password 5 times
        for i in range(5):
            response = client.post(
                "/api/v1/auth/login",
                json={"username": admin_user.username, "password": "wrongpassword"},
            )
            assert response.status_code == 401
            if i < 4:
                assert "attempt(s) remaining" in response.json()["detail"]

        # 6th attempt should lock the account
        response = client.post(
            "/api/v1/auth/login",
            json={"username": admin_user.username, "password": "wrongpassword"},
        )
        assert response.status_code == 423  # Locked
        assert "locked" in response.json()["detail"].lower()

    def test_successful_login_clears_failed_attempts(self, db_session: Session, admin_user):
        """Test that successful login clears failed attempts"""
        # Fail a few times
        for _ in range(3):
            client.post(
                "/api/v1/auth/login",
                json={"username": admin_user.username, "password": "wrongpassword"},
            )

        # Successful login should work
        response = client.post(
            "/api/v1/auth/login",
            json={"username": admin_user.username, "password": "testpass123"},
        )
        assert response.status_code == 200

        # Failed attempts should be cleared
        response = client.post(
            "/api/v1/auth/login",
            json={"username": admin_user.username, "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "4 attempt(s) remaining" in response.json()["detail"]


class TestUserProfileUpdate:
    """Test user profile update functionality"""

    def test_update_profile(self, db_session: Session, admin_user):
        """Test updating user profile"""
        token = get_auth_token()
        assert token is not None

        response = client.patch(
            "/api/v1/users/me",
            json={"full_name": "Updated Name", "email": "updated@example.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Name"
        assert response.json()["email"] == "updated@example.com"

    def test_update_profile_cannot_change_role(self, db_session: Session, admin_user):
        """Test that users cannot change their role through profile update"""
        token = get_auth_token()
        assert token is not None

        response = client.patch(
            "/api/v1/users/me",
            json={"role": "viewer"},  # Try to change role
            headers={"Authorization": f"Bearer {token}"},
        )
        # Should succeed but role should not change
        assert response.status_code == 200
        # Role should remain admin (or whatever it was)
        user_response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert user_response.json()["role"] == "admin"


class TestChangePassword:
    """Test password change functionality"""

    def test_change_password_success(self, db_session: Session, admin_user):
        """Test successful password change"""
        token = get_auth_token()
        assert token is not None

        response = client.patch(
            "/api/v1/users/me/change-password",
            json={"current_password": "testpass123", "new_password": "newpass123"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()

        # Verify new password works
        new_token = get_auth_token(password="newpass123")
        assert new_token is not None

        # Change it back
        client.patch(
            "/api/v1/users/me/change-password",
            json={"current_password": "newpass123", "new_password": "testpass123"},
            headers={"Authorization": f"Bearer {new_token}"},
        )

    def test_change_password_wrong_current(self, db_session: Session, admin_user):
        """Test password change with wrong current password"""
        token = get_auth_token()
        assert token is not None

        response = client.patch(
            "/api/v1/users/me/change-password",
            json={"current_password": "wrongpassword", "new_password": "newpass123"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert "incorrect" in response.json()["detail"].lower()


class TestNotificationPreferences:
    """Test notification preferences functionality"""

    def test_get_preferences(self, db_session: Session, admin_user):
        """Test getting user preferences"""
        token = get_auth_token()
        assert token is not None

        response = client.get(
            "/api/v1/users/me/preferences",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert "email_notifications" in response.json()
        assert "course_updates" in response.json()
        assert "system_announcements" in response.json()

    def test_update_preferences(self, db_session: Session, admin_user):
        """Test updating user preferences"""
        token = get_auth_token()
        assert token is not None

        response = client.patch(
            "/api/v1/users/me/preferences",
            json={"email_notifications": False, "course_updates": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["email_notifications"] is False
        assert response.json()["course_updates"] is True


class TestCoursePrerequisites:
    """Test course prerequisites functionality"""

    def test_get_available_prerequisites(self, db_session: Session, admin_user, test_course):
        """Test getting available prerequisite courses"""
        token = get_auth_token()
        assert token is not None

        response = client.get(
            "/api/v1/courses/prerequisites/available",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_course_with_prerequisites(self, db_session: Session, admin_user, test_course):
        """Test creating a course with prerequisites"""
        token = get_auth_token()
        assert token is not None

        response = client.post(
            "/api/v1/courses",
            json={
                "title": "Advanced Course",
                "description": "Requires test course",
                "prerequisites": [test_course.id],
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["prerequisites"] == [test_course.id]

    def test_cannot_set_self_as_prerequisite(self, db_session: Session, admin_user, test_course):
        """Test that a course cannot be a prerequisite for itself"""
        token = get_auth_token()
        assert token is not None

        response = client.patch(
            f"/api/v1/courses/{test_course.id}",
            json={"prerequisites": [test_course.id]},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 400
        assert "prerequisite for itself" in response.json()["detail"].lower()


class TestStaffActivityLogs:
    """Test staff activity logs functionality"""

    def test_get_activity_logs(self, db_session: Session, admin_user):
        """Test getting staff activity logs"""
        token = get_auth_token()
        assert token is not None

        response = client.get(
            "/api/v1/audit/activity",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestErrorHandling:
    """Test error handling improvements"""

    def test_404_returns_json(self, db_session: Session, admin_user):
        """Test that 404 errors return JSON format"""
        token = get_auth_token()
        assert token is not None

        response = client.get(
            "/api/v1/courses/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
        assert response.headers["content-type"] == "application/json"
        assert "detail" in response.json()
        assert "status_code" in response.json()

    def test_content_404_returns_json(self, db_session: Session, admin_user):
        """Test that content 404 errors return JSON format"""
        token = get_auth_token()
        assert token is not None

        response = client.get(
            "/api/v1/content/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404
        assert response.headers["content-type"] == "application/json"
        assert "detail" in response.json()

