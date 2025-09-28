#!/usr/bin/env python3
"""
Standalone script to create admin user without importing application modules
"""
import os
import sys
import hashlib
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
        
        # Check if admin user exists
        cursor.execute("SELECT id FROM users WHERE email = %s", ('course.tracker.admin@eastgate.church',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("✅ Admin user already exists!")
            return True
        
        # Create admin user with simple SHA256 hash
        simple_password = 'Matthew778*'
        hashed_password = hashlib.sha256(simple_password.encode()).hexdigest()
        
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
        print("✅ Admin user created successfully!")
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

