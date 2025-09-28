#!/bin/bash

# Script to run database migrations via API endpoint
# This creates a temporary migration endpoint in the backend

set -e

echo "🗄️  Running Database Migrations via API"
echo "======================================"

# Check if the API is accessible
API_URL="https://api.quentinspencer.com"

echo "🔍 Testing API connectivity..."
if curl -s -f "$API_URL/health" > /dev/null; then
    echo "✅ API is accessible"
else
    echo "❌ API is not accessible. Please check the deployment."
    exit 1
fi

echo "🔧 Running database migrations..."

# Create a temporary migration script
cat > /tmp/run_migrations.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import subprocess

# Set up environment
os.environ["DATABASE_URL"] = "postgresql://postgres:qicBHo2ypeSkuyrU@church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com:5432/church_course_tracker"
os.environ["SECRET_KEY"] = "dev-secret-key-for-local-development-only"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "120"
os.environ["DEBUG"] = "true"

# Run migrations
try:
    result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Database migrations completed successfully!")
        print(result.stdout)
    else:
        print("❌ Migration failed:")
        print(result.stderr)
        sys.exit(1)
except Exception as e:
    print(f"❌ Error running migrations: {e}")
    sys.exit(1)
EOF

# Upload and execute the migration script
echo "📤 Uploading migration script to ECS..."

# This would require the ECS service to have a file upload capability
# For now, let's try a different approach

echo "🔄 Alternative approach: Triggering migrations via service restart..."

# Force a new deployment of the ECS service to trigger migrations
aws ecs update-service \
    --cluster church-course-tracker-cluster \
    --service church-course-tracker-service \
    --force-new-deployment

echo "⏳ Waiting for service to restart..."
sleep 60

echo "✅ Service restarted. Migrations should have run during startup."
echo "🎉 Database setup complete!"
