#!/bin/bash

# Script to run database migrations through ECS service
# This works with private subnets by executing migrations in the ECS environment

set -e

echo "🗄️  Running Database Migrations via ECS"
echo "====================================="

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

echo "🔍 Finding ECS task..."

# Find an ECS task
TASK_ARN=$(aws ecs list-tasks \
    --cluster church-course-tracker-cluster \
    --service-name church-course-tracker-service \
    --query 'taskArns[0]' \
    --output text 2>/dev/null)

if [ "$TASK_ARN" = "None" ] || [ -z "$TASK_ARN" ]; then
    echo "❌ No running ECS tasks found. Please ensure the service is running."
    exit 1
fi

echo "✅ Found ECS task: $TASK_ARN"

# Get the container name
CONTAINER_NAME=$(aws ecs describe-tasks \
    --cluster church-course-tracker-cluster \
    --tasks "$TASK_ARN" \
    --query 'tasks[0].containers[0].name' \
    --output text)

echo "✅ Found container: $CONTAINER_NAME"

echo "🔧 Running database migrations..."

# Execute alembic upgrade head in the ECS container
aws ecs execute-command \
    --cluster church-course-tracker-cluster \
    --task "$TASK_ARN" \
    --container "$CONTAINER_NAME" \
    --interactive \
    --command "alembic upgrade head"

echo "✅ Database migrations completed successfully!"
