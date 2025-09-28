#!/usr/bin/env python3
"""
Script to update admin user credentials in the AWS database.
This script is designed to be run inside the ECS container.
"""

import os
import sys
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Add the app directory to the path
sys.path.append('/app/app')

from app.models.user import User
from app.core.config import settings

def hash_password(password: str) -> str:
    """Hash password using bcrypt (same as the app uses)"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)

def update_admin_user():
    """Update admin user in the database"""
    
    print(f"🔧 Connecting to database...")
    print(f"   Database URL: {settings.DATABASE_URL}")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        print("✅ Database connection successful!")
        
        # Check if user already exists
        existing_user = session.query(User).filter(User.username == "Admin").first()
        
        if existing_user:
            print(f"⚠️  User 'Admin' already exists!")
            print(f"   ID: {existing_user.id}")
            print(f"   Email: {existing_user.email}")
            print(f"   Role: {existing_user.role}")
            print(f"   Active: {existing_user.is_active}")
            
            # Update the existing user
            print("🔄 Updating existing user...")
            existing_user.hashed_password = hash_password("Matthew778*")
            existing_user.email = "admin@quentinspencer.com"
            existing_user.full_name = "Admin User"
            existing_user.role = "admin"
            existing_user.is_active = True
            
            session.commit()
            print("✅ User updated successfully!")
            
        else:
            print("🆕 Creating new admin user...")
            
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
            
            print("✅ Admin user created successfully!")
            print(f"   Username: Admin")
            print(f"   Password: Matthew778*")
            print(f"   Email: admin@quentinspencer.com")
            print(f"   Role: admin")
        
        # Verify the user was created/updated
        print("\n🔍 Verifying user...")
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

if __name__ == "__main__":
    print("🚀 Updating Admin User in AWS Database")
    print("=" * 40)
    
    # Update the admin user
    success = update_admin_user()
    
    if success:
        print("\n🎉 Admin user setup complete!")
        print("\n📝 Credentials:")
        print("   Username: Admin")
        print("   Password: Matthew778*")
    else:
        print("\n❌ Admin user setup failed!")
        sys.exit(1)