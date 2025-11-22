"""make content_audit_logs.content_id nullable

Revision ID: u1v2w3x4y5z6
Revises: o6p7q8r9s0t1
Create Date: 2025-11-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'u1v2w3x4y5z6'
down_revision = 'o6p7q8r9s0t1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make content_id nullable in content_audit_logs
    with op.batch_alter_table('content_audit_logs') as batch_op:
        batch_op.alter_column('content_id',
               existing_type=sa.Integer(),
               nullable=True)


def downgrade() -> None:
    # Make content_id not nullable in content_audit_logs
    with op.batch_alter_table('content_audit_logs') as batch_op:
        batch_op.alter_column('content_id',
               existing_type=sa.Integer(),
               nullable=False)

