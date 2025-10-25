#!/usr/bin/env python3
"""
Script to fix database migrations for Church Course Tracker
"""
import os
import psycopg2
import sys
from urllib.parse import urlparse

def get_database_connection():
    """Get database connection from environment or direct connection"""
    # Try to get from environment first
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        # Fallback to direct connection
        database_url = "postgresql://church_course_tracker:qicBHo2ypeSkuyrU@church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com:5432/church_course_tracker"
    
    # Parse the URL
    parsed = urlparse(database_url)
    
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path[1:],  # Remove leading slash
        user=parsed.username,
        password=parsed.password
    )
    return conn

def reset_alembic_version_table(conn):
    """Reset the alembic_version table to fix migration conflicts"""
    cursor = conn.cursor()
    
    try:
        print("🔧 Resetting alembic_version table...")
        cursor.execute("DROP TABLE IF EXISTS alembic_version CASCADE;")
        conn.commit()
        print("✅ alembic_version table dropped")
    except Exception as e:
        print(f"❌ Error resetting alembic_version: {e}")
        conn.rollback()
    finally:
        cursor.close()

def create_basic_tables(conn):
    """Create basic tables that the application needs"""
    cursor = conn.cursor()
    
    try:
        print("🔧 Creating basic tables...")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) UNIQUE,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                role VARCHAR(50) DEFAULT 'viewer',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create courses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                status VARCHAR(50) DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create enrollments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                course_id INTEGER REFERENCES courses(id),
                status VARCHAR(50) DEFAULT 'active',
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id)
            );
        """)
        
        # Create alembic_version table with initial migration
        cursor.execute("""
            CREATE TABLE alembic_version (
                version_num VARCHAR(32) NOT NULL,
                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
            );
        """)
        
        # Insert initial version
        cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('001_initial_migration');")
        
        conn.commit()
        print("✅ Basic tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
    finally:
        cursor.close()

def create_admin_user(conn):
    """Create the default admin user"""
    cursor = conn.cursor()
    
    try:
        print("👤 Creating admin user...")
        
        # Check if admin user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", ('course.tracker.admin@eastgate.church',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("✅ Admin user already exists")
            return
        
        # Create admin user (password: Matthew778*)
        cursor.execute("""
            INSERT INTO users (email, username, hashed_password, full_name, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            'course.tracker.admin@eastgate.church',
            'admin',
            '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBbL8pLzrV7E8K',  # Matthew778*
            'Admin',
            'admin',
            True
        ))
        
        conn.commit()
        print("✅ Admin user created successfully")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        conn.rollback()
    finally:
        cursor.close()

def main():
    """Main function to fix the database"""
    print("🚀 Starting database fix...")
    
    try:
        # Connect to database
        conn = get_database_connection()
        print("✅ Connected to database")
        
        # Reset alembic version table
        reset_alembic_version_table(conn)
        
        # Create basic tables
        create_basic_tables(conn)
        
        # Create admin user
        create_admin_user(conn)
        
        print("🎉 Database fix completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
