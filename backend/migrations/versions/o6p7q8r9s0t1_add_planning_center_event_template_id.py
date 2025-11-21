"""Add planning_center_event_template_id column to courses table

Revision ID: o6p7q8r9s0t1
Revises: n5o6p7q8r9s0
Create Date: 2025-01-15 12:00:00.000000

This migration adds the planning_center_event_template_id column to the courses table.
This column stores the Planning Center event template/series ID for Master Courses,
distinguishing it from the specific event ID used in CourseInstance.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'o6p7q8r9s0t1'
down_revision = 'n5o6p7q8r9s0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add planning_center_event_template_id column to courses table
    op.add_column('courses', sa.Column('planning_center_event_template_id', sa.String(length=50), nullable=True))
    
    # Create index on the new column (model has index=True)
    op.create_index(op.f('ix_courses_planning_center_event_template_id'), 'courses', ['planning_center_event_template_id'], unique=False)


def downgrade() -> None:
    # Drop index first
    op.drop_index(op.f('ix_courses_planning_center_event_template_id'), table_name='courses')
    
    # Drop column
    op.drop_column('courses', 'planning_center_event_template_id')

