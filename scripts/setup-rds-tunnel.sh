#!/bin/bash

# Script to set up secure tunnel to RDS using AWS Systems Manager
# This is more secure than opening the security group

set -e

echo "🔐 Setting up Secure RDS Tunnel"
echo "==============================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Check if Session Manager plugin is installed
if ! aws ssm start-session --help > /dev/null 2>&1; then
    echo "❌ AWS Session Manager plugin not installed."
    echo "Please install it from: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html"
    exit 1
fi

echo "🔍 Finding ECS task instance..."

# Find an ECS task instance that can access RDS
TASK_ARN=$(aws ecs list-tasks \
    --cluster church-course-tracker-cluster \
    --service-name church-course-tracker-service \
    --query 'taskArns[0]' \
    --output text)

if [ "$TASK_ARN" = "None" ] || [ -z "$TASK_ARN" ]; then
    echo "❌ No running ECS tasks found. Please ensure the service is running."
    exit 1
fi

echo "✅ Found ECS task: $TASK_ARN"

# Get the instance ID
INSTANCE_ID=$(aws ecs describe-tasks \
    --cluster church-course-tracker-cluster \
    --tasks "$TASK_ARN" \
    --query 'tasks[0].containerInstanceArn' \
    --output text | cut -d'/' -f2)

echo "✅ Found instance: $INSTANCE_ID"

echo "🔧 Setting up port forwarding..."
echo "This will forward local port 5433 to RDS port 5432"
echo "Press Ctrl+C to stop the tunnel"
echo ""

# Start port forwarding session
aws ssm start-session \
    --target "$INSTANCE_ID" \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters '{"host":["church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com"],"portNumber":["5432"],"localPortNumber":["5433"]}'
