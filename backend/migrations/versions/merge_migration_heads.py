"""Merge migration heads

Revision ID: merge_heads_001
Revises: 8a1b2c3d4e5f, 6e85db6cd84c, add_csv_source_tracking
Create Date: 2025-10-13 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads_001'
down_revision = ('8a1b2c3d4e5f', '6e85db6cd84c', 'add_csv_source_tracking')
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Merge all migration heads - no schema changes needed"""
    pass


def downgrade() -> None:
    """Downgrade merge - no schema changes needed"""
    pass
