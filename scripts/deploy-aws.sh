#!/bin/bash

# AWS Deployment Script for Church Course Tracker
set -e

# Configuration
AWS_REGION="us-east-1"
APP_NAME="church-course-tracker"
ENVIRONMENT="production"
ECR_REPOSITORY="${APP_NAME}-backend"
S3_BUCKET="${APP_NAME}-static"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Starting AWS deployment for Church Course Tracker..."
echo "📍 AWS Account: $AWS_ACCOUNT_ID"
echo "🌍 AWS Region: $AWS_REGION"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# 1. Build and push backend image to ECR
echo "📦 Building and pushing backend image..."

# Create ECR repository if it doesn't exist
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION || \
aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION

# Get ECR login token
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build backend image
cd backend
docker build -f Dockerfile.prod -t $ECR_REPOSITORY:latest .

# Tag and push image
docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

echo "✅ Backend image pushed to ECR"

# 2. Build and deploy frontend to S3
echo "🌐 Building and deploying frontend..."

# Increment version before building
echo "📌 Incrementing application version..."
cd "$(dirname "$0")/.."
chmod +x scripts/increment-version.sh
NEW_VERSION=$(scripts/increment-version.sh)
echo "✅ Version incremented to $NEW_VERSION"

cd frontend/church-course-tracker

# Install dependencies
npm ci

# Build for production
npm run build --configuration=production

# Sync to S3
aws s3 sync dist/church-course-tracker/ s3://$S3_BUCKET --delete

echo "✅ Frontend deployed to S3"

# 3. Update ECS service
echo "🔄 Updating ECS service..."

# Update ECS service with new image
aws ecs update-service \
    --cluster $APP_NAME-cluster \
    --service $APP_NAME-service \
    --force-new-deployment \
    --region $AWS_REGION

echo "✅ ECS service updated"

# 4. Run database migrations
echo "🗄️ Running database migrations..."

# Get ECS task ARN
TASK_ARN=$(aws ecs list-tasks --cluster $APP_NAME-cluster --service-name $APP_NAME-service --region $AWS_REGION --query 'taskArns[0]' --output text)

if [ "$TASK_ARN" != "None" ] && [ "$TASK_ARN" != "" ]; then
    # Run migrations
    aws ecs execute-command \
        --cluster $APP_NAME-cluster \
        --task $TASK_ARN \
        --container backend \
        --command "alembic upgrade head" \
        --interactive \
        --region $AWS_REGION
fi

echo "✅ Database migrations completed"

# 5. Health check
echo "🏥 Performing health check..."

# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers --names $APP_NAME-alb --region $AWS_REGION --query 'LoadBalancers[0].DNSName' --output text)

# Wait for service to be healthy
echo "⏳ Waiting for service to be healthy..."
aws elbv2 wait target-in-service \
    --target-group-arn $(aws elbv2 describe-target-groups --names $APP_NAME-tg --region $AWS_REGION --query 'TargetGroups[0].TargetGroupArn' --output text) \
    --region $AWS_REGION

echo "✅ Health check passed"

echo "🎉 Deployment completed successfully!"
echo "🌐 Application URL: http://$ALB_DNS"
echo "📊 CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#logsV2:log-groups"
