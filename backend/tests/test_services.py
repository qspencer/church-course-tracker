"""
Tests for service layer
"""

import pytest
from datetime import datetime, date
from unittest.mock import Mock, patch

from app.services.people_service import PeopleService
from app.services.course_service import CourseService
from app.services.enrollment_service import CourseEnrollmentService
from app.services.planning_center_sync_service import PlanningCenterSyncService
from app.models.member import People
from app.models.course import Course
from app.models.enrollment import CourseEnrollment
from app.schemas.people import PeopleCreate, PeopleUpdate
from app.schemas.course import CourseCreate, CourseUpdate
from app.schemas.enrollment import CourseEnrollmentCreate, CourseEnrollmentUpdate


class TestPeopleService:
    """Test PeopleService"""
    
    def test_get_people(self, db_session, sample_people_data):
        """Test getting all people"""
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
        
        service = PeopleService(db_session)
        people_list = service.get_people()
        
        assert len(people_list) == 2
        assert people_list[0].first_name == "John"
        assert people_list[1].first_name == "Jane"
    
    def test_get_people_with_filter(self, db_session, sample_people_data):
        """Test getting people with active filter"""
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
        
        service = PeopleService(db_session)
        active_people = service.get_people(is_active=True)
        inactive_people = service.get_people(is_active=False)
        
        assert len(active_people) == 1
        assert len(inactive_people) == 1
        assert active_people[0].first_name == "John"
        assert inactive_people[0].first_name == "Jane"
    
    def test_get_person(self, db_session, sample_people_data):
        """Test getting a specific person"""
        people = People(**sample_people_data)
        db_session.add(people)
        db_session.commit()
        
        service = PeopleService(db_session)
        found_people = service.get_person(people.id)
        
        assert found_people is not None
        assert found_people.first_name == "John"
        assert found_people.last_name == "Doe"
    
    def test_get_person_by_pc_id(self, db_session, sample_people_data):
        """Test getting person by Planning Center ID"""
        people = People(**sample_people_data)
        db_session.add(people)
        db_session.commit()
        
        service = PeopleService(db_session)
        found_people = service.get_person_by_pc_id("pc_12345")
        
        assert found_people is not None
        assert found_people.first_name == "John"
        assert found_people.planning_center_id == "pc_12345"
    
    def test_search_people(self, db_session, sample_people_data):
        """Test searching people by name or email"""
        people1 = People(**sample_people_data)
        people2 = People(
            planning_center_id="pc_67890",
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com"
        )
        db_session.add_all([people1, people2])
        db_session.commit()
        
        service = PeopleService(db_session)
        
        # Search by first name
        results = service.search_people("John")
        assert len(results) == 1
        assert results[0].first_name == "John"
        
        # Search by last name
        results = service.search_people("Smith")
        assert len(results) == 1
        assert results[0].last_name == "Smith"
        
        # Search by email
        results = service.search_people("jane.smith")
        assert len(results) == 1
        assert results[0].email == "jane.smith@example.com"
    
    def test_create_person(self, db_session):
        """Test creating a person"""
        people_data = PeopleCreate(
            planning_center_id="pc_12345",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )
        
        service = PeopleService(db_session)
        created_people = service.create_person(people_data)
        
        assert created_people.id is not None
        assert created_people.first_name == "John"
        assert created_people.last_name == "Doe"
        assert created_people.email == "john.doe@example.com"
        assert created_people.created_at is not None
        assert created_people.updated_at is not None
    
    def test_update_person(self, db_session, sample_people_data):
        """Test updating a person"""
        people = People(**sample_people_data)
        db_session.add(people)
        db_session.commit()
        
        update_data = PeopleUpdate(
            first_name="Jane",
            email="jane.doe@example.com"
        )
        
        service = PeopleService(db_session)
        updated_people = service.update_person(people.id, update_data)
        
        assert updated_people is not None
        assert updated_people.first_name == "Jane"
        assert updated_people.email == "jane.doe@example.com"
        assert updated_people.last_name == "Doe"  # Unchanged
    
    def test_delete_person(self, db_session, sample_people_data):
        """Test deleting a person"""
        people = People(**sample_people_data)
        db_session.add(people)
        db_session.commit()
        
        service = PeopleService(db_session)
        success = service.delete_person(people.id)
        
        assert success is True
        
        # Verify person is deleted
        deleted_people = service.get_person(people.id)
        assert deleted_people is None
    
    def test_sync_from_planning_center_new_person(self, db_session):
        """Test syncing new person from Planning Center"""
        pc_person_data = {
            "id": "pc_12345",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "555-1234",
            "status": "active"
        }
        
        service = PeopleService(db_session)
        synced_people = service.sync_from_planning_center(pc_person_data)
        
        assert synced_people.id is not None
        assert synced_people.planning_center_id == "pc_12345"
        assert synced_people.first_name == "John"
        assert synced_people.last_name == "Doe"
        assert synced_people.email == "john.doe@example.com"
        assert synced_people.phone == "555-1234"
        assert synced_people.status == "active"
    
    def test_sync_from_planning_center_existing_person(self, db_session, sample_people_data):
        """Test syncing existing person from Planning Center"""
        people = People(**sample_people_data)
        db_session.add(people)
        db_session.commit()
        
        pc_person_data = {
            "id": "pc_12345",
            "first_name": "John Updated",
            "last_name": "Doe Updated",
            "email": "john.updated@example.com",
            "phone": "555-9999",
            "status": "inactive"
        }
        
        service = PeopleService(db_session)
        synced_people = service.sync_from_planning_center(pc_person_data)
        
        assert synced_people.id == people.id  # Same record
        assert synced_people.first_name == "John Updated"
        assert synced_people.last_name == "Doe Updated"
        assert synced_people.email == "john.updated@example.com"
        assert synced_people.phone == "555-9999"
        assert synced_people.status == "inactive"


class TestCourseService:
    """Test CourseService"""
    
    def test_get_courses(self, db_session, sample_course_data):
        """Test getting all courses"""
        course1 = Course(**sample_course_data)
        course2 = Course(
            name="Advanced Faith",
            description="Advanced course on Christian faith",
            planning_center_event_id="evt_456",
            is_active=True
        )
        db_session.add_all([course1, course2])
        db_session.commit()
        
        service = CourseService(db_session)
        courses = service.get_courses()
        
        assert len(courses) == 2
        assert courses[0].name == "Introduction to Faith"
        assert courses[1].name == "Advanced Faith"
    
    def test_get_course(self, db_session, sample_course_data):
        """Test getting a specific course"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        service = CourseService(db_session)
        found_course = service.get_course(course.id)
        
        assert found_course is not None
        assert found_course.name == "Introduction to Faith"
        assert found_course.planning_center_event_id == "evt_123"
    
    def test_get_course_by_pc_event_id(self, db_session, sample_course_data):
        """Test getting course by Planning Center event ID"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        service = CourseService(db_session)
        found_course = service.get_course_by_pc_event_id("evt_123")
        
        assert found_course is not None
        assert found_course.name == "Introduction to Faith"
        assert found_course.planning_center_event_id == "evt_123"
    
    def test_create_course(self, db_session):
        """Test creating a course"""
        course_data = CourseCreate(
            name="Introduction to Faith",
            description="Basic course on Christian faith",
            planning_center_event_id="evt_123",
            max_capacity=50,
            is_active=True
        )
        
        service = CourseService(db_session)
        created_course = service.create_course(course_data)
        
        assert created_course.id is not None
        assert created_course.name == "Introduction to Faith"
        assert created_course.planning_center_event_id == "evt_123"
        assert created_course.max_capacity == 50
        assert created_course.created_at is not None
        assert created_course.updated_at is not None
    
    def test_update_course(self, db_session, sample_course_data):
        """Test updating a course"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        update_data = CourseUpdate(
            name="Updated Course Name",
            max_capacity=75
        )
        
        service = CourseService(db_session)
        updated_course = service.update_course(course.id, update_data)
        
        assert updated_course is not None
        assert updated_course.name == "Updated Course Name"
        assert updated_course.max_capacity == 75
        assert updated_course.description == "Basic course on Christian faith"  # Unchanged
    
    def test_delete_course(self, db_session, sample_course_data):
        """Test deleting a course"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        service = CourseService(db_session)
        success = service.delete_course(course.id)
        
        assert success is True
        
        # Verify course is deleted
        deleted_course = service.get_course(course.id)
        assert deleted_course is None
    
    def test_sync_from_planning_center_new_course(self, db_session):
        """Test syncing new course from Planning Center"""
        pc_event_data = {
            "id": "evt_123",
            "name": "Introduction to Faith",
            "description": "Basic course on Christian faith",
            "start_date": datetime(2024, 2, 1, 9, 0),
            "end_date": datetime(2024, 2, 1, 12, 0),
            "max_capacity": 50,
            "current_registrations": 25
        }
        
        service = CourseService(db_session)
        synced_course = service.sync_from_planning_center(pc_event_data)
        
        assert synced_course.id is not None
        assert synced_course.planning_center_event_id == "evt_123"
        assert synced_course.name == "Introduction to Faith"
        assert synced_course.max_capacity == 50
        assert synced_course.current_registrations == 25
    
    def test_sync_from_planning_center_existing_course(self, db_session, sample_course_data):
        """Test syncing existing course from Planning Center"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        pc_event_data = {
            "id": "evt_123",
            "name": "Updated Course Name",
            "description": "Updated description",
            "start_date": datetime(2024, 3, 1, 9, 0),
            "end_date": datetime(2024, 3, 1, 12, 0),
            "max_capacity": 75,
            "current_registrations": 50
        }
        
        service = CourseService(db_session)
        synced_course = service.sync_from_planning_center(pc_event_data)
        
        assert synced_course.id == course.id  # Same record
        assert synced_course.name == "Updated Course Name"
        assert synced_course.description == "Updated description"
        assert synced_course.max_capacity == 75
        assert synced_course.current_registrations == 50


class TestCourseEnrollmentService:
    """Test CourseEnrollmentService"""
    
    def test_get_enrollments(self, db_session, sample_people_data, sample_course_data):
        """Test getting all enrollments"""
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
        
        service = CourseEnrollmentService(db_session)
        enrollments = service.get_enrollments()
        
        assert len(enrollments) == 2
        assert enrollments[0].status == "enrolled"
        assert enrollments[1].status == "completed"
    
    def test_get_enrollments_with_filters(self, db_session, sample_people_data, sample_course_data):
        """Test getting enrollments with filters"""
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
        
        service = CourseEnrollmentService(db_session)
        
        # Filter by status
        enrolled = service.get_enrollments(status="enrolled")
        completed = service.get_enrollments(status="completed")
        
        assert len(enrolled) == 1
        assert len(completed) == 1
        assert enrolled[0].status == "enrolled"
        assert completed[0].status == "completed"
        
        # Filter by course
        course_enrollments = service.get_enrollments(course_id=course.id)
        assert len(course_enrollments) == 2
        
        # Filter by people
        people_enrollments = service.get_enrollments(people_id=people.id)
        assert len(people_enrollments) == 2
    
    def test_get_enrollment(self, db_session, sample_people_data, sample_course_data):
        """Test getting a specific enrollment"""
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
        
        service = CourseEnrollmentService(db_session)
        found_enrollment = service.get_enrollment(enrollment.id)
        
        assert found_enrollment is not None
        assert found_enrollment.status == "enrolled"
        assert found_enrollment.people_id == people.id
        assert found_enrollment.course_id == course.id
    
    def test_create_enrollment(self, db_session, sample_people_data, sample_course_data):
        """Test creating an enrollment"""
        # Create related records
        people = People(**sample_people_data)
        course = Course(**sample_course_data)
        db_session.add_all([people, course])
        db_session.commit()
        
        enrollment_data = CourseEnrollmentCreate(
            people_id=people.id,
            course_id=course.id,
            enrollment_date=datetime.utcnow(),
            status="enrolled"
        )
        
        service = CourseEnrollmentService(db_session)
        created_enrollment = service.create_enrollment(enrollment_data)
        
        assert created_enrollment.id is not None
        assert created_enrollment.people_id == people.id
        assert created_enrollment.course_id == course.id
        assert created_enrollment.status == "enrolled"
        assert created_enrollment.created_at is not None
        assert created_enrollment.updated_at is not None
    
    def test_update_enrollment(self, db_session, sample_people_data, sample_course_data):
        """Test updating an enrollment"""
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
        
        update_data = CourseEnrollmentUpdate(
            status="in_progress",
            progress_percentage=50.0
        )
        
        service = CourseEnrollmentService(db_session)
        updated_enrollment = service.update_enrollment(enrollment.id, update_data)
        
        assert updated_enrollment is not None
        assert updated_enrollment.status == "in_progress"
        assert updated_enrollment.progress_percentage == 50.0
    
    def test_update_progress(self, db_session, sample_people_data, sample_course_data):
        """Test updating enrollment progress"""
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
        
        service = CourseEnrollmentService(db_session)
        updated_enrollment = service.update_progress(enrollment.id, 75.0)
        
        assert updated_enrollment is not None
        assert updated_enrollment.progress_percentage == 75.0
        assert updated_enrollment.status == "in_progress"
        assert updated_enrollment.completion_date is None  # Not 100% yet
        
        # Test completion
        completed_enrollment = service.update_progress(enrollment.id, 100.0)
        assert completed_enrollment.progress_percentage == 100.0
        assert completed_enrollment.status == "completed"
        assert completed_enrollment.completion_date is not None
    
    def test_bulk_enroll(self, db_session, sample_course_data):
        """Test bulk enrollment"""
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
        
        service = CourseEnrollmentService(db_session)
        enrollments = service.bulk_enroll(course.id, [people1.id, people2.id])
        
        assert len(enrollments) == 2
        assert enrollments[0].people_id == people1.id
        assert enrollments[1].people_id == people2.id
        assert enrollments[0].course_id == course.id
        assert enrollments[1].course_id == course.id
    
    def test_delete_enrollment(self, db_session, sample_people_data, sample_course_data):
        """Test deleting an enrollment"""
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
        
        service = CourseEnrollmentService(db_session)
        success = service.delete_enrollment(enrollment.id)
        
        assert success is True
        
        # Verify enrollment is deleted
        deleted_enrollment = service.get_enrollment(enrollment.id)
        assert deleted_enrollment is None


class TestPlanningCenterSyncService:
    """Test PlanningCenterSyncService"""
    
    def test_create_sync_task(self, db_session):
        """Test creating a sync task"""
        service = PlanningCenterSyncService(db_session)
        task_id = service._create_sync_task("sync_people")
        
        assert task_id is not None
        assert len(task_id) > 0
        
        # Check task was created
        task_status = service.get_sync_task_status(task_id)
        assert task_status is not None
        assert task_status["task_type"] == "sync_people"
        assert task_status["status"] == "pending"
        assert task_status["progress"] == 0
    
    def test_update_sync_task(self, db_session):
        """Test updating a sync task"""
        service = PlanningCenterSyncService(db_session)
        task_id = service._create_sync_task("sync_people")
        
        # Update task
        service._update_sync_task(task_id, status="running", progress=50, message="Processing...")
        
        task_status = service.get_sync_task_status(task_id)
        assert task_status["status"] == "running"
        assert task_status["progress"] == 50
        assert task_status["message"] == "Processing..."
    
    def test_list_sync_tasks(self, db_session):
        """Test listing sync tasks"""
        service = PlanningCenterSyncService(db_session)
        
        # Create multiple tasks
        task1 = service._create_sync_task("sync_people")
        task2 = service._create_sync_task("sync_events")
        task3 = service._create_sync_task("sync_people")
        
        # List all tasks
        all_tasks = service.list_sync_tasks()
        assert len(all_tasks) == 3
        
        # List filtered tasks
        people_tasks = service.list_sync_tasks("sync_people")
        assert len(people_tasks) == 2
        
        events_tasks = service.list_sync_tasks("sync_events")
        assert len(events_tasks) == 1
    
    @patch('app.services.planning_center_sync_service.httpx.AsyncClient')
    def test_start_sync_people(self, mock_client, db_session):
        """Test starting people sync"""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "pc_123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john@example.com"
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        service = PlanningCenterSyncService(db_session)
        task_id = service.start_sync_people()
        
        assert task_id is not None
        
        # Check task was created
        task_status = service.get_sync_task_status(task_id)
        assert task_status is not None
        assert task_status["task_type"] == "sync_people"
        assert task_status["status"] == "pending"
    
    @patch('app.services.planning_center_sync_service.httpx.AsyncClient')
    def test_start_sync_events(self, mock_client, db_session):
        """Test starting events sync"""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "evt_123",
                    "name": "Introduction to Faith",
                    "description": "Basic course",
                    "max_capacity": 50
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        service = PlanningCenterSyncService(db_session)
        task_id = service.start_sync_events()
        
        assert task_id is not None
        
        # Check task was created
        task_status = service.get_sync_task_status(task_id)
        assert task_status is not None
        assert task_status["task_type"] == "sync_events"
        assert task_status["status"] == "pending"
    
    def test_process_webhook_event(self, db_session):
        """Test processing webhook event"""
        webhook_data = {
            "event_type": "person.created",
            "id": "pc_123",
            "name": "John Doe"
        }
        
        service = PlanningCenterSyncService(db_session)
        result = service.process_webhook_event(webhook_data)
        
        assert result["status"] == "success"
        assert result["message"] == "Webhook processed successfully"
        
        # Check webhook event was stored
        from app.models.planning_center_webhook_events import PlanningCenterWebhookEvents
        webhook_events = db_session.query(PlanningCenterWebhookEvents).all()
        assert len(webhook_events) == 1
        assert webhook_events[0].event_type == "person.created"
        assert webhook_events[0].planning_center_id == "pc_123"
        assert webhook_events[0].processed is True
