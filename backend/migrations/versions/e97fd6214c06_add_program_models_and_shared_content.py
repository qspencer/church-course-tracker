"""add_program_models_and_shared_content

Revision ID: e97fd6214c06
Revises: b2e1ac26a75b
Create Date: 2025-11-24 03:26:58.730761

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e97fd6214c06'
down_revision = 'b2e1ac26a75b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create shared_content table first (no dependencies)
    op.create_table('shared_content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content_type', sa.Enum('DOCUMENT', 'VIDEO', 'AUDIO', 'IMAGE', 'EXTERNAL_LINK', 'EMBEDDED', name='contenttype'), nullable=False),
        sa.Column('storage_type', sa.Enum('DATABASE', 'S3', 'EXTERNAL', name='storagetype'), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('external_url', sa.String(length=1000), nullable=True),
        sa.Column('embedded_content', sa.Text(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('used_in_courses', sa.JSON(), nullable=True),
        sa.Column('used_in_programs', sa.JSON(), nullable=True),
        sa.Column('data_source', sa.String(length=20), nullable=True),
        sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shared_content_id'), 'shared_content', ['id'], unique=False)
    
    # Add shared_content_id to course_content
    # SQLite doesn't support ALTER TABLE for foreign keys, so we use batch mode
    with op.batch_alter_table('course_content', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shared_content_id', sa.Integer(), nullable=True))
        batch_op.create_index(op.f('ix_course_content_shared_content_id'), ['shared_content_id'], unique=False)
        batch_op.create_foreign_key('fk_course_content_shared_content', 'shared_content', ['shared_content_id'], ['id'])
    
    # Create programs table
    op.create_table('programs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('role_definitions', sa.JSON(), nullable=True),
        sa.Column('relationship_config', sa.JSON(), nullable=True),
        sa.Column('locations', sa.JSON(), nullable=True),
        sa.Column('delivery_modes', sa.JSON(), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        sa.Column('planning_center_event_template_id', sa.String(length=50), nullable=True),
        sa.Column('planning_center_event_id', sa.String(length=50), nullable=True),
        sa.Column('planning_center_event_name', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('data_source', sa.String(length=20), nullable=True),
        sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_programs_id'), 'programs', ['id'], unique=False)
    op.create_index(op.f('ix_programs_planning_center_event_template_id'), 'programs', ['planning_center_event_template_id'], unique=False)
    op.create_index(op.f('ix_programs_planning_center_event_id'), 'programs', ['planning_center_event_id'], unique=True)
    
    # Create program_admins table
    op.create_table('program_admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('can_manage_participants', sa.Boolean(), nullable=False),
        sa.Column('can_manage_pairings', sa.Boolean(), nullable=False),
        sa.Column('can_manage_content', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_program_admins_id'), 'program_admins', ['id'], unique=False)
    op.create_index(op.f('ix_program_admins_program_id'), 'program_admins', ['program_id'], unique=False)
    op.create_index(op.f('ix_program_admins_user_id'), 'program_admins', ['user_id'], unique=False)
    
    # Create program_participants table
    op.create_table('program_participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('people_id', sa.Integer(), nullable=False),
        sa.Column('role_name', sa.String(length=100), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('progress_percentage', sa.Float(), nullable=False),
        sa.Column('last_activity_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
        sa.ForeignKeyConstraint(['people_id'], ['people.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_program_participants_id'), 'program_participants', ['id'], unique=False)
    op.create_index(op.f('ix_program_participants_program_id'), 'program_participants', ['program_id'], unique=False)
    op.create_index(op.f('ix_program_participants_people_id'), 'program_participants', ['people_id'], unique=False)
    
    # Create program_pairings table
    op.create_table('program_pairings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('primary_participant_id', sa.Integer(), nullable=False),
        sa.Column('secondary_participant_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
        sa.ForeignKeyConstraint(['primary_participant_id'], ['program_participants.id'], ),
        sa.ForeignKeyConstraint(['secondary_participant_id'], ['program_participants.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_program_pairings_id'), 'program_pairings', ['id'], unique=False)
    op.create_index(op.f('ix_program_pairings_program_id'), 'program_pairings', ['program_id'], unique=False)
    op.create_index(op.f('ix_program_pairings_primary_participant_id'), 'program_pairings', ['primary_participant_id'], unique=False)
    op.create_index(op.f('ix_program_pairings_secondary_participant_id'), 'program_pairings', ['secondary_participant_id'], unique=False)
    
    # Create program_modules table
    op.create_table('program_modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('data_source', sa.String(length=20), nullable=True),
        sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_program_modules_id'), 'program_modules', ['id'], unique=False)
    
    # Create program_content table
    op.create_table('program_content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=True),
        sa.Column('shared_content_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content_type', sa.Enum('DOCUMENT', 'VIDEO', 'AUDIO', 'IMAGE', 'EXTERNAL_LINK', 'EMBEDDED', name='contenttype'), nullable=True),
        sa.Column('storage_type', sa.Enum('DATABASE', 'S3', 'EXTERNAL', name='storagetype'), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('external_url', sa.String(length=1000), nullable=True),
        sa.Column('embedded_content', sa.Text(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('data_source', sa.String(length=20), nullable=True),
        sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
        sa.ForeignKeyConstraint(['module_id'], ['program_modules.id'], ),
        sa.ForeignKeyConstraint(['shared_content_id'], ['shared_content.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_program_content_id'), 'program_content', ['id'], unique=False)
    op.create_index(op.f('ix_program_content_shared_content_id'), 'program_content', ['shared_content_id'], unique=False)
    
    # Create program_content_access_logs table
    op.create_table('program_content_access_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=False),
        sa.Column('access_type', sa.String(length=20), nullable=False),
        sa.Column('access_timestamp', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('progress_percentage', sa.Integer(), nullable=True),
        sa.Column('time_spent', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['content_id'], ['program_content.id'], ),
        sa.ForeignKeyConstraint(['participant_id'], ['program_participants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_program_content_access_logs_id'), 'program_content_access_logs', ['id'], unique=False)
    
    # Create program_sessions table
    op.create_table('program_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('pairing_id', sa.Integer(), nullable=True),
        sa.Column('session_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('session_type', sa.String(length=50), nullable=True),
        sa.Column('participant_ids', sa.JSON(), nullable=True),
        sa.Column('topics_covered', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('content_completed', sa.JSON(), nullable=True),
        sa.Column('milestones_achieved', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
        sa.ForeignKeyConstraint(['pairing_id'], ['program_pairings.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_program_sessions_id'), 'program_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_program_sessions_program_id'), 'program_sessions', ['program_id'], unique=False)
    op.create_index(op.f('ix_program_sessions_pairing_id'), 'program_sessions', ['pairing_id'], unique=False)
    
    # Create program_progress table
    op.create_table('program_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=False),
        sa.Column('progress_type', sa.String(length=50), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=True),
        sa.Column('completion_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completion_percentage', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('milestone_name', sa.String(length=200), nullable=True),
        sa.Column('milestone_description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
        sa.ForeignKeyConstraint(['participant_id'], ['program_participants.id'], ),
        sa.ForeignKeyConstraint(['content_id'], ['program_content.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['program_sessions.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_program_progress_id'), 'program_progress', ['id'], unique=False)
    op.create_index(op.f('ix_program_progress_program_id'), 'program_progress', ['program_id'], unique=False)
    op.create_index(op.f('ix_program_progress_participant_id'), 'program_progress', ['participant_id'], unique=False)
    op.create_index(op.f('ix_program_progress_content_id'), 'program_progress', ['content_id'], unique=False)
    op.create_index(op.f('ix_program_progress_session_id'), 'program_progress', ['session_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_program_progress_session_id'), table_name='program_progress')
    op.drop_index(op.f('ix_program_progress_content_id'), table_name='program_progress')
    op.drop_index(op.f('ix_program_progress_participant_id'), table_name='program_progress')
    op.drop_index(op.f('ix_program_progress_program_id'), table_name='program_progress')
    op.drop_index(op.f('ix_program_progress_id'), table_name='program_progress')
    op.drop_table('program_progress')
    
    op.drop_index(op.f('ix_program_sessions_pairing_id'), table_name='program_sessions')
    op.drop_index(op.f('ix_program_sessions_program_id'), table_name='program_sessions')
    op.drop_index(op.f('ix_program_sessions_id'), table_name='program_sessions')
    op.drop_table('program_sessions')
    
    op.drop_index(op.f('ix_program_content_access_logs_id'), table_name='program_content_access_logs')
    op.drop_table('program_content_access_logs')
    
    op.drop_index(op.f('ix_program_content_shared_content_id'), table_name='program_content')
    op.drop_index(op.f('ix_program_content_id'), table_name='program_content')
    op.drop_table('program_content')
    
    op.drop_index(op.f('ix_program_modules_id'), table_name='program_modules')
    op.drop_table('program_modules')
    
    op.drop_index(op.f('ix_program_pairings_secondary_participant_id'), table_name='program_pairings')
    op.drop_index(op.f('ix_program_pairings_primary_participant_id'), table_name='program_pairings')
    op.drop_index(op.f('ix_program_pairings_program_id'), table_name='program_pairings')
    op.drop_index(op.f('ix_program_pairings_id'), table_name='program_pairings')
    op.drop_table('program_pairings')
    
    op.drop_index(op.f('ix_program_participants_people_id'), table_name='program_participants')
    op.drop_index(op.f('ix_program_participants_program_id'), table_name='program_participants')
    op.drop_index(op.f('ix_program_participants_id'), table_name='program_participants')
    op.drop_table('program_participants')
    
    op.drop_index(op.f('ix_program_admins_user_id'), table_name='program_admins')
    op.drop_index(op.f('ix_program_admins_program_id'), table_name='program_admins')
    op.drop_index(op.f('ix_program_admins_id'), table_name='program_admins')
    op.drop_table('program_admins')
    
    op.drop_index(op.f('ix_programs_planning_center_event_id'), table_name='programs')
    op.drop_index(op.f('ix_programs_planning_center_event_template_id'), table_name='programs')
    op.drop_index(op.f('ix_programs_id'), table_name='programs')
    op.drop_table('programs')
    
    # Remove shared_content_id from course_content
    op.drop_constraint('fk_course_content_shared_content', 'course_content', type_='foreignkey')
    op.drop_index(op.f('ix_course_content_shared_content_id'), table_name='course_content')
    op.drop_column('course_content', 'shared_content_id')
    
    op.drop_index(op.f('ix_shared_content_id'), table_name='shared_content')
    op.drop_table('shared_content')
