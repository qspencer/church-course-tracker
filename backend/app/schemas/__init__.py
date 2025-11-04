# Pydantic schemas

# Import all schemas
from .audit_log import AuditLog, AuditLogCreate
from .campus import Campus, CampusCreate, CampusUpdate
from .certification import (Certification, CertificationCreate,
                            CertificationUpdate)
from .certification_progress import (CertificationProgress,
                                     CertificationProgressCreate,
                                     CertificationProgressUpdate)
from .content import Content, ContentCreate, ContentUpdate
from .content_type import ContentType, ContentTypeCreate, ContentTypeUpdate
from .course import Course, CourseCreate, CourseUpdate
from .course_content import (ContentAccessLog, ContentAccessLogCreate,
                             ContentAuditLog, ContentAuditLogCreate,
                             ContentDownloadRequest, ContentProgressUpdate,
                             ContentUploadResponse, CourseContent,
                             CourseContentCreate, CourseContentSummary,
                             CourseContentUpdate, CourseModule,
                             CourseModuleCreate, CourseModuleUpdate)
from .course_role import CourseRole, CourseRoleCreate, CourseRoleUpdate
from .enrollment import (CourseEnrollment, CourseEnrollmentCreate,
                         CourseEnrollmentUpdate)
from .people import People, PeopleCreate, PeopleUpdate
from .people_campus import PeopleCampus, PeopleCampusCreate, PeopleCampusUpdate
from .people_role import PeopleRole, PeopleRoleCreate, PeopleRoleUpdate
from .planning_center_sync import (PlanningCenterEventsCache,
                                   PlanningCenterEventsCacheCreate,
                                   PlanningCenterEventsCacheUpdate,
                                   PlanningCenterRegistrationsCache,
                                   PlanningCenterRegistrationsCacheCreate,
                                   PlanningCenterRegistrationsCacheUpdate,
                                   PlanningCenterSyncLog,
                                   PlanningCenterSyncLogCreate,
                                   PlanningCenterWebhookEvent,
                                   PlanningCenterWebhookEventCreate,
                                   PlanningCenterWebhookEventUpdate)
from .progress import (ContentCompletion, ContentCompletionCreate,
                       ContentCompletionUpdate)
from .report import (ReportData, ReportResponse, ReportType, SyncResponse,
                     SyncStatus)
from .role import Role, RoleCreate, RoleUpdate
from .sync import SyncResponse, SyncStatus
from .user import User, UserCreate, UserUpdate

__all__ = [
    # User schemas
    "User",
    "UserCreate",
    "UserUpdate",
    # Core entity schemas
    "People",
    "PeopleCreate",
    "PeopleUpdate",
    "Campus",
    "CampusCreate",
    "CampusUpdate",
    "Role",
    "RoleCreate",
    "RoleUpdate",
    "Course",
    "CourseCreate",
    "CourseUpdate",
    "Content",
    "ContentCreate",
    "ContentUpdate",
    "ContentType",
    "ContentTypeCreate",
    "ContentTypeUpdate",
    "CourseModule",
    "CourseModuleCreate",
    "CourseModuleUpdate",
    "CourseContent",
    "CourseContentCreate",
    "CourseContentUpdate",
    "ContentAccessLog",
    "ContentAccessLogCreate",
    "ContentAuditLog",
    "ContentAuditLogCreate",
    "ContentUploadResponse",
    "ContentDownloadRequest",
    "ContentProgressUpdate",
    "CourseContentSummary",
    "Certification",
    "CertificationCreate",
    "CertificationUpdate",
    # Relationship schemas
    "PeopleCampus",
    "PeopleCampusCreate",
    "PeopleCampusUpdate",
    "PeopleRole",
    "PeopleRoleCreate",
    "PeopleRoleUpdate",
    "CourseEnrollment",
    "CourseEnrollmentCreate",
    "CourseEnrollmentUpdate",
    "CourseRole",
    "CourseRoleCreate",
    "CourseRoleUpdate",
    "CertificationProgress",
    "CertificationProgressCreate",
    "CertificationProgressUpdate",
    "ContentCompletion",
    "ContentCompletionCreate",
    "ContentCompletionUpdate",
    # Planning Center integration schemas
    "PlanningCenterSyncLog",
    "PlanningCenterSyncLogCreate",
    "PlanningCenterWebhookEvent",
    "PlanningCenterWebhookEventCreate",
    "PlanningCenterWebhookEventUpdate",
    "PlanningCenterEventsCache",
    "PlanningCenterEventsCacheCreate",
    "PlanningCenterEventsCacheUpdate",
    "PlanningCenterRegistrationsCache",
    "PlanningCenterRegistrationsCacheCreate",
    "PlanningCenterRegistrationsCacheUpdate",
    # Audit and reporting schemas
    "AuditLog",
    "AuditLogCreate",
    "ReportResponse",
    "ReportData",
    "ReportType",
    "SyncStatus",
    "SyncResponse",
]
