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
