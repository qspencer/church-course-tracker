# SQLAlchemy models

# Import all models to ensure they are registered with SQLAlchemy
from .audit_log import AuditLog
from .campus import Campus
from .certification import Certification
from .certification_progress import CertificationProgress
from .content import Content
from .content_type import ContentType
from .course import Course
from .course_content import (ContentAccessLog, ContentAuditLog, CourseContent,
                             CourseModule)
from .course_instance import CourseInstance, CourseInstanceTeacher
from .course_role import CourseRole
from .enrollment import CourseEnrollment
from .member import People
from .people_campus import PeopleCampus
from .people_role import PeopleRole
from .planning_center_events_cache import PlanningCenterEventsCache
from .planning_center_registrations_cache import \
    PlanningCenterRegistrationsCache
from .planning_center_sync_log import PlanningCenterSyncLog
from .planning_center_webhook_events import PlanningCenterWebhookEvents
from .progress import ContentCompletion
from .program import Program, ProgramAdmin, ProgramParticipant, ProgramPairing
from .program_content import ProgramContent, ProgramModule
from .program_progress import ProgramProgress, ProgramSession
from .role import Role
from .shared_content import SharedContent
from .user import User
from .failed_login_attempt import FailedLoginAttempt
from .user_preference import UserPreference

__all__ = [
    "User",
    "People",
    "Campus",
    "Role",
    "Course",
    "Content",
    "ContentType",
    "CourseModule",
    "CourseContent",
    "ContentAccessLog",
    "ContentAuditLog",
    "CourseInstance",
    "CourseInstanceTeacher",
    "Certification",
    "PeopleCampus",
    "PeopleRole",
    "CourseEnrollment",
    "CourseRole",
    "CertificationProgress",
    "ContentCompletion",
    "PlanningCenterSyncLog",
    "PlanningCenterWebhookEvents",
    "PlanningCenterEventsCache",
    "PlanningCenterRegistrationsCache",
    "AuditLog",
    "FailedLoginAttempt",
    "UserPreference",
    "CourseInstance",
    "CourseInstanceTeacher",
    "Program",
    "ProgramAdmin",
    "ProgramParticipant",
    "ProgramPairing",
    "ProgramModule",
    "ProgramContent",
    "ProgramSession",
    "ProgramProgress",
    "SharedContent",
]
