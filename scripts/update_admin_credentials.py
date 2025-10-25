#!/usr/bin/env python3
"""
Script to update admin user credentials
"""
import os
import sys
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
DATABASE_URL = "postgresql://postgres:qicBHo2ypeSkuyrU@church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com:5432/church_course_tracker"

def update_admin_credentials():
    """Update admin user credentials"""
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if admin user exists
        cursor.execute("SELECT id, username, email FROM users WHERE email = %s", ('course.tracker.admin@eastgate.church',))
        existing_user = cursor.fetchone()
        
        if not existing_user:
            print("❌ Admin user not found!")
            return False
        
        print(f"📝 Found admin user: ID={existing_user['id']}, Username={existing_user['username']}")
        
        # Update admin user credentials
        new_username = 'Admin'
        new_password = 'Matthew778*'
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        
        cursor.execute("""
            UPDATE users 
            SET username = %s, hashed_password = %s, updated_at = NOW()
            WHERE email = %s
        """, (new_username, hashed_password, 'course.tracker.admin@eastgate.church'))
        
        conn.commit()
        print("✅ Admin user credentials updated successfully!")
        print(f"   New Username: {new_username}")
        print(f"   New Password: {new_password}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating admin user: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    update_admin_credentials()
