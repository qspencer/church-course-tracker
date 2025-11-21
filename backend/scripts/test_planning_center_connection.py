#!/usr/bin/env python3
"""
Test Planning Center API connection
Verifies that credentials are configured correctly and API is accessible
"""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

import httpx
import base64
from app.core.config import settings

def test_planning_center_connection():
    """Test connection to Planning Center API"""
    print("🔌 Testing Planning Center API Connection")
    print("=" * 60)
    
    # Check credentials
    app_id = settings.PLANNING_CENTER_APP_ID
    secret = settings.PLANNING_CENTER_SECRET
    use_mock = settings.USE_MOCK_PLANNING_CENTER
    
    print(f"✅ Planning Center API URL: {settings.PLANNING_CENTER_API_URL}")
    print(f"✅ Using Mock API: {use_mock}")
    
    if use_mock:
        print("⚠️  WARNING: USE_MOCK_PLANNING_CENTER is set to 'true'")
        print("   Set USE_MOCK_PLANNING_CENTER=false in .env to use real API")
        return False
    
    if not app_id:
        print("❌ PLANNING_CENTER_APP_ID not configured")
        return False
    
    if not secret:
        print("❌ PLANNING_CENTER_SECRET not configured")
        return False
    
    print(f"✅ App ID: {app_id[:20]}... (truncated)")
    print(f"✅ Secret: {secret[:20]}... (truncated)")
    print()
    
    # Test connection
    print("🌐 Testing API connection...")
    try:
        # Create Basic Auth header
        credentials = f"{app_id}:{secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }
        
        # Test with a simple endpoint (GET /people/v2/people with limit=1)
        base_url = settings.PLANNING_CENTER_API_URL
        test_url = f"{base_url}/people/v2/people?per_page=1"
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(test_url, headers=headers)
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                total_count = data.get("meta", {}).get("total_count", 0)
                print(f"✅ Connection successful!")
                print(f"   Total people in Planning Center: {total_count}")
                return True
            elif response.status_code == 401:
                print("❌ Authentication failed - Invalid credentials")
                print(f"   Response: {response.text[:200]}")
                return False
            elif response.status_code == 403:
                print("❌ Access forbidden - Check API permissions")
                print(f"   Response: {response.text[:200]}")
                return False
            else:
                print(f"❌ Connection failed with status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
    except httpx.TimeoutException:
        print("❌ Connection timeout - Planning Center API not reachable")
        return False
    except httpx.RequestError as e:
        print(f"❌ Connection error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_planning_center_connection()
    print()
    print("=" * 60)
    if success:
        print("✅ Planning Center connection test PASSED")
        sys.exit(0)
    else:
        print("❌ Planning Center connection test FAILED")
        print()
        print("📝 Next Steps:")
        print("   1. Verify credentials in backend/.env")
        print("   2. Check USE_MOCK_PLANNING_CENTER=false")
        print("   3. Verify API credentials in Planning Center")
        print("   4. Check network connectivity")
        sys.exit(1)

