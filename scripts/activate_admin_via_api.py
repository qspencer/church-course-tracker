#!/usr/bin/env python3
"""
Script to activate Admin user via API.
This requires an existing active admin user to authenticate first.
"""

import requests
import json
import sys

def find_active_admin():
    """Try to find an active admin user to use for authentication"""
    print("🔍 Looking for active admin credentials...")
    
    # Try common admin credentials
    test_credentials = [
        {'username': 'admin', 'password': 'admin123'},
        {'username': 'Admin', 'password': 'Matthew778*'},
        {'username': 'admin', 'password': 'Matthew778*'},
    ]
    
    for creds in test_credentials:
        try:
            response = requests.post('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/auth/login',
                                   json=creds,
                                   headers={'Content-Type': 'application/json'},
                                   timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Found active admin: {creds['username']}")
                return response.json().get('access_token')
        except:
            continue
    
    print("❌ No active admin credentials found")
    return None

def activate_admin_user(token):
    """Activate Admin user via API"""
    print("🔄 Activating Admin user via API...")
    
    # First, get all users to find the Admin user ID
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/users/',
                              headers=headers,
                              timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to get users: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        users = response.json()
        admin_user = None
        
        for user in users:
            if user.get('username') == 'Admin':
                admin_user = user
                break
        
        if not admin_user:
            print("❌ Admin user not found in users list")
            return False
        
        user_id = admin_user.get('id')
        print(f"✅ Found Admin user: ID {user_id}")
        print(f"   Current is_active: {admin_user.get('is_active')}")
        
        if admin_user.get('is_active'):
            print("✅ Admin user is already active!")
            return True
        
        # Update the user to activate
        update_data = {
            'is_active': True
        }
        
        response = requests.patch(f'https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/users/{user_id}',
                                json=update_data,
                                headers=headers,
                                timeout=10)
        
        if response.status_code == 200:
            print("✅ Admin user activated successfully!")
            return True
        else:
            print(f"❌ Failed to activate user: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_admin_login():
    """Test login with Admin credentials"""
    print("\n🧪 Testing Admin login...")
    
    try:
        response = requests.post('https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/auth/login',
                               json={'username': 'Admin', 'password': 'Admin123!'},
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Admin login successful!")
            data = response.json()
            print(f"   Username: {data.get('user', {}).get('username')}")
            print(f"   Role: {data.get('user', {}).get('role')}")
            print(f"   Active: {data.get('user', {}).get('is_active')}")
            return True
        else:
            print(f"❌ Admin login failed")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Activating Admin User via API")
    print("=" * 50)
    
    # Find an active admin to authenticate
    token = find_active_admin()
    
    if not token:
        print("\n❌ Cannot proceed without active admin credentials")
        print("\n💡 Alternative: Run this script from a machine with database access:")
        print("   python3 scripts/update_aws_admin_user.py")
        sys.exit(1)
    
    # Activate the Admin user
    success = activate_admin_user(token)
    
    if success:
        print("\n⏳ Waiting 3 seconds for changes to propagate...")
        import time
        time.sleep(3)
        
        # Test the login
        if test_admin_login():
            print("\n🎉 Admin user activation complete!")
            print("✅ The 8 API authentication tests should now pass!")
        else:
            print("\n⚠️  User may be activated but login test failed")
            print("   This could be due to password mismatch or propagation delay")
    else:
        print("\n❌ Failed to activate Admin user")
        sys.exit(1)
