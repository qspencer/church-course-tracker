#!/usr/bin/env python3
"""
Script to create the default administrator user using the same database connection as the app
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_default_admin():
    """Create the default administrator user"""
    
    # Create a session using the existing SessionLocal
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(
            (User.username == "Admin") | (User.email == "admin@church.com")
        ).first()
        
        if existing_admin:
            print("✅ Default admin user already exists!")
            print(f"   Username: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role}")
            return
        
        # Hash the password
        hashed_password = pwd_context.hash("Matthew778*")
        
        # Create the admin user
        admin_user = User(
            username="Admin",
            email="admin@church.com",
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
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating default administrator user...")
    create_default_admin()
    print("Done!")
