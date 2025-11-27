"""add_autocomplete_suggestions_table

Revision ID: ad32f739f15c
Revises: 34f567c52953
Create Date: 2024-11-27 17:18:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad32f739f15c'
down_revision = '34f567c52953'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('autocomplete_suggestions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('field_type', sa.String(length=50), nullable=False),
    sa.Column('value', sa.String(length=200), nullable=False),
    sa.Column('usage_count', sa.Integer(), nullable=False, server_default='1'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_autocomplete_suggestions_id'), 'autocomplete_suggestions', ['id'], unique=False)
    op.create_index(op.f('ix_autocomplete_suggestions_field_type'), 'autocomplete_suggestions', ['field_type'], unique=False)
    op.create_index(op.f('ix_autocomplete_suggestions_value'), 'autocomplete_suggestions', ['value'], unique=False)
    op.create_index('ix_autocomplete_suggestions_field_type_value', 'autocomplete_suggestions', ['field_type', 'value'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_autocomplete_suggestions_field_type_value', table_name='autocomplete_suggestions')
    op.drop_index(op.f('ix_autocomplete_suggestions_value'), table_name='autocomplete_suggestions')
    op.drop_index(op.f('ix_autocomplete_suggestions_field_type'), table_name='autocomplete_suggestions')
    op.drop_index(op.f('ix_autocomplete_suggestions_id'), table_name='autocomplete_suggestions')
    op.drop_table('autocomplete_suggestions')
