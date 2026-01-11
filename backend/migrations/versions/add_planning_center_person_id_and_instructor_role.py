"""add_planning_center_person_id_and_instructor_role_to_users

Revision ID: add_pc_person_id_instructor
Revises: 89341846d406
Create Date: 2025-11-29 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_pc_person_id_instructor'
down_revision = 'ad32f739f15c'  # Points to latest head
branch_labels = None
depends_on = None


def upgrade():
    # Add planning_center_person_id column if it doesn't exist
    # Check if column exists first (SQLite doesn't support IF NOT EXISTS for columns)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'planning_center_person_id' not in columns:
        op.add_column('users', sa.Column('planning_center_person_id', sa.String(length=50), nullable=True))
        op.create_index(op.f('ix_users_planning_center_person_id'), 'users', ['planning_center_person_id'], unique=True)
    
    # Note: The role column already exists, we just need to allow 'instructor' as a value
    # SQLite doesn't support CHECK constraints well, so we'll rely on application-level validation
    # For PostgreSQL/MySQL, you could add: ALTER TABLE users ADD CONSTRAINT check_role CHECK (role IN ('admin', 'staff', 'viewer', 'instructor'))


def downgrade():
    # Remove index and column
    op.drop_index(op.f('ix_users_planning_center_person_id'), table_name='users')
    op.drop_column('users', 'planning_center_person_id')

