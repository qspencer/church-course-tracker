#!/bin/bash

# Local Development Deployment Script (no AWS required)
set -e

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

# Function to check backend compilation
check_backend_compilation() {
    echo "🔍 Checking backend compilation..."
    cd "$PROJECT_ROOT/backend"
    
    # Check if virtual environment exists
    if [ -d "venv_new" ]; then
        source venv_new/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Check main.py syntax
    if ! python3 -m py_compile main.py > /tmp/backend-compile.log 2>&1; then
        echo "❌ Backend compilation error: main.py has syntax errors"
        cat /tmp/backend-compile.log
        return 1
    fi
    
    # Check all Python files in app directory
    COMPILE_ERRORS=""
    ERROR_COUNT=0
    > /tmp/backend-compile.log  # Clear log file
    
    while IFS= read -r -d '' file; do
        if ! python3 -m py_compile "$file" >> /tmp/backend-compile.log 2>&1; then
            COMPILE_ERRORS="${COMPILE_ERRORS}  - ${file}\n"
            ERROR_COUNT=$((ERROR_COUNT + 1))
        fi
    done < <(find app -name "*.py" -type f -print0 2>/dev/null)
    
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "❌ Backend compilation errors found in $ERROR_COUNT file(s):"
        echo -e "$COMPILE_ERRORS"
        echo ""
        echo "💡 Full compilation output saved to /tmp/backend-compile.log"
        echo "   Last 30 lines of errors:"
        tail -30 /tmp/backend-compile.log | grep -v "^$" || true
        return 1
    fi
    
    echo "✅ Backend compilation check passed"
    return 0
}

# Function to check frontend compilation
check_frontend_compilation() {
    echo "🔍 Checking frontend compilation..."
    cd "$PROJECT_ROOT/frontend/church-course-tracker"
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies for compilation check..."
        npm install --silent > /dev/null 2>&1
    fi
    
    # Run a build to check for compilation errors
    # Use a timeout to prevent hanging
    echo "   Running build check (this may take a minute)..."
    BUILD_OUTPUT=$(timeout 180 npm run build 2>&1)
    BUILD_EXIT_CODE=$?
    
    # Save full output
    echo "$BUILD_OUTPUT" > /tmp/frontend-build-errors.log
    
    if [ $BUILD_EXIT_CODE -ne 0 ]; then
        echo "❌ Frontend compilation failed (exit code: $BUILD_EXIT_CODE)"
        echo ""
        echo "   Compilation errors found:"
        echo "$BUILD_OUTPUT" | grep -E "(Error:|error TS|error NG|Failed to compile)" | head -30
        echo ""
        echo "💡 Full build output saved to /tmp/frontend-build-errors.log"
        return 1
    fi
    
    # Check for any error messages in the output even if exit code is 0
    ERROR_COUNT=$(echo "$BUILD_OUTPUT" | grep -cE "(Error:|error TS|error NG|Failed to compile)" || echo "0")
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo "❌ Frontend compilation errors found in build output:"
        echo "$BUILD_OUTPUT" | grep -E "(Error:|error TS|error NG|Failed)" | head -30
        echo ""
        echo "💡 Full build output saved to /tmp/frontend-build-errors.log"
        return 1
    fi
    
    echo "✅ Frontend compilation check passed"
    return 0
}

echo "🚀 Local Development Deployment for Church Course Tracker"
echo "========================================================"
echo ""

# Configuration
DOMAIN_NAME="apps.eastgate.church"
APP_NAME="church-course-tracker"

echo "📋 Configuration:"
echo "   Domain: $DOMAIN_NAME (for future AWS deployment)"
echo "   Environment: development"
echo "   Mode: Local development (no AWS required)"
echo "   Project Root: $PROJECT_ROOT"
echo ""

# Create development environment file
echo "📝 Creating development environment configuration..."
mkdir -p backend
cat > backend/.env.development << EOF
# Development Environment Configuration
APP_NAME="Church Course Tracker"
ENVIRONMENT="development"
DEBUG=true
SECRET_KEY="dev-secret-key-$(date +%s)"

# Database (SQLite for development)
DATABASE_URL="sqlite:///./data/church_course_tracker.db"

# Mock Planning Center API (for development)
USE_MOCK_PLANNING_CENTER=true
PLANNING_CENTER_APP_ID=""
PLANNING_CENTER_SECRET=""

# AWS Configuration (not needed for local development)
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_S3_BUCKET=""
AWS_REGION="us-east-1"

# CORS for development
ALLOWED_ORIGINS="http://localhost:4200,http://localhost:3000,http://127.0.0.1:4200,http://127.0.0.1:3000"

# Logging
LOG_LEVEL="DEBUG"
EOF

echo "✅ Development environment configuration created!"

# Create frontend development environment
echo "📝 Creating frontend development environment..."

# Get version from environment.prod.ts to keep versions in sync
DEV_VERSION="0.01"
if [ -f "frontend/church-course-tracker/src/environments/environment.prod.ts" ]; then
    # Extract version from environment.prod.ts
    DEV_VERSION=$(grep -oP "version:\s*['\"]\K[^'\"]*" "frontend/church-course-tracker/src/environments/environment.prod.ts" 2>/dev/null || echo "0.01")
fi

cat > frontend/church-course-tracker/src/environments/environment.dev.ts << EOF
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  appName: 'Church Course Tracker',
  version: '$DEV_VERSION',
  enableAnalytics: false,
  enableErrorReporting: false,
  logLevel: 'debug'
};
EOF

echo "✅ Frontend development environment created! (version: $DEV_VERSION)"

# Check backend compilation before starting
if ! check_backend_compilation; then
    echo ""
    echo "❌ Backend compilation check failed. Aborting deployment."
    echo "   Please fix the compilation errors before running this script again."
    exit 1
fi

# Start the backend server
echo "🚀 Starting backend server..."
cd "$PROJECT_ROOT/backend"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ] && [ ! -d "venv_new" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Use venv_new if it exists, otherwise use venv
if [ -d "venv_new" ]; then
    source venv_new/bin/activate
else
    source venv/bin/activate
fi

# Install dependencies if needed
if [ ! -f ".deps_installed" ]; then
    echo "📦 Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch .deps_installed
fi

# Run database migrations with safeguards
echo "🗄️ Running database migrations..."

# Function to backup database before migrations
backup_database() {
    local db_path="$PROJECT_ROOT/backend/data/church_course_tracker.db"
    if [ -f "$db_path" ]; then
        local backup_path="${db_path}.backup.$(date +%Y%m%d_%H%M%S)"
        echo "💾 Creating database backup..."
        cp "$db_path" "$backup_path"
        echo "✅ Backup created: $backup_path"
        # Keep only last 5 backups
        ls -t "${db_path}.backup."* 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true
    fi
}

# Function to check if database has data
check_database_has_data() {
    local db_path="$PROJECT_ROOT/backend/data/church_course_tracker.db"
    if [ ! -f "$db_path" ]; then
        return 1  # Database doesn't exist
    fi
    
    # Check if database has any tables with data
    python3 -c "
import sqlite3
import sys
db_path = '$db_path'
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Check for any non-empty tables
    cursor.execute(\"\"\"
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version'
    \"\"\")
    tables = cursor.fetchall()
    has_data = False
    for (table_name,) in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        count = cursor.fetchone()[0]
        if count > 0:
            has_data = True
            break
    conn.close()
    sys.exit(0 if has_data else 1)
except Exception as e:
    sys.exit(1)
" 2>/dev/null
    return $?
}

# Ensure DATABASE_URL is set for migrations
# CRITICAL: Use relative path to ensure we're using the dev database, not test database
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"

# SAFEGUARD: Verify DATABASE_URL points to dev database, not test database
if echo "$DATABASE_URL" | grep -q "/tmp/"; then
    echo "❌ ERROR: DATABASE_URL points to /tmp/ (test database location)"
    echo "   This would cause data loss. Aborting."
    exit 1
fi

if echo "$DATABASE_URL" | grep -q "test"; then
    echo "❌ ERROR: DATABASE_URL contains 'test' - this might be the test database"
    echo "   This would cause data loss. Aborting."
    exit 1
fi

# Check if database exists and has data
if check_database_has_data; then
    echo "⚠️  Database contains data - creating backup before migrations..."
    backup_database
elif [ -f "$PROJECT_ROOT/backend/data/church_course_tracker.db" ]; then
    echo "ℹ️  Database exists but appears empty"
else
    echo "ℹ️  Database does not exist - will be created by migrations"
fi

# Run Alembic migrations
cd "$PROJECT_ROOT/backend"
if alembic upgrade head 2>&1 | tee /tmp/alembic-migration.log; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migrations failed!"
    echo "   Check /tmp/alembic-migration.log for details"
    if [ -f "$PROJECT_ROOT/backend/data/church_course_tracker.db.backup."* ]; then
        echo "💡 A backup was created before migrations - you can restore if needed"
    fi
    exit 1
fi

# Create default admin user
echo "👤 Creating default admin user..."
# Use the script from scripts directory - it's designed for local development
if [ -f "$PROJECT_ROOT/scripts/create_default_admin.py" ]; then
    # Run from backend directory so it can import app modules, with proper PYTHONPATH
    cd "$PROJECT_ROOT/backend"
    PYTHONPATH="$PROJECT_ROOT/backend:$PYTHONPATH" python "$PROJECT_ROOT/scripts/create_default_admin.py"
    ADMIN_EXIT_CODE=$?
    cd "$PROJECT_ROOT"
    if [ $ADMIN_EXIT_CODE -eq 0 ]; then
        echo "✅ Default admin user created or already exists!"
    else
        echo "⚠️  Admin user creation had issues, but continuing..."
    fi
else
    echo "⚠️  Admin creation script not found at $PROJECT_ROOT/scripts/create_default_admin.py"
    echo "   You can create an admin user manually later using:"
    echo "   python scripts/create_admin_user.py"
fi

# Check if port 8000 is already in use
if lsof -ti:8000 > /dev/null 2>&1; then
    EXISTING_BACKEND_PID=$(lsof -ti:8000 | head -1)
    echo "⚠️  Port 8000 is already in use (PID: $EXISTING_BACKEND_PID)"
    echo "   Using existing backend server..."
    BACKEND_PID=$EXISTING_BACKEND_PID
else
    # Start the backend server in background
    echo "🌐 Starting backend server on port 8000..."
    # Make sure we're in the backend directory and start uvicorn from there
    # Use a subshell to change directory and run uvicorn
    (
        cd "$PROJECT_ROOT/backend"
        # Activate venv if we're not already in it
        if [ -d "venv_new" ]; then
            source venv_new/bin/activate
        elif [ -d "venv" ]; then
            source venv/bin/activate
        fi
        python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ) &
    BACKEND_PID=$!
fi

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Test backend
echo "🧪 Testing backend..."
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ Backend is running successfully!"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Check frontend compilation before starting
if ! check_frontend_compilation; then
    echo ""
    echo "❌ Frontend compilation check failed. Aborting deployment."
    echo "   Please fix the compilation errors before running this script again."
    echo "   Check /tmp/frontend-build-errors.log for full details."
    exit 1
fi

# Start the frontend server
echo "🌐 Starting frontend server..."
# Change to frontend directory
cd "$PROJECT_ROOT/frontend/church-course-tracker"

# Check if port 4200 is already in use
if lsof -ti:4200 > /dev/null 2>&1; then
    EXISTING_FRONTEND_PID=$(lsof -ti:4200 | head -1)
    echo "⚠️  Port 4200 is already in use (PID: $EXISTING_FRONTEND_PID)"
    echo "   Using existing frontend server..."
    FRONTEND_PID=$EXISTING_FRONTEND_PID
else
    # Start frontend server
    echo "🚀 Starting frontend server on port 4200..."
    # Start frontend using helper script that handles the autocompletion prompt
    # Run in background and capture PID
    bash "$PROJECT_ROOT/scripts/start-frontend.sh" > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
fi

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Test frontend (give it more time and check the log)
echo "🧪 Testing frontend..."
sleep 5
# Check if ng serve process is running
if pgrep -f "ng serve" > /dev/null; then
    echo "✅ Frontend process is running!"
    # Give it a bit more time to fully start
    sleep 5
    if curl -f http://localhost:4200 &> /dev/null; then
        echo "✅ Frontend is accessible at http://localhost:4200"
    else
        echo "⚠️  Frontend process is running but not yet accessible"
        echo "   Check /tmp/frontend.log for details"
        echo "   It may still be starting up..."
    fi
else
    echo "❌ Frontend process failed to start"
    echo "   Check /tmp/frontend.log for error details:"
    tail -20 /tmp/frontend.log 2>/dev/null || echo "   (log file not found)"
    echo ""
    echo "💡 If you see an autocompletion prompt error, run this once manually:"
    echo "   cd frontend/church-course-tracker && npm start"
    echo "   Answer 'n' to the autocompletion prompt, then Ctrl+C"
    echo "   Then run this script again"
    # Don't exit - backend is running, user can start frontend manually
fi

echo ""
echo "🎉 Local development deployment completed successfully!"
echo "====================================================="
echo ""
echo "🔗 Your application is now running at:"
echo "   Frontend: http://localhost:4200"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "🔐 Default admin credentials:"
echo "   Username: Admin"
echo "   Email: course.tracker.admin@eastgate.church"
echo "   Password: Matthew778*"
echo ""
echo "📊 Mock Planning Center API:"
echo "   Test connection: http://localhost:8000/api/v1/mock-planning-center/test-connection"
echo "   Get people: http://localhost:8000/api/v1/mock-planning-center/people"
echo "   Get events: http://localhost:8000/api/v1/mock-planning-center/events"
echo ""
echo "🛑 To stop the servers:"
if [ -n "$BACKEND_PID" ]; then
    echo "   Backend PID: $BACKEND_PID"
fi
if [ -n "$FRONTEND_PID" ]; then
    echo "   Frontend PID: $FRONTEND_PID"
    echo "   kill $BACKEND_PID $FRONTEND_PID"
else
    echo "   pkill -f 'ng serve'  # to stop frontend"
    echo "   kill $BACKEND_PID    # to stop backend"
fi
echo ""
echo "✅ Local development environment is ready!"
echo ""
echo "📋 Next steps for AWS deployment:"
echo "   1. Configure AWS CLI: ./scripts/configure-aws.sh"
echo "   2. Install Terraform and Docker"
echo "   3. Run: ./scripts/setup-dev-deployment.sh"
echo ""
echo "Press Ctrl+C to stop all servers"
wait
