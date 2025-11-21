"""Add Course Offerings (CourseInstance) architecture

Revision ID: n5o6p7q8r9s0
Revises: m4n5o6p7q8r9
Create Date: 2025-01-15 10:30:00.000000

This migration:
1. Creates course_instances table (Course Offerings)
2. Creates course_instance_teachers table
3. Updates course_enrollment to reference course_instance_id instead of course_id
4. Moves instance-specific fields from courses to course_instances
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'n5o6p7q8r9s0'
down_revision = 'm4n5o6p7q8r9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Create course_instances table (Course Offerings)
    op.create_table(
        'course_instances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('instance_name', sa.String(length=200), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('schedule', sa.JSON(), nullable=True),  # Optional: day, time, frequency
        sa.Column('max_capacity', sa.Integer(), nullable=True),
        sa.Column('current_enrollments', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('planning_center_event_id', sa.String(length=50), nullable=True),
        sa.Column('planning_center_event_name', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('enrollment_open', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('enrollment_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('campus_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['campus_id'], ['campus.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('planning_center_event_id')
    )
    op.create_index(op.f('ix_course_instances_id'), 'course_instances', ['id'], unique=False)
    op.create_index(op.f('ix_course_instances_course_id'), 'course_instances', ['course_id'], unique=False)
    op.create_index(op.f('ix_course_instances_planning_center_event_id'), 'course_instances', ['planning_center_event_id'], unique=True)
    op.create_index(op.f('ix_course_instances_start_date'), 'course_instances', ['start_date'], unique=False)
    
    # Step 2: Create course_instance_teachers table
    op.create_table(
        'course_instance_teachers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_instance_id', sa.Integer(), nullable=False),
        sa.Column('people_id', sa.Integer(), nullable=False),
        sa.Column('role_type', sa.String(length=50), nullable=False),  # 'teacher', 'mentor', 'assistant', 'co-teacher'
        sa.Column('assigned_date', sa.Date(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('max_students', sa.Integer(), nullable=True),  # For 1:1 discipleship tracking
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['course_instance_id'], ['course_instances.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['people_id'], ['people.id'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_course_instance_teachers_id'), 'course_instance_teachers', ['id'], unique=False)
    op.create_index(op.f('ix_course_instance_teachers_course_instance_id'), 'course_instance_teachers', ['course_instance_id'], unique=False)
    op.create_index(op.f('ix_course_instance_teachers_people_id'), 'course_instance_teachers', ['people_id'], unique=False)
    
    # Step 3: Add course_instance_id and assigned_teacher_id to course_enrollment
    op.add_column('course_enrollment', sa.Column('course_instance_id', sa.Integer(), nullable=True))
    op.add_column('course_enrollment', sa.Column('assigned_teacher_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_course_enrollment_course_instance_id',
        'course_enrollment',
        'course_instances',
        ['course_instance_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_course_enrollment_assigned_teacher_id',
        'course_enrollment',
        'course_instance_teachers',
        ['assigned_teacher_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_index(op.f('ix_course_enrollment_course_instance_id'), 'course_enrollment', ['course_instance_id'], unique=False)
    op.create_index(op.f('ix_course_enrollment_assigned_teacher_id'), 'course_enrollment', ['assigned_teacher_id'], unique=False)
    
    # Step 4: Create default course instances from existing courses and migrate enrollments
    # For each course with event_start_date, create a default instance
    connection = op.get_bind()
    
    # Create course instances from existing courses
    connection.execute(sa.text("""
        INSERT INTO course_instances (
            course_id, instance_name, start_date, end_date, max_capacity,
            current_enrollments, planning_center_event_id, planning_center_event_name,
            is_active, enrollment_open, created_at, updated_at
        )
        SELECT 
            id,
            COALESCE(planning_center_event_name, title) || ' - Initial Instance' as instance_name,
            event_start_date as start_date,
            event_end_date as end_date,
            max_capacity,
            current_registrations as current_enrollments,
            planning_center_event_id,
            planning_center_event_name,
            is_active,
            1 as enrollment_open,
            created_at,
            updated_at
        FROM courses
        WHERE event_start_date IS NOT NULL OR planning_center_event_id IS NOT NULL
    """))
    
    # Migrate existing enrollments to reference course instances
    # Link enrollments to the default instance for each course
    connection.execute(sa.text("""
        UPDATE course_enrollment
        SET course_instance_id = (
            SELECT ci.id
            FROM course_instances ci
            WHERE ci.course_id = course_enrollment.course_id
            ORDER BY ci.created_at ASC
            LIMIT 1
        )
        WHERE course_instance_id IS NULL
    """))
    
    # Step 5: Make course_instance_id NOT NULL after migration
    # But keep nullable for now in case there are courses without instances
    # We'll make it required in application logic


def downgrade() -> None:
    # Remove course_instance_id and assigned_teacher_id from course_enrollment
    op.drop_index(op.f('ix_course_enrollment_assigned_teacher_id'), table_name='course_enrollment')
    op.drop_index(op.f('ix_course_enrollment_course_instance_id'), table_name='course_enrollment')
    op.drop_constraint('fk_course_enrollment_assigned_teacher_id', 'course_enrollment', type_='foreignkey')
    op.drop_constraint('fk_course_enrollment_course_instance_id', 'course_enrollment', type_='foreignkey')
    op.drop_column('course_enrollment', 'assigned_teacher_id')
    op.drop_column('course_enrollment', 'course_instance_id')
    
    # Drop course_instance_teachers table
    op.drop_index(op.f('ix_course_instance_teachers_people_id'), table_name='course_instance_teachers')
    op.drop_index(op.f('ix_course_instance_teachers_course_instance_id'), table_name='course_instance_teachers')
    op.drop_index(op.f('ix_course_instance_teachers_id'), table_name='course_instance_teachers')
    op.drop_table('course_instance_teachers')
    
    # Drop course_instances table
    op.drop_index(op.f('ix_course_instances_start_date'), table_name='course_instances')
    op.drop_index(op.f('ix_course_instances_planning_center_event_id'), table_name='course_instances')
    op.drop_index(op.f('ix_course_instances_course_id'), table_name='course_instances')
    op.drop_index(op.f('ix_course_instances_id'), table_name='course_instances')
    op.drop_table('course_instances')

