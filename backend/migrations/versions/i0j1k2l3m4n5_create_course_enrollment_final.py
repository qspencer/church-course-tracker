"""create_course_enrollment_final

Revision ID: i0j1k2l3m4n5
Revises: h9i0j1k2l3m4
Create Date: 2025-11-01 14:55:00.000000

Create course_enrollment table - this migration runs after people and courses are confirmed to exist.

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'i0j1k2l3m4n5'
down_revision = 'h9i0j1k2l3m4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create course_enrollment table"""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()
    
    if 'course_enrollment' not in existing_tables:
        # Verify dependencies exist
        if 'people' not in existing_tables:
            raise Exception("Cannot create course_enrollment: 'people' table does not exist")
        if 'courses' not in existing_tables:
            raise Exception("Cannot create course_enrollment: 'courses' table does not exist")
        
        print("Creating course_enrollment table...")
        op.execute("""
            CREATE TABLE course_enrollment (
                id SERIAL PRIMARY KEY,
                people_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                planning_center_registration_id VARCHAR(50),
                enrollment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) NOT NULL,
                progress_percentage FLOAT NOT NULL,
                completion_date TIMESTAMP WITH TIME ZONE,
                notes TEXT,
                dependency_override BOOLEAN NOT NULL DEFAULT false,
                dependency_override_by INTEGER,
                planning_center_synced BOOLEAN NOT NULL DEFAULT false,
                registration_status VARCHAR(20),
                registration_notes TEXT,
                data_source VARCHAR(20),
                csv_loaded_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                updated_by INTEGER,
                FOREIGN KEY (people_id) REFERENCES people(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)
        op.execute("CREATE INDEX ix_course_enrollment_course_id ON course_enrollment (course_id)")
        op.execute("CREATE INDEX ix_course_enrollment_id ON course_enrollment (id)")
        op.execute("CREATE INDEX ix_course_enrollment_people_id ON course_enrollment (people_id)")
        op.execute("CREATE UNIQUE INDEX ix_course_enrollment_planning_center_registration_id ON course_enrollment (planning_center_registration_id)")
        print("✅ course_enrollment table created successfully")
    else:
        print("course_enrollment table already exists, skipping")


def downgrade() -> None:
    """Drop course_enrollment table"""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()
    
    if 'course_enrollment' in existing_tables:
        op.execute("DROP TABLE IF EXISTS course_enrollment CASCADE")

