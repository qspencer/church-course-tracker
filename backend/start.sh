#!/bin/bash

# Church Course Tracker - ECS Startup Script
echo "🚀 Starting Church Course Tracker..."

# Environment variables are set by ECS task definition
# No need to override them here

# Run database migrations
echo "🔄 Running database migrations..."
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
            except Exception as e:
                print(f"⚠️  Could not add planning_center_event_name column: {e}")
                conn.rollback()
       else:
           print("✅ courses already has planning_center_event_name column")
       
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
           except Exception as e:
               print(f"⚠️  Could not add event_start_date column: {e}")
               conn.rollback()
       else:
           print("✅ courses already has event_start_date column")
       
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
           except Exception as e:
               print(f"⚠️  Could not add event_end_date column: {e}")
               conn.rollback()
       else:
           print("✅ courses already has event_end_date column")
       
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
           except Exception as e:
               print(f"⚠️  Could not add max_capacity column: {e}")
               conn.rollback()
       else:
           print("✅ courses already has max_capacity column")
       
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
           except Exception as e:
               print(f"⚠️  Could not add current_registrations column: {e}")
               conn.rollback()
       else:
           print("✅ courses already has current_registrations column")
       
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
           except Exception as e:
               print(f"⚠️  Could not add content_unlock_mode column: {e}")
               conn.rollback()
       else:
           print("✅ courses already has content_unlock_mode column")
       
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
           except Exception as e:
               print(f"⚠️  Could not add max_file_size_mb column: {e}")
               conn.rollback()
       else:
           print("✅ courses already has max_file_size_mb column")
       
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
           except Exception as e:
               print(f"⚠️  Could not add created_by column: {e}")
               conn.rollback()
       else:
           print("✅ role already has created_by column")
       
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
           except Exception as e:
               print(f"⚠️  Could not add updated_by column: {e}")
               conn.rollback()
       else:
           print("✅ role already has updated_by column")
       
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
           except Exception as e:
               print(f"⚠️  Could not add title column: {e}")
               conn.rollback()
       else:
           print("✅ course_modules already has title column")
       
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
               except Exception as e:
                   print(f"⚠️  Could not add {col_name} column: {e}")
                   conn.rollback()
           else:
               print(f"✅ course_content already has {col_name} column")
        
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
            except Exception as e:
                print(f"⚠️  Could not add username column: {e}")
                conn.rollback()
        else:
            print("✅ users already has username column")
        
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
            except Exception as e:
                print(f"⚠️  Could not add last_login column: {e}")
                conn.rollback()
        else:
            print("✅ users already has last_login column")
        
        cur.close()
        conn.close()
        print("✅ Schema verification and column addition complete")
    except Exception as e:
        print(f"⚠️  Could not add data_source columns: {e}")
PYTHON_SCRIPT

# Create default admin user if it doesn't exist
echo "👤 Creating default admin user..."
python3 /app/create_admin_standalone.py

if [ $? -eq 0 ]; then
    echo "✅ Admin user setup completed!"
else
    echo "⚠️  Admin user setup failed - user may already exist. Continuing..."
fi

# Create test users (staff and viewer) for E2E testing
echo "👥 Creating test users for E2E testing..."
python3 /app/create_test_users_standalone.py

if [ $? -eq 0 ]; then
    echo "✅ Test users setup completed!"
else
    echo "⚠️  Test users setup failed - users may already exist. Continuing..."
fi

# Start the application
echo "🚀 Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
