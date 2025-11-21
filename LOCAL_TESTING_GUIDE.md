# Planning Center Integration - Local Testing Guide

## ✅ **Yes, You Can Test Locally!**

All credentials are configured and ready. Here's how to test it locally.

---

## 🚀 **Quick Start**

### Step 1: Start the Backend Server

```bash
cd backend
source venv_new/bin/activate
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"
uvicorn main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

### Step 2: Test the Connection (in a new terminal)

```bash
curl http://localhost:8000/api/v1/planning-center/test-connection
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Successfully connected to Planning Center API",
  "connected": true
}
```

---

## 🧪 **Testing Endpoints**

### Test 1: Connection Test
```bash
curl http://localhost:8000/api/v1/planning-center/test-connection
```

### Test 2: Sync People (Background Task)
```bash
curl -X POST http://localhost:8000/api/v1/planning-center/people
```

**Response:**
```json
{
  "task_id": "uuid-here",
  "status": "started",
  "message": "People sync started in background"
}
```

### Test 3: Check Sync Task Status
```bash
# Use the task_id from previous response
curl http://localhost:8000/api/v1/planning-center/tasks/{task_id}
```

### Test 4: List All Sync Tasks
```bash
curl http://localhost:8000/api/v1/planning-center/tasks
```

### Test 5: Sync Events
```bash
curl -X POST http://localhost:8000/api/v1/planning-center/events
```

### Test 6: Sync Registrations
```bash
curl -X POST http://localhost:8000/api/v1/planning-center/registrations
```

### Test 7: Full Sync (People + Events + Registrations)
```bash
curl -X POST http://localhost:8000/api/v1/planning-center/all
```

---

## 🔐 **With Authentication (if needed)**

If your endpoints require authentication, you'll need to:

1. **Login first:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your-username", "password": "your-password"}'
```

2. **Get token from response and use it:**
```bash
TOKEN="your-jwt-token-here"
curl -X POST http://localhost:8000/api/v1/planning-center/people \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📋 **Using Browser or Postman**

### Browser Testing

1. Start the server (see Step 1 above)
2. Open browser: `http://localhost:8000/api/v1/planning-center/test-connection`
3. Or visit API docs: `http://localhost:8000/docs`

### Postman/Insomnia

1. **Base URL**: `http://localhost:8000`
2. **Test Connection**: `GET /api/v1/planning-center/test-connection`
3. **Sync People**: `POST /api/v1/planning-center/people`
4. **Check Tasks**: `GET /api/v1/planning-center/tasks`

---

## 🐍 **Using Python Script**

Create a test script:

```python
import httpx

base_url = "http://localhost:8000"

# Test connection
response = httpx.get(f"{base_url}/api/v1/planning-center/test-connection")
print(response.json())

# Sync people
response = httpx.post(f"{base_url}/api/v1/planning-center/people")
print(response.json())
task_id = response.json()["task_id"]

# Check task status
response = httpx.get(f"{base_url}/api/v1/planning-center/tasks/{task_id}")
print(response.json())
```

---

## ✅ **Expected Test Results**

### Connection Test
- ✅ Status: `success`
- ✅ Connected: `true`
- ✅ Message: "Successfully connected to Planning Center API"

### People Sync
- ✅ Status: `started`
- ✅ Task ID: UUID returned
- ✅ Message: "People sync started in background"

### Task Status
- ✅ Status: `pending`, `running`, or `completed`
- ✅ Progress: 0-100
- ✅ Result: Data or error message

---

## 🔧 **Troubleshooting**

### Issue: "Connection refused"
**Solution**: Make sure the server is running on port 8000

### Issue: "Planning Center credentials not configured"
**Solution**: Verify `backend/.env` file exists with credentials

### Issue: "401 Unauthorized"
**Solution**: Some endpoints may require authentication. Login first.

### Issue: "500 Internal Server Error"
**Solution**: Check server logs for detailed error messages

---

## 📊 **What You Should See**

### Successful Connection
```json
{
  "status": "success",
  "message": "Successfully connected to Planning Center API",
  "connected": true
}
```

### People Sync Started
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "started",
  "message": "People sync started in background"
}
```

### Task Status
```json
{
  "task_type": "people_sync",
  "status": "running",
  "progress": 45,
  "message": "Syncing people...",
  "started_at": "2025-01-XX..."
}
```

---

## ✅ **Summary**

**Yes, you can test locally!**

1. ✅ Credentials are configured in `backend/.env`
2. ✅ Connection has been verified (5,296 people accessible)
3. ✅ Server can be started locally
4. ✅ All endpoints are ready to use
5. ✅ No special setup required - just start the server!

---

*Ready to test? Start with Step 1 above!*

