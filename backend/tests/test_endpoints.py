"""
Tests for API endpoints
"""

import pytest
from datetime import datetime, date
from fastapi.testclient import TestClient

from app.models.member import People
from app.models.course import Course
from app.models.enrollment import CourseEnrollment
from app.models.campus import Campus
from app.models.role import Role
from app.models.content_type import ContentType
from app.models.content import Content
from app.models.certification import Certification


class TestPeopleEndpoints:
    """Test People API endpoints"""
    
    def test_get_people(self, client, db_session, sample_people_data):
        """Test GET /people endpoint"""
        # Create test data
        people1 = People(**sample_people_data)
        people2 = People(
            planning_center_id="pc_67890",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com"
        )
        db_session.add_all([people1, people2])
        db_session.commit()
        
        response = client.get("/api/v1/people/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["first_name"] == "John"
        assert data[1]["first_name"] == "Jane"
    
    def test_get_people_with_filter(self, client, db_session, sample_people_data):
        """Test GET /people with active filter"""
        # Create test data
        people1 = People(**sample_people_data)
        people2 = People(
            planning_center_id="pc_67890",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            is_active=False
        )
        db_session.add_all([people1, people2])
        db_session.commit()
        
        # Test active filter
        response = client.get("/api/v1/people/?is_active=true")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["first_name"] == "John"
        assert data[0]["is_active"] is True
        
        # Test inactive filter
        response = client.get("/api/v1/people/?is_active=false")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["first_name"] == "Jane"
        assert data[0]["is_active"] is False
    
    def test_get_person(self, client, db_session, sample_people_data):
        """Test GET /people/{person_id} endpoint"""
        people = People(**sample_people_data)
        db_session.add(people)
        db_session.commit()
        
        response = client.get(f"/api/v1/people/{people.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == people.id
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == "john.doe@example.com"
    
    def test_get_person_not_found(self, client):
        """Test GET /people/{person_id} with non-existent ID"""
        response = client.get("/api/v1/people/999")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Person not found"
    
    def test_get_person_by_pc_id(self, client, db_session, sample_people_data):
        """Test GET /people/pc-id/{pc_id} endpoint"""
        people = People(**sample_people_data)
        db_session.add(people)
        db_session.commit()
        
        response = client.get(f"/api/v1/people/pc-id/{people.planning_center_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == people.id
        assert data["planning_center_id"] == "pc_12345"
        assert data["first_name"] == "John"
    
    def test_search_people(self, client, db_session, sample_people_data):
        """Test GET /people/search/{search_term} endpoint"""
        people1 = People(**sample_people_data)
        people2 = People(
            planning_center_id="pc_67890",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com"
        )
        db_session.add_all([people1, people2])
        db_session.commit()
        
        # Search by first name
        response = client.get("/api/v1/people/search/John")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["first_name"] == "John"
        
        # Search by last name
        response = client.get("/api/v1/people/search/Smith")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["last_name"] == "Smith"
    
    def test_create_person(self, client):
        """Test POST /people endpoint"""
        people_data = {
            "planning_center_id": "pc_12345",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "555-1234",
            "is_active": True
        }
        
        response = client.post("/api/v1/people/", json=people_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["id"] is not None
        assert data["created_at"] is not None
    
    def test_update_person(self, client, db_session, sample_people_data):
        """Test PUT /people/{person_id} endpoint"""
        people = People(**sample_people_data)
        db_session.add(people)
        db_session.commit()
        
        update_data = {
            "first_name": "Jane",
            "email": "jane.doe@example.com"
        }
        
        response = client.put(f"/api/v1/people/{people.id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["email"] == "jane.doe@example.com"
        assert data["last_name"] == "Doe"  # Unchanged
    
    def test_delete_person(self, client, db_session, sample_people_data):
        """Test DELETE /people/{person_id} endpoint"""
        people = People(**sample_people_data)
        db_session.add(people)
        db_session.commit()
        
        response = client.delete(f"/api/v1/people/{people.id}")
        assert response.status_code == 204
        
        # Verify person is deleted
        response = client.get(f"/api/v1/people/{people.id}")
        assert response.status_code == 404


class TestCourseEndpoints:
    """Test Course API endpoints"""
    
    def test_get_courses(self, client, db_session, sample_course_data):
        """Test GET /courses endpoint"""
        course1 = Course(**sample_course_data)
        course2 = Course(
            title="Advanced Faith",
            description="Advanced course on Christian faith",
            planning_center_event_id="evt_456",
            is_active=True
        )
        db_session.add_all([course1, course2])
        db_session.commit()
        
        response = client.get("/api/v1/courses/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Introduction to Faith"
        assert data[1]["title"] == "Advanced Faith"
    
    def test_get_courses_with_filter(self, client, db_session, sample_course_data):
        """Test GET /courses with active filter"""
        course1 = Course(**sample_course_data)
        course2 = Course(
            title="Inactive Course",
            description="This course is inactive",
            planning_center_event_id="evt_456",
            is_active=False
        )
        db_session.add_all([course1, course2])
        db_session.commit()
        
        # Test active filter
        response = client.get("/api/v1/courses/?is_active=true")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Introduction to Faith"
        assert data[0]["is_active"] is True
        
        # Test inactive filter
        response = client.get("/api/v1/courses/?is_active=false")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Inactive Course"
        assert data[0]["is_active"] is False
    
    def test_get_course(self, client, db_session, sample_course_data):
        """Test GET /courses/{course_id} endpoint"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        response = client.get(f"/api/v1/courses/{course.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == course.id
        assert data["title"] == "Introduction to Faith"
        assert data["planning_center_event_id"] == "evt_123"
    
    def test_get_course_by_pc_event_id(self, client, db_session, sample_course_data):
        """Test GET /courses/pc-event/{pc_event_id} endpoint"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        response = client.get(f"/api/v1/courses/pc-event/{course.planning_center_event_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == course.id
        assert data["planning_center_event_id"] == "evt_123"
        assert data["title"] == "Introduction to Faith"
    
    def test_create_course_unauthorized(self, client):
        """Test POST /courses endpoint without authentication"""
        course_data = {
            "title": "Introduction to Faith",
            "description": "Basic course on Christian faith",
            "planning_center_event_id": "evt_123",
            "max_capacity": 50,
            "is_active": True
        }
        
        response = client.post("/api/v1/courses/", json=course_data)
        assert response.status_code == 401  # Unauthorized
    
    def test_create_course_as_admin(self, client, admin_token):
        """Test POST /courses endpoint as admin user"""
        course_data = {
            "title": "Introduction to Faith",
            "description": "Basic course on Christian faith",
            "planning_center_event_id": "evt_123",
            "max_capacity": 50,
            "is_active": True
        }
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post("/api/v1/courses/", json=course_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Introduction to Faith"
        assert data["planning_center_event_id"] == "evt_123"
        assert data["max_capacity"] == 50
        assert data["id"] is not None
        assert data["created_at"] is not None
    
    def test_create_course_as_staff(self, client, staff_token):
        """Test POST /courses endpoint as staff user"""
        course_data = {
            "title": "Staff Course",
            "description": "Course created by staff",
            "planning_center_event_id": "evt_staff",
            "max_capacity": 30,
            "is_active": True
        }
        
        headers = {"Authorization": f"Bearer {staff_token}"}
        response = client.post("/api/v1/courses/", json=course_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Staff Course"
        assert data["planning_center_event_id"] == "evt_staff"
    
    def test_create_course_as_viewer_forbidden(self, client, viewer_token):
        """Test POST /courses endpoint as viewer user (should be forbidden)"""
        course_data = {
            "title": "Viewer Course",
            "description": "Course created by viewer",
            "planning_center_event_id": "evt_viewer",
            "max_capacity": 20,
            "is_active": True
        }
        
        headers = {"Authorization": f"Bearer {viewer_token}"}
        response = client.post("/api/v1/courses/", json=course_data, headers=headers)
        assert response.status_code == 403  # Forbidden
        
        data = response.json()
        assert "Only admin and staff users can create courses" in data["detail"]
    
    def test_update_course_unauthorized(self, client, db_session, sample_course_data):
        """Test PUT /courses/{course_id} endpoint without authentication"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        update_data = {
            "title": "Updated Course Name",
            "max_capacity": 75
        }
        
        response = client.put(f"/api/v1/courses/{course.id}", json=update_data)
        assert response.status_code == 401  # Unauthorized
    
    def test_update_course_as_admin(self, client, admin_token, db_session, sample_course_data):
        """Test PUT /courses/{course_id} endpoint as admin user"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        update_data = {
            "title": "Updated Course Name",
            "max_capacity": 75
        }
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.put(f"/api/v1/courses/{course.id}", json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated Course Name"
        assert data["max_capacity"] == 75
        assert data["description"] == "Basic course on Christian faith"  # Unchanged
    
    def test_update_course_as_staff(self, client, staff_token, db_session, sample_course_data):
        """Test PUT /courses/{course_id} endpoint as staff user"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        update_data = {
            "title": "Staff Updated Course",
            "max_capacity": 60
        }
        
        headers = {"Authorization": f"Bearer {staff_token}"}
        response = client.put(f"/api/v1/courses/{course.id}", json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Staff Updated Course"
        assert data["max_capacity"] == 60
    
    def test_update_course_as_viewer_forbidden(self, client, viewer_token, db_session, sample_course_data):
        """Test PUT /courses/{course_id} endpoint as viewer user (should be forbidden)"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        update_data = {
            "title": "Viewer Updated Course",
            "max_capacity": 40
        }
        
        headers = {"Authorization": f"Bearer {viewer_token}"}
        response = client.put(f"/api/v1/courses/{course.id}", json=update_data, headers=headers)
        assert response.status_code == 403  # Forbidden
        
        data = response.json()
        assert "Only admin and staff users can update courses" in data["detail"]
    
    def test_delete_course_unauthorized(self, client, db_session, sample_course_data):
        """Test DELETE /courses/{course_id} endpoint without authentication"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        response = client.delete(f"/api/v1/courses/{course.id}")
        assert response.status_code == 401  # Unauthorized
    
    def test_delete_course_as_admin(self, client, admin_token, db_session, sample_course_data):
        """Test DELETE /courses/{course_id} endpoint as admin user"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete(f"/api/v1/courses/{course.id}", headers=headers)
        assert response.status_code == 204
        
        # Verify course is deleted
        response = client.get(f"/api/v1/courses/{course.id}")
        assert response.status_code == 404
    
    def test_delete_course_as_staff_forbidden(self, client, staff_token, db_session, sample_course_data):
        """Test DELETE /courses/{course_id} endpoint as staff user (should be forbidden)"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {staff_token}"}
        response = client.delete(f"/api/v1/courses/{course.id}", headers=headers)
        assert response.status_code == 403  # Forbidden
        
        data = response.json()
        assert "Only admin users can delete courses" in data["detail"]
    
    def test_delete_course_as_viewer_forbidden(self, client, viewer_token, db_session, sample_course_data):
        """Test DELETE /courses/{course_id} endpoint as viewer user (should be forbidden)"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {viewer_token}"}
        response = client.delete(f"/api/v1/courses/{course.id}", headers=headers)
        assert response.status_code == 403  # Forbidden
        
        data = response.json()
        assert "Only admin users can delete courses" in data["detail"]


class TestEnrollmentEndpoints:
    """Test CourseEnrollment API endpoints"""
    
    def test_get_enrollments(self, client, db_session, sample_people_data, sample_course_data):
        """Test GET /enrollments endpoint"""
        # Create related records
        people = People(**sample_people_data)
        course = Course(**sample_course_data)
        db_session.add_all([people, course])
        db_session.commit()
        
        # Create enrollments
        enrollment1 = CourseEnrollment(
            people_id=people.id,
            course_id=course.id,
            enrollment_date=datetime.utcnow(),
            status="enrolled"
        )
        enrollment2 = CourseEnrollment(
            people_id=people.id,
            course_id=course.id,
            enrollment_date=datetime.utcnow(),
            status="completed"
        )
        db_session.add_all([enrollment1, enrollment2])
        db_session.commit()
        
        response = client.get("/api/v1/enrollments/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["status"] == "enrolled"
        assert data[1]["status"] == "completed"
    
    def test_get_enrollments_with_filters(self, client, db_session, sample_people_data, sample_course_data):
        """Test GET /enrollments with filters"""
        # Create related records
        people = People(**sample_people_data)
        course = Course(**sample_course_data)
        db_session.add_all([people, course])
        db_session.commit()
        
        # Create enrollments
        enrollment1 = CourseEnrollment(
            people_id=people.id,
            course_id=course.id,
            enrollment_date=datetime.utcnow(),
            status="enrolled"
        )
        enrollment2 = CourseEnrollment(
            people_id=people.id,
            course_id=course.id,
            enrollment_date=datetime.utcnow(),
            status="completed"
        )
        db_session.add_all([enrollment1, enrollment2])
        db_session.commit()
        
        # Filter by status
        response = client.get("/api/v1/enrollments/?status=enrolled")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "enrolled"
        
        # Filter by course
        response = client.get(f"/api/v1/enrollments/?course_id={course.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        
        # Filter by people
        response = client.get(f"/api/v1/enrollments/?people_id={people.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
    
    def test_get_enrollment(self, client, db_session, sample_people_data, sample_course_data):
        """Test GET /enrollments/{enrollment_id} endpoint"""
        # Create related records
        people = People(**sample_people_data)
        course = Course(**sample_course_data)
        db_session.add_all([people, course])
        db_session.commit()
        
        # Create enrollment
        enrollment = CourseEnrollment(
            people_id=people.id,
            course_id=course.id,
            enrollment_date=datetime.utcnow(),
            status="enrolled"
        )
        db_session.add(enrollment)
        db_session.commit()
        
        response = client.get(f"/api/v1/enrollments/{enrollment.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == enrollment.id
        assert data["status"] == "enrolled"
        assert data["people_id"] == people.id
        assert data["course_id"] == course.id
    
    def test_create_enrollment(self, client, db_session, sample_people_data, sample_course_data):
        """Test POST /enrollments endpoint"""
        # Create related records
        people = People(**sample_people_data)
        course = Course(**sample_course_data)
        db_session.add_all([people, course])
        db_session.commit()
        
        enrollment_data = {
            "people_id": people.id,
            "course_id": course.id,
            "enrollment_date": datetime.utcnow().isoformat(),
            "status": "enrolled"
        }
        
        response = client.post("/api/v1/enrollments/", json=enrollment_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["people_id"] == people.id
        assert data["course_id"] == course.id
        assert data["status"] == "enrolled"
        assert data["id"] is not None
        assert data["created_at"] is not None
    
    def test_bulk_enroll(self, client, db_session, sample_course_data):
        """Test POST /enrollments/bulk endpoint"""
        # Create course
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        # Create people
        people1 = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        people2 = People(
            planning_center_id="pc_456",
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )
        db_session.add_all([people1, people2])
        db_session.commit()
        
        response = client.post(f"/api/v1/enrollments/bulk?course_id={course.id}&people_ids={people1.id}&people_ids={people2.id}")
        assert response.status_code == 201
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["people_id"] == people1.id
        assert data[1]["people_id"] == people2.id
        assert data[0]["course_id"] == course.id
        assert data[1]["course_id"] == course.id
    
    def test_update_enrollment(self, client, db_session, sample_people_data, sample_course_data):
        """Test PUT /enrollments/{enrollment_id} endpoint"""
        # Create related records
        people = People(**sample_people_data)
        course = Course(**sample_course_data)
        db_session.add_all([people, course])
        db_session.commit()
        
        # Create enrollment
        enrollment = CourseEnrollment(
            people_id=people.id,
            course_id=course.id,
            enrollment_date=datetime.utcnow(),
            status="enrolled"
        )
        db_session.add(enrollment)
        db_session.commit()
        
        update_data = {
            "status": "in_progress",
            "progress_percentage": 50.0
        }
        
        response = client.put(f"/api/v1/enrollments/{enrollment.id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["progress_percentage"] == 50.0
    
    def test_update_progress(self, client, db_session, sample_people_data, sample_course_data):
        """Test PUT /enrollments/{enrollment_id}/progress endpoint"""
        # Create related records
        people = People(**sample_people_data)
        course = Course(**sample_course_data)
        db_session.add_all([people, course])
        db_session.commit()
        
        # Create enrollment
        enrollment = CourseEnrollment(
            people_id=people.id,
            course_id=course.id,
            enrollment_date=datetime.utcnow(),
            status="enrolled",
            progress_percentage=0.0
        )
        db_session.add(enrollment)
        db_session.commit()
        
        response = client.put(f"/api/v1/enrollments/{enrollment.id}/progress?progress_percentage=75.0")
        assert response.status_code == 200
        
        data = response.json()
        assert data["progress_percentage"] == 75.0
        assert data["status"] == "in_progress"
    
    def test_delete_enrollment(self, client, db_session, sample_people_data, sample_course_data):
        """Test DELETE /enrollments/{enrollment_id} endpoint"""
        # Create related records
        people = People(**sample_people_data)
        course = Course(**sample_course_data)
        db_session.add_all([people, course])
        db_session.commit()
        
        # Create enrollment
        enrollment = CourseEnrollment(
            people_id=people.id,
            course_id=course.id,
            enrollment_date=datetime.utcnow(),
            status="enrolled"
        )
        db_session.add(enrollment)
        db_session.commit()
        
        response = client.delete(f"/api/v1/enrollments/{enrollment.id}")
        assert response.status_code == 204
        
        # Verify enrollment is deleted
        response = client.get(f"/api/v1/enrollments/{enrollment.id}")
        assert response.status_code == 404


class TestPlanningCenterSyncEndpoints:
    """Test Planning Center sync API endpoints"""
    
    def test_start_sync_people(self, client):
        """Test POST /planning-center/people endpoint"""
        response = client.post("/api/v1/planning-center/people")
        assert response.status_code == 200
        
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "started"
        assert data["message"] == "People sync started in background"
    
    def test_start_sync_events(self, client):
        """Test POST /planning-center/events endpoint"""
        response = client.post("/api/v1/planning-center/events")
        assert response.status_code == 200
        
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "started"
        assert data["message"] == "Events sync started in background"
    
    def test_start_sync_registrations(self, client):
        """Test POST /planning-center/registrations endpoint"""
        response = client.post("/api/v1/planning-center/registrations")
        assert response.status_code == 200
        
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "started"
        assert data["message"] == "Registrations sync started in background"
    
    def test_start_sync_all(self, client):
        """Test POST /planning-center/all endpoint"""
        response = client.post("/api/v1/planning-center/all")
        assert response.status_code == 200
        
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "started"
        assert data["message"] == "Full sync started in background"
    
    def test_list_sync_tasks(self, client):
        """Test GET /planning-center/tasks endpoint"""
        response = client.get("/api/v1/planning-center/tasks")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_sync_task_status(self, client):
        """Test GET /planning-center/tasks/{task_id} endpoint"""
        # First create a task
        response = client.post("/api/v1/planning-center/people")
        assert response.status_code == 200
        
        task_data = response.json()
        task_id = task_data["task_id"]
        
        # Then get its status
        response = client.get(f"/api/v1/planning-center/tasks/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["task_type"] == "sync_people"
        # Status might be "pending" or "running" depending on timing
        assert data["status"] in ["pending", "running", "failed"]
        assert data["progress"] == 0
    
    def test_get_sync_task_status_not_found(self, client):
        """Test GET /planning-center/tasks/{task_id} with non-existent task"""
        response = client.get("/api/v1/planning-center/tasks/non-existent-task-id")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Task not found"
    
    def test_process_webhook(self, client):
        """Test POST /planning-center/webhook endpoint"""
        webhook_data = {
            "event_type": "person.created",
            "id": "pc_123",
            "name": "John Doe"
        }
        
        response = client.post("/api/v1/planning-center/webhook", json=webhook_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "Webhook processed successfully"
    
    def test_process_webhook_invalid_json(self, client):
        """Test POST /planning-center/webhook with invalid JSON"""
        response = client.post("/api/v1/planning-center/webhook", data="invalid json")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Invalid JSON payload"
