"""add_data_source_columns

Revision ID: 69026e93dba9
Revises: 5fabddda5acb
Create Date: 2025-10-25 15:19:59.186835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69026e93dba9'
down_revision = '5fabddda5acb'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add data_source column to users table
    op.add_column('users', sa.Column('data_source', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add data_source column to role table
    op.add_column('role', sa.Column('data_source', sa.String(length=20), nullable=True))
    op.add_column('role', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add data_source column to campus table
    op.add_column('campus', sa.Column('data_source', sa.String(length=20), nullable=True))
    op.add_column('campus', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add data_source column to people table (members)
    op.add_column('people', sa.Column('data_source', sa.String(length=20), nullable=True))
    op.add_column('people', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add data_source column to courses table
    op.add_column('courses', sa.Column('data_source', sa.String(length=20), nullable=True))
    op.add_column('courses', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add data_source column to course_modules table
    op.add_column('course_modules', sa.Column('data_source', sa.String(length=20), nullable=True))
    op.add_column('course_modules', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add data_source column to course_content table
    op.add_column('course_content', sa.Column('data_source', sa.String(length=20), nullable=True))
    op.add_column('course_content', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add data_source column to course_enrollment table
    op.add_column('course_enrollment', sa.Column('data_source', sa.String(length=20), nullable=True))
    op.add_column('course_enrollment', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove data_source columns in reverse order
    op.drop_column('course_enrollment', 'csv_loaded_at')
    op.drop_column('course_enrollment', 'data_source')
    op.drop_column('course_content', 'csv_loaded_at')
    op.drop_column('course_content', 'data_source')
    op.drop_column('course_modules', 'csv_loaded_at')
    op.drop_column('course_modules', 'data_source')
    op.drop_column('courses', 'csv_loaded_at')
    op.drop_column('courses', 'data_source')
    op.drop_column('people', 'csv_loaded_at')
    op.drop_column('people', 'data_source')
    op.drop_column('campus', 'csv_loaded_at')
    op.drop_column('campus', 'data_source')
    op.drop_column('role', 'csv_loaded_at')
    op.drop_column('role', 'data_source')
    op.drop_column('users', 'csv_loaded_at')
    op.drop_column('users', 'data_source')
