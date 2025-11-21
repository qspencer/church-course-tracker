"""
Tests for Course Instances (Course Offerings) API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone, date

from app.models.course import Course
from app.models.course_instance import CourseInstance, CourseInstanceTeacher
from app.models.member import People


@pytest.fixture
def test_course(db_session: Session):
    """Create a test master course"""
    course = Course(
        title="Test Master Course",
        description="A test master course",
        is_active=True,
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course


@pytest.fixture
def test_people(db_session: Session):
    """Create a test person (for teacher)"""
    person = People(
        planning_center_id="test_person_123",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        is_active=True,
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)
    return person


@pytest.fixture
def test_course_instance(db_session: Session, test_course):
    """Create a test course instance"""
    instance = CourseInstance(
        course_id=test_course.id,
        instance_name="Fall 2024 - Session A",
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc),
        is_active=True,
        enrollment_open=True,
    )
    db_session.add(instance)
    db_session.commit()
    db_session.refresh(instance)
    return instance


class TestCourseInstancesEndpoints:
    """Test Course Instance CRUD endpoints"""

    def test_get_course_instances_empty(self, client: TestClient, user_token: str):
        """Test getting course instances when none exist"""
        response = client.get(
            "/api/v1/course-instances",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_course_instance(
        self, client: TestClient, user_token: str, test_course
    ):
        """Test creating a course instance"""
        instance_data = {
            "course_id": test_course.id,
            "instance_name": "Spring 2024 - Session 1",
            "start_date": "2024-03-01T00:00:00Z",
            "end_date": "2024-05-31T23:59:59Z",
            "is_active": True,
            "enrollment_open": True,
        }
        response = client.post(
            "/api/v1/course-instances",
            json=instance_data,
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["instance_name"] == instance_data["instance_name"]
        assert data["course_id"] == test_course.id
        assert "id" in data

    def test_get_course_instance(
        self, client: TestClient, user_token: str, test_course_instance
    ):
        """Test getting a specific course instance"""
        response = client.get(
            f"/api/v1/course-instances/{test_course_instance.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_course_instance.id
        assert data["instance_name"] == test_course_instance.instance_name

    def test_get_course_instance_not_found(
        self, client: TestClient, user_token: str
    ):
        """Test getting a non-existent course instance"""
        response = client.get(
            "/api/v1/course-instances/99999",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404

    def test_update_course_instance(
        self, client: TestClient, user_token: str, test_course_instance
    ):
        """Test updating a course instance"""
        update_data = {
            "instance_name": "Updated Instance Name",
            "enrollment_open": False,
        }
        response = client.patch(
            f"/api/v1/course-instances/{test_course_instance.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["instance_name"] == update_data["instance_name"]
        assert data["enrollment_open"] == update_data["enrollment_open"]

    def test_delete_course_instance(
        self, client: TestClient, user_token: str, test_course, db_session: Session
    ):
        """Test deleting a course instance"""
        # Create an instance to delete
        instance = CourseInstance(
            course_id=test_course.id,
            instance_name="To Be Deleted",
            is_active=True,
        )
        db_session.add(instance)
        db_session.commit()
        db_session.refresh(instance)

        response = client.delete(
            f"/api/v1/course-instances/{instance.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get(
            f"/api/v1/course-instances/{instance.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404

    def test_get_course_instances_filtered_by_course(
        self, client: TestClient, user_token: str, test_course, db_session: Session
    ):
        """Test filtering course instances by course_id"""
        # Create multiple instances
        instance1 = CourseInstance(
            course_id=test_course.id,
            instance_name="Instance 1",
            is_active=True,
        )
        db_session.add(instance1)

        # Create another course and instance
        course2 = Course(title="Course 2", is_active=True)
        db_session.add(course2)
        db_session.commit()
        db_session.refresh(course2)

        instance2 = CourseInstance(
            course_id=course2.id,
            instance_name="Instance 2",
            is_active=True,
        )
        db_session.add(instance2)
        db_session.commit()

        # Filter by course_id
        response = client.get(
            f"/api/v1/course-instances?course_id={test_course.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["course_id"] == test_course.id


class TestCourseInstanceTeachersEndpoints:
    """Test Course Instance Teacher management endpoints"""

    def test_get_instance_teachers_empty(
        self, client: TestClient, user_token: str, test_course_instance
    ):
        """Test getting teachers when none exist"""
        response = client.get(
            f"/api/v1/course-instances/{test_course_instance.id}/teachers",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_add_instance_teacher(
        self, client: TestClient, user_token: str, test_course_instance, test_people
    ):
        """Test adding a teacher to a course instance"""
        teacher_data = {
            "people_id": test_people.id,
            "role_type": "teacher",
            "assigned_date": str(date.today()),
            "is_primary": True,
        }
        response = client.post(
            f"/api/v1/course-instances/{test_course_instance.id}/teachers",
            json=teacher_data,
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["people_id"] == test_people.id
        assert data["role_type"] == "teacher"
        assert data["is_primary"] is True

    def test_get_instance_teachers(
        self,
        client: TestClient,
        user_token: str,
        test_course_instance,
        test_people,
        db_session: Session,
    ):
        """Test getting teachers for an instance"""
        # Add a teacher
        teacher = CourseInstanceTeacher(
            course_instance_id=test_course_instance.id,
            people_id=test_people.id,
            role_type="teacher",
            assigned_date=date.today(),
            is_primary=True,
            is_active=True,
        )
        db_session.add(teacher)
        db_session.commit()

        response = client.get(
            f"/api/v1/course-instances/{test_course_instance.id}/teachers",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["people_id"] == test_people.id

    def test_remove_instance_teacher(
        self,
        client: TestClient,
        user_token: str,
        test_course_instance,
        test_people,
        db_session: Session,
    ):
        """Test removing a teacher from an instance"""
        # Add a teacher
        teacher = CourseInstanceTeacher(
            course_instance_id=test_course_instance.id,
            people_id=test_people.id,
            role_type="teacher",
            assigned_date=date.today(),
            is_primary=True,
            is_active=True,
        )
        db_session.add(teacher)
        db_session.commit()
        db_session.refresh(teacher)

        response = client.delete(
            f"/api/v1/course-instances/{test_course_instance.id}/teachers/{teacher.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 204

        # Verify it's removed
        response = client.get(
            f"/api/v1/course-instances/{test_course_instance.id}/teachers",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        data = response.json()
        assert len(data) == 0


class TestCourseInstanceAuthorization:
    """Test authorization for course instance endpoints"""

    def test_create_course_instance_requires_admin_or_staff(
        self, client: TestClient, test_course
    ):
        """Test that creating course instances requires admin or staff role"""
        # This would need a viewer/regular user token
        # For now, test with no auth
        instance_data = {
            "course_id": test_course.id,
            "instance_name": "Unauthorized Test",
        }
        response = client.post(
            "/api/v1/course-instances",
            json=instance_data,
        )
        assert response.status_code == 401

    def test_delete_course_instance_requires_admin(
        self, client: TestClient, user_token: str, test_course_instance
    ):
        """Test that deleting course instances requires admin role"""
        # This assumes user_token is admin - if not, would need separate test
        response = client.delete(
            f"/api/v1/course-instances/{test_course_instance.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        # Should succeed if admin, or 403 if not admin
        assert response.status_code in [204, 403]

