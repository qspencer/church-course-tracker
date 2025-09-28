#!/bin/bash

# Database Migration Script for Church Course Tracker
set -e

echo "🗄️ Migrating database from SQLite to PostgreSQL..."

# Check if required tools are installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL client (psql) is not installed."
    echo "📖 Install with: sudo apt-get install postgresql-client"
    exit 1
fi

# Get database connection details from Terraform output
cd infrastructure
DATABASE_ENDPOINT=$(terraform output -raw database_endpoint)
DATABASE_PORT=$(terraform output -raw database_port)
cd ..

# Database connection details
DB_HOST=$(echo $DATABASE_ENDPOINT | cut -d: -f1)
DB_PORT=$DATABASE_PORT
DB_NAME="church_course_tracker"
DB_USER="postgres"

echo "🔗 Connecting to database: $DB_HOST:$DB_PORT"

# Prompt for database password
read -s -p "Enter database password: " DB_PASSWORD
echo ""

# Set PGPASSWORD environment variable
export PGPASSWORD=$DB_PASSWORD

# Test database connection
echo "🔍 Testing database connection..."
if ! psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT 1;" &> /dev/null; then
    echo "❌ Cannot connect to database. Please check your credentials."
    exit 1
fi

echo "✅ Database connection successful!"

# Create database if it doesn't exist
echo "📝 Creating database if it doesn't exist..."
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "Database already exists."

# Set environment variables for migration
export DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"

# Navigate to backend directory
cd backend

# Install PostgreSQL dependencies
echo "📦 Installing PostgreSQL dependencies..."
pip install psycopg2-binary

# Run Alembic migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Create default admin user
echo "👤 Creating default admin user..."
python create_default_admin.py

echo "✅ Database migration completed successfully!"
echo ""
echo "🔐 Default admin credentials:"
echo "   Username: Admin"
echo "   Email: course.tracker.admin@eastgate.church"
echo "   Password: Matthew778*"
echo ""
echo "⚠️  Please change the default password after first login!"
