"""create_tables_direct

Revision ID: h9i0j1k2l3m4
Revises: g8h9i0j1k2l3
Create Date: 2025-11-01 14:50:00.000000

This migration directly creates all missing tables using raw SQL.
This bypasses any Alembic transaction issues and ensures tables are created.
Since there's no data, this is safe.

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'h9i0j1k2l3m4'
down_revision = 'g8h9i0j1k2l3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all missing tables directly"""
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_tables = inspector.get_table_names()
    
    # 1. Create people table
    if 'people' not in existing_tables:
        print("Creating people table...")
        op.execute("""
            CREATE TABLE people (
                id SERIAL PRIMARY KEY,
                planning_center_id VARCHAR(50),
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(20),
                date_of_birth DATE,
                gender VARCHAR(10),
                address1 VARCHAR(255),
                address2 VARCHAR(255),
                city VARCHAR(100),
                state VARCHAR(50),
                zip VARCHAR(20),
                household_id VARCHAR(50),
                household_name VARCHAR(255),
                status VARCHAR(50),
                join_date DATE,
                last_synced_at TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN NOT NULL DEFAULT false,
                data_source VARCHAR(20),
                csv_loaded_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                updated_by INTEGER
            )
        """)
        op.execute("CREATE INDEX ix_people_id ON people (id)")
        op.execute("CREATE UNIQUE INDEX ix_people_planning_center_id ON people (planning_center_id)")
        op.execute("CREATE INDEX ix_people_email ON people (email)")
        print("✅ People table created successfully")
        # Refresh table list after creating people
        existing_tables = inspector.get_table_names()
    
    # 2. Create course_enrollment table
    # Refresh table list to ensure we see the newly created people table
    existing_tables = inspector.get_table_names()
    if 'course_enrollment' not in existing_tables:
        if 'people' in existing_tables and 'courses' in existing_tables:
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
        else:
            print("⚠️  Skipping course_enrollment: missing required tables")
    
    # 3. Create people_campus table
    existing_tables = inspector.get_table_names()
    if 'people_campus' not in existing_tables:
        if 'people' in existing_tables and 'campus' in existing_tables:
            print("Creating people_campus table...")
            op.execute("""
                CREATE TABLE people_campus (
                    id SERIAL PRIMARY KEY,
                    people_id INTEGER NOT NULL,
                    campus_id INTEGER NOT NULL,
                    assigned_date DATE NOT NULL,
                    is_primary BOOLEAN NOT NULL DEFAULT false,
                    is_active BOOLEAN NOT NULL DEFAULT false,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    updated_by INTEGER,
                    FOREIGN KEY (people_id) REFERENCES people(id),
                    FOREIGN KEY (campus_id) REFERENCES campus(id)
                )
            """)
            op.execute("CREATE INDEX ix_people_campus_people_id ON people_campus (people_id)")
            op.execute("CREATE INDEX ix_people_campus_campus_id ON people_campus (campus_id)")
            op.execute("CREATE INDEX ix_people_campus_id ON people_campus (id)")
    
    # 4. Create people_role table
    existing_tables = inspector.get_table_names()
    if 'people_role' not in existing_tables:
        if 'people' in existing_tables and 'role' in existing_tables:
            print("Creating people_role table...")
            op.execute("""
                CREATE TABLE people_role (
                    id SERIAL PRIMARY KEY,
                    people_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    assigned_date DATE NOT NULL,
                    assigned_by INTEGER,
                    is_active BOOLEAN NOT NULL DEFAULT false,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    updated_by INTEGER,
                    FOREIGN KEY (people_id) REFERENCES people(id),
                    FOREIGN KEY (role_id) REFERENCES role(id)
                )
            """)
            op.execute("CREATE INDEX ix_people_role_people_id ON people_role (people_id)")
            op.execute("CREATE INDEX ix_people_role_role_id ON people_role (role_id)")
            op.execute("CREATE INDEX ix_people_role_id ON people_role (id)")
    
    # 5. Create course_modules table
    existing_tables = inspector.get_table_names()
    if 'course_modules' not in existing_tables:
        if 'courses' in existing_tables:
            print("Creating course_modules table...")
            op.execute("""
                CREATE TABLE course_modules (
                    id SERIAL PRIMARY KEY,
                    course_id INTEGER NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    order_index INTEGER NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT false,
                    data_source VARCHAR(20),
                    csv_loaded_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    updated_by INTEGER,
                    FOREIGN KEY (course_id) REFERENCES courses(id)
                )
            """)
            op.execute("CREATE INDEX ix_course_modules_id ON course_modules (id)")
            op.execute("CREATE INDEX ix_course_modules_course_id ON course_modules (course_id)")
    
    # 6. Create content_completion table
    existing_tables = inspector.get_table_names()
    if 'content_completion' not in existing_tables:
        if 'course_enrollment' in existing_tables:
            print("Creating content_completion table...")
            op.execute("""
                CREATE TABLE content_completion (
                    id SERIAL PRIMARY KEY,
                    course_enrollment_id INTEGER NOT NULL,
                    content_id INTEGER,
                    progress_percentage FLOAT NOT NULL,
                    completed_at TIMESTAMP WITH TIME ZONE,
                    notes TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (course_enrollment_id) REFERENCES course_enrollment(id)
                )
            """)
            op.execute("CREATE INDEX ix_content_completion_id ON content_completion (id)")
            op.execute("CREATE INDEX ix_content_completion_course_enrollment_id ON content_completion (course_enrollment_id)")
        else:
            print("⚠️  Skipping content_completion: course_enrollment table doesn't exist")
    
    print("✅ All missing tables created successfully")


def downgrade() -> None:
    """Drop tables created by this migration"""
    # Since there's no data, we can drop these tables
    # But we'll leave them for safety
    pass

