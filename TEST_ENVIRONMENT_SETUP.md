# Testing Environment Setup Guide

## Overview

This guide explains what needs to be done to get the testing environment ready for running automated tests for Phase 2 and Phase 3 features.

---

## Current Status

### ✅ What's Already Configured

1. **Test Dependencies**: Listed in `backend/requirements.txt`
   - ✅ pytest==7.4.3
   - ✅ pytest-asyncio==0.21.1
   - ✅ pytest-cov==4.1.0
   - ✅ All required testing libraries

2. **Test Configuration**: `backend/pytest.ini` configured
   - ✅ Test paths defined
   - ✅ Markers configured
   - ✅ Output formatting configured

3. **Test Fixtures**: `backend/tests/conftest.py` ready
   - ✅ Database setup
   - ✅ Test client configuration
   - ✅ Fixtures for models
   - ✅ Auto-migration attempt

4. **Test Files**: Tests created
   - ✅ `backend/tests/test_course_instances.py` (38 test cases)
   - ✅ Existing test files for other features

5. **Database Schema**: Verified
   - ✅ All tables exist
   - ✅ Migrations ready

### ⚠️ What Needs to Be Set Up

1. **Virtual Environment**: Activate and install dependencies
2. **Alembic**: Ensure migrations can run
3. **Test Database**: Ensure test database is properly initialized
4. **Environment Variables**: Set up for testing

---

## Step-by-Step Setup

### Step 1: Activate Virtual Environment

The project has multiple virtual environments. Choose one:

**Option A: Use existing `venv_new` (recommended)**
```bash
cd backend
source venv_new/bin/activate
```

**Option B: Use existing `venv`**
```bash
cd backend
source venv/bin/activate
```

**Option C: Create new virtual environment**
```bash
cd backend
python3 -m venv venv_test
source venv_test/bin/activate
```

### Step 2: Install Dependencies

Install all required packages including testing dependencies:

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

**Verify installation:**
```bash
# Check pytest is installed
pytest --version

# Check alembic is installed
alembic --version

# Check other key dependencies
python -c "import pytest, alembic, sqlalchemy, fastapi; print('All dependencies installed')"
```

### Step 3: Set Up Test Database

The test database is automatically created by `conftest.py`, but we can verify:

```bash
cd backend

# Ensure data directory exists
mkdir -p data

# Verify database exists or will be created
ls -la data/church_course_tracker.db

# If needed, create tables directly (alternative to migrations)
python -c "
from app.core.database import Base, engine
from app.models import *
Base.metadata.create_all(bind=engine)
print('✅ Tables created')
"
```

### Step 4: Run Migrations (If Needed)

The tests try to run migrations automatically, but you can run them manually:

```bash
cd backend

# Set DATABASE_URL for SQLite
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"

# Run migrations
alembic upgrade head
```

**If alembic command not found in PATH:**
```bash
# Use Python module instead
python -m alembic upgrade head
```

### Step 5: Verify Test Environment

Run a simple test to verify everything works:

```bash
cd backend

# Run a simple test
pytest tests/test_simple.py -v

# Or test the new course instances tests
pytest tests/test_course_instances.py::TestCourseInstancesEndpoints::test_get_course_instances_empty -v
```

---

## Troubleshooting Common Issues

### Issue 1: "ModuleNotFoundError: No module named 'pytest'"

**Solution:**
```bash
cd backend
source venv_new/bin/activate  # Or your chosen venv
pip install pytest pytest-asyncio pytest-cov
```

### Issue 2: "alembic: command not found"

**Solution:**
```bash
# Option A: Install alembic
pip install alembic

# Option B: Use Python module
python -m alembic upgrade head
```

### Issue 3: "Migration failed" in conftest.py

**Solution:**
The conftest.py has a fallback that creates tables directly. This is acceptable for testing. To fix migrations:

```bash
cd backend
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"

# Check current migration state
python -m alembic current

# Upgrade to head
python -m alembic upgrade head

# If multiple heads issue
python -m alembic merge heads -m "merge heads"
python -m alembic upgrade head
```

### Issue 4: "Database is locked" (SQLite)

**Solution:**
```bash
# Check if database file is locked
lsof data/church_course_tracker.db

# Close any processes using it
# Or use a fresh test database
rm data/church_course_tracker.db
# Tests will recreate it
```

### Issue 5: Import Errors

**Solution:**
```bash
cd backend
# Ensure PYTHONPATH includes backend directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install in editable mode
pip install -e .
```

---

## Automated Setup Script

Create a setup script to automate the process:

```bash
#!/bin/bash
# setup-test-env.sh

set -e

echo "🧪 Setting up Testing Environment"
echo "================================"

cd backend

# Activate virtual environment
if [ -d "venv_new" ]; then
    echo "📦 Activating venv_new..."
    source venv_new/bin/activate
elif [ -d "venv" ]; then
    echo "📦 Activating venv..."
    source venv/bin/activate
else
    echo "📦 Creating new virtual environment..."
    python3 -m venv venv_test
    source venv_test/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set up database
echo "🗄️  Setting up test database..."
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"
mkdir -p data

# Run migrations
echo "🔄 Running migrations..."
python -m alembic upgrade head || {
    echo "⚠️  Migrations failed, creating tables directly..."
    python -c "
from app.core.database import Base, engine
from app.models import *
Base.metadata.create_all(bind=engine)
print('✅ Tables created')
"
}

# Verify installation
echo "✅ Verifying installation..."
pytest --version
python -m alembic --version

echo ""
echo "✅ Testing environment setup complete!"
echo ""
echo "Run tests with:"
echo "  pytest tests/test_course_instances.py -v"
```

---

## Running Tests

### Run All Tests
```bash
cd backend
source venv_new/bin/activate  # Or your venv
pytest tests/ -v
```

### Run Course Instances Tests Only
```bash
cd backend
source venv_new/bin/activate
pytest tests/test_course_instances.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_course_instances.py::TestCourseInstancesEndpoints -v
```

### Run Single Test
```bash
pytest tests/test_course_instances.py::TestCourseInstancesEndpoints::test_get_course_instances_empty -v
```

### Run with Coverage
```bash
pytest tests/test_course_instances.py --cov=app.services.course_instance_service --cov=app.api.v1.endpoints.course_instances -v
```

### Run with Output
```bash
pytest tests/test_course_instances.py -v -s
```

---

## Quick Start Checklist

- [ ] Navigate to backend directory: `cd backend`
- [ ] Activate virtual environment: `source venv_new/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify pytest: `pytest --version`
- [ ] Verify alembic: `python -m alembic --version`
- [ ] Set DATABASE_URL: `export DATABASE_URL="sqlite:///./data/church_course_tracker.db"`
- [ ] Ensure data directory exists: `mkdir -p data`
- [ ] Run migrations: `python -m alembic upgrade head`
- [ ] Run test: `pytest tests/test_course_instances.py::TestCourseInstancesEndpoints::test_get_course_instances_empty -v`

---

## Environment Variables for Testing

The `conftest.py` automatically sets these, but you can set them manually:

```bash
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"
export RATE_LIMIT_ENABLED="false"
export PLANNING_CENTER_APP_ID="test_app_id"
export PLANNING_CENTER_SECRET="test_secret"
export PLANNING_CENTER_ACCESS_TOKEN="test_token"
```

---

## Alternative: Use Docker

If you prefer using Docker:

```bash
# Build and run tests in Docker container
docker-compose -f docker/docker-compose.dev.yml run --rm backend pytest tests/test_course_instances.py -v
```

---

## Summary

**Minimum Requirements:**
1. ✅ Python 3.11+
2. ✅ Virtual environment activated
3. ✅ Dependencies installed (`pip install -r requirements.txt`)
4. ✅ Test database accessible
5. ✅ Migrations run (or tables created directly)

**Quick Setup (5 minutes):**
```bash
cd backend
source venv_new/bin/activate
pip install -r requirements.txt
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"
pytest tests/test_course_instances.py -v
```

---

*Last Updated: January 2025*  
*Status: Ready for testing setup*

