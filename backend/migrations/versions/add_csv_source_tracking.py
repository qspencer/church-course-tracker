"""Add CSV source tracking fields

Revision ID: add_csv_source_tracking
Revises: 
Create Date: 2024-09-29 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_csv_source_tracking'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add source tracking fields to all relevant tables"""
    
    # Add source tracking to courses
    op.add_column('courses', sa.Column('data_source', sa.String(20), nullable=True))
    op.add_column('courses', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add source tracking to users
    op.add_column('users', sa.Column('data_source', sa.String(20), nullable=True))
    op.add_column('users', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add source tracking to people
    op.add_column('people', sa.Column('data_source', sa.String(20), nullable=True))
    op.add_column('people', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add source tracking to campuses
    op.add_column('campus', sa.Column('data_source', sa.String(20), nullable=True))
    op.add_column('campus', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add source tracking to roles
    op.add_column('role', sa.Column('data_source', sa.String(20), nullable=True))
    op.add_column('role', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add source tracking to course modules
    op.add_column('course_modules', sa.Column('data_source', sa.String(20), nullable=True))
    op.add_column('course_modules', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add source tracking to course content
    op.add_column('course_content', sa.Column('data_source', sa.String(20), nullable=True))
    op.add_column('course_content', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add source tracking to course enrollments
    op.add_column('course_enrollments', sa.Column('data_source', sa.String(20), nullable=True))
    op.add_column('course_enrollments', sa.Column('csv_loaded_at', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    """Remove source tracking fields"""
    
    # Remove source tracking from courses
    op.drop_column('courses', 'csv_loaded_at')
    op.drop_column('courses', 'data_source')
    
    # Remove source tracking from users
    op.drop_column('users', 'csv_loaded_at')
    op.drop_column('users', 'data_source')
    
    # Remove source tracking from people
    op.drop_column('people', 'csv_loaded_at')
    op.drop_column('people', 'data_source')
    
    # Remove source tracking from campuses
    op.drop_column('campus', 'csv_loaded_at')
    op.drop_column('campus', 'data_source')
    
    # Remove source tracking from roles
    op.drop_column('role', 'csv_loaded_at')
    op.drop_column('role', 'data_source')
    
    # Remove source tracking from course modules
    op.drop_column('course_modules', 'csv_loaded_at')
    op.drop_column('course_modules', 'data_source')
    
    # Remove source tracking from course content
    op.drop_column('course_content', 'csv_loaded_at')
    op.drop_column('course_content', 'data_source')
    
    # Remove source tracking from course enrollments
    op.drop_column('course_enrollments', 'csv_loaded_at')
    op.drop_column('course_enrollments', 'data_source')
