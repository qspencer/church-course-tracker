#!/usr/bin/env python3
"""
Script to update the AWS PostgreSQL database with admin user credentials.
This script connects to the AWS RDS PostgreSQL database and creates/updates a user with:
- Username: Admin
- Password: Matthew778*
- Email: admin@quentinspencer.com
- Role: admin
"""

import os
import sys
import asyncio
import hashlib
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.user import User
from passlib.context import CryptContext

def hash_password(password: str) -> str:
    """Hash password using bcrypt (same as the app uses)"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def update_aws_admin_user():
    """Update admin user in the AWS PostgreSQL database"""
    
    # Load environment variables
    load_dotenv()
    
    # AWS RDS PostgreSQL connection string
    # Format: postgresql://username:password@host:port/database
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
        
        # Check if user already exists
        existing_user = session.query(User).filter(User.username == "Admin").first()
        
        if existing_user:
            print(f"⚠️  User 'Admin' already exists in AWS database!")
            print(f"   ID: {existing_user.id}")
            print(f"   Email: {existing_user.email}")
            print(f"   Role: {existing_user.role}")
            print(f"   Active: {existing_user.is_active}")
            
            # Update the existing user
            print("🔄 Updating existing user in AWS database...")
            existing_user.hashed_password = hash_password("Matthew778*")
            existing_user.email = "admin@quentinspencer.com"
            existing_user.full_name = "Admin User"
            existing_user.role = "admin"
            existing_user.is_active = True
            
            session.commit()
            print("✅ User updated successfully in AWS database!")
            
        else:
            print("🆕 Creating new admin user in AWS database...")
            
            # Create new admin user
            admin_user = User(
                username="Admin",
                email="admin@quentinspencer.com",
                full_name="Admin User",
                hashed_password=hash_password("Matthew778*"),
                role="admin",
                is_active=True
            )
            
            session.add(admin_user)
            session.commit()
            
            print("✅ Admin user created successfully in AWS database!")
            print(f"   Username: Admin")
            print(f"   Password: Matthew778*")
            print(f"   Email: admin@quentinspencer.com")
            print(f"   Role: admin")
        
        # Verify the user was created/updated
        print("\n🔍 Verifying user in AWS database...")
        user = session.query(User).filter(User.username == "Admin").first()
        
        if user:
            print("✅ User verification successful!")
            print(f"   ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Full Name: {user.full_name}")
            print(f"   Role: {user.role}")
            print(f"   Active: {user.is_active}")
            print(f"   Created: {user.created_at}")
        else:
            print("❌ User verification failed!")
            
        session.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def test_login():
    """Test the login with the new credentials"""
    print("\n🧪 Testing login with new credentials...")
    
    try:
        import requests
        
        response = requests.post('https://api.quentinspencer.com/api/v1/auth/login', 
                               json={'username': 'Admin', 'password': 'Matthew778*'}, 
                               timeout=10)
        
        if response.status_code == 200:
            print("✅ Login test successful!")
            data = response.json()
            print(f"   Token: {data.get('access_token', 'Not found')[:20]}...")
            print(f"   User: {data.get('user', {}).get('username', 'Unknown')}")
            print(f"   Role: {data.get('user', {}).get('role', 'Unknown')}")
        else:
            print(f"❌ Login test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Login test error: {e}")

if __name__ == "__main__":
    print("🚀 Updating AWS Admin User")
    print("=" * 40)
    
    # Update the admin user in AWS database
    success = update_aws_admin_user()
    
    if success:
        print("\n🎉 AWS admin user setup complete!")
        
        # Test the login
        test_login()
        
        print("\n📝 Next Steps:")
        print("   1. Go to: https://apps.quentinspencer.com/auth")
        print("   2. Username: Admin")
        print("   3. Password: Matthew778*")
        print("   4. Click Sign In")
        
    else:
        print("\n❌ AWS admin user setup failed!")
        sys.exit(1)
