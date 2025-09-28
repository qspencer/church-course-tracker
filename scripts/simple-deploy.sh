#!/bin/bash

# Simple Deployment Script (without Terraform/Docker for now)
set -e

echo "🚀 Simple Deployment for Church Course Tracker"
echo "=============================================="
echo ""

# Configuration
DOMAIN_NAME="apps.eastgate.church"
AWS_REGION="us-east-1"
APP_NAME="church-course-tracker"

echo "📋 Configuration:"
echo "   Domain: $DOMAIN_NAME"
echo "   AWS Region: $AWS_REGION"
echo "   Environment: development"
echo ""

# Check AWS CLI
echo "🔍 Checking AWS CLI..."
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please run: ./scripts/configure-aws.sh"
    exit 1
fi

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured."
    echo "Please run: ./scripts/configure-aws.sh"
    exit 1
fi

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ AWS credentials configured for account: $AWS_ACCOUNT_ID"

# Create development environment file
echo "📝 Creating development environment configuration..."
cat > backend/.env.development << EOF
# Development Environment Configuration
APP_NAME="Church Course Tracker"
ENVIRONMENT="development"
DEBUG=true
SECRET_KEY="$(openssl rand -base64 32 2>/dev/null || echo "dev-secret-key-$(date +%s)")"

# Database (SQLite for development)
DATABASE_URL="sqlite:///./data/church_course_tracker.db"

# Mock Planning Center API (for development)
USE_MOCK_PLANNING_CENTER=true
PLANNING_CENTER_APP_ID=""
PLANNING_CENTER_SECRET=""

# AWS Configuration (minimal for development)
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_S3_BUCKET=""
AWS_REGION="$AWS_REGION"

# CORS for development
ALLOWED_ORIGINS="https://$DOMAIN_NAME,http://localhost:4200,http://localhost:3000"

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
echo "🎉 Development deployment completed successfully!"
echo "=============================================="
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
echo "✅ Development environment is ready!"

# Keep the script running
echo "Press Ctrl+C to stop all servers"
wait
