# Planning Center Integration Setup Guide

## Overview

This guide explains how to configure and test the Planning Center integration with the provided credentials.

---

## ✅ **Credentials Configured**

**Planning Center Client ID**: `[CONFIGURED]`  
**Planning Center Secret**: `[CONFIGURED]`

**Note**: These credentials are stored in `backend/.env` (not committed to git).

---

## 📋 **Configuration Steps**

### Step 1: Environment Variables

The credentials are stored in `backend/.env`:

```env
# Planning Center API
PLANNING_CENTER_API_URL="https://api.planningcenteronline.com"
PLANNING_CENTER_APP_ID="[CONFIGURED]"
PLANNING_CENTER_SECRET="[CONFIGURED]"
USE_MOCK_PLANNING_CENTER=false
```

**Important**: 
- ✅ `.env` file is in `.gitignore` - credentials won't be committed
- ✅ `USE_MOCK_PLANNING_CENTER=false` - using real API

### Step 2: Verify Configuration

Check that credentials are loaded:

```bash
cd backend
source venv_new/bin/activate
python3 -c "
from app.core.config import settings
print(f'App ID: {\"SET\" if settings.PLANNING_CENTER_APP_ID else \"NOT SET\"}')
print(f'Secret: {\"SET\" if settings.PLANNING_CENTER_SECRET else \"NOT SET\"}')
print(f'Use Mock: {settings.USE_MOCK_PLANNING_CENTER}')
"
```

---

## 🧪 **Testing the Connection**

### Option 1: Use Test Script

```bash
cd backend
source venv_new/bin/activate
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"
python3 scripts/test_planning_center_connection.py
```

**Expected Output**:
- ✅ Connection successful!
- ✅ Total people in Planning Center: [number]

### Option 2: Use API Endpoint

Start the backend server and test via API:

```bash
cd backend
source venv_new/bin/activate
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"
uvicorn main:app --reload
```

Then test the connection endpoint:

```bash
curl http://localhost:8000/api/v1/planning-center/test-connection
```

**Expected Response**:
```json
{
  "status": "success",
  "message": "Successfully connected to Planning Center API",
  "connected": true
}
```

### Option 3: Test via Python

```python
from app.services.planning_center_sync_service import PlanningCenterSyncService
from app.core.database import SessionLocal

db = SessionLocal()
service = PlanningCenterSyncService(db)

# Test connection
try:
    headers = service._get_auth_headers()
    print("✅ Credentials configured correctly")
    print(f"Authorization header: {headers['Authorization'][:30]}...")
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## 🔧 **Authentication Method**

Planning Center uses **HTTP Basic Authentication** with Personal Access Tokens:

1. **Format**: `{APP_ID}:{SECRET}`
2. **Encoding**: Base64 encoded
3. **Header**: `Authorization: Basic {encoded_credentials}`

**Example**:
```
APP_ID: [CONFIGURED]
SECRET: [CONFIGURED]
```

The service automatically encodes these credentials when making API calls.

---

## 📚 **Available API Endpoints**

### Connection Testing
- **GET** `/api/v1/planning-center/test-connection` - Test API connection

### People Sync
- **POST** `/api/v1/planning-center/people` - Start sync of people
- **GET** `/api/v1/planning-center/tasks` - List sync tasks
- **GET** `/api/v1/planning-center/tasks/{task_id}` - Get task status

### Events Sync
- **POST** `/api/v1/planning-center/events` - Start sync of events

### Registrations Sync
- **POST** `/api/v1/planning-center/registrations` - Start sync of registrations

### Full Sync
- **POST** `/api/v1/planning-center/all` - Start full sync (people, events, registrations)

---

## 🔍 **Troubleshooting**

### Issue 1: "Planning Center credentials not configured"

**Solution**:
- Verify `.env` file exists in `backend/` directory
- Check `PLANNING_CENTER_APP_ID` and `PLANNING_CENTER_SECRET` are set
- Restart the server after updating `.env`

### Issue 2: "Connection failed: 401 Unauthorized"

**Possible Causes**:
- Invalid credentials
- Expired Personal Access Token
- Incorrect encoding

**Solution**:
- Verify credentials in Planning Center
- Check token hasn't expired
- Verify credentials are set correctly in `.env`

### Issue 3: "Connection failed: 403 Forbidden"

**Possible Causes**:
- Token doesn't have required permissions
- API endpoint access restricted

**Solution**:
- Check token permissions in Planning Center
- Verify token has access to People, Events, and Registrations APIs

### Issue 4: Using Mock API Instead of Real API

**Solution**:
- Set `USE_MOCK_PLANNING_CENTER=false` in `.env`
- Restart server
- Verify with connection test

---

## 🔒 **Security Notes**

### Credential Storage

- ✅ **Local Development**: Credentials stored in `backend/.env` (not committed)
- ✅ **Production**: Store credentials in environment variables or AWS Secrets Manager
- ✅ **Never Commit**: `.env` is in `.gitignore` - credentials won't be committed to git

### Credential Rotation

If credentials need to be rotated:

1. Update `backend/.env` with new credentials
2. Restart the backend server
3. Test connection with `/api/v1/planning-center/test-connection`
4. Update production environment variables (if applicable)

---

## 📝 **Next Steps**

### Immediate Actions

1. **Test Connection**
   ```bash
   cd backend
   source venv_new/bin/activate
   python3 scripts/test_planning_center_connection.py
   ```

2. **Start Backend Server**
   ```bash
   uvicorn main:app --reload
   ```

3. **Test via API**
   ```bash
   curl http://localhost:8000/api/v1/planning-center/test-connection
   ```

### Short-Term Actions

1. **Sync People**
   - Test syncing people from Planning Center
   - Verify people are imported correctly

2. **Sync Events**
   - Test syncing events from Planning Center
   - Verify events are converted to Course Instances

3. **Sync Registrations**
   - Test bulk enrollment from Planning Center events
   - Verify enrollments are created correctly

### Long-Term Actions

1. **Automated Sync Jobs**
   - Set up periodic sync jobs
   - Monitor sync status

2. **Campus Sync**
   - Implement campus syncing from Planning Center
   - Update campus assignments

3. **Webhook Integration**
   - Set up Planning Center webhooks
   - Real-time updates when data changes

---

## ✅ **Status**

- ✅ Credentials configured in `.env`
- ✅ `USE_MOCK_PLANNING_CENTER=false` set
- ✅ Test script created
- ⏭️ Ready for connection testing

---

*Setup Date: January 2025*  
*Status: ✅ CONFIGURED - Ready for Testing*

