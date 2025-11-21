# Planning Center Route Testing - Issue Found

## Issue

The endpoint `/api/v1/planning-center/test-connection` is returning a 404 HTML page instead of JSON. This suggests:

1. **Route not registered**: The planning center router might not be registered correctly
2. **Wrong server**: A documentation server (mkdocs) might be running instead of the FastAPI app
3. **Routing conflict**: There might be a routing conflict

## Solution

The Planning Center routes are registered in `backend/app/api/v1/api.py`:

```python
# Planning Center integration endpoints
api_router.include_router(
    planning_center_sync.router, prefix="/planning-center", tags=["planning-center"]
)
```

The endpoint should be available at:
- `GET /api/v1/planning-center/test-connection`

## Testing

Make sure you're running the **FastAPI backend server**, not the documentation server:

```bash
cd backend
source venv_new/bin/activate
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"
uvicorn main:app --reload
```

Then test:
```bash
curl http://localhost:8000/api/v1/planning-center/test-connection
```

Or check the FastAPI docs:
```bash
curl http://localhost:8000/docs
```

If you see the FastAPI Swagger documentation, the server is running correctly.

