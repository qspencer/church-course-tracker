"""add_planning_center_event_id_column

Revision ID: a1b2c3d4e5f6
Revises: 69026e93dba9
Create Date: 2025-10-31 21:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '69026e93dba9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add planning_center_event_id column to courses table if it doesn't exist"""
    # Check if column exists before adding it (to handle cases where it might already exist)
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('courses')]
    
    if 'planning_center_event_id' not in columns:
        # Add the column
        op.add_column('courses', sa.Column('planning_center_event_id', sa.String(length=50), nullable=True))
        
        # Create unique index on the column
        try:
            op.create_index(op.f('ix_courses_planning_center_event_id'), 'courses', ['planning_center_event_id'], unique=True)
        except Exception:
            # Index might already exist, ignore
            pass


def downgrade() -> None:
    """Remove planning_center_event_id column from courses table"""
    # Drop the index first
    try:
        op.drop_index(op.f('ix_courses_planning_center_event_id'), table_name='courses')
    except Exception:
        # Index might not exist, ignore
        pass
    
    # Drop the column
    try:
        op.drop_column('courses', 'planning_center_event_id')
    except Exception:
        # Column might not exist, ignore
        pass

