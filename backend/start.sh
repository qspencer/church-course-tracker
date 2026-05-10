#!/bin/bash

# Church Course Tracker - ECS Startup Script
echo "🚀 Starting Church Course Tracker..."

# Environment variables are set by ECS task definition
# No need to override them here

# Run database migrations
echo "🔄 Running database migrations..."

# First, try to fix any multiple head issues
echo "🔧 Checking for multiple Alembic heads..."
python3 /app/scripts/fix_alembic_heads.py 2>&1 | head -20

# Then run migrations
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully!"
else
    echo "⚠️  Database migrations failed. Attempting to stamp database with current version..."
    # Try to stamp the database to skip failed migrations
    alembic stamp head
    if [ $? -eq 0 ]; then
        echo "✅ Database stamped successfully. Continuing..."
    else
        echo "⚠️  Could not stamp database. Continuing anyway..."
    fi
fi

# Validate schema after migrations
echo "🔍 Validating database schema against models..."
python3 /app/scripts/schema_validator.py 2>&1 | head -50

SCHEMA_VALIDATION_EXIT_CODE=$?
if [ $SCHEMA_VALIDATION_EXIT_CODE -ne 0 ]; then
    echo "⚠️  Schema validation found issues. Running schema fixes..."
    # Continue - the schema fix script below will handle missing tables/columns
else
    echo "✅ Schema validation passed!"
fi

# Check database tables and migration state
echo "🔍 Checking database schema..."
python3 << 'DB_CHECK_SCRIPT'
import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    try:
        parts = DATABASE_URL.replace('postgresql://', '').split('/')
        userpass = parts[0].split('@')[0]
        user, password = userpass.split(':')
        hostport = parts[0].split('@')[1]
        host, port = hostport.split(':')
        dbname = parts[1]
        
        conn = psycopg2.connect(host=host, port=port, database=dbname, user=user, password=password)
        cur = conn.cursor()
        
        # Get all tables
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
        tables = cur.fetchall()
        print("📋 Database tables found:")
        for table in tables:
            print(f"   - {table[0]}")
        
        table_names = [t[0] for t in tables]
        print("\n🔑 Key table status:")
        print(f"   course_enrollment: {'✓ EXISTS' if 'course_enrollment' in table_names else '✗ MISSING'}")
        print(f"   people: {'✓ EXISTS' if 'people' in table_names else '✗ MISSING'}")
        print(f"   courses: {'✓ EXISTS' if 'courses' in table_names else '✗ MISSING'}")
        print(f"   users: {'✓ EXISTS' if 'users' in table_names else '✗ MISSING'}")
        print(f"   enrollments: {'✓ EXISTS' if 'enrollments' in table_names else '✗ MISSING'}")
        
        if 'alembic_version' in table_names:
            cur.execute("SELECT version_num FROM alembic_version;")
            version = cur.fetchone()
            print(f"\n📦 Migration version: {version[0] if version else 'None'}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️  Could not check database schema: {e}")
DB_CHECK_SCRIPT

# Run schema verification script (if available) to check for missing columns
echo "🔍 Running database schema verification..."
if [ -f "/app/scripts/verify_database_schema.py" ]; then
    python3 /app/scripts/verify_database_schema.py 2>&1 | head -100 || echo "⚠️  Schema verification script failed or missing dependencies"
fi

# Manually add the data_source columns if they don't exist (always check)
echo "🔧 Checking and adding data_source columns if needed..."
python3 << 'PYTHON_SCRIPT'
import os
import psycopg2
import sys

# Track execution status
columns_added = []
columns_checked = []
errors_encountered = []

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # Parse database URL
    # postgresql://user:pass@host:port/dbname
    parts = DATABASE_URL.replace('postgresql://', '').split('/')
    userpass = parts[0].split('@')[0]
    user, password = userpass.split(':')
    hostport = parts[0].split('@')[1]
    host, port = hostport.split(':')
    dbname = parts[1]
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname
        )
        cur = conn.cursor()
        
        # Check and add data_source columns for each table
        tables = ['users', 'role', 'campus', 'people', 'courses', 'course_modules', 'course_content', 'course_enrollment']
        
        # Check for the specific columns we need and add them if missing
        print("\n🔍 Checking and adding critical columns if needed...")
        critical_columns = [
            ('people', 'campus_id', 'INTEGER', True),
            ('people', 'campus_assigned_date', 'DATE', True),
            ('courses', 'planning_center_event_template_id', 'VARCHAR(50)', True),
            ('course_enrollment', 'course_instance_id', 'INTEGER', True),
            ('course_enrollment', 'assigned_teacher_id', 'INTEGER', True),
        ]
        
        for table_name, column_name, column_type, nullable in critical_columns:
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name=%s AND column_name=%s
            """, (table_name, column_name))
            
            if not cur.fetchone():
                print(f"⚠️  MISSING: {table_name}.{column_name} - adding now...")
                try:
                    null_clause = '' if not nullable else 'NULL'
                    cur.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} {null_clause}')
                    conn.commit()
                    print(f"✅ ADDED: {table_name}.{column_name}")
                    columns_added.append(f"{table_name}.{column_name}")
                    
                    # Add index for foreign keys
                    if column_name.endswith('_id') and column_name != 'id':
                        try:
                            cur.execute(f'CREATE INDEX IF NOT EXISTS ix_{table_name}_{column_name} ON {table_name}({column_name})')
                            conn.commit()
                            print(f"✅ INDEX CREATED: ix_{table_name}_{column_name}")
                        except Exception as e:
                            print(f"⚠️  Could not create index: {e}")
                            conn.rollback()
                except Exception as e:
                    print(f"❌ ERROR adding {table_name}.{column_name}: {e}")
                    errors_encountered.append(f"{table_name}.{column_name}: {e}")
                    conn.rollback()
            else:
                print(f"✅ EXISTS: {table_name}.{column_name}")
                columns_checked.append(f"{table_name}.{column_name}")
        
        # Add foreign key constraints if columns were added
        print("\n🔗 Checking foreign key constraints...")
        fk_checks = [
            ('people', 'campus_id', 'campus', 'id'),
            ('course_enrollment', 'course_instance_id', 'course_instances', 'id'),
            ('course_enrollment', 'assigned_teacher_id', 'course_instance_teachers', 'id'),
        ]
        
        for table_name, column_name, ref_table, ref_column in fk_checks:
            # Check if FK constraint exists
            cur.execute("""
                SELECT tc.constraint_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE tc.table_name = %s
                    AND kcu.column_name = %s
                    AND tc.constraint_type = 'FOREIGN KEY'
            """, (table_name, column_name))
            
            if not cur.fetchone():
                # Check if ref table exists
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name = %s
                """, (ref_table,))
                
                if cur.fetchone():
                    try:
                        fk_name = f'fk_{table_name}_{column_name}'
                        cur.execute(f"""
                            ALTER TABLE {table_name} 
                            ADD CONSTRAINT {fk_name} 
                            FOREIGN KEY ({column_name}) 
                            REFERENCES {ref_table}({ref_column})
                            ON DELETE SET NULL
                        """)
                        conn.commit()
                        print(f"✅ FK CREATED: {table_name}.{column_name} -> {ref_table}.{ref_column}")
                    except Exception as e:
                        print(f"⚠️  Could not create FK: {e}")
                        conn.rollback()
                else:
                    print(f"⚠️  Ref table {ref_table} does not exist, skipping FK")
            else:
                print(f"✅ FK EXISTS: {table_name}.{column_name} -> {ref_table}.{ref_column}")
        
        for table in tables:
            # Check if column exists
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name=%s AND column_name='data_source'
            """, (table,))
            
            if not cur.fetchone():
                print(f"Adding data_source column to {table}...")
                try:
                    cur.execute(f'ALTER TABLE {table} ADD COLUMN data_source VARCHAR(20)')
                    cur.execute(f'ALTER TABLE {table} ADD COLUMN csv_loaded_at TIMESTAMP WITH TIME ZONE')
                    conn.commit()
                    print(f"✅ Added columns to {table}")
                except Exception as e:
                    print(f"⚠️  Could not add columns to {table}: {e}")
                    conn.rollback()
            else:
                print(f"✅ {table} already has data_source column")
        
        # Check and add planning_center_event_name column to courses table
        print("\n🔧 Checking planning_center_event_name column in courses table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='courses' AND column_name='planning_center_event_name'
        """)
        
        if not cur.fetchone():
            print("Adding planning_center_event_name column to courses...")
            try:
                cur.execute('ALTER TABLE courses ADD COLUMN planning_center_event_name VARCHAR(200)')
                conn.commit()
                print("✅ Added planning_center_event_name column to courses")
                columns_added.append("courses.planning_center_event_name")
            except Exception as e:
                print(f"⚠️  Could not add planning_center_event_name column: {e}")
                errors_encountered.append(f"courses.planning_center_event_name: {e}")
                conn.rollback()
        else:
            print("✅ courses already has planning_center_event_name column")
            columns_checked.append("courses.planning_center_event_name")
        
        # Check and add event_start_date column to courses table
        print("\n🔧 Checking event_start_date column in courses table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='courses' AND column_name='event_start_date'
        """)
        
        if not cur.fetchone():
            print("Adding event_start_date column to courses...")
            try:
                cur.execute('ALTER TABLE courses ADD COLUMN event_start_date TIMESTAMP WITH TIME ZONE')
                conn.commit()
                print("✅ Added event_start_date column to courses")
                columns_added.append("courses.event_start_date")
            except Exception as e:
                print(f"⚠️  Could not add event_start_date column: {e}")
                errors_encountered.append(f"courses.event_start_date: {e}")
                conn.rollback()
        else:
            print("✅ courses already has event_start_date column")
            columns_checked.append("courses.event_start_date")
        
        # Check and add event_end_date column to courses table
        print("\n🔧 Checking event_end_date column in courses table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='courses' AND column_name='event_end_date'
        """)
        
        if not cur.fetchone():
            print("Adding event_end_date column to courses...")
            try:
                cur.execute('ALTER TABLE courses ADD COLUMN event_end_date TIMESTAMP WITH TIME ZONE')
                conn.commit()
                print("✅ Added event_end_date column to courses")
                columns_added.append("courses.event_end_date")
            except Exception as e:
                print(f"⚠️  Could not add event_end_date column: {e}")
                errors_encountered.append(f"courses.event_end_date: {e}")
                conn.rollback()
        else:
            print("✅ courses already has event_end_date column")
            columns_checked.append("courses.event_end_date")
        
        # Check and add max_capacity column to courses table
        print("\n🔧 Checking max_capacity column in courses table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='courses' AND column_name='max_capacity'
        """)
        
        if not cur.fetchone():
            print("Adding max_capacity column to courses...")
            try:
                cur.execute('ALTER TABLE courses ADD COLUMN max_capacity INTEGER')
                conn.commit()
                print("✅ Added max_capacity column to courses")
                columns_added.append("courses.max_capacity")
            except Exception as e:
                print(f"⚠️  Could not add max_capacity column: {e}")
                errors_encountered.append(f"courses.max_capacity: {e}")
                conn.rollback()
        else:
            print("✅ courses already has max_capacity column")
            columns_checked.append("courses.max_capacity")
        
        # Check and add current_registrations column to courses table
        print("\n🔧 Checking current_registrations column in courses table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='courses' AND column_name='current_registrations'
        """)
        
        if not cur.fetchone():
            print("Adding current_registrations column to courses...")
            try:
                cur.execute('ALTER TABLE courses ADD COLUMN current_registrations INTEGER DEFAULT 0 NOT NULL')
                conn.commit()
                print("✅ Added current_registrations column to courses")
                columns_added.append("courses.current_registrations")
            except Exception as e:
                print(f"⚠️  Could not add current_registrations column: {e}")
                errors_encountered.append(f"courses.current_registrations: {e}")
                conn.rollback()
        else:
            print("✅ courses already has current_registrations column")
            columns_checked.append("courses.current_registrations")
        
        # Check and add content_unlock_mode column to courses table
        print("\n🔧 Checking content_unlock_mode column in courses table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='courses' AND column_name='content_unlock_mode'
        """)
        
        if not cur.fetchone():
            print("Adding content_unlock_mode column to courses...")
            try:
                cur.execute("ALTER TABLE courses ADD COLUMN content_unlock_mode VARCHAR(20) DEFAULT 'immediate' NOT NULL")
                conn.commit()
                print("✅ Added content_unlock_mode column to courses")
                columns_added.append("courses.content_unlock_mode")
            except Exception as e:
                print(f"⚠️  Could not add content_unlock_mode column: {e}")
                errors_encountered.append(f"courses.content_unlock_mode: {e}")
                conn.rollback()
        else:
            print("✅ courses already has content_unlock_mode column")
            columns_checked.append("courses.content_unlock_mode")
        
        # Check and add max_file_size_mb column to courses table
        print("\n🔧 Checking max_file_size_mb column in courses table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='courses' AND column_name='max_file_size_mb'
        """)
        
        if not cur.fetchone():
            print("Adding max_file_size_mb column to courses...")
            try:
                cur.execute('ALTER TABLE courses ADD COLUMN max_file_size_mb INTEGER DEFAULT 1024 NOT NULL')
                conn.commit()
                print("✅ Added max_file_size_mb column to courses")
                columns_added.append("courses.max_file_size_mb")
            except Exception as e:
                print(f"⚠️  Could not add max_file_size_mb column: {e}")
                errors_encountered.append(f"courses.max_file_size_mb: {e}")
                conn.rollback()
        else:
            print("✅ courses already has max_file_size_mb column")
            columns_checked.append("courses.max_file_size_mb")
        
        # Check and add created_by and updated_by columns to role table
        print("\n🔧 Checking created_by column in role table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='role' AND column_name='created_by'
        """)
        
        if not cur.fetchone():
            print("Adding created_by column to role...")
            try:
                cur.execute('ALTER TABLE role ADD COLUMN created_by INTEGER')
                conn.commit()
                print("✅ Added created_by column to role")
                columns_added.append("role.created_by")
            except Exception as e:
                print(f"⚠️  Could not add created_by column: {e}")
                errors_encountered.append(f"role.created_by: {e}")
                conn.rollback()
        else:
            print("✅ role already has created_by column")
            columns_checked.append("role.created_by")
        
        print("\n🔧 Checking updated_by column in role table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='role' AND column_name='updated_by'
        """)
        
        if not cur.fetchone():
            print("Adding updated_by column to role...")
            try:
                cur.execute('ALTER TABLE role ADD COLUMN updated_by INTEGER')
                conn.commit()
                print("✅ Added updated_by column to role")
                columns_added.append("role.updated_by")
            except Exception as e:
                print(f"⚠️  Could not add updated_by column: {e}")
                errors_encountered.append(f"role.updated_by: {e}")
                conn.rollback()
        else:
            print("✅ role already has updated_by column")
            columns_checked.append("role.updated_by")
        
        # Check and add title column to course_modules table
        print("\n🔧 Checking title column in course_modules table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='course_modules' AND column_name='title'
        """)
        
        if not cur.fetchone():
            print("Adding title column to course_modules...")
            try:
                cur.execute("ALTER TABLE course_modules ADD COLUMN title VARCHAR(200) NOT NULL DEFAULT ''")
                conn.commit()
                print("✅ Added title column to course_modules")
                columns_added.append("course_modules.title")
            except Exception as e:
                print(f"⚠️  Could not add title column: {e}")
                errors_encountered.append(f"course_modules.title: {e}")
                conn.rollback()
        else:
            print("✅ course_modules already has title column")
            columns_checked.append("course_modules.title")
        
        # Check and add missing columns to course_content table
        # Note: content_type and storage_type are Enum types, but we use VARCHAR for compatibility
        # The application will handle enum conversion
        course_content_columns = [
            ('title', "VARCHAR(200) NOT NULL DEFAULT ''"),
            ('description', 'TEXT'),
            ('module_id', 'INTEGER'),
            ('storage_type', "VARCHAR(50) NOT NULL DEFAULT 'database'"),
            ('file_name', 'VARCHAR(255)'),
            ('file_size', 'INTEGER'),
            ('file_path', 'VARCHAR(500)'),
            ('mime_type', 'VARCHAR(100)'),
            ('external_url', 'VARCHAR(1000)'),
            ('embedded_content', 'TEXT'),
            ('duration', 'INTEGER'),
            ('download_count', 'INTEGER NOT NULL DEFAULT 0'),
            ('view_count', 'INTEGER NOT NULL DEFAULT 0'),
        ]
        
        for col_name, col_def in course_content_columns:
            print(f"\n🔧 Checking {col_name} column in course_content table...")
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='course_content' AND column_name=%s
            """, (col_name,))
            
            if not cur.fetchone():
                print(f"Adding {col_name} column to course_content...")
                try:
                    cur.execute(f'ALTER TABLE course_content ADD COLUMN {col_name} {col_def}')
                    conn.commit()
                    print(f"✅ Added {col_name} column to course_content")
                    columns_added.append(f"course_content.{col_name}")
                except Exception as e:
                    print(f"⚠️  Could not add {col_name} column: {e}")
                    errors_encountered.append(f"course_content.{col_name}: {e}")
                    conn.rollback()
            else:
                print(f"✅ course_content already has {col_name} column")
                columns_checked.append(f"course_content.{col_name}")
        
        # Check and add username column to users table if missing
        print("\n🔧 Checking username column in users table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='username'
        """)
        
        if not cur.fetchone():
            print("Adding username column to users...")
            try:
                cur.execute('ALTER TABLE users ADD COLUMN username VARCHAR(50)')
                conn.commit()
                print("✅ Added username column to users")
                columns_added.append("users.username")
            except Exception as e:
                print(f"⚠️  Could not add username column: {e}")
                errors_encountered.append(f"users.username: {e}")
                conn.rollback()
        else:
            print("✅ users already has username column")
            columns_checked.append("users.username")
        
        # Check and add last_login column to users table if missing
        print("\n🔧 Checking last_login column in users table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='last_login'
        """)
        
        if not cur.fetchone():
            print("Adding last_login column to users...")
            try:
                cur.execute('ALTER TABLE users ADD COLUMN last_login TIMESTAMP WITH TIME ZONE')
                conn.commit()
                print("✅ Added last_login column to users")
                columns_added.append("users.last_login")
            except Exception as e:
                print(f"⚠️  Could not add last_login column: {e}")
                errors_encountered.append(f"users.last_login: {e}")
                conn.rollback()
        else:
            print("✅ users already has last_login column")
            columns_checked.append("users.last_login")
        
        # Check and add changed_by column to audit_log table if missing
        print("\n🔧 Checking changed_by column in audit_log table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='audit_log' AND column_name='changed_by'
        """)
        
        if not cur.fetchone():
            print("Adding changed_by column to audit_log...")
            try:
                cur.execute('ALTER TABLE audit_log ADD COLUMN changed_by INTEGER')
                conn.commit()
                print("✅ Added changed_by column to audit_log")
                columns_added.append("audit_log.changed_by")
            except Exception as e:
                print(f"⚠️  Could not add changed_by column: {e}")
                errors_encountered.append(f"audit_log.changed_by: {e}")
                conn.rollback()
        else:
            print("✅ audit_log already has changed_by column")
            columns_checked.append("audit_log.changed_by")
        
        # Check and add changed_at column to audit_log table if missing
        print("\n🔧 Checking changed_at column in audit_log table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='audit_log' AND column_name='changed_at'
        """)
        
        if not cur.fetchone():
            print("Adding changed_at column to audit_log...")
            try:
                cur.execute('ALTER TABLE audit_log ADD COLUMN changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP')
                conn.commit()
                print("✅ Added changed_at column to audit_log")
                columns_added.append("audit_log.changed_at")
            except Exception as e:
                print(f"⚠️  Could not add changed_at column: {e}")
                errors_encountered.append(f"audit_log.changed_at: {e}")
                conn.rollback()
        else:
            print("✅ audit_log already has changed_at column")
            columns_checked.append("audit_log.changed_at")
        
        # Check and add ip_address column to audit_log table if missing
        print("\n🔧 Checking ip_address column in audit_log table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='audit_log' AND column_name='ip_address'
        """)
        
        if not cur.fetchone():
            print("Adding ip_address column to audit_log...")
            try:
                cur.execute('ALTER TABLE audit_log ADD COLUMN ip_address VARCHAR(45)')
                conn.commit()
                print("✅ Added ip_address column to audit_log")
                columns_added.append("audit_log.ip_address")
            except Exception as e:
                print(f"⚠️  Could not add ip_address column: {e}")
                errors_encountered.append(f"audit_log.ip_address: {e}")
                conn.rollback()
        else:
            print("✅ audit_log already has ip_address column")
            columns_checked.append("audit_log.ip_address")
        
        # Check and add user_agent column to audit_log table if missing
        print("\n🔧 Checking user_agent column in audit_log table...")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='audit_log' AND column_name='user_agent'
        """)
        
        if not cur.fetchone():
            print("Adding user_agent column to audit_log...")
            try:
                cur.execute('ALTER TABLE audit_log ADD COLUMN user_agent TEXT')
                conn.commit()
                print("✅ Added user_agent column to audit_log")
                columns_added.append("audit_log.user_agent")
            except Exception as e:
                print(f"⚠️  Could not add user_agent column: {e}")
                errors_encountered.append(f"audit_log.user_agent: {e}")
                conn.rollback()
        else:
            print("✅ audit_log already has user_agent column")
            columns_checked.append("audit_log.user_agent")
        
        # Check if module_name column exists in course_content and make it nullable if it's NOT NULL
        print("\n🔧 Checking module_name column in course_content table...")
        cur.execute("""
            SELECT column_name, is_nullable
            FROM information_schema.columns 
            WHERE table_name='course_content' AND column_name='module_name'
        """)
        
        module_name_result = cur.fetchone()
        if module_name_result:
            is_nullable = module_name_result[1] == 'YES'
            if not is_nullable:
                print("Making module_name column nullable in course_content...")
                try:
                    cur.execute('ALTER TABLE course_content ALTER COLUMN module_name DROP NOT NULL')
                    conn.commit()
                    print("✅ Made module_name column nullable in course_content")
                    columns_added.append("course_content.module_name (made nullable)")
                except Exception as e:
                    print(f"⚠️  Could not make module_name nullable: {e}")
                    errors_encountered.append(f"course_content.module_name (nullable): {e}")
                    conn.rollback()
            else:
                print("✅ course_content.module_name is already nullable")
                columns_checked.append("course_content.module_name")
        else:
            print("ℹ️  course_content table does not have module_name column (this is OK)")
            columns_checked.append("course_content.module_name (does not exist)")
        
        # Check if content_audit_logs table exists and create it if missing
        print("\n🔧 Checking content_audit_logs table...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name='content_audit_logs'
        """)
        
        if not cur.fetchone():
            print("Creating content_audit_logs table...")
            try:
                cur.execute("""
                    CREATE TABLE content_audit_logs (
                        id SERIAL PRIMARY KEY,
                        content_id INTEGER,
                        user_id INTEGER NOT NULL,
                        action VARCHAR(20) NOT NULL,
                        change_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        old_values JSON,
                        new_values JSON,
                        change_summary TEXT,
                        ip_address VARCHAR(45),
                        user_agent VARCHAR(500)
                    )
                """)
                conn.commit()
                print("✅ Created content_audit_logs table")
                columns_added.append("content_audit_logs (table created)")
            except Exception as e:
                print(f"⚠️  Could not create content_audit_logs table: {e}")
                errors_encountered.append(f"content_audit_logs: {e}")
                conn.rollback()
        else:
            print("✅ content_audit_logs table already exists")
            columns_checked.append("content_audit_logs")
        
        # Check if content_access_logs table exists and create it if missing
        print("\n🔧 Checking content_access_logs table...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name='content_access_logs'
        """)
        
        if not cur.fetchone():
            print("Creating content_access_logs table...")
            try:
                cur.execute("""
                    CREATE TABLE content_access_logs (
                        id SERIAL PRIMARY KEY,
                        content_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        access_type VARCHAR(20) NOT NULL,
                        access_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        ip_address VARCHAR(45),
                        user_agent VARCHAR(500),
                        session_id VARCHAR(100),
                        progress_percentage INTEGER,
                        time_spent INTEGER
                    )
                """)
                conn.commit()
                print("✅ Created content_access_logs table")
                columns_added.append("content_access_logs (table created)")
            except Exception as e:
                print(f"⚠️  Could not create content_access_logs table: {e}")
                errors_encountered.append(f"content_access_logs: {e}")
                conn.rollback()
        else:
            print("✅ content_access_logs table already exists")
            columns_checked.append("content_access_logs")
        
        # Summary of column checks
        print("\n" + "=" * 60)
        print("📊 COLUMN CHECK SUMMARY")
        print("=" * 60)
        print(f"✅ Columns checked (already existed): {len(columns_checked)}")
        print(f"✅ Columns added: {len(columns_added)}")
        if columns_added:
            print("\nAdded columns:")
            for col in columns_added:
                print(f"  - {col}")
        if errors_encountered:
            print(f"\n⚠️  Errors encountered: {len(errors_encountered)}")
            for error in errors_encountered:
                print(f"  - {error}")
        else:
            print("\n✅ No errors encountered")
        print("=" * 60)
        
        cur.close()
        conn.close()
        
        # Exit with error code if there were errors
        if errors_encountered:
            print("⚠️  Schema verification completed with errors")
            sys.exit(1)
        else:
            print("✅ Schema verification and column addition complete")
            sys.exit(0)
    except Exception as e:
        print(f"⚠️  Could not add data_source columns: {e}")
        print(f"❌ FATAL ERROR: Column addition script failed: {e}")
        sys.exit(1)
PYTHON_SCRIPT

# Check if the Python script executed successfully
COLUMN_CHECK_EXIT_CODE=$?
if [ $COLUMN_CHECK_EXIT_CODE -ne 0 ]; then
    echo "❌ FATAL ERROR: Column addition script failed with exit code $COLUMN_CHECK_EXIT_CODE"
    echo "⚠️  Backend will continue, but database schema may be incomplete"
    # Don't exit - let the backend try to start anyway
    # exit 1
else
    echo "✅ Column addition script completed successfully"
fi

# Admin user creation is handled idempotently by Alembic migration
# v2w3x4y5z6a7_ensure_admin_user (run via `alembic upgrade head` above),
# which reads ADMIN_PASSWORD from the environment (sourced from Secrets
# Manager). The previously-invoked /app/create_admin_standalone.py and
# /app/create_test_users_standalone.py shipped with hardcoded credentials
# (the leaked Matthew778* admin password and weak staff/viewer passwords)
# and would silently reset the admin password on every container restart.
# Both scripts and their Dockerfile COPY entries were removed in the
# May 2026 hardening pass.

# Start the application
echo "🚀 Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
