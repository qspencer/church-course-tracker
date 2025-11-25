"""add_instructors_locations_delivery_modes_to_courses

Revision ID: b2e1ac26a75b
Revises: v2w3x4y5z6a7
Create Date: 2025-11-24 01:08:55.826957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2e1ac26a75b'
down_revision = 'v2w3x4y5z6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to courses table
    op.add_column('courses', sa.Column('instructors', sa.JSON(), nullable=True))
    op.add_column('courses', sa.Column('locations', sa.JSON(), nullable=True))
    op.add_column('courses', sa.Column('delivery_modes', sa.JSON(), nullable=True))


def downgrade() -> None:
    # Remove the new columns
    op.drop_column('courses', 'delivery_modes')
    op.drop_column('courses', 'locations')
    op.drop_column('courses', 'instructors')
