# Starting the Backend Server

## ⚠️ Issue Found

The server currently running on `localhost:8000` is serving **documentation (mkdocs)**, not the **FastAPI backend**. That's why you're getting HTML 404 pages instead of JSON responses.

## ✅ Solution: Start the FastAPI Backend Server

### Step 1: Stop any existing server on port 8000

If something is already running, stop it first:
```bash
# Find what's running on port 8000
lsof -ti:8000 | xargs kill -9

# Or check what's running
ps aux | grep -E "uvicorn|python.*main|mkdocs" | grep -v grep
```

### Step 2: Start the FastAPI Backend Server

```bash
cd backend
source venv_new/bin/activate
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 3: Verify FastAPI is Running

Open in browser or curl:
```bash
# Check FastAPI docs (should show Swagger UI, not mkdocs)
curl http://localhost:8000/docs
```

You should see FastAPI's Swagger documentation, not the mkdocs HTML.

### Step 4: Test Planning Center Endpoint

Once FastAPI is running, test the endpoint:
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

## 🔍 How to Tell Which Server is Running

### FastAPI Backend (Correct)
- **`/docs`** shows Swagger UI with API endpoints
- **`/api/v1/planning-center/test-connection`** returns JSON
- Server logs show: `Uvicorn running on...`

### MkDocs Documentation (Wrong for API testing)
- **`/docs`** shows mkdocs HTML documentation
- **`/api/v1/...`** returns HTML 404 page
- Server logs show: `mkdocs serve...` or similar

---

## 📝 Quick Test Script

Once the FastAPI server is running, use the test script:
```bash
./scripts/QUICK_TEST.sh
```

This should now work and return JSON responses!

---

*Make sure you're running `uvicorn main:app`, not `mkdocs serve`!*

