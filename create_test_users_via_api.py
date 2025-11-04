#!/usr/bin/env python3
"""
Create test users via API endpoint
"""
import requests
import json

API_BASE = "https://api.quentinspencer.com/api/v1"

def login():
    """Login as admin and get token"""
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def create_user(token, user_data):
    """Create a user via API"""
    response = requests.post(
        f"{API_BASE}/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    )
    
    if response.status_code in [200, 201]:
        print(f"✅ Created user: {user_data['username']}")
        return True
    elif response.status_code == 409:
        print(f"⚠️  User {user_data['username']} already exists")
        return True
    else:
        print(f"❌ Failed to create {user_data['username']}: {response.status_code} - {response.text}")
        return False

def main():
    print("👥 Creating test users via API...")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        print("❌ Failed to authenticate")
        return False
    
    # Create test users
    test_users = [
        {
            "username": "staff",
            "email": "staff@church.com",
            "full_name": "Church Staff",
            "password": "staff123",
            "role": "staff",
            "is_active": True
        },
        {
            "username": "viewer",
            "email": "viewer@church.com",
            "full_name": "Course Viewer",
            "password": "viewer123",
            "role": "viewer",
            "is_active": True
        }
    ]
    
    success = 0
    for user_data in test_users:
        if create_user(token, user_data):
            success += 1
    
    print("=" * 60)
    print(f"✅ Created {success}/{len(test_users)} test users")
    return success == len(test_users)

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)


