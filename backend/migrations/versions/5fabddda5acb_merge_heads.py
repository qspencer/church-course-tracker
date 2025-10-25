"""merge_heads

Revision ID: 5fabddda5acb
Revises: 6e85db6cd84c, 8a1b2c3d4e5f
Create Date: 2025-10-24 22:08:24.691848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fabddda5acb'
down_revision = ('6e85db6cd84c', '8a1b2c3d4e5f')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
