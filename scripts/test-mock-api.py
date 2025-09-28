#!/usr/bin/env python3
"""
Test script for Mock Planning Center API
Tests all mock endpoints to ensure they work correctly
"""

import asyncio
import httpx
import json
from typing import Dict, Any


class MockAPITester:
    """Test the mock Planning Center API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1/mock-planning-center"
    
    async def test_connection(self) -> bool:
        """Test the connection endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}/test-connection")
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Connection test passed")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Connected: {data.get('connected')}")
                    if 'mock_data_summary' in data:
                        summary = data['mock_data_summary']
                        print(f"   Mock data: {summary['total_people']} people, {summary['total_events']} events, {summary['total_registrations']} registrations")
                    return True
                else:
                    print(f"❌ Connection test failed: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Connection test error: {e}")
            return False
    
    async def test_people_endpoints(self) -> bool:
        """Test people-related endpoints"""
        try:
            async with httpx.AsyncClient() as client:
                # Test get people
                response = await client.get(f"{self.api_url}/people?per_page=5")
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Get people test passed")
                    print(f"   Retrieved {len(data.get('data', []))} people")
                    
                    # Test get specific person
                    if data.get('data'):
                        person_id = data['data'][0]['id']
                        person_response = await client.get(f"{self.api_url}/people/{person_id}")
                        if person_response.status_code == 200:
                            print("✅ Get specific person test passed")
                            return True
                        else:
                            print(f"❌ Get specific person test failed: {person_response.status_code}")
                            return False
                    else:
                        print("❌ No people data available")
                        return False
                else:
                    print(f"❌ Get people test failed: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ People endpoints test error: {e}")
            return False
    
    async def test_events_endpoints(self) -> bool:
        """Test events-related endpoints"""
        try:
            async with httpx.AsyncClient() as client:
                # Test get events
                response = await client.get(f"{self.api_url}/events?per_page=5")
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Get events test passed")
                    print(f"   Retrieved {len(data.get('data', []))} events")
                    
                    # Test get specific event
                    if data.get('data'):
                        event_id = data['data'][0]['id']
                        event_response = await client.get(f"{self.api_url}/events/{event_id}")
                        if event_response.status_code == 200:
                            print("✅ Get specific event test passed")
                            return True
                        else:
                            print(f"❌ Get specific event test failed: {event_response.status_code}")
                            return False
                    else:
                        print("❌ No events data available")
                        return False
                else:
                    print(f"❌ Get events test failed: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Events endpoints test error: {e}")
            return False
    
    async def test_registrations_endpoints(self) -> bool:
        """Test registrations-related endpoints"""
        try:
            async with httpx.AsyncClient() as client:
                # First get an event with registrations
                events_response = await client.get(f"{self.api_url}/events?per_page=10")
                if events_response.status_code != 200:
                    print("❌ Could not get events for registration test")
                    return False
                
                events_data = events_response.json()
                if not events_data.get('data'):
                    print("❌ No events available for registration test")
                    return False
                
                # Test event registrations
                event_id = events_data['data'][0]['id']
                reg_response = await client.get(f"{self.api_url}/events/{event_id}/registrations?per_page=5")
                if reg_response.status_code == 200:
                    print("✅ Get event registrations test passed")
                    reg_data = reg_response.json()
                    print(f"   Retrieved {len(reg_data.get('data', []))} registrations for event {event_id}")
                else:
                    print(f"❌ Get event registrations test failed: {reg_response.status_code}")
                    return False
                
                # Test person registrations
                people_response = await client.get(f"{self.api_url}/people?per_page=5")
                if people_response.status_code == 200:
                    people_data = people_response.json()
                    if people_data.get('data'):
                        person_id = people_data['data'][0]['id']
                        person_reg_response = await client.get(f"{self.api_url}/people/{person_id}/registrations?per_page=5")
                        if person_reg_response.status_code == 200:
                            print("✅ Get person registrations test passed")
                            person_reg_data = person_reg_response.json()
                            print(f"   Retrieved {len(person_reg_data.get('data', []))} registrations for person {person_id}")
                        else:
                            print(f"❌ Get person registrations test failed: {person_reg_response.status_code}")
                            return False
                
                return True
        except Exception as e:
            print(f"❌ Registrations endpoints test error: {e}")
            return False
    
    async def test_mock_data_management(self) -> bool:
        """Test mock data management endpoints"""
        try:
            async with httpx.AsyncClient() as client:
                # Test mock data summary
                summary_response = await client.get(f"{self.api_url}/mock-data/summary")
                if summary_response.status_code == 200:
                    print("✅ Mock data summary test passed")
                    summary_data = summary_response.json()
                    print(f"   Data summary: {summary_data.get('data', {})}")
                else:
                    print(f"❌ Mock data summary test failed: {summary_response.status_code}")
                    return False
                
                # Test mock data reset
                reset_response = await client.get(f"{self.api_url}/mock-data/reset")
                if reset_response.status_code == 200:
                    print("✅ Mock data reset test passed")
                    reset_data = reset_response.json()
                    print(f"   Reset message: {reset_data.get('message')}")
                else:
                    print(f"❌ Mock data reset test failed: {reset_response.status_code}")
                    return False
                
                return True
        except Exception as e:
            print(f"❌ Mock data management test error: {e}")
            return False
    
    async def run_all_tests(self) -> bool:
        """Run all tests"""
        print("🧪 Testing Mock Planning Center API")
        print("=" * 50)
        
        tests = [
            ("Connection Test", self.test_connection),
            ("People Endpoints", self.test_people_endpoints),
            ("Events Endpoints", self.test_events_endpoints),
            ("Registrations Endpoints", self.test_registrations_endpoints),
            ("Mock Data Management", self.test_mock_data_management)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            try:
                if await test_func():
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} ERROR: {e}")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Mock API is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
            return False


async def main():
    """Main test function"""
    tester = MockAPITester()
    
    print("🚀 Starting Mock Planning Center API Tests")
    print("Make sure the backend server is running on http://localhost:8000")
    print()
    
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ Mock API is ready for development!")
        print("🔗 You can now use the mock endpoints for testing and development.")
        print("📖 See docs/MOCK_PLANNING_CENTER_API.md for full documentation.")
    else:
        print("\n❌ Mock API tests failed. Please check the backend server.")
        print("💡 Make sure to run: uvicorn main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())
