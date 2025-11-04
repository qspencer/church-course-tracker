"""add_planning_center_event_name_column

Revision ID: j1k2l3m4n5o6
Revises: i0j1k2l3m4n5
Create Date: 2025-11-04 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'j1k2l3m4n5o6'
down_revision = 'i0j1k2l3m4n5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add planning_center_event_name column to courses table if it doesn't exist"""
    # Check if column exists before adding it (to handle cases where it might already exist)
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    # Check if courses table exists
    if inspector.has_table('courses'):
        columns = [col['name'] for col in inspector.get_columns('courses')]
        
        if 'planning_center_event_name' not in columns:
            # Add the column
            op.add_column('courses', sa.Column('planning_center_event_name', sa.String(length=200), nullable=True))
            print("✅ Added planning_center_event_name column to courses table")
        else:
            print("⚠️ planning_center_event_name column already exists, skipping")
    else:
        print("⚠️ courses table does not exist, skipping")


def downgrade() -> None:
    """Remove planning_center_event_name column from courses table"""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    
    # Check if courses table exists and column exists
    if inspector.has_table('courses'):
        columns = [col['name'] for col in inspector.get_columns('courses')]
        
        if 'planning_center_event_name' in columns:
            # Drop the column
            try:
                op.drop_column('courses', 'planning_center_event_name')
                print("✅ Removed planning_center_event_name column from courses table")
            except Exception as e:
                print(f"⚠️ Error removing column: {e}")

