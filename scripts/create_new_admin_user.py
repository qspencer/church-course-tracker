#!/usr/bin/env python3
"""
Script to create a new admin user with the desired credentials.
"""

import requests
import json
import time
import sys

def test_current_credentials():
    """Test current working credentials"""
    print("🔍 Testing current credentials...")
    
    try:
        response = requests.post('https://api.quentinspencer.com/api/v1/auth/login', 
                               json={'username': 'admin', 'password': 'admin123'}, 
                               timeout=10)
        
        if response.status_code == 200:
            print("✅ Current credentials work!")
            data = response.json()
            token = data.get('access_token')
            print(f"   Token: {token[:20]}...")
            return token
        else:
            print(f"❌ Current credentials failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def create_new_admin_user(token):
    """Create a new admin user"""
    print("🆕 Creating new admin user...")
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Create new user data
        user_data = {
            'username': 'Admin',
            'email': 'admin@quentinspencer.com',
            'full_name': 'Admin User',
            'password': 'Matthew778*',
            'role': 'admin',
            'is_active': True
        }
        
        response = requests.post('https://api.quentinspencer.com/api/v1/users', 
                               json=user_data, 
                               headers=headers, 
                               timeout=10)
        
        print(f"   Create user response: {response.status_code}")
        
        if response.status_code == 201:
            print("✅ New admin user created successfully!")
            return True
        elif response.status_code == 409:
            print("⚠️  User already exists!")
            return True
        else:
            print(f"❌ User creation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_new_credentials():
    """Test the new credentials"""
    print("🧪 Testing new credentials...")
    
    try:
        response = requests.post('https://api.quentinspencer.com/api/v1/auth/login', 
                               json={'username': 'Admin', 'password': 'Matthew778*'}, 
                               timeout=10)
        
        print(f"   New credentials test: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ New credentials work!")
            data = response.json()
            print(f"   User: {data.get('user', {}).get('username', 'Unknown')}")
            print(f"   Role: {data.get('user', {}).get('role', 'Unknown')}")
            return True
        else:
            print(f"❌ New credentials failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Creating New Admin User")
    print("=" * 40)
    
    # Test current credentials
    token = test_current_credentials()
    
    if not token:
        print("❌ Cannot proceed without valid token!")
        return False
    
    # Create new admin user
    success = create_new_admin_user(token)
    
    if success:
        print("\n⏳ Waiting for changes to propagate...")
        time.sleep(5)
        
        # Test new credentials
        if test_new_credentials():
            print("\n🎉 New admin user created successfully!")
            print("\n📝 New Credentials:")
            print("   Username: Admin")
            print("   Password: Matthew778*")
            print("\n✅ You can now use these credentials to log in!")
            return True
        else:
            print("\n⚠️  User may have been created but credentials not working yet")
            print("   Try logging in with: Admin / Matthew778*")
            return False
    else:
        print("\n❌ Could not create new admin user")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n🔧 Alternative approach needed:")
        print("   1. Use current working credentials: admin / admin123")
        print("   2. Or manually update the database through AWS Console")
        sys.exit(1)
