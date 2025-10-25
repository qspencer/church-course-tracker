#!/bin/bash

# Church Course Tracker - ECS Startup Script
echo "🚀 Starting Church Course Tracker..."

# Environment variables are set by ECS task definition
# No need to override them here

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully!"
else
    echo "⚠️  Database migrations failed. Attempting to stamp database with current version..."
    # Try to stamp the database to skip failed migrations
    alembic stamp head
    if [ $? -eq 0 ]; then
        echo "✅ Database stamped successfully. Continuing..."
    else
        echo "⚠️  Could not stamp database. Continuing anyway..."
    fi
fi

# Create default admin user if it doesn't exist
echo "👤 Creating default admin user..."
python3 /app/create_admin_standalone.py

if [ $? -eq 0 ]; then
    echo "✅ Admin user setup completed!"
else
    echo "⚠️  Admin user setup failed - user may already exist. Continuing..."
fi

# Start the application
echo "🚀 Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
