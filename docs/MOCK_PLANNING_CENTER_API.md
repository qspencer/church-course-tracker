# 🎭 Mock Planning Center API Documentation

This document describes the mock Planning Center API endpoints that simulate real Planning Center API responses for development and testing purposes.

## 🚀 **Getting Started**

The mock API is automatically enabled when:
- `ENVIRONMENT=development` in your configuration
- Planning Center credentials are not configured
- You explicitly use the mock endpoints

## 📍 **Base URL**

```
http://localhost:8000/api/v1/mock-planning-center
```

## 🔗 **Available Endpoints**

### **Connection Testing**

#### `GET /test-connection`
Test connection to the mock Planning Center API.

**Response:**
```json
{
  "status": "success",
  "message": "Successfully connected to mock Planning Center API",
  "connected": true,
  "mock_data_summary": {
    "total_people": 50,
    "total_events": 20,
    "total_registrations": 150,
    "active_people": 45,
    "upcoming_events": 12,
    "recent_registrations": 25
  }
}
```

### **People Management**

#### `GET /people`
Get a list of people from the mock Planning Center.

**Query Parameters:**
- `per_page` (int, optional): Number of people per page (1-100, default: 50)
- `offset` (int, optional): Number of people to skip (default: 0)

**Response:**
```json
{
  "data": [
    {
      "id": "pc_person_001",
      "first_name": "John",
      "last_name": "Smith",
      "email": "person1@example.com",
      "phone": "555-123-4567",
      "date_of_birth": "1985-06-15",
      "gender": "Male",
      "address1": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip": "12345",
      "household_id": "hh_001",
      "household_name": "Smith Family",
      "status": "active",
      "join_date": "2020-01-15",
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-12-01T00:00:00"
    }
  ],
  "meta": {
    "total_count": 50,
    "count": 50,
    "next": null,
    "prev": null
  }
}
```

#### `GET /people/{person_id}`
Get a specific person by ID.

**Response:**
```json
{
  "data": {
    "id": "pc_person_001",
    "first_name": "John",
    "last_name": "Smith",
    "email": "person1@example.com",
    "phone": "555-123-4567",
    "date_of_birth": "1985-06-15",
    "gender": "Male",
    "address1": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip": "12345",
    "household_id": "hh_001",
    "household_name": "Smith Family",
    "status": "active",
    "join_date": "2020-01-15",
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-12-01T00:00:00"
  }
}
```

### **Events Management**

#### `GET /events`
Get a list of events from the mock Planning Center.

**Query Parameters:**
- `per_page` (int, optional): Number of events per page (1-100, default: 50)
- `offset` (int, optional): Number of events to skip (default: 0)

**Response:**
```json
{
  "data": [
    {
      "id": "pc_event_001",
      "name": "Sunday Service",
      "description": "Join us for Sunday Service",
      "start_time": "2024-01-15T10:00:00",
      "end_time": "2024-01-15T12:00:00",
      "location": "Main Sanctuary",
      "capacity": 200,
      "registration_open": true,
      "registration_deadline": "2024-01-14T23:59:59",
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-12-01T00:00:00"
    }
  ],
  "meta": {
    "total_count": 20,
    "count": 20,
    "next": null,
    "prev": null
  }
}
```

#### `GET /events/{event_id}`
Get a specific event by ID.

**Response:**
```json
{
  "data": {
    "id": "pc_event_001",
    "name": "Sunday Service",
    "description": "Join us for Sunday Service",
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T12:00:00",
    "location": "Main Sanctuary",
    "capacity": 200,
    "registration_open": true,
    "registration_deadline": "2024-01-14T23:59:59",
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-12-01T00:00:00"
  }
}
```

### **Registrations Management**

#### `GET /events/{event_id}/registrations`
Get registrations for a specific event.

**Query Parameters:**
- `per_page` (int, optional): Number of registrations per page (1-100, default: 50)
- `offset` (int, optional): Number of registrations to skip (default: 0)

**Response:**
```json
{
  "data": [
    {
      "id": "pc_registration_001",
      "person_id": "pc_person_001",
      "event_id": "pc_event_001",
      "status": "registered",
      "registration_date": "2024-01-10T09:00:00",
      "notes": "First time attendee",
      "created_at": "2024-01-10T09:00:00",
      "updated_at": "2024-01-10T09:00:00"
    }
  ],
  "meta": {
    "total_count": 25,
    "count": 25,
    "next": null,
    "prev": null
  }
}
```

#### `GET /people/{person_id}/registrations`
Get registrations for a specific person.

**Query Parameters:**
- `per_page` (int, optional): Number of registrations per page (1-100, default: 50)
- `offset` (int, optional): Number of registrations to skip (default: 0)

**Response:**
```json
{
  "data": [
    {
      "id": "pc_registration_001",
      "person_id": "pc_person_001",
      "event_id": "pc_event_001",
      "status": "registered",
      "registration_date": "2024-01-10T09:00:00",
      "notes": "First time attendee",
      "created_at": "2024-01-10T09:00:00",
      "updated_at": "2024-01-10T09:00:00"
    }
  ],
  "meta": {
    "total_count": 5,
    "count": 5,
    "next": null,
    "prev": null
  }
}
```

#### `POST /events/{event_id}/registrations`
Create a new registration.

**Request Body:**
```json
{
  "person_id": "pc_person_001",
  "notes": "First time attendee"
}
```

**Response:**
```json
{
  "data": {
    "id": "pc_registration_001",
    "person_id": "pc_person_001",
    "event_id": "pc_event_001",
    "status": "registered",
    "registration_date": "2024-01-10T09:00:00",
    "notes": "First time attendee",
    "created_at": "2024-01-10T09:00:00",
    "updated_at": "2024-01-10T09:00:00"
  }
}
```

#### `PUT /registrations/{registration_id}`
Update an existing registration.

**Request Body:**
```json
{
  "status": "cancelled",
  "notes": "Cancelled due to conflict"
}
```

**Response:**
```json
{
  "data": {
    "id": "pc_registration_001",
    "person_id": "pc_person_001",
    "event_id": "pc_event_001",
    "status": "cancelled",
    "registration_date": "2024-01-10T09:00:00",
    "notes": "Cancelled due to conflict",
    "created_at": "2024-01-10T09:00:00",
    "updated_at": "2024-01-10T10:00:00"
  }
}
```

#### `DELETE /registrations/{registration_id}`
Delete a registration.

**Response:**
```json
{
  "success": true,
  "message": "Registration deleted successfully"
}
```

### **Mock Data Management**

#### `GET /mock-data/summary`
Get a summary of mock data for debugging.

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_people": 50,
    "total_events": 20,
    "total_registrations": 150,
    "active_people": 45,
    "upcoming_events": 12,
    "recent_registrations": 25
  }
}
```

#### `GET /mock-data/reset`
Reset mock data to initial state.

**Response:**
```json
{
  "status": "success",
  "message": "Mock data reset successfully",
  "data": {
    "total_people": 50,
    "total_events": 20,
    "total_registrations": 150,
    "active_people": 45,
    "upcoming_events": 12,
    "recent_registrations": 25
  }
}
```

## 🎯 **Mock Data Characteristics**

### **People Data**
- **Total**: 50 people
- **Names**: Realistic first and last names
- **Contact Info**: Generated email addresses and phone numbers
- **Addresses**: Various addresses across different states
- **Status**: Mix of active, inactive, and pending
- **Households**: 20 different household groups

### **Events Data**
- **Total**: 20 events
- **Types**: Sunday Service, Bible Study, Youth Group, etc.
- **Timing**: Mix of past, present, and future events
- **Capacity**: 20-200 people per event
- **Locations**: Various church locations

### **Registrations Data**
- **Total**: ~150 registrations
- **Distribution**: First 10 events have registrations
- **Status**: Mix of registered, waitlisted, and cancelled
- **Timing**: Recent registrations within the last 30 days

## 🔧 **Integration with Sync Service**

The sync service automatically uses mock data when:
- `ENVIRONMENT=development`
- Planning Center credentials are not configured
- `PLANNING_CENTER_APP_ID` or `PLANNING_CENTER_SECRET` is missing

## 🧪 **Testing the Mock API**

### **Using curl:**
```bash
# Test connection
curl http://localhost:8000/api/v1/mock-planning-center/test-connection

# Get people
curl http://localhost:8000/api/v1/mock-planning-center/people

# Get events
curl http://localhost:8000/api/v1/mock-planning-center/events

# Get specific person
curl http://localhost:8000/api/v1/mock-planning-center/people/pc_person_001
```

### **Using the API Documentation:**
Visit `http://localhost:8000/docs` and look for the "mock-planning-center" section.

## 🚀 **Benefits of Mock API**

1. **Development**: Develop without Planning Center credentials
2. **Testing**: Consistent test data for automated tests
3. **Demo**: Show functionality without real data
4. **Offline**: Work without internet connection
5. **Performance**: Fast responses for development

## 🔄 **Switching to Real API**

When you're ready to use the real Planning Center API:

1. Set `ENVIRONMENT=production`
2. Configure `PLANNING_CENTER_APP_ID` and `PLANNING_CENTER_SECRET`
3. The sync service will automatically switch to real API calls

## 📝 **Notes**

- Mock data is generated fresh on each application restart
- All timestamps are realistic and recent
- Data relationships are maintained (people belong to households, registrations link people to events)
- Error responses match Planning Center API error formats
- Pagination works the same as the real API
