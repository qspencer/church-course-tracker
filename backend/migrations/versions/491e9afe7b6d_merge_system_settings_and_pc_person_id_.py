"""merge system_settings and pc_person_id heads

Revision ID: 491e9afe7b6d
Revises: add_pc_person_id_instructor, x3y4z5a6b7c8
Create Date: 2026-01-11 22:01:47.908898

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '491e9afe7b6d'
down_revision = ('add_pc_person_id_instructor', 'x3y4z5a6b7c8')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
