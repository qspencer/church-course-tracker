#!/usr/bin/env python3
"""
Standalone script to create admin user without importing application modules
"""
import os
import sys
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DATABASE_URL = "postgresql://postgres:qicBHo2ypeSkuyrU@church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com:5432/church_course_tracker"

def create_admin_user():
    """Create admin user directly in database"""
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Delete existing admin user if it exists (to force recreation with bcrypt)
        cursor.execute("DELETE FROM users WHERE email = %s", ('course.tracker.admin@eastgate.church',))
        conn.commit()
        print("✅ Deleted existing admin user if it existed")
        
        # Create admin user with bcrypt hash
        simple_password = 'Matthew778*'
        hashed_password = bcrypt.hashpw(simple_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert admin user
        cursor.execute("""
            INSERT INTO users (email, username, full_name, hashed_password, role, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        """, (
            'course.tracker.admin@eastgate.church',
            'Admin',
            'Admin User',
            hashed_password,
            'admin',
            True
        ))
        
        conn.commit()
        print("✅ Admin user created successfully with bcrypt hash!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_admin_user()

