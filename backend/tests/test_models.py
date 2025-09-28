"""
Tests for SQLAlchemy models
"""

import pytest
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError

from app.models.member import People
from app.models.campus import Campus
from app.models.role import Role
from app.models.course import Course
from app.models.content_type import ContentType
from app.models.content import Content
from app.models.certification import Certification
from app.models.people_campus import PeopleCampus
from app.models.people_role import PeopleRole
from app.models.enrollment import CourseEnrollment
from app.models.course_role import CourseRole
from app.models.certification_progress import CertificationProgress
from app.models.progress import ContentCompletion
from app.models.planning_center_sync_log import PlanningCenterSyncLog
from app.models.planning_center_webhook_events import PlanningCenterWebhookEvents
from app.models.planning_center_events_cache import PlanningCenterEventsCache
from app.models.planning_center_registrations_cache import PlanningCenterRegistrationsCache
from app.models.audit_log import AuditLog


class TestPeopleModel:
    """Test People model"""
    
    def test_create_people(self, db_session, sample_people_data):
        """Test creating a people record"""
        people = People(**sample_people_data)
        db_session.add(people)
        db_session.commit()
        
        assert people.id is not None
        assert people.planning_center_id == "pc_12345"
        assert people.first_name == "John"
        assert people.last_name == "Doe"
        assert people.email == "john.doe@example.com"
        assert people.is_active is True
        assert people.created_at is not None
        assert people.updated_at is not None
    
    def test_people_required_fields(self, db_session):
        """Test that required fields are enforced"""
        people = People(
            planning_center_id="pc_123",
            first_name="Jane",
            last_name="Smith"
        )
        db_session.add(people)
        db_session.commit()
        
        assert people.id is not None
    
    def test_people_relationships(self, db_session, sample_people_data, sample_campus_data, sample_role_data):
        """Test people relationships"""
        # Create related records
        campus = Campus(**sample_campus_data)
        role = Role(**sample_role_data)
        db_session.add_all([campus, role])
        db_session.commit()
        
        # Create people
        people = People(**sample_people_data)
        db_session.add(people)
        db_session.commit()
        
        # Create relationships
        people_campus = PeopleCampus(
            people_id=people.id,
            campus_id=campus.id,
            assigned_date=date.today(),
            is_primary=True
        )
        people_role = PeopleRole(
            people_id=people.id,
            role_id=role.id,
            assigned_date=date.today()
        )
        db_session.add_all([people_campus, people_role])
        db_session.commit()
        
        # Test relationships
        assert len(people.people_campus) == 1
        assert len(people.people_role) == 1
        assert people.people_campus[0].campus.name == "Main Campus"
        assert people.people_role[0].role.name == "Teacher"


class TestCampusModel:
    """Test Campus model"""
    
    def test_create_campus(self, db_session, sample_campus_data):
        """Test creating a campus record"""
        campus = Campus(**sample_campus_data)
        db_session.add(campus)
        db_session.commit()
        
        assert campus.id is not None
        assert campus.name == "Main Campus"
        assert campus.address == "123 Church St"
        assert campus.is_active is True
        assert campus.created_at is not None
        assert campus.updated_at is not None


class TestRoleModel:
    """Test Role model"""
    
    def test_create_role(self, db_session, sample_role_data):
        """Test creating a role record"""
        role = Role(**sample_role_data)
        db_session.add(role)
        db_session.commit()
        
        assert role.id is not None
        assert role.name == "Teacher"
        assert role.description == "Course instructor"
        assert role.permissions == ["teach", "grade"]
        assert role.is_active is True


class TestCourseModel:
    """Test Course model"""
    
    def test_create_course(self, db_session, sample_course_data):
        """Test creating a course record"""
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        assert course.id is not None
        assert course.title == "Introduction to Faith"
        assert course.planning_center_event_id == "evt_123"
        assert course.max_capacity == 50
        assert course.current_registrations == 0
        assert course.is_active is True
    
    def test_course_relationships(self, db_session, sample_course_data, sample_people_data, sample_content_type_data):
        """Test course relationships"""
        # Create related records
        people = People(**sample_people_data)
        content_type = ContentType(**sample_content_type_data)
        db_session.add_all([people, content_type])
        db_session.commit()
        
        # Create course
        course = Course(**sample_course_data)
        db_session.add(course)
        db_session.commit()
        
        # Create content
        content = Content(
            course_id=course.id,
            title="Welcome Video",
            content_type_id=content_type.id,
            order_sequence=1,
            file_path="/videos/welcome.mp4",
            duration_minutes=15,
            is_required=True
        )
        db_session.add(content)
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
        
        # Test relationships
        assert len(course.content) == 1
        assert len(course.course_enrollments) == 1
        assert course.content[0].title == "Welcome Video"
        assert course.course_enrollments[0].people.first_name == "John"


class TestContentTypeModel:
    """Test ContentType model"""
    
    def test_create_content_type(self, db_session, sample_content_type_data):
        """Test creating a content type record"""
        content_type = ContentType(**sample_content_type_data)
        db_session.add(content_type)
        db_session.commit()
        
        assert content_type.id is not None
        assert content_type.name == "Video"
        assert content_type.description == "Video content"
        assert content_type.icon_class == "fas fa-video"
        assert content_type.is_active is True


class TestContentModel:
    """Test Content model"""
    
    def test_create_content(self, db_session, sample_course_data, sample_content_type_data):
        """Test creating a content record"""
        # Create related records
        course = Course(**sample_course_data)
        content_type = ContentType(**sample_content_type_data)
        db_session.add_all([course, content_type])
        db_session.commit()
        
        # Create content
        content = Content(
            course_id=course.id,
            title="Welcome Video",
            content_type_id=content_type.id,
            order_sequence=1,
            file_path="/videos/welcome.mp4",
            duration_minutes=15,
            is_required=True
        )
        db_session.add(content)
        db_session.commit()
        
        assert content.id is not None
        assert content.title == "Welcome Video"
        assert content.course_id == course.id
        assert content.content_type_id == content_type.id
        assert content.duration_minutes == 15
        assert content.is_required is True


class TestCertificationModel:
    """Test Certification model"""
    
    def test_create_certification(self, db_session, sample_certification_data):
        """Test creating a certification record"""
        certification = Certification(**sample_certification_data)
        db_session.add(certification)
        db_session.commit()
        
        assert certification.id is not None
        assert certification.name == "Basic Christian Education"
        assert certification.description == "Complete basic Christian education program"
        assert certification.validity_months == 12
        assert certification.is_active is True


class TestCourseEnrollmentModel:
    """Test CourseEnrollment model"""
    
    def test_create_enrollment(self, db_session, sample_people_data, sample_course_data):
        """Test creating an enrollment record"""
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
        
        assert enrollment.id is not None
        assert enrollment.people_id == people.id
        assert enrollment.course_id == course.id
        assert enrollment.status == "enrolled"
        assert enrollment.progress_percentage == 0.0
        assert enrollment.planning_center_synced is False
    
    def test_enrollment_relationships(self, db_session, sample_people_data, sample_course_data, sample_content_type_data):
        """Test enrollment relationships"""
        # Create related records
        people = People(**sample_people_data)
        course = Course(**sample_course_data)
        content_type = ContentType(**sample_content_type_data)
        db_session.add_all([people, course, content_type])
        db_session.commit()
        
        # Create content
        content = Content(
            course_id=course.id,
            title="Welcome Video",
            content_type_id=content_type.id,
            order_sequence=1
        )
        db_session.add(content)
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
        
        # Create content completion
        completion = ContentCompletion(
            course_enrollment_id=enrollment.id,
            content_id=content.id,
            completed_at=datetime.utcnow(),
            time_spent_minutes=15,
            score=95.0
        )
        db_session.add(completion)
        db_session.commit()
        
        # Test relationships
        assert len(enrollment.content_completion) == 1
        assert enrollment.content_completion[0].content.title == "Welcome Video"
        assert enrollment.content_completion[0].score == 95.0


class TestPlanningCenterModels:
    """Test Planning Center integration models"""
    
    def test_planning_center_sync_log(self, db_session):
        """Test PlanningCenterSyncLog model"""
        sync_log = PlanningCenterSyncLog(
            sync_type="people",
            sync_direction="from_pc",
            records_processed=100,
            records_successful=98,
            records_failed=2,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db_session.add(sync_log)
        db_session.commit()
        
        assert sync_log.id is not None
        assert sync_log.sync_type == "people"
        assert sync_log.sync_direction == "from_pc"
        assert sync_log.records_processed == 100
        assert sync_log.records_successful == 98
        assert sync_log.records_failed == 2
    
    def test_planning_center_webhook_events(self, db_session):
        """Test PlanningCenterWebhookEvents model"""
        webhook_event = PlanningCenterWebhookEvents(
            event_type="person.created",
            planning_center_id="pc_123",
            payload={"id": "pc_123", "name": "John Doe"},
            processed=False
        )
        db_session.add(webhook_event)
        db_session.commit()
        
        assert webhook_event.id is not None
        assert webhook_event.event_type == "person.created"
        assert webhook_event.planning_center_id == "pc_123"
        assert webhook_event.payload == {"id": "pc_123", "name": "John Doe"}
        assert webhook_event.processed is False
    
    def test_planning_center_events_cache(self, db_session):
        """Test PlanningCenterEventsCache model"""
        event_cache = PlanningCenterEventsCache(
            planning_center_event_id="evt_123",
            event_name="Introduction to Faith",
            event_description="Basic course on Christian faith",
            start_date=datetime(2024, 2, 1, 9, 0),
            end_date=datetime(2024, 2, 1, 12, 0),
            max_capacity=50,
            current_registrations_count=25,
            event_status="active"
        )
        db_session.add(event_cache)
        db_session.commit()
        
        assert event_cache.id is not None
        assert event_cache.planning_center_event_id == "evt_123"
        assert event_cache.event_name == "Introduction to Faith"
        assert event_cache.max_capacity == 50
        assert event_cache.current_registrations_count == 25
    
    def test_planning_center_registrations_cache(self, db_session):
        """Test PlanningCenterRegistrationsCache model"""
        registration_cache = PlanningCenterRegistrationsCache(
            planning_center_registration_id="reg_123",
            planning_center_event_id="evt_123",
            planning_center_person_id="pc_123",
            registration_status="registered",
            registration_date=datetime.utcnow(),
            custom_field_responses={"emergency_contact": "555-1234"}
        )
        db_session.add(registration_cache)
        db_session.commit()
        
        assert registration_cache.id is not None
        assert registration_cache.planning_center_registration_id == "reg_123"
        assert registration_cache.planning_center_event_id == "evt_123"
        assert registration_cache.planning_center_person_id == "pc_123"
        assert registration_cache.registration_status == "registered"
        assert registration_cache.custom_field_responses == {"emergency_contact": "555-1234"}


class TestAuditLogModel:
    """Test AuditLog model"""
    
    def test_create_audit_log(self, db_session):
        """Test creating an audit log record"""
        audit_log = AuditLog(
            table_name="people",
            record_id=1,
            action="insert",
            new_values={"first_name": "John", "last_name": "Doe"},
            changed_by=1,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        db_session.add(audit_log)
        db_session.commit()
        
        assert audit_log.id is not None
        assert audit_log.table_name == "people"
        assert audit_log.record_id == 1
        assert audit_log.action == "insert"
        assert audit_log.new_values == {"first_name": "John", "last_name": "Doe"}
        assert audit_log.changed_by == 1
        assert audit_log.ip_address == "192.168.1.1"
        assert audit_log.user_agent == "Mozilla/5.0"
        assert audit_log.changed_at is not None
