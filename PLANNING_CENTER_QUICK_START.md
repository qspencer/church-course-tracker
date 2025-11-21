# Planning Center Integration - Quick Start

## ✅ **Credentials Configured**

Planning Center credentials have been set in `backend/.env`:
- **App ID**: `2cb1d73153fd0ec7e5cfb4580b5334d541831d67911bbbd826d0bb4251acff8d`
- **Secret**: Personal Access Token (configured)
- **Use Mock**: `false` (using real API)

---

## 🧪 **Quick Test**

### Test Connection

```bash
cd backend
source venv_new/bin/activate
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"

# Test connection
python3 scripts/test_planning_center_connection.py
```

**Expected**: ✅ Connection successful!

### Test via API

```bash
# Start server
uvicorn main:app --reload

# Test endpoint
curl http://localhost:8000/api/v1/planning-center/test-connection
```

---

## 📋 **Available Endpoints**

- **GET** `/api/v1/planning-center/test-connection` - Test API connection
- **POST** `/api/v1/planning-center/people` - Sync people
- **POST** `/api/v1/planning-center/events` - Sync events
- **POST** `/api/v1/planning-center/all` - Full sync

---

## 🔒 **Security**

- ✅ Credentials in `.env` (not committed to git)
- ✅ `.env` is in `.gitignore`
- ✅ Never commit credentials to repository

---

*Status: ✅ Configured - Ready for Testing*

