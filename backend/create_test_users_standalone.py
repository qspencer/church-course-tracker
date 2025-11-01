#!/usr/bin/env python3
"""
Standalone script to create test users (staff and viewer) for E2E testing
"""
import os
import sys
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor

# Get database URL from environment or use default (same as create_admin_standalone.py)
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://postgres:qicBHo2ypeSkuyrU@church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com:5432/church_course_tracker"

if not DATABASE_URL:
    print("❌ DATABASE_URL not set")
    sys.exit(1)

def create_user(username: str, email: str, full_name: str, password: str, role: str):
    """Create a user directly in database"""
    try:
        # Parse database URL
        # postgresql://user:pass@host:port/dbname
        parts = DATABASE_URL.replace('postgresql://', '').split('/')
        userpass = parts[0].split('@')[0]
        db_user, db_password = userpass.split(':')
        hostport = parts[0].split('@')[1]
        host, port = hostport.split(':')
        dbname = parts[1]
        
        # Connect to database
        conn = psycopg2.connect(host=host, port=port, database=dbname, user=db_user, password=db_password)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if user already exists
        cursor.execute("SELECT id, username, email FROM users WHERE username = %s OR email = %s", (username, email))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️  User '{username}' already exists (id: {existing['id']})")
            cursor.close()
            conn.close()
            return True
        
        # Hash password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert user
        cursor.execute("""
            INSERT INTO users (username, email, full_name, hashed_password, role, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """, (
            username,
            email,
            full_name,
            hashed_password,
            role,
            True
        ))
        
        user_id = cursor.fetchone()['id']
        conn.commit()
        print(f"✅ User '{username}' ({role}) created successfully! (id: {user_id})")
        return True
        
    except Exception as e:
        print(f"❌ Error creating user '{username}': {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def create_test_users():
    """Create all test users for E2E testing"""
    print("👥 Creating test users for E2E testing...")
    print("=" * 60)
    
    test_users = [
        {
            'username': 'staff',
            'email': 'staff@church.com',
            'full_name': 'Church Staff',
            'password': 'staff123',
            'role': 'staff'
        },
        {
            'username': 'viewer',
            'email': 'viewer@church.com',
            'full_name': 'Course Viewer',
            'password': 'viewer123',
            'role': 'viewer'
        }
    ]
    
    success_count = 0
    for user_data in test_users:
        if create_user(**user_data):
            success_count += 1
        else:
            print(f"⚠️  Failed to create {user_data['username']}")
    
    print("=" * 60)
    print(f"✅ Created {success_count}/{len(test_users)} test users")
    return success_count == len(test_users)

if __name__ == "__main__":
    success = create_test_users()
    sys.exit(0 if success else 1)

