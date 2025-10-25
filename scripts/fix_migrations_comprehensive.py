#!/usr/bin/env python3
"""
Comprehensive script to fix database migrations and application deployment
"""
import os
import sys
import psycopg2
from urllib.parse import urlparse
import json

def get_database_connection():
    """Get database connection"""
    database_url = "postgresql://church_course_tracker:qicBHo2ypeSkuyrU@church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com:5432/church_course_tracker"
    
    parsed = urlparse(database_url)
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path[1:],
        user=parsed.username,
        password=parsed.password
    )
    return conn

def reset_database_completely(conn):
    """Reset the database completely"""
    cursor = conn.cursor()
    
    try:
        print("🗑️ Resetting database completely...")
        
        # Drop all tables
        cursor.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """)
        
        conn.commit()
        print("✅ All tables dropped")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        conn.rollback()
    finally:
        cursor.close()

def create_clean_schema(conn):
    """Create a clean, working database schema"""
    cursor = conn.cursor()
    
    try:
        print("🏗️ Creating clean database schema...")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) UNIQUE,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                role VARCHAR(50) DEFAULT 'viewer',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );
        """)
        
        # Create campus table
        cursor.execute("""
            CREATE TABLE campus (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                address TEXT,
                phone VARCHAR(20),
                email VARCHAR(255),
                planning_center_location_id VARCHAR(50),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES users(id),
                updated_by INTEGER REFERENCES users(id)
            );
        """)
        
        # Create role table
        cursor.execute("""
            CREATE TABLE role (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                description TEXT,
                permissions JSON,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create members table
        cursor.execute("""
            CREATE TABLE members (
                id SERIAL PRIMARY KEY,
                planning_center_id VARCHAR(50) UNIQUE,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(20),
                address TEXT,
                campus_id INTEGER REFERENCES campus(id),
                role_id INTEGER REFERENCES role(id),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES users(id),
                updated_by INTEGER REFERENCES users(id)
            );
        """)
        
        # Create courses table
        cursor.execute("""
            CREATE TABLE courses (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                duration_weeks INTEGER,
                prerequisites JSON,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES users(id),
                updated_by INTEGER REFERENCES users(id)
            );
        """)
        
        # Create course_content table
        cursor.execute("""
            CREATE TABLE course_content (
                id SERIAL PRIMARY KEY,
                course_id INTEGER NOT NULL REFERENCES courses(id),
                module_name VARCHAR(200) NOT NULL,
                content_type VARCHAR(50) NOT NULL,
                content_data JSON,
                order_index INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES users(id),
                updated_by INTEGER REFERENCES users(id)
            );
        """)
        
        # Create enrollments table
        cursor.execute("""
            CREATE TABLE enrollments (
                id SERIAL PRIMARY KEY,
                member_id INTEGER NOT NULL REFERENCES members(id),
                course_id INTEGER NOT NULL REFERENCES courses(id),
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES users(id),
                updated_by INTEGER REFERENCES users(id),
                UNIQUE(member_id, course_id)
            );
        """)
        
        # Create progress table
        cursor.execute("""
            CREATE TABLE progress (
                id SERIAL PRIMARY KEY,
                enrollment_id INTEGER NOT NULL REFERENCES enrollments(id),
                module_name VARCHAR(200) NOT NULL,
                completion_percentage FLOAT DEFAULT 0,
                completed_at TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER REFERENCES users(id),
                updated_by INTEGER REFERENCES users(id)
            );
        """)
        
        # Create audit_log table
        cursor.execute("""
            CREATE TABLE audit_log (
                id SERIAL PRIMARY KEY,
                table_name VARCHAR(100) NOT NULL,
                record_id INTEGER,
                action VARCHAR(20) NOT NULL,
                old_values JSON,
                new_values JSON,
                user_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_users_email ON users(email);")
        cursor.execute("CREATE INDEX idx_members_planning_center_id ON members(planning_center_id);")
        cursor.execute("CREATE INDEX idx_members_email ON members(email);")
        cursor.execute("CREATE INDEX idx_courses_title ON courses(title);")
        cursor.execute("CREATE INDEX idx_enrollments_member_id ON enrollments(member_id);")
        cursor.execute("CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);")
        cursor.execute("CREATE INDEX idx_progress_enrollment_id ON progress(enrollment_id);")
        cursor.execute("CREATE INDEX idx_audit_log_table_name ON audit_log(table_name);")
        cursor.execute("CREATE INDEX idx_audit_log_record_id ON audit_log(record_id);")
        
        conn.commit()
        print("✅ Clean database schema created")
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        conn.rollback()
    finally:
        cursor.close()

def setup_alembic_version(conn):
    """Setup alembic version table"""
    cursor = conn.cursor()
    
    try:
        print("🔧 Setting up alembic version table...")
        
        cursor.execute("""
            CREATE TABLE alembic_version (
                version_num VARCHAR(32) NOT NULL,
                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
            );
        """)
        
        # Set to the latest migration
        cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('002_refined_schema_with_pc_integration');")
        
        conn.commit()
        print("✅ Alembic version table set up")
        
    except Exception as e:
        print(f"❌ Error setting up alembic: {e}")
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

def create_sample_data(conn):
    """Create some sample data for testing"""
    cursor = conn.cursor()
    
    try:
        print("📊 Creating sample data...")
        
        # Create default role
        cursor.execute("""
            INSERT INTO role (name, description, permissions)
            VALUES (%s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        """, ('viewer', 'Can view courses and progress', '{"view": true}'))
        
        # Create default campus
        cursor.execute("""
            INSERT INTO campus (name, address, is_active)
            VALUES (%s, %s, %s)
        """, ('Main Campus', '123 Church Street', True))
        
        # Create sample course
        cursor.execute("""
            INSERT INTO courses (title, description, duration_weeks, is_active)
            VALUES (%s, %s, %s, %s)
        """, ('Introduction to Church Leadership', 'Basic principles of church leadership', 8, True))
        
        conn.commit()
        print("✅ Sample data created")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        conn.rollback()
    finally:
        cursor.close()

def main():
    """Main function to fix the database"""
    print("🚀 Starting comprehensive database fix...")
    
    try:
        # Connect to database
        conn = get_database_connection()
        print("✅ Connected to database")
        
        # Reset database completely
        reset_database_completely(conn)
        
        # Create clean schema
        create_clean_schema(conn)
        
        # Setup alembic version
        setup_alembic_version(conn)
        
        # Create admin user
        create_admin_user(conn)
        
        # Create sample data
        create_sample_data(conn)
        
        print("🎉 Database fix completed successfully!")
        print("\n📋 Summary:")
        print("✅ Database completely reset")
        print("✅ Clean schema created")
        print("✅ Alembic version table set up")
        print("✅ Admin user created")
        print("✅ Sample data added")
        print("\n🔑 Admin Credentials:")
        print("Email: course.tracker.admin@eastgate.church")
        print("Username: admin")
        print("Password: Matthew778*")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
