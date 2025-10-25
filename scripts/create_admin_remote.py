#!/usr/bin/env python3
"""
Create admin user via the deployed API
"""

import requests
import json
import sys

# Configuration
API_BASE_URL = "http://church-course-tracker-alb-776928604.us-east-1.elb.amazonaws.com/api/v1"
ADMIN_EMAIL = "course.tracker.admin@eastgate.church"
ADMIN_PASSWORD = "admin123"  # Change this in production
ADMIN_FIRST_NAME = "Admin"
ADMIN_LAST_NAME = "User"

def create_admin_user():
    """Create admin user via API"""
    print("🏗️  Church Course Tracker - Remote Admin User Setup")
    print("=" * 50)
    print("Creating default administrator user via API...")
    print()
    
    try:
        # First, try to register the admin user
        register_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "first_name": ADMIN_FIRST_NAME,
            "last_name": ADMIN_LAST_NAME,
            "role": "admin"
        }
        
        print(f"📧 Creating admin user: {ADMIN_EMAIL}")
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json=register_data,
            timeout=30
        )
        
        if response.status_code == 201:
            print("✅ Admin user created successfully!")
            print(f"   Email: {ADMIN_EMAIL}")
            print(f"   Password: {ADMIN_PASSWORD}")
            print()
            print("🔐 You can now log in with these credentials.")
            return True
        elif response.status_code == 400:
            # User might already exist, try to get user info
            print("⚠️  User might already exist. Checking...")
            
            # Try to get user info
            get_response = requests.get(
                f"{API_BASE_URL}/users/me",
                headers={"Authorization": f"Bearer {ADMIN_EMAIL}"},
                timeout=30
            )
            
            if get_response.status_code == 200:
                print("✅ Admin user already exists!")
                print(f"   Email: {ADMIN_EMAIL}")
                print(f"   Password: {ADMIN_PASSWORD}")
                return True
            else:
                print(f"❌ Error checking user: {get_response.status_code}")
                print(f"   Response: {get_response.text}")
                return False
        else:
            print(f"❌ Error creating admin user: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = create_admin_user()
    if success:
        print("🎉 Admin user setup completed!")
        sys.exit(0)
    else:
        print("❌ Admin user setup failed!")
        sys.exit(1)

