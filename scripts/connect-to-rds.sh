#!/bin/bash

# Script to connect to AWS RDS database from local machine
# This script provides multiple connection methods

set -e

echo "🗄️  Church Course Tracker - RDS Connection Helper"
echo "==============================================="

# RDS endpoint
RDS_ENDPOINT="church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com"
RDS_PORT="5432"
DB_NAME="church_course_tracker"
DB_USER="postgres"

echo "📍 RDS Endpoint: $RDS_ENDPOINT"
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

echo "🔍 Checking RDS security group..."

# Find the RDS security group
RDS_SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=*rds*" \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null)

if [ "$RDS_SG_ID" = "None" ] || [ -z "$RDS_SG_ID" ]; then
    echo "⚠️  Could not find RDS security group automatically."
    echo "Please check your AWS deployment and ensure the RDS instance exists."
    exit 1
fi

echo "✅ Found RDS security group: $RDS_SG_ID"

# Get current public IP
CURRENT_IP=$(curl -s https://checkip.amazonaws.com)
echo "📍 Your current public IP: $CURRENT_IP"

echo ""
echo "🔧 Choose connection method:"
echo "1. Add your IP to security group (Quick but less secure)"
echo "2. Use AWS Systems Manager tunnel (More secure)"
echo "3. Check current security group rules"
echo "4. Test connection (if already configured)"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🔐 Adding your IP to RDS security group..."
        
        # Check if rule already exists
        EXISTING_RULE=$(aws ec2 describe-security-groups \
            --group-ids "$RDS_SG_ID" \
            --query "SecurityGroups[0].IpPermissions[?FromPort==\`5432\` && IpRanges[?CidrIp==\`$CURRENT_IP/32\`]]" \
            --output text 2>/dev/null)
        
        if [ -n "$EXISTING_RULE" ]; then
            echo "✅ Rule already exists for your IP"
        else
            aws ec2 authorize-security-group-ingress \
                --group-id "$RDS_SG_ID" \
                --protocol tcp \
                --port 5432 \
                --cidr "$CURRENT_IP/32"
            echo "✅ Added rule for your IP address"
        fi
        
        echo ""
        echo "🎉 You can now connect to the database!"
        echo "Connection string:"
        echo "  Host: $RDS_ENDPOINT"
        echo "  Port: $RDS_PORT"
        echo "  Database: $DB_NAME"
        echo "  Username: $DB_USER"
        echo "  Password: [your-db-password]"
        echo ""
        echo "⚠️  Remember to remove this rule when done for security!"
        ;;
        
    2)
        echo "🔐 Setting up secure tunnel via AWS Systems Manager..."
        echo "This method is more secure as it doesn't open the security group."
        echo ""
        echo "Starting tunnel (press Ctrl+C to stop)..."
        echo "The database will be available at localhost:5433"
        echo ""
        
        # Find ECS task
        TASK_ARN=$(aws ecs list-tasks \
            --cluster church-course-tracker-cluster \
            --service-name church-course-tracker-service \
            --query 'taskArns[0]' \
            --output text 2>/dev/null)
        
        if [ "$TASK_ARN" = "None" ] || [ -z "$TASK_ARN" ]; then
            echo "❌ No running ECS tasks found. Please ensure the service is running."
            exit 1
        fi
        
        # Get instance ID
        INSTANCE_ID=$(aws ecs describe-tasks \
            --cluster church-course-tracker-cluster \
            --tasks "$TASK_ARN" \
            --query 'tasks[0].containerInstanceArn' \
            --output text | cut -d'/' -f2)
        
        echo "✅ Found ECS instance: $INSTANCE_ID"
        echo "🔧 Starting port forwarding..."
        
        aws ssm start-session \
            --target "$INSTANCE_ID" \
            --document-name AWS-StartPortForwardingSessionToRemoteHost \
            --parameters "{\"host\":[\"$RDS_ENDPOINT\"],\"portNumber\":[\"$RDS_PORT\"],\"localPortNumber\":[\"5433\"]}"
        ;;
        
    3)
        echo "🔍 Current security group rules:"
        aws ec2 describe-security-groups \
            --group-ids "$RDS_SG_ID" \
            --query 'SecurityGroups[0].IpPermissions[?FromPort==`5432`]' \
            --output table
        ;;
        
    4)
        echo "🧪 Testing database connection..."
        
        # Check if psql is available
        if ! command -v psql &> /dev/null; then
            echo "❌ psql not found. Please install PostgreSQL client."
            echo "On Ubuntu/Debian: sudo apt-get install postgresql-client"
            echo "On macOS: brew install postgresql"
            exit 1
        fi
        
        echo "Testing connection to $RDS_ENDPOINT:$RDS_PORT..."
        
        # Test connection (without password for now)
        if timeout 10 psql -h "$RDS_ENDPOINT" -p "$RDS_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" 2>/dev/null; then
            echo "✅ Connection successful!"
        else
            echo "❌ Connection failed. Please check:"
            echo "  1. Security group allows your IP"
            echo "  2. RDS instance is running"
            echo "  3. Database credentials are correct"
        fi
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "📚 Next steps:"
echo "1. Set up your local environment variables:"
echo "   export DATABASE_URL=\"postgresql://postgres:[password]@$RDS_ENDPOINT:5432/$DB_NAME\""
echo ""
echo "2. Run database migrations:"
echo "   cd backend && alembic upgrade head"
echo ""
echo "3. Run the application:"
echo "   uvicorn main:app --reload"
