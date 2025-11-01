"""create_course_enrollment_if_missing

Revision ID: f7e8d9c0b1a2
Revises: a1b2c3d4e5f6
Create Date: 2025-11-01 12:30:00.000000

This migration creates the course_enrollment table if it doesn't exist.
This is a safety migration for production databases that may not have
migration 002 applied properly.

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'f7e8d9c0b1a2'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create course_enrollment table if it doesn't exist"""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()
    
    # Check if required parent tables exist
    if 'course_enrollment' not in existing_tables:
        # Verify required tables exist before creating foreign keys
        if 'people' not in existing_tables:
            raise Exception("Cannot create course_enrollment: 'people' table does not exist. Please run migration 002 first.")
        if 'courses' not in existing_tables:
            raise Exception("Cannot create course_enrollment: 'courses' table does not exist. Please run migration 002 first.")
        
        # Create the course_enrollment table without foreign keys first, then add them
        try:
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
                sa.Column('data_source', sa.String(length=20), nullable=True),
                sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True),
                sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
                sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
                sa.Column('created_by', sa.Integer(), nullable=True),
                sa.Column('updated_by', sa.Integer(), nullable=True),
                sa.PrimaryKeyConstraint('id')
            )
            
            # Add foreign key constraints
            op.create_foreign_key('fk_course_enrollment_course_id', 'course_enrollment', 'courses', ['course_id'], ['id'])
            op.create_foreign_key('fk_course_enrollment_people_id', 'course_enrollment', 'people', ['people_id'], ['id'])
            
            # Create indexes
            op.create_index('ix_course_enrollment_course_id', 'course_enrollment', ['course_id'], unique=False)
            op.create_index('ix_course_enrollment_id', 'course_enrollment', ['id'], unique=False)
            op.create_index('ix_course_enrollment_people_id', 'course_enrollment', ['people_id'], unique=False)
            op.create_index('ix_course_enrollment_planning_center_registration_id', 'course_enrollment', ['planning_center_registration_id'], unique=True)
        except Exception as e:
            # If creation fails, log but don't crash - the table might exist from another source
            import logging
            logging.warning(f"Failed to create course_enrollment table: {e}")
            raise


def downgrade() -> None:
    """Drop course_enrollment table (only if this migration created it)"""
    # This is a safety migration, so we don't want to drop the table
    # if it was created by migration 002
    pass

