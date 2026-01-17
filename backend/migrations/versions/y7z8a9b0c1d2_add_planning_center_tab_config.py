"""add planning_center_tab_config to programs

Revision ID: y7z8a9b0c1d2
Revises: 491e9afe7b6d
Create Date: 2026-01-17 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'y7z8a9b0c1d2'
down_revision = '491e9afe7b6d'
branch_labels = None
depends_on = None


def upgrade():
    # Add planning_center_tab_config JSON column to programs table
    op.add_column('programs', sa.Column('planning_center_tab_config', sa.JSON(), nullable=True))


def downgrade():
    # Remove planning_center_tab_config column
    op.drop_column('programs', 'planning_center_tab_config')
