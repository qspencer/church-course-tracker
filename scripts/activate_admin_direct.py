#!/usr/bin/env python3
"""
Direct script to activate Admin user - can be run from any machine with database access
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Production database URL
DB_URL = "postgresql://postgres:church_course_tracker_password@church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com:5432/church_course_tracker"

def activate_admin():
    """Activate Admin user directly via SQL"""
    print("🔧 Connecting to database...")
    try:
        engine = create_engine(DB_URL, connect_args={"connect_timeout": 10})
        
        with engine.connect() as conn:
            # Update and return the result
            result = conn.execute(
                text("UPDATE users SET is_active = true WHERE username = 'Admin' RETURNING id, username, email, is_active;")
            )
            row = result.fetchone()
            
            if row:
                conn.commit()
                print(f"✅ Admin user activated!")
                print(f"   ID: {row[0]}")
                print(f"   Username: {row[1]}")
                print(f"   Email: {row[2]}")
                print(f"   is_active: {row[3]}")
                return True
            else:
                print("❌ Admin user not found in database")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Activating Admin User")
    print("=" * 40)
    success = activate_admin()
    sys.exit(0 if success else 1)
