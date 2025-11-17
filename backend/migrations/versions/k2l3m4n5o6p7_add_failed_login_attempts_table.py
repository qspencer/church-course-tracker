"""Add failed login attempts table

Revision ID: k2l3m4n5o6p7
Revises: j1k2l3m4n5o6
Create Date: 2025-11-15 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'k2l3m4n5o6p7'
down_revision = 'j1k2l3m4n5o6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create failed_login_attempts table
    op.create_table(
        'failed_login_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username_or_email', sa.String(length=255), nullable=False),
        sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_attempt_time', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_failed_login_attempts_id'), 'failed_login_attempts', ['id'], unique=False)
    op.create_index(op.f('ix_failed_login_attempts_username_or_email'), 'failed_login_attempts', ['username_or_email'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_failed_login_attempts_username_or_email'), table_name='failed_login_attempts')
    op.drop_index(op.f('ix_failed_login_attempts_id'), table_name='failed_login_attempts')
    op.drop_table('failed_login_attempts')

