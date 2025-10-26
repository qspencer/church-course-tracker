#!/usr/bin/env python3
"""
Standalone script to create admin user without importing application modules
"""
import os
import sys
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext

# Database connection
DATABASE_URL = "postgresql://postgres:qicBHo2ypeSkuyrU@church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com:5432/church_course_tracker"

# Initialize passlib context for bcrypt hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        
        # Delete existing admin user if it exists (to force recreation with proper hash)
        cursor.execute("DELETE FROM users WHERE email = %s", ('course.tracker.admin@eastgate.church',))
        conn.commit()
        print("✅ Deleted existing admin user if it existed")
        
        # Create admin user with passlib bcrypt hash (password must be <= 72 bytes)
        simple_password = 'Admin123!'
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

