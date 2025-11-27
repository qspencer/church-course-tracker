"""add_custom_attributes_table

Revision ID: 34f567c52953
Revises: e97fd6214c06
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34f567c52953'
down_revision = 'e97fd6214c06'
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy import inspect
    
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # Create custom_attributes table
    if 'custom_attributes' not in existing_tables:
        op.create_table('custom_attributes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('attribute_name', sa.String(length=200), nullable=False),
        sa.Column('pc_attribute_name', sa.String(length=200), nullable=True),
        sa.Column('attribute_value', sa.Text(), nullable=True),
        sa.Column('attribute_type', sa.String(length=50), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='planning_center'),
        sa.Column('planning_center_source_id', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes for efficient lookups
        op.create_index(op.f('ix_custom_attributes_id'), 'custom_attributes', ['id'], unique=False)
        op.create_index(op.f('ix_custom_attributes_entity_type'), 'custom_attributes', ['entity_type'], unique=False)
        op.create_index(op.f('ix_custom_attributes_entity_id'), 'custom_attributes', ['entity_id'], unique=False)
        op.create_index(op.f('ix_custom_attributes_attribute_name'), 'custom_attributes', ['attribute_name'], unique=False)
        op.create_index(op.f('ix_custom_attributes_planning_center_source_id'), 'custom_attributes', ['planning_center_source_id'], unique=False)
        
        # Create composite index for entity lookups
        op.create_index('ix_custom_attributes_entity', 'custom_attributes', ['entity_type', 'entity_id'], unique=False)


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_custom_attributes_entity', table_name='custom_attributes')
    op.drop_index(op.f('ix_custom_attributes_planning_center_source_id'), table_name='custom_attributes')
    op.drop_index(op.f('ix_custom_attributes_attribute_name'), table_name='custom_attributes')
    op.drop_index(op.f('ix_custom_attributes_entity_id'), table_name='custom_attributes')
    op.drop_index(op.f('ix_custom_attributes_entity_type'), table_name='custom_attributes')
    op.drop_index(op.f('ix_custom_attributes_id'), table_name='custom_attributes')
    
    # Drop table
    op.drop_table('custom_attributes')

