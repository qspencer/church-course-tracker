"""Add system settings table

Revision ID: x3y4z5a6b7c8
Revises: v2w3x4y5z6a7
Create Date: 2025-01-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'x3y4z5a6b7c8'
down_revision = 'v2w3x4y5z6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create system_settings table
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('data_type', sa.String(length=20), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_sensitive', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_system_settings_id'), 'system_settings', ['id'], unique=False)
    op.create_index(op.f('ix_system_settings_key'), 'system_settings', ['key'], unique=True)
    op.create_index(op.f('ix_system_settings_category'), 'system_settings', ['category'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_system_settings_category'), table_name='system_settings')
    op.drop_index(op.f('ix_system_settings_key'), table_name='system_settings')
    op.drop_index(op.f('ix_system_settings_id'), table_name='system_settings')
    op.drop_table('system_settings')
