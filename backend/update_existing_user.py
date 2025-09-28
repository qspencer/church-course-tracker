#!/usr/bin/env python3
"""
Script to update the existing admin user credentials.
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

def get_user_info(token):
    """Get current user information"""
    print("🔍 Getting current user info...")
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get('https://api.quentinspencer.com/api/v1/users', 
                              headers=headers, 
                              timeout=10)
        
        print(f"   Users endpoint: {response.status_code}")
        
        if response.status_code == 200:
            users = response.json()
            print(f"   Found {len(users)} users:")
            for user in users:
                print(f"     - ID: {user.get('id')}, Username: {user.get('username')}, Email: {user.get('email')}")
            return users
        else:
            print(f"❌ Failed to get users: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def update_user(token, user_id):
    """Update user credentials"""
    print(f"🔄 Updating user ID {user_id}...")
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Update user data
        update_data = {
            'username': 'Admin',
            'email': 'admin@quentinspencer.com',
            'full_name': 'Admin User',
            'password': 'Matthew778*',
            'role': 'admin',
            'is_active': True
        }
        
        response = requests.put(f'https://api.quentinspencer.com/api/v1/users/{user_id}', 
                              json=update_data, 
                              headers=headers, 
                              timeout=10)
        
        print(f"   Update response: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ User updated successfully!")
            return True
        else:
            print(f"❌ User update failed: {response.text}")
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
    print("🚀 Updating Existing Admin User")
    print("=" * 40)
    
    # Test current credentials
    token = test_current_credentials()
    
    if not token:
        print("❌ Cannot proceed without valid token!")
        return False
    
    # Get user information
    users = get_user_info(token)
    
    if not users:
        print("❌ Cannot get user information!")
        return False
    
    # Find the admin user
    admin_user = None
    for user in users:
        if user.get('role') == 'admin':
            admin_user = user
            break
    
    if not admin_user:
        print("❌ No admin user found!")
        return False
    
    print(f"✅ Found admin user: ID {admin_user.get('id')}, Username: {admin_user.get('username')}")
    
    # Update the user
    success = update_user(token, admin_user.get('id'))
    
    if success:
        print("\n⏳ Waiting for changes to propagate...")
        time.sleep(5)
        
        # Test new credentials
        if test_new_credentials():
            print("\n🎉 Admin user update complete!")
            print("\n📝 New Credentials:")
            print("   Username: Admin")
            print("   Password: Matthew778*")
            print("\n✅ You can now use these credentials to log in!")
            return True
        else:
            print("\n⚠️  User may have been updated but credentials not working yet")
            print("   Try logging in with: Admin / Matthew778*")
            return False
    else:
        print("\n❌ Could not update admin user")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n🔧 Alternative approach needed:")
        print("   1. Use current working credentials: admin / admin123")
        print("   2. Or manually update the database through AWS Console")
        sys.exit(1)
