"""Add performance indexes for frequently queried fields

Revision ID: 8a1b2c3d4e5f
Revises: 7ddbf9820c62
Create Date: 2025-01-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a1b2c3d4e5f'
down_revision = '7ddbf9820c62'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance indexes for frequently queried fields"""
    
    # Course model indexes
    op.create_index('idx_courses_is_active', 'courses', ['is_active'])
    op.create_index('idx_courses_created_at', 'courses', ['created_at'])
    op.create_index('idx_courses_event_dates', 'courses', ['event_start_date', 'event_end_date'])
    op.create_index('idx_courses_name_active', 'courses', ['name', 'is_active'])
    
    # User model indexes
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    op.create_index('idx_users_last_login', 'users', ['last_login'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # People model indexes
    op.create_index('idx_people_is_active', 'people', ['is_active'])
    op.create_index('idx_people_planning_center_id', 'people', ['planning_center_id'])
    op.create_index('idx_people_last_synced', 'people', ['last_synced_at'])
    op.create_index('idx_people_household_id', 'people', ['household_id'])
    op.create_index('idx_people_name_search', 'people', ['first_name', 'last_name'])
    
    # CourseEnrollment model indexes
    op.create_index('idx_enrollment_status', 'course_enrollment', ['status'])
    op.create_index('idx_enrollment_progress', 'course_enrollment', ['progress_percentage'])
    op.create_index('idx_enrollment_dates', 'course_enrollment', ['enrollment_date', 'completion_date'])
    op.create_index('idx_enrollment_people_course', 'course_enrollment', ['people_id', 'course_id'])
    op.create_index('idx_enrollment_synced', 'course_enrollment', ['planning_center_synced'])
    
    # Content model indexes
    op.create_index('idx_content_course_id', 'content', ['course_id'])
    op.create_index('idx_content_is_active', 'content', ['is_active'])
    op.create_index('idx_content_order', 'content', ['order_sequence'])
    op.create_index('idx_content_type', 'content', ['content_type_id'])
    
    # CourseModule model indexes
    op.create_index('idx_course_modules_course', 'course_modules', ['course_id'])
    op.create_index('idx_course_modules_order', 'course_modules', ['order_sequence'])
    op.create_index('idx_course_modules_active', 'course_modules', ['is_active'])
    
    # CourseContent model indexes
    op.create_index('idx_course_content_module', 'course_content', ['module_id'])
    op.create_index('idx_course_content_order', 'course_content', ['order_sequence'])
    op.create_index('idx_course_content_active', 'course_content', ['is_active'])
    op.create_index('idx_course_content_type', 'course_content', ['content_type'])
    
    # ContentCompletion model indexes
    op.create_index('idx_content_completion_enrollment', 'content_completion', ['course_enrollment_id'])
    op.create_index('idx_content_completion_content', 'content_completion', ['content_id'])
    op.create_index('idx_content_completion_completed', 'content_completion', ['completed_at'])
    op.create_index('idx_content_completion_progress', 'content_completion', ['progress_percentage'])
    
    # AuditLog model indexes
    op.create_index('idx_audit_log_table', 'audit_log', ['table_name'])
    op.create_index('idx_audit_log_action', 'audit_log', ['action'])
    op.create_index('idx_audit_log_changed_by', 'audit_log', ['changed_by'])
    op.create_index('idx_audit_log_changed_at', 'audit_log', ['changed_at'])
    op.create_index('idx_audit_log_record_id', 'audit_log', ['record_id'])
    
    # Composite indexes for common queries
    op.create_index('idx_courses_active_created', 'courses', ['is_active', 'created_at'])
    op.create_index('idx_enrollment_status_progress', 'course_enrollment', ['status', 'progress_percentage'])
    op.create_index('idx_people_active_synced', 'people', ['is_active', 'last_synced_at'])
    op.create_index('idx_users_active_role', 'users', ['is_active', 'role'])


def downgrade():
    """Remove performance indexes"""
    
    # Drop composite indexes
    op.drop_index('idx_users_active_role', 'users')
    op.drop_index('idx_people_active_synced', 'people')
    op.drop_index('idx_enrollment_status_progress', 'course_enrollment')
    op.drop_index('idx_courses_active_created', 'courses')
    
    # Drop audit log indexes
    op.drop_index('idx_audit_log_record_id', 'audit_log')
    op.drop_index('idx_audit_log_changed_at', 'audit_log')
    op.drop_index('idx_audit_log_changed_by', 'audit_log')
    op.drop_index('idx_audit_log_action', 'audit_log')
    op.drop_index('idx_audit_log_table', 'audit_log')
    
    # Drop content completion indexes
    op.drop_index('idx_content_completion_progress', 'content_completion')
    op.drop_index('idx_content_completion_completed', 'content_completion')
    op.drop_index('idx_content_completion_content', 'content_completion')
    op.drop_index('idx_content_completion_enrollment', 'content_completion')
    
    # Drop course content indexes
    op.drop_index('idx_course_content_type', 'course_content')
    op.drop_index('idx_course_content_active', 'course_content')
    op.drop_index('idx_course_content_order', 'course_content')
    op.drop_index('idx_course_content_module', 'course_content')
    
    # Drop course module indexes
    op.drop_index('idx_course_modules_active', 'course_modules')
    op.drop_index('idx_course_modules_order', 'course_modules')
    op.drop_index('idx_course_modules_course', 'course_modules')
    
    # Drop content indexes
    op.drop_index('idx_content_type', 'content')
    op.drop_index('idx_content_order', 'content')
    op.drop_index('idx_content_is_active', 'content')
    op.drop_index('idx_content_course_id', 'content')
    
    # Drop enrollment indexes
    op.drop_index('idx_enrollment_synced', 'course_enrollment')
    op.drop_index('idx_enrollment_people_course', 'course_enrollment')
    op.drop_index('idx_enrollment_dates', 'course_enrollment')
    op.drop_index('idx_enrollment_progress', 'course_enrollment')
    op.drop_index('idx_enrollment_status', 'course_enrollment')
    
    # Drop people indexes
    op.drop_index('idx_people_name_search', 'people')
    op.drop_index('idx_people_household_id', 'people')
    op.drop_index('idx_people_last_synced', 'people')
    op.drop_index('idx_people_planning_center_id', 'people')
    op.drop_index('idx_people_is_active', 'people')
    
    # Drop user indexes
    op.drop_index('idx_users_created_at', 'users')
    op.drop_index('idx_users_last_login', 'users')
    op.drop_index('idx_users_is_active', 'users')
    op.drop_index('idx_users_role', 'users')
    
    # Drop course indexes
    op.drop_index('idx_courses_name_active', 'courses')
    op.drop_index('idx_courses_event_dates', 'courses')
    op.drop_index('idx_courses_created_at', 'courses')
    op.drop_index('idx_courses_is_active', 'courses')
