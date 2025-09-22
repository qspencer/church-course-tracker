"""Refined schema with Planning Center integration

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old tables first
    op.drop_table('progress')
    op.drop_table('enrollments')
    op.drop_table('courses')
    op.drop_table('members')
    
    # Create new tables
    
    # Campus table
    op.create_table('campus',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('planning_center_location_id', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campus_id'), 'campus', ['id'], unique=False)
    op.create_index(op.f('ix_campus_name'), 'campus', ['name'], unique=False)

    # Role table
    op.create_table('role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_role_id'), 'role', ['id'], unique=False)
    op.create_index(op.f('ix_role_name'), 'role', ['name'], unique=True)

    # ContentType table
    op.create_table('content_type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon_class', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_type_id'), 'content_type', ['id'], unique=False)
    op.create_index(op.f('ix_content_type_name'), 'content_type', ['name'], unique=True)

    # People table (replaces members)
    op.create_table('people',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('planning_center_id', sa.String(length=50), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('address1', sa.String(length=255), nullable=True),
        sa.Column('address2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('zip', sa.String(length=20), nullable=True),
        sa.Column('household_id', sa.String(length=50), nullable=True),
        sa.Column('household_name', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('join_date', sa.Date(), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_people_email'), 'people', ['email'], unique=False)
    op.create_index(op.f('ix_people_id'), 'people', ['id'], unique=False)
    op.create_index(op.f('ix_people_planning_center_id'), 'people', ['planning_center_id'], unique=True)

    # Courses table (updated with PC integration)
    op.create_table('courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('duration_weeks', sa.Integer(), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        sa.Column('planning_center_event_id', sa.String(length=50), nullable=True),
        sa.Column('planning_center_event_name', sa.String(length=200), nullable=True),
        sa.Column('event_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('event_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_capacity', sa.Integer(), nullable=True),
        sa.Column('current_registrations', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_courses_id'), 'courses', ['id'], unique=False)
    op.create_index(op.f('ix_courses_name'), 'courses', ['name'], unique=False)
    op.create_index(op.f('ix_courses_planning_center_event_id'), 'courses', ['planning_center_event_id'], unique=True)

    # Content table
    op.create_table('content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content_type_id', sa.Integer(), nullable=False),
        sa.Column('order_sequence', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_course_id'), 'content', ['course_id'], unique=False)
    op.create_index(op.f('ix_content_content_type_id'), 'content', ['content_type_id'], unique=False)
    op.create_index(op.f('ix_content_id'), 'content', ['id'], unique=False)

    # Certification table
    op.create_table('certification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('required_courses', sa.JSON(), nullable=True),
        sa.Column('validity_months', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_certification_id'), 'certification', ['id'], unique=False)
    op.create_index(op.f('ix_certification_name'), 'certification', ['name'], unique=False)

    # Relationship tables
    op.create_table('people_campus',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('people_id', sa.Integer(), nullable=False),
        sa.Column('campus_id', sa.Integer(), nullable=False),
        sa.Column('assigned_date', sa.Date(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['campus_id'], ['campus.id'], ),
        sa.ForeignKeyConstraint(['people_id'], ['people.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_people_campus_campus_id'), 'people_campus', ['campus_id'], unique=False)
    op.create_index(op.f('ix_people_campus_id'), 'people_campus', ['id'], unique=False)
    op.create_index(op.f('ix_people_campus_people_id'), 'people_campus', ['people_id'], unique=False)

    op.create_table('people_role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('people_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('assigned_date', sa.Date(), nullable=False),
        sa.Column('assigned_by', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['people_id'], ['people.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_people_role_id'), 'people_role', ['id'], unique=False)
    op.create_index(op.f('ix_people_role_people_id'), 'people_role', ['people_id'], unique=False)
    op.create_index(op.f('ix_people_role_role_id'), 'people_role', ['role_id'], unique=False)

    op.create_table('course_enrollment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('people_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('planning_center_registration_id', sa.String(length=50), nullable=True),
        sa.Column('enrollment_date', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('progress_percentage', sa.Float(), nullable=False),
        sa.Column('completion_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('dependency_override', sa.Boolean(), nullable=False),
        sa.Column('dependency_override_by', sa.Integer(), nullable=True),
        sa.Column('planning_center_synced', sa.Boolean(), nullable=False),
        sa.Column('registration_status', sa.String(length=20), nullable=True),
        sa.Column('registration_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['people_id'], ['people.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_course_enrollment_course_id'), 'course_enrollment', ['course_id'], unique=False)
    op.create_index(op.f('ix_course_enrollment_id'), 'course_enrollment', ['id'], unique=False)
    op.create_index(op.f('ix_course_enrollment_people_id'), 'course_enrollment', ['people_id'], unique=False)
    op.create_index(op.f('ix_course_enrollment_planning_center_registration_id'), 'course_enrollment', ['planning_center_registration_id'], unique=True)

    op.create_table('course_role',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('people_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('role_type', sa.String(length=50), nullable=False),
        sa.Column('assigned_date', sa.Date(), nullable=False),
        sa.Column('assigned_by', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['people_id'], ['people.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_course_role_course_id'), 'course_role', ['course_id'], unique=False)
    op.create_index(op.f('ix_course_role_id'), 'course_role', ['id'], unique=False)
    op.create_index(op.f('ix_course_role_people_id'), 'course_role', ['people_id'], unique=False)

    op.create_table('certification_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('people_id', sa.Integer(), nullable=False),
        sa.Column('certification_id', sa.Integer(), nullable=False),
        sa.Column('started_date', sa.Date(), nullable=False),
        sa.Column('completed_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('expires_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['certification_id'], ['certification.id'], ),
        sa.ForeignKeyConstraint(['people_id'], ['people.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_certification_progress_certification_id'), 'certification_progress', ['certification_id'], unique=False)
    op.create_index(op.f('ix_certification_progress_id'), 'certification_progress', ['id'], unique=False)
    op.create_index(op.f('ix_certification_progress_people_id'), 'certification_progress', ['people_id'], unique=False)

    op.create_table('content_completion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_enrollment_id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_spent_minutes', sa.Integer(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['content_id'], ['content.id'], ),
        sa.ForeignKeyConstraint(['course_enrollment_id'], ['course_enrollment.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_completion_content_id'), 'content_completion', ['content_id'], unique=False)
    op.create_index(op.f('ix_content_completion_course_enrollment_id'), 'content_completion', ['course_enrollment_id'], unique=False)
    op.create_index(op.f('ix_content_completion_id'), 'content_completion', ['id'], unique=False)

    # Planning Center integration tables
    op.create_table('planning_center_sync_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sync_type', sa.String(length=50), nullable=False),
        sa.Column('sync_direction', sa.String(length=20), nullable=False),
        sa.Column('records_processed', sa.Integer(), nullable=False),
        sa.Column('records_successful', sa.Integer(), nullable=False),
        sa.Column('records_failed', sa.Integer(), nullable=False),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_planning_center_sync_log_id'), 'planning_center_sync_log', ['id'], unique=False)

    op.create_table('planning_center_webhook_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('planning_center_id', sa.String(length=50), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('processed', sa.Boolean(), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_planning_center_webhook_events_id'), 'planning_center_webhook_events', ['id'], unique=False)
    op.create_index(op.f('ix_planning_center_webhook_events_planning_center_id'), 'planning_center_webhook_events', ['planning_center_id'], unique=False)

    op.create_table('planning_center_events_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('planning_center_event_id', sa.String(length=50), nullable=False),
        sa.Column('event_name', sa.String(length=200), nullable=False),
        sa.Column('event_description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_capacity', sa.Integer(), nullable=True),
        sa.Column('current_registrations_count', sa.Integer(), nullable=False),
        sa.Column('registration_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('event_status', sa.String(length=50), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_planning_center_events_cache_id'), 'planning_center_events_cache', ['id'], unique=False)
    op.create_index(op.f('ix_planning_center_events_cache_planning_center_event_id'), 'planning_center_events_cache', ['planning_center_event_id'], unique=True)

    op.create_table('planning_center_registrations_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('planning_center_registration_id', sa.String(length=50), nullable=False),
        sa.Column('planning_center_event_id', sa.String(length=50), nullable=False),
        sa.Column('planning_center_person_id', sa.String(length=50), nullable=False),
        sa.Column('registration_status', sa.String(length=50), nullable=True),
        sa.Column('registration_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('registration_notes', sa.Text(), nullable=True),
        sa.Column('custom_field_responses', sa.JSON(), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_planning_center_registrations_cache_id'), 'planning_center_registrations_cache', ['id'], unique=False)
    op.create_index(op.f('ix_planning_center_registrations_cache_planning_center_registration_id'), 'planning_center_registrations_cache', ['planning_center_registration_id'], unique=True)
    op.create_index(op.f('ix_planning_center_registrations_cache_planning_center_event_id'), 'planning_center_registrations_cache', ['planning_center_event_id'], unique=False)
    op.create_index(op.f('ix_planning_center_registrations_cache_planning_center_person_id'), 'planning_center_registrations_cache', ['planning_center_person_id'], unique=False)

    # Audit log table
    op.create_table('audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('table_name', sa.String(length=100), nullable=False),
        sa.Column('record_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('changed_by', sa.Integer(), nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_log_id'), 'audit_log', ['id'], unique=False)
    op.create_index(op.f('ix_audit_log_record_id'), 'audit_log', ['record_id'], unique=False)
    op.create_index(op.f('ix_audit_log_table_name'), 'audit_log', ['table_name'], unique=False)

    # Certification required courses association table
    op.create_table('certification_required_courses',
        sa.Column('certification_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['certification_id'], ['certification.id'], ),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.PrimaryKeyConstraint('certification_id', 'course_id')
    )

    # Foreign key constraints are already included in table creation


def downgrade() -> None:
    # Drop all new tables
    op.drop_table('certification_required_courses')
    op.drop_table('audit_log')
    op.drop_table('planning_center_registrations_cache')
    op.drop_table('planning_center_events_cache')
    op.drop_table('planning_center_webhook_events')
    op.drop_table('planning_center_sync_log')
    op.drop_table('content_completion')
    op.drop_table('certification_progress')
    op.drop_table('course_role')
    op.drop_table('course_enrollment')
    op.drop_table('people_role')
    op.drop_table('people_campus')
    op.drop_table('certification')
    op.drop_table('content')
    op.drop_table('courses')
    op.drop_table('people')
    op.drop_table('content_type')
    op.drop_table('role')
    op.drop_table('campus')
    
    # Recreate old tables (simplified for downgrade)
    op.create_table('members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('planning_center_id', sa.String(length=50), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('courses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('duration_weeks', sa.Integer(), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('enrollments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['member_id'], ['members.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('enrollment_id', sa.Integer(), nullable=False),
        sa.Column('module_name', sa.String(length=200), nullable=False),
        sa.Column('completion_percentage', sa.Float(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['enrollment_id'], ['enrollments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
