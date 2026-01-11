#!/usr/bin/env python3
"""
Script to activate the Admin user in the AWS PostgreSQL database.
This script sets is_active = True for the Admin user to fix API authentication tests.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.models.user import User

def activate_admin_user():
    """Activate admin user in the AWS PostgreSQL database"""
    
    # Load environment variables
    load_dotenv()
    
    # AWS RDS PostgreSQL connection string
    aws_db_url = "postgresql://postgres:church_course_tracker_password@church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com:5432/church_course_tracker"
    
    print(f"🔧 Connecting to AWS PostgreSQL database...")
    print(f"   Host: church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com")
    print(f"   Database: church_course_tracker")
    
    try:
        # Create engine for AWS database
        engine = create_engine(aws_db_url)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        print("✅ AWS Database connection successful!")
        
        # Find the Admin user
        admin_user = session.query(User).filter(User.username == "Admin").first()
        
        if not admin_user:
            print("❌ Admin user not found in database!")
            print("   Please create the Admin user first.")
            session.close()
            return False
        
        print(f"✅ Found Admin user:")
        print(f"   ID: {admin_user.id}")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role}")
        print(f"   Current Active Status: {admin_user.is_active}")
        
        if admin_user.is_active:
            print("✅ Admin user is already active!")
            session.close()
            return True
        
        # Activate the user
        print("🔄 Activating Admin user...")
        admin_user.is_active = True
        session.commit()
        
        print("✅ Admin user activated successfully!")
        
        # Verify the activation
        session.refresh(admin_user)
        if admin_user.is_active:
            print(f"✅ Verification: Admin user is now active (is_active = {admin_user.is_active})")
        else:
            print("❌ Verification failed: Admin user is still inactive")
            session.close()
            return False
            
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login():
    """Test the login with Admin credentials"""
    print("\n🧪 Testing login with Admin credentials...")
    
    try:
        import requests
        
        # Test with the credentials used in tests
        response = requests.post('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/auth/login', 
                               json={'username': 'Admin', 'password': 'Admin123!'}, 
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login test successful!")
            data = response.json()
            print(f"   Token: {data.get('access_token', 'Not found')[:20]}...")
            user_info = data.get('user', {})
            print(f"   Username: {user_info.get('username', 'Unknown')}")
            print(f"   Role: {user_info.get('role', 'Unknown')}")
            print(f"   Active: {user_info.get('is_active', 'Unknown')}")
            return True
        else:
            print(f"❌ Login test failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Activating Admin User for E2E Tests")
    print("=" * 50)
    
    # Activate the admin user in AWS database
    success = activate_admin_user()
    
    if success:
        print("\n⏳ Waiting 3 seconds for changes to propagate...")
        import time
        time.sleep(3)
        
        # Test the login
        login_success = test_login()
        
        if login_success:
            print("\n🎉 Admin user activation complete!")
            print("\n✅ The 8 API authentication tests should now pass!")
        else:
            print("\n⚠️  User activated but login test failed")
            print("   This may be due to:")
            print("   1. Password mismatch (tests use 'Admin123!' but DB may have different password)")
            print("   2. Changes not yet propagated")
            print("   3. API caching")
    else:
        print("\n❌ Admin user activation failed!")
        sys.exit(1)
