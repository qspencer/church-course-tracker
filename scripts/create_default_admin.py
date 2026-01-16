#!/usr/bin/env python3
"""
Script to create the default administrator user for the Church Course Tracker application.

This script creates a default admin user with the following credentials:
- Username: Admin
- Email: course.tracker.admin@eastgate.church
- Password: Matthew778*
- Role: admin

Usage:
    python create_default_admin.py

The script will check if an admin user already exists and skip creation if found.
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
# Get the project root (parent of scripts directory)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
backend_dir = os.path.join(project_root, "backend")
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal, Base
from app.models.user import User
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_default_admin():
    """
    Create the default administrator user.
    
    Returns:
        bool: True if user was created or already exists, False if there was an error
    """
    
    # Create a session using the existing SessionLocal
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(
            (User.username == "Admin") | (User.email == "course.tracker.admin@eastgate.church")
        ).first()
        
        if existing_admin:
            print("✅ Default admin user already exists!")
            print(f"   Username: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role}")
            print(f"   User ID: {existing_admin.id}")
            return True
        
        # Hash the password
        hashed_password = pwd_context.hash("Matthew778*")
        
        # Create the admin user
        admin_user = User(
            username="Admin",
            email="course.tracker.admin@eastgate.church",
            full_name="System Administrator",
            hashed_password=hashed_password,
            role="admin",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add to database
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Default administrator user created successfully!")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Password: Matthew778*")
        print(f"   Role: {admin_user.role}")
        print(f"   User ID: {admin_user.id}")
        print("\n🔐 You can now log in to the application using these credentials.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🏗️  Church Course Tracker - Admin User Setup")
    print("=" * 50)
    print("Creating default administrator user...")
    print()
    
    success = create_default_admin()
    
    if success:
        print()
        print("✅ Setup completed successfully!")
        print("🌐 You can now access the application at: http://localhost:4200")
    else:
        print()
        print("❌ Setup failed. Please check the error messages above.")
        sys.exit(1)
