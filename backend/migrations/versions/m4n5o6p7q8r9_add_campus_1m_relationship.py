"""Add Campus 1:M relationship and historical tracking

Revision ID: m4n5o6p7q8r9
Revises: l3m4n5o6p7q8
Create Date: 2025-01-15 10:00:00.000000

This migration:
1. Adds campus_id directly to people table (1:M relationship)
2. Adds campus_assigned_date to people table
3. Adds unassigned_date to people_campus table for historical tracking
4. Migrates existing active campus assignments to people.campus_id
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite
from datetime import date

# revision identifiers, used by Alembic.
revision = 'm4n5o6p7q8r9'
down_revision = 'l3m4n5o6p7q8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Add campus_id and campus_assigned_date to people table
    with op.batch_alter_table('people') as batch_op:
        batch_op.add_column(sa.Column('campus_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('campus_assigned_date', sa.Date(), nullable=True))
        batch_op.create_foreign_key(
            'fk_people_campus_id',
            'campus',
            ['campus_id'],
            ['id'],
            ondelete='SET NULL'
        )
        batch_op.create_index('ix_people_campus_assignment', ['campus_id'], unique=False)
    
    # Step 2: Add unassigned_date to people_campus table for historical tracking
    with op.batch_alter_table('people_campus') as batch_op:
        batch_op.add_column(sa.Column('unassigned_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))
    
    # Step 3: Migrate existing active campus assignments to people.campus_id
    # This will set the current active campus (is_primary=True or first active) to people.campus_id
    connection = op.get_bind()
    
    # Update people with their current active campus assignment
    # Priority: is_primary=True, then first active assignment
    # SQLite uses 1/0 for boolean, but we need to handle it properly
    connection.execute(sa.text("""
        UPDATE people
        SET campus_id = (
            SELECT pc.campus_id
            FROM people_campus pc
            WHERE pc.people_id = people.id
                AND pc.is_active = 1
            ORDER BY pc.is_primary DESC, pc.assigned_date DESC
            LIMIT 1
        ),
        campus_assigned_date = (
            SELECT pc.assigned_date
            FROM people_campus pc
            WHERE pc.people_id = people.id
                AND pc.is_active = 1
                AND pc.campus_id = (
                    SELECT pc2.campus_id
                    FROM people_campus pc2
                    WHERE pc2.people_id = people.id
                        AND pc2.is_active = 1
                    ORDER BY pc2.is_primary DESC, pc2.assigned_date DESC
                    LIMIT 1
                )
            ORDER BY pc.is_primary DESC, pc.assigned_date DESC
            LIMIT 1
        )
        WHERE EXISTS (
            SELECT 1
            FROM people_campus pc
            WHERE pc.people_id = people.id
                AND pc.is_active = 1
        )
    """))


def downgrade() -> None:
    # Remove campus_id and campus_assigned_date from people table
    with op.batch_alter_table('people') as batch_op:
        batch_op.drop_index('ix_people_campus_assignment')
        batch_op.drop_constraint('fk_people_campus_id', type_='foreignkey')
        batch_op.drop_column('campus_assigned_date')
        batch_op.drop_column('campus_id')
    
    # Remove unassigned_date from people_campus table
    with op.batch_alter_table('people_campus') as batch_op:
        batch_op.drop_column('notes')
        batch_op.drop_column('unassigned_date')

