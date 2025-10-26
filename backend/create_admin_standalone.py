#!/usr/bin/env python3
"""
Standalone script to create admin user without importing application modules
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext

# Database connection
DATABASE_URL = "postgresql://postgres:qicBHo2ypeSkuyrU@church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com:5432/church_course_tracker"

# Use the same password context as the application
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def create_admin_user():
    """Create admin user directly in database"""
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Delete existing admin user if it exists (to force recreation with proper hash)
        cursor.execute("DELETE FROM users WHERE email = %s", ('course.tracker.admin@eastgate.church',))
        conn.commit()
        print("✅ Deleted existing admin user if it existed")
        
        # Create admin user with passlib bcrypt hash (same as application)
        simple_password = 'Admin123!'
        # Use passlib's hash method (same as get_password_hash in security.py)
        hashed_password = pwd_context.hash(simple_password)
        
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
        print(f"✅ Admin user created successfully! Password hash: {hashed_password[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_admin_user()

