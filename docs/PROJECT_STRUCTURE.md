# Project Structure

## Directory Organization

This project follows a clean directory structure for better organization and maintainability.

---

## 📁 **Root Directory**

The root directory contains only essential project files:
- `README.md` - Main project documentation
- Configuration files (`.gitignore`, `package.json`, etc.)
- Infrastructure files (`docker-compose.yml`, etc.)

---

## 📁 **Scripts Directory** (`scripts/`)

All executable scripts are located in the `scripts/` subdirectory:

### Shell Scripts
- `QUICK_TEST.sh` - Quick test script for Planning Center integration
- `backend-start.sh` - Start backend server
- `deploy-frontend.sh` - Deploy frontend to AWS
- `deploy-aws.sh` - Deploy to AWS
- `setup-dev.sh` - Development environment setup
- `migrate-database.sh` - Run database migrations
- And more...

### Python Scripts
- `create_admin_user.py` - Create admin users
- `health_check.py` - Health check utilities
- `test-mock-api.py` - Test mock API
- And more...

**Usage:**
```bash
# Run scripts from project root
./scripts/QUICK_TEST.sh
./scripts/backend-start.sh
```

---

## 📁 **Documentation Directory** (`docs/`)

All project documentation is located in the `docs/` subdirectory:

### Main Documentation
- `GETTING_STARTED.md` - Getting started guide
- `USER_GUIDE.md` - User guide
- `FEATURES.md` - Features overview
- `PROJECT_PLAN_HTML_DOCUMENTATION.md` - Project plan

### Status and Progress Documents
- `CURRENT_STATUS_AND_NEXT_STEPS.md` - Current status
- `IMPLEMENTATION_PROGRESS.md` - Implementation progress
- `TEST_RESULTS_SUMMARY.md` - Test results
- And more...

### Planning Center Integration
- `PLANNING_CENTER_INTEGRATION_SETUP.md` - Setup guide
- `PLANNING_CENTER_QUICK_START.md` - Quick start
- `PLANNING_CENTER_TEST_RESULTS.md` - Test results
- `LOCAL_TESTING_GUIDE.md` - Local testing guide
- `START_SERVER.md` - Server startup guide

### Images
- `docs/images/` - Project images, screenshots, and diagrams
  - Debug screenshots
  - Test result images
  - Documentation diagrams

### Archive
- `docs/archive/` - Historical documentation and archived files

**Note:** `README.md` remains in the root directory as the main project entry point.

---

## 📁 **Other Directories**

### Backend (`backend/`)
- Application code
- Database migrations
- Tests
- Backend-specific scripts in `backend/scripts/`

### Frontend (`frontend/`)
- Angular application
- Frontend-specific configuration

### Infrastructure (`infrastructure/`)
- Terraform configurations
- Infrastructure documentation

### Tests (`tests/`)
- End-to-end tests
- Test results and reports

---

## 📝 **File Naming Conventions**

### Scripts
- Shell scripts: `*.sh`
- Python scripts: `*.py`
- All in `scripts/` directory

### Documentation
- Markdown files: `*.md`
- All in `docs/` directory (except `README.md`)

---

## 🔄 **Recent Changes**

All scripts and documentation have been reorganized:
- ✅ All scripts moved to `scripts/`
- ✅ All documentation moved to `docs/` (except `README.md`)
- ✅ Project structure is now cleaner and more organized

---

*Last Updated: January 2025*

