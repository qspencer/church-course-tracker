# Pydantic schemas

# Import all schemas
from .user import User, UserCreate, UserUpdate
from .people import People, PeopleCreate, PeopleUpdate
from .campus import Campus, CampusCreate, CampusUpdate
from .role import Role, RoleCreate, RoleUpdate
from .course import Course, CourseCreate, CourseUpdate
from .content import Content, ContentCreate, ContentUpdate
from .content_type import ContentType, ContentTypeCreate, ContentTypeUpdate
from .course_content import (
    CourseModule, CourseModuleCreate, CourseModuleUpdate,
    CourseContent, CourseContentCreate, CourseContentUpdate,
    ContentAccessLog, ContentAccessLogCreate,
    ContentAuditLog, ContentAuditLogCreate,
    ContentUploadResponse, ContentDownloadRequest, ContentProgressUpdate,
    CourseContentSummary
)
from .certification import Certification, CertificationCreate, CertificationUpdate
from .people_campus import PeopleCampus, PeopleCampusCreate, PeopleCampusUpdate
from .people_role import PeopleRole, PeopleRoleCreate, PeopleRoleUpdate
from .enrollment import CourseEnrollment, CourseEnrollmentCreate, CourseEnrollmentUpdate
from .course_role import CourseRole, CourseRoleCreate, CourseRoleUpdate
from .certification_progress import CertificationProgress, CertificationProgressCreate, CertificationProgressUpdate
from .progress import ContentCompletion, ContentCompletionCreate, ContentCompletionUpdate
from .planning_center_sync import (
    PlanningCenterSyncLog, PlanningCenterSyncLogCreate,
    PlanningCenterWebhookEvent, PlanningCenterWebhookEventCreate, PlanningCenterWebhookEventUpdate,
    PlanningCenterEventsCache, PlanningCenterEventsCacheCreate, PlanningCenterEventsCacheUpdate,
    PlanningCenterRegistrationsCache, PlanningCenterRegistrationsCacheCreate, PlanningCenterRegistrationsCacheUpdate
)
from .audit_log import AuditLog, AuditLogCreate
from .report import ReportResponse, ReportData, ReportType, SyncStatus, SyncResponse
from .sync import SyncStatus, SyncResponse

__all__ = [
    # User schemas
    "User", "UserCreate", "UserUpdate",
    
    # Core entity schemas
    "People", "PeopleCreate", "PeopleUpdate",
    "Campus", "CampusCreate", "CampusUpdate", 
    "Role", "RoleCreate", "RoleUpdate",
    "Course", "CourseCreate", "CourseUpdate",
    "Content", "ContentCreate", "ContentUpdate",
    "ContentType", "ContentTypeCreate", "ContentTypeUpdate",
    "CourseModule", "CourseModuleCreate", "CourseModuleUpdate",
    "CourseContent", "CourseContentCreate", "CourseContentUpdate",
    "ContentAccessLog", "ContentAccessLogCreate",
    "ContentAuditLog", "ContentAuditLogCreate",
    "ContentUploadResponse", "ContentDownloadRequest", "ContentProgressUpdate",
    "CourseContentSummary",
    "Certification", "CertificationCreate", "CertificationUpdate",
    
    # Relationship schemas
    "PeopleCampus", "PeopleCampusCreate", "PeopleCampusUpdate",
    "PeopleRole", "PeopleRoleCreate", "PeopleRoleUpdate",
    "CourseEnrollment", "CourseEnrollmentCreate", "CourseEnrollmentUpdate",
    "CourseRole", "CourseRoleCreate", "CourseRoleUpdate",
    "CertificationProgress", "CertificationProgressCreate", "CertificationProgressUpdate",
    "ContentCompletion", "ContentCompletionCreate", "ContentCompletionUpdate",
    
    # Planning Center integration schemas
    "PlanningCenterSyncLog", "PlanningCenterSyncLogCreate",
    "PlanningCenterWebhookEvent", "PlanningCenterWebhookEventCreate", "PlanningCenterWebhookEventUpdate",
    "PlanningCenterEventsCache", "PlanningCenterEventsCacheCreate", "PlanningCenterEventsCacheUpdate",
    "PlanningCenterRegistrationsCache", "PlanningCenterRegistrationsCacheCreate", "PlanningCenterRegistrationsCacheUpdate",
    
    # Audit and reporting schemas
    "AuditLog", "AuditLogCreate",
    "ReportResponse", "ReportData", "ReportType", "SyncStatus", "SyncResponse"
]
