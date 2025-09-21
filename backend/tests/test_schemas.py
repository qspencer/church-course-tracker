"""
Tests for Pydantic schemas
"""

import pytest
from datetime import datetime, date
from pydantic import ValidationError

from app.schemas.people import People, PeopleCreate, PeopleUpdate
from app.schemas.campus import Campus, CampusCreate, CampusUpdate
from app.schemas.role import Role, RoleCreate, RoleUpdate
from app.schemas.course import Course, CourseCreate, CourseUpdate
from app.schemas.content_type import ContentType, ContentTypeCreate, ContentTypeUpdate
from app.schemas.content import Content, ContentCreate, ContentUpdate
from app.schemas.certification import Certification, CertificationCreate, CertificationUpdate
from app.schemas.people_campus import PeopleCampus, PeopleCampusCreate, PeopleCampusUpdate
from app.schemas.people_role import PeopleRole, PeopleRoleCreate, PeopleRoleUpdate
from app.schemas.enrollment import CourseEnrollment, CourseEnrollmentCreate, CourseEnrollmentUpdate
from app.schemas.course_role import CourseRole, CourseRoleCreate, CourseRoleUpdate
from app.schemas.certification_progress import CertificationProgress, CertificationProgressCreate, CertificationProgressUpdate
from app.schemas.progress import ContentCompletion, ContentCompletionCreate, ContentCompletionUpdate
from app.schemas.planning_center_sync import (
    PlanningCenterSyncLog, PlanningCenterSyncLogCreate,
    PlanningCenterWebhookEvent, PlanningCenterWebhookEventCreate, PlanningCenterWebhookEventUpdate,
    PlanningCenterEventsCache, PlanningCenterEventsCacheCreate, PlanningCenterEventsCacheUpdate,
    PlanningCenterRegistrationsCache, PlanningCenterRegistrationsCacheCreate, PlanningCenterRegistrationsCacheUpdate
)
from app.schemas.audit_log import AuditLog, AuditLogCreate


class TestPeopleSchemas:
    """Test People schemas"""
    
    def test_people_create_valid(self):
        """Test valid PeopleCreate schema"""
        people_data = {
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
        
        people = PeopleCreate(**people_data)
        assert people.planning_center_id == "pc_12345"
        assert people.first_name == "John"
        assert people.last_name == "Doe"
        assert people.email == "john.doe@example.com"
        assert people.is_active is True
    
    def test_people_create_minimal(self):
        """Test PeopleCreate with minimal required fields"""
        people_data = {
            "planning_center_id": "pc_12345",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        people = PeopleCreate(**people_data)
        assert people.planning_center_id == "pc_12345"
        assert people.first_name == "John"
        assert people.last_name == "Doe"
        assert people.is_active is True  # Default value
    
    def test_people_create_invalid_email(self):
        """Test PeopleCreate with invalid email"""
        people_data = {
            "planning_center_id": "pc_12345",
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email"
        }
        
        with pytest.raises(ValidationError):
            PeopleCreate(**people_data)
    
    def test_people_update_partial(self):
        """Test PeopleUpdate with partial data"""
        update_data = {
            "first_name": "Jane",
            "email": "jane.doe@example.com"
        }
        
        people_update = PeopleUpdate(**update_data)
        assert people_update.first_name == "Jane"
        assert people_update.email == "jane.doe@example.com"
        assert people_update.last_name is None  # Not provided
    
    def test_people_response_schema(self):
        """Test People response schema"""
        people_data = {
            "planning_center_id": "pc_12345",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "is_active": True,
            "id": 1,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        people = People(**people_data)
        assert people.id == 1
        assert people.planning_center_id == "pc_12345"
        assert people.first_name == "John"
        assert people.created_at is not None
        assert people.updated_at is not None


class TestCampusSchemas:
    """Test Campus schemas"""
    
    def test_campus_create_valid(self):
        """Test valid CampusCreate schema"""
        campus_data = {
            "name": "Main Campus",
            "address": "123 Church St",
            "phone": "555-5678",
            "email": "main@church.com",
            "planning_center_location_id": "loc_123",
            "is_active": True
        }
        
        campus = CampusCreate(**campus_data)
        assert campus.name == "Main Campus"
        assert campus.address == "123 Church St"
        assert campus.email == "main@church.com"
        assert campus.is_active is True
    
    def test_campus_update_partial(self):
        """Test CampusUpdate with partial data"""
        update_data = {
            "name": "Updated Campus Name",
            "is_active": False
        }
        
        campus_update = CampusUpdate(**update_data)
        assert campus_update.name == "Updated Campus Name"
        assert campus_update.is_active is False
        assert campus_update.address is None  # Not provided


class TestRoleSchemas:
    """Test Role schemas"""
    
    def test_role_create_valid(self):
        """Test valid RoleCreate schema"""
        role_data = {
            "name": "Teacher",
            "description": "Course instructor",
            "permissions": ["teach", "grade"],
            "is_active": True
        }
        
        role = RoleCreate(**role_data)
        assert role.name == "Teacher"
        assert role.description == "Course instructor"
        assert role.permissions == ["teach", "grade"]
        assert role.is_active is True
    
    def test_role_create_minimal(self):
        """Test RoleCreate with minimal required fields"""
        role_data = {
            "name": "Student"
        }
        
        role = RoleCreate(**role_data)
        assert role.name == "Student"
        assert role.is_active is True  # Default value


class TestCourseSchemas:
    """Test Course schemas"""
    
    def test_course_create_valid(self):
        """Test valid CourseCreate schema"""
        course_data = {
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
        
        course = CourseCreate(**course_data)
        assert course.name == "Introduction to Faith"
        assert course.planning_center_event_id == "evt_123"
        assert course.max_capacity == 50
        assert course.is_active is True
    
    def test_course_update_partial(self):
        """Test CourseUpdate with partial data"""
        update_data = {
            "name": "Updated Course Name",
            "max_capacity": 75
        }
        
        course_update = CourseUpdate(**update_data)
        assert course_update.name == "Updated Course Name"
        assert course_update.max_capacity == 75
        assert course_update.description is None  # Not provided


class TestContentTypeSchemas:
    """Test ContentType schemas"""
    
    def test_content_type_create_valid(self):
        """Test valid ContentTypeCreate schema"""
        content_type_data = {
            "name": "Video",
            "description": "Video content",
            "icon_class": "fas fa-video",
            "is_active": True
        }
        
        content_type = ContentTypeCreate(**content_type_data)
        assert content_type.name == "Video"
        assert content_type.description == "Video content"
        assert content_type.icon_class == "fas fa-video"
        assert content_type.is_active is True


class TestContentSchemas:
    """Test Content schemas"""
    
    def test_content_create_valid(self):
        """Test valid ContentCreate schema"""
        content_data = {
            "course_id": 1,
            "title": "Welcome Video",
            "content_type_id": 1,
            "order_sequence": 1,
            "file_path": "/videos/welcome.mp4",
            "duration_minutes": 15,
            "is_required": True,
            "is_active": True
        }
        
        content = ContentCreate(**content_data)
        assert content.course_id == 1
        assert content.title == "Welcome Video"
        assert content.content_type_id == 1
        assert content.duration_minutes == 15
        assert content.is_required is True
    
    def test_content_update_partial(self):
        """Test ContentUpdate with partial data"""
        update_data = {
            "title": "Updated Video Title",
            "duration_minutes": 20
        }
        
        content_update = ContentUpdate(**update_data)
        assert content_update.title == "Updated Video Title"
        assert content_update.duration_minutes == 20
        assert content_update.course_id is None  # Not provided


class TestCertificationSchemas:
    """Test Certification schemas"""
    
    def test_certification_create_valid(self):
        """Test valid CertificationCreate schema"""
        certification_data = {
            "name": "Basic Christian Education",
            "description": "Complete basic Christian education program",
            "required_courses": [1, 2, 3],
            "validity_months": 12,
            "is_active": True
        }
        
        certification = CertificationCreate(**certification_data)
        assert certification.name == "Basic Christian Education"
        assert certification.description == "Complete basic Christian education program"
        assert certification.required_courses == [1, 2, 3]
        assert certification.validity_months == 12
        assert certification.is_active is True


class TestCourseEnrollmentSchemas:
    """Test CourseEnrollment schemas"""
    
    def test_enrollment_create_valid(self):
        """Test valid CourseEnrollmentCreate schema"""
        enrollment_data = {
            "people_id": 1,
            "course_id": 1,
            "enrollment_date": datetime.utcnow(),
            "status": "enrolled",
            "progress_percentage": 0.0,
            "planning_center_synced": False,
            "registration_status": "registered"
        }
        
        enrollment = CourseEnrollmentCreate(**enrollment_data)
        assert enrollment.people_id == 1
        assert enrollment.course_id == 1
        assert enrollment.status == "enrolled"
        assert enrollment.progress_percentage == 0.0
        assert enrollment.planning_center_synced is False
    
    def test_enrollment_create_invalid_status(self):
        """Test CourseEnrollmentCreate with invalid status"""
        enrollment_data = {
            "people_id": 1,
            "course_id": 1,
            "status": "invalid_status"
        }
        
        with pytest.raises(ValidationError):
            CourseEnrollmentCreate(**enrollment_data)
    
    def test_enrollment_update_progress(self):
        """Test CourseEnrollmentUpdate with progress update"""
        update_data = {
            "progress_percentage": 75.5,
            "status": "in_progress"
        }
        
        enrollment_update = CourseEnrollmentUpdate(**update_data)
        assert enrollment_update.progress_percentage == 75.5
        assert enrollment_update.status == "in_progress"
    
    def test_enrollment_update_invalid_progress(self):
        """Test CourseEnrollmentUpdate with invalid progress percentage"""
        update_data = {
            "progress_percentage": 150.0  # Invalid: > 100
        }
        
        with pytest.raises(ValidationError):
            CourseEnrollmentUpdate(**update_data)


class TestContentCompletionSchemas:
    """Test ContentCompletion schemas"""
    
    def test_content_completion_create_valid(self):
        """Test valid ContentCompletionCreate schema"""
        completion_data = {
            "course_enrollment_id": 1,
            "content_id": 1,
            "completed_at": datetime.utcnow(),
            "time_spent_minutes": 15,
            "score": 95.0,
            "notes": "Great video!"
        }
        
        completion = ContentCompletionCreate(**completion_data)
        assert completion.course_enrollment_id == 1
        assert completion.content_id == 1
        assert completion.time_spent_minutes == 15
        assert completion.score == 95.0
        assert completion.notes == "Great video!"
    
    def test_content_completion_update_partial(self):
        """Test ContentCompletionUpdate with partial data"""
        update_data = {
            "score": 98.5,
            "notes": "Updated notes"
        }
        
        completion_update = ContentCompletionUpdate(**update_data)
        assert completion_update.score == 98.5
        assert completion_update.notes == "Updated notes"
        assert completion_update.completed_at is None  # Not provided


class TestPlanningCenterSyncSchemas:
    """Test Planning Center sync schemas"""
    
    def test_sync_log_create_valid(self):
        """Test valid PlanningCenterSyncLogCreate schema"""
        sync_log_data = {
            "sync_type": "people",
            "sync_direction": "from_pc",
            "records_processed": 100,
            "records_successful": 98,
            "records_failed": 2,
            "started_at": datetime.utcnow()
        }
        
        sync_log = PlanningCenterSyncLogCreate(**sync_log_data)
        assert sync_log.sync_type == "people"
        assert sync_log.sync_direction == "from_pc"
        assert sync_log.records_processed == 100
        assert sync_log.records_successful == 98
        assert sync_log.records_failed == 2
    
    def test_webhook_event_create_valid(self):
        """Test valid PlanningCenterWebhookEventCreate schema"""
        webhook_data = {
            "event_type": "person.created",
            "planning_center_id": "pc_123",
            "payload": {"id": "pc_123", "name": "John Doe"},
            "processed": False
        }
        
        webhook_event = PlanningCenterWebhookEventCreate(**webhook_data)
        assert webhook_event.event_type == "person.created"
        assert webhook_event.planning_center_id == "pc_123"
        assert webhook_event.payload == {"id": "pc_123", "name": "John Doe"}
        assert webhook_event.processed is False
    
    def test_events_cache_create_valid(self):
        """Test valid PlanningCenterEventsCacheCreate schema"""
        cache_data = {
            "planning_center_event_id": "evt_123",
            "event_name": "Introduction to Faith",
            "event_description": "Basic course on Christian faith",
            "start_date": datetime(2024, 2, 1, 9, 0),
            "end_date": datetime(2024, 2, 1, 12, 0),
            "max_capacity": 50,
            "current_registrations_count": 25,
            "event_status": "active"
        }
        
        cache = PlanningCenterEventsCacheCreate(**cache_data)
        assert cache.planning_center_event_id == "evt_123"
        assert cache.event_name == "Introduction to Faith"
        assert cache.max_capacity == 50
        assert cache.current_registrations_count == 25
    
    def test_registrations_cache_create_valid(self):
        """Test valid PlanningCenterRegistrationsCacheCreate schema"""
        cache_data = {
            "planning_center_registration_id": "reg_123",
            "planning_center_event_id": "evt_123",
            "planning_center_person_id": "pc_123",
            "registration_status": "registered",
            "registration_date": datetime.utcnow(),
            "custom_field_responses": {"emergency_contact": "555-1234"}
        }
        
        cache = PlanningCenterRegistrationsCacheCreate(**cache_data)
        assert cache.planning_center_registration_id == "reg_123"
        assert cache.planning_center_event_id == "evt_123"
        assert cache.planning_center_person_id == "pc_123"
        assert cache.registration_status == "registered"
        assert cache.custom_field_responses == {"emergency_contact": "555-1234"}


class TestAuditLogSchemas:
    """Test AuditLog schemas"""
    
    def test_audit_log_create_valid(self):
        """Test valid AuditLogCreate schema"""
        audit_data = {
            "table_name": "people",
            "record_id": 1,
            "action": "insert",
            "new_values": {"first_name": "John", "last_name": "Doe"},
            "changed_by": 1,
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0"
        }
        
        audit_log = AuditLogCreate(**audit_data)
        assert audit_log.table_name == "people"
        assert audit_log.record_id == 1
        assert audit_log.action == "insert"
        assert audit_log.new_values == {"first_name": "John", "last_name": "Doe"}
        assert audit_log.changed_by == 1
        assert audit_log.ip_address == "192.168.1.1"
        assert audit_log.user_agent == "Mozilla/5.0"
    
    def test_audit_log_create_invalid_action(self):
        """Test AuditLogCreate with invalid action"""
        audit_data = {
            "table_name": "people",
            "record_id": 1,
            "action": "invalid_action"
        }
        
        with pytest.raises(ValidationError):
            AuditLogCreate(**audit_data)
