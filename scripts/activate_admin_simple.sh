#!/bin/bash
# Simple script to activate Admin user using psql

DB_HOST="church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com"
DB_NAME="church_course_tracker"
DB_USER="postgres"
DB_PASS="church_course_tracker_password"

echo "🔧 Activating Admin user in AWS PostgreSQL database..."

# Try using psql if available
if command -v psql &> /dev/null; then
    PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "UPDATE users SET is_active = true WHERE username = 'Admin';" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Admin user activated successfully!"
        
        # Verify
        PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT username, email, role, is_active FROM users WHERE username = 'Admin';" 2>&1
        
        echo ""
        echo "🧪 Testing login..."
        sleep 2
        
        curl -X POST 'https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/auth/login' \
             -H 'Content-Type: application/json' \
             -d '{"username":"Admin","password":"Admin123!"}' \
             2>/dev/null | python3 -m json.tool 2>/dev/null || echo "Login test completed"
    else
        echo "❌ Failed to activate Admin user"
        exit 1
    fi
else
    echo "❌ psql not found. Please install PostgreSQL client or use Python script."
    echo "   Alternatively, run: python3 scripts/update_aws_admin_user.py"
    exit 1
fi
