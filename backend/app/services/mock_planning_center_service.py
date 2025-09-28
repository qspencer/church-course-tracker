"""
Mock Planning Center API Service
Simulates Planning Center API responses for development and testing
"""

import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
import random


class MockPlanningCenterService:
    """Mock service that simulates Planning Center API responses"""
    
    def __init__(self):
        self.base_url = "https://api.planningcenteronline.com"
        self.mock_data = self._generate_mock_data()
    
    def _generate_mock_data(self) -> Dict[str, Any]:
        """Generate realistic mock data for Planning Center"""
        
        # Mock people data
        people_data = []
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa", 
                       "James", "Mary", "William", "Jennifer", "Richard", "Linda", "Charles", "Patricia"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                      "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas"]
        
        for i in range(50):  # Generate 50 mock people
            person = {
                "id": f"pc_person_{i+1:03d}",
                "first_name": random.choice(first_names),
                "last_name": random.choice(last_names),
                "email": f"person{i+1}@example.com",
                "phone": f"555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "date_of_birth": (date.today() - timedelta(days=random.randint(18*365, 80*365))).isoformat(),
                "gender": random.choice(["Male", "Female", "Other"]),
                "address1": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Maple', 'Cedar'])} St",
                "city": random.choice(["Anytown", "Springfield", "Riverside", "Hillside", "Valley"]),
                "state": random.choice(["CA", "TX", "FL", "NY", "IL"]),
                "zip": f"{random.randint(10000, 99999)}",
                "household_id": f"hh_{random.randint(1, 20):03d}",
                "household_name": f"{random.choice(['Smith', 'Johnson', 'Williams'])} Family",
                "status": random.choice(["active", "inactive", "pending"]),
                "join_date": (date.today() - timedelta(days=random.randint(30, 3650))).isoformat(),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            }
            people_data.append(person)
        
        # Mock events data
        events_data = []
        event_names = [
            "Sunday Service", "Bible Study", "Youth Group", "Women's Ministry", 
            "Men's Fellowship", "Children's Church", "Prayer Meeting", "Community Outreach",
            "Leadership Training", "New Member Class", "Marriage Counseling", "Financial Peace",
            "Alpha Course", "Discipleship Program", "Mission Trip Planning"
        ]
        
        for i in range(20):  # Generate 20 mock events
            start_date = datetime.now() + timedelta(days=random.randint(-30, 90))
            end_date = start_date + timedelta(hours=random.randint(1, 4))
            
            event = {
                "id": f"pc_event_{i+1:03d}",
                "name": random.choice(event_names),
                "description": f"Join us for {random.choice(event_names).lower()}",
                "start_time": start_date.isoformat(),
                "end_time": end_date.isoformat(),
                "location": random.choice(["Main Sanctuary", "Fellowship Hall", "Youth Room", "Conference Room"]),
                "capacity": random.randint(20, 200),
                "registration_open": start_date > datetime.now(),
                "registration_deadline": (start_date - timedelta(days=1)).isoformat(),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                "updated_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            }
            events_data.append(event)
        
        # Mock registrations data
        registrations_data = []
        for event in events_data[:10]:  # Only first 10 events have registrations
            num_registrations = random.randint(0, min(50, event["capacity"]))
            for i in range(num_registrations):
                person = random.choice(people_data)
                registration = {
                    "id": f"pc_registration_{len(registrations_data)+1:03d}",
                    "person_id": person["id"],
                    "event_id": event["id"],
                    "status": random.choice(["registered", "waitlisted", "cancelled"]),
                    "registration_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                    "notes": random.choice(["", "First time attendee", "Returning member", "Special needs"]) if random.random() > 0.7 else "",
                    "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                    "updated_at": (datetime.now() - timedelta(days=random.randint(1, 7))).isoformat()
                }
                registrations_data.append(registration)
        
        return {
            "people": people_data,
            "events": events_data,
            "registrations": registrations_data
        }
    
    async def test_connection(self) -> bool:
        """Test connection to mock Planning Center API"""
        return True
    
    async def get_people(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get people from mock Planning Center API"""
        people = self.mock_data["people"][offset:offset + limit]
        
        return {
            "data": people,
            "meta": {
                "total_count": len(self.mock_data["people"]),
                "count": len(people),
                "next": f"{self.base_url}/people/v2/people?per_page={limit}&offset={offset + limit}" if offset + limit < len(self.mock_data["people"]) else None,
                "prev": f"{self.base_url}/people/v2/people?per_page={limit}&offset={max(0, offset - limit)}" if offset > 0 else None
            }
        }
    
    async def get_person(self, person_id: str) -> Dict[str, Any]:
        """Get a specific person from mock Planning Center API"""
        person = next((p for p in self.mock_data["people"] if p["id"] == person_id), None)
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person with ID {person_id} not found"
            )
        return {"data": person}
    
    async def get_events(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get events from mock Planning Center API"""
        events = self.mock_data["events"][offset:offset + limit]
        
        return {
            "data": events,
            "meta": {
                "total_count": len(self.mock_data["events"]),
                "count": len(events),
                "next": f"{self.base_url}/registrations/v2/events?per_page={limit}&offset={offset + limit}" if offset + limit < len(self.mock_data["events"]) else None,
                "prev": f"{self.base_url}/registrations/v2/events?per_page={limit}&offset={max(0, offset - limit)}" if offset > 0 else None
            }
        }
    
    async def get_event(self, event_id: str) -> Dict[str, Any]:
        """Get a specific event from mock Planning Center API"""
        event = next((e for e in self.mock_data["events"] if e["id"] == event_id), None)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        return {"data": event}
    
    async def get_event_registrations(self, event_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get registrations for a specific event"""
        registrations = [r for r in self.mock_data["registrations"] if r["event_id"] == event_id]
        paginated_registrations = registrations[offset:offset + limit]
        
        return {
            "data": paginated_registrations,
            "meta": {
                "total_count": len(registrations),
                "count": len(paginated_registrations),
                "next": f"{self.base_url}/registrations/v2/events/{event_id}/registrations?per_page={limit}&offset={offset + limit}" if offset + limit < len(registrations) else None,
                "prev": f"{self.base_url}/registrations/v2/events/{event_id}/registrations?per_page={limit}&offset={max(0, offset - limit)}" if offset > 0 else None
            }
        }
    
    async def get_person_registrations(self, person_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get registrations for a specific person"""
        registrations = [r for r in self.mock_data["registrations"] if r["person_id"] == person_id]
        paginated_registrations = registrations[offset:offset + limit]
        
        return {
            "data": paginated_registrations,
            "meta": {
                "total_count": len(registrations),
                "count": len(paginated_registrations),
                "next": f"{self.base_url}/registrations/v2/people/{person_id}/registrations?per_page={limit}&offset={offset + limit}" if offset + limit < len(registrations) else None,
                "prev": f"{self.base_url}/registrations/v2/people/{person_id}/registrations?per_page={limit}&offset={max(0, offset - limit)}" if offset > 0 else None
            }
        }
    
    async def create_registration(self, event_id: str, person_id: str, **kwargs) -> Dict[str, Any]:
        """Create a new registration"""
        # Check if person and event exist
        person = next((p for p in self.mock_data["people"] if p["id"] == person_id), None)
        event = next((e for e in self.mock_data["events"] if e["id"] == event_id), None)
        
        if not person:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person with ID {person_id} not found"
            )
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        # Check if registration already exists
        existing_registration = next((r for r in self.mock_data["registrations"] 
                                    if r["person_id"] == person_id and r["event_id"] == event_id), None)
        
        if existing_registration:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Registration already exists"
            )
        
        # Create new registration
        new_registration = {
            "id": f"pc_registration_{len(self.mock_data['registrations'])+1:03d}",
            "person_id": person_id,
            "event_id": event_id,
            "status": "registered",
            "registration_date": datetime.now().isoformat(),
            "notes": kwargs.get("notes", ""),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.mock_data["registrations"].append(new_registration)
        
        return {"data": new_registration}
    
    async def update_registration(self, registration_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing registration"""
        registration = next((r for r in self.mock_data["registrations"] if r["id"] == registration_id), None)
        
        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registration with ID {registration_id} not found"
            )
        
        # Update registration
        for key, value in kwargs.items():
            if key in registration:
                registration[key] = value
        
        registration["updated_at"] = datetime.now().isoformat()
        
        return {"data": registration}
    
    async def delete_registration(self, registration_id: str) -> bool:
        """Delete a registration"""
        registration = next((r for r in self.mock_data["registrations"] if r["id"] == registration_id), None)
        
        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registration with ID {registration_id} not found"
            )
        
        self.mock_data["registrations"].remove(registration)
        return True
    
    def get_mock_data_summary(self) -> Dict[str, Any]:
        """Get summary of mock data for debugging"""
        return {
            "total_people": len(self.mock_data["people"]),
            "total_events": len(self.mock_data["events"]),
            "total_registrations": len(self.mock_data["registrations"]),
            "active_people": len([p for p in self.mock_data["people"] if p["status"] == "active"]),
            "upcoming_events": len([e for e in self.mock_data["events"] if datetime.fromisoformat(e["start_time"]) > datetime.now()]),
            "recent_registrations": len([r for r in self.mock_data["registrations"] 
                                       if datetime.fromisoformat(r["registration_date"]) > datetime.now() - timedelta(days=7)])
        }
