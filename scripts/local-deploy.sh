#!/bin/bash

# Local Development Deployment Script (no AWS required)
set -e

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
echo ""

# Create development environment file
echo "📝 Creating development environment configuration..."
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
cat > frontend/church-course-tracker/src/environments/environment.dev.ts << EOF
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  appName: 'Church Course Tracker',
  version: '1.0.0',
  enableAnalytics: false,
  enableErrorReporting: false,
  logLevel: 'debug'
};
EOF

echo "✅ Frontend development environment created!"

# Start the backend server
echo "🚀 Starting backend server..."
cd backend
source venv/bin/activate

# Run database migrations
echo "🗄️ Running database migrations..."
python -c "
import sys
sys.path.append('.')
from app.core.database import SessionLocal, Base
from app.models import *
Base.metadata.create_all(bind=SessionLocal().bind)
print('✅ Database tables created')
"

# Create default admin user
echo "👤 Creating default admin user..."
python create_default_admin.py

echo "✅ Default admin user created!"

# Start the backend server in background
echo "🌐 Starting backend server on port 8000..."
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

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

# Start the frontend server
echo "🌐 Starting frontend server..."
cd ../frontend/church-course-tracker

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend server
echo "🚀 Starting frontend server on port 4200..."
npm start &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Test frontend
echo "🧪 Testing frontend..."
if curl -f http://localhost:4200 &> /dev/null; then
    echo "✅ Frontend is running successfully!"
else
    echo "❌ Frontend failed to start"
    exit 1
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
echo "   kill $BACKEND_PID $FRONTEND_PID"
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
