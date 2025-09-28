#!/bin/bash

# Development Application Deployment Script
set -e

echo "🚀 Deploying Church Course Tracker to AWS (Development)"
echo "======================================================"
echo ""

# Configuration
DOMAIN_NAME="apps.eastgate.church"
AWS_REGION="us-east-1"
APP_NAME="church-course-tracker"

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📍 AWS Account: $AWS_ACCOUNT_ID"
echo "🌍 AWS Region: $AWS_REGION"
echo ""

# Build and push backend image
echo "📦 Building and pushing backend image..."

# Get ECR repository URL
ECR_REPOSITORY=$(terraform -chdir=infrastructure output -raw ecr_repository_url)
echo "📦 ECR Repository: $ECR_REPOSITORY"

# Login to ECR
echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | sudo docker login --username AWS --password-stdin $ECR_REPOSITORY

# Build backend image
echo "🏗️  Building backend image..."
cd backend
sudo docker build -f Dockerfile.prod -t $APP_NAME-backend:latest .

# Tag and push image
echo "📤 Pushing backend image to ECR..."
sudo docker tag $APP_NAME-backend:latest $ECR_REPOSITORY:latest
sudo docker push $ECR_REPOSITORY:latest

echo "✅ Backend image pushed to ECR!"

# Build and deploy frontend
echo "🌐 Building and deploying frontend..."

cd ../frontend/church-course-tracker

# Install dependencies
echo "📦 Installing frontend dependencies..."
npm ci

# Build for production
echo "🏗️  Building frontend for production..."
npm run build --configuration=production

# Get S3 bucket name
S3_BUCKET=$(terraform -chdir=../../infrastructure output -raw s3_static_bucket)

# Sync to S3
echo "📤 Deploying frontend to S3..."
aws s3 sync dist/church-course-tracker/ s3://$S3_BUCKET --delete

echo "✅ Frontend deployed to S3!"

# Update ECS service
echo "🔄 Updating ECS service..."
aws ecs update-service \
    --cluster $APP_NAME-cluster \
    --service $APP_NAME-service \
    --force-new-deployment \
    --region $AWS_REGION

# Wait for service to be stable
echo "⏳ Waiting for service to be stable..."
aws ecs wait services-stable \
    --cluster $APP_NAME-cluster \
    --services $APP_NAME-service \
    --region $AWS_REGION

echo "✅ ECS service updated!"

# Run database migrations
echo "🗄️ Running database migrations..."
TASK_ARN=$(aws ecs list-tasks --cluster $APP_NAME-cluster --service-name $APP_NAME-service --region $AWS_REGION --query 'taskArns[0]' --output text)

if [ "$TASK_ARN" != "None" ] && [ "$TASK_ARN" != "" ]; then
    echo "🔄 Running Alembic migrations..."
    aws ecs execute-command \
        --cluster $APP_NAME-cluster \
        --task $TASK_ARN \
        --container backend \
        --command "alembic upgrade head" \
        --interactive \
        --region $AWS_REGION
fi

echo "✅ Database migrations completed!"

# Create default admin user
echo "👤 Creating default admin user..."
if [ "$TASK_ARN" != "None" ] && [ "$TASK_ARN" != "" ]; then
    aws ecs execute-command \
        --cluster $APP_NAME-cluster \
        --task $TASK_ARN \
        --container backend \
        --command "python create_default_admin.py" \
        --interactive \
        --region $AWS_REGION
fi

echo "✅ Default admin user created!"

# Get application URLs
CLOUDFRONT_DOMAIN=$(terraform -chdir=../../infrastructure output -raw cloudfront_domain)
ALB_DNS=$(terraform -chdir=../../infrastructure output -raw alb_dns_name)

echo ""
echo "🎉 Application deployment completed successfully!"
echo "=============================================="
echo ""
echo "🔗 Your application is now live at:"
echo "   Frontend: https://$DOMAIN_NAME"
echo "   API: https://api.$DOMAIN_NAME"
echo ""
echo "🌐 Direct URLs (while DNS propagates):"
echo "   Frontend: https://$CLOUDFRONT_DOMAIN"
echo "   API: http://$ALB_DNS"
echo ""
echo "🔐 Default admin credentials:"
echo "   Username: Admin"
echo "   Email: course.tracker.admin@eastgate.church"
echo "   Password: Matthew778*"
echo ""
echo "📊 Monitoring:"
echo "   CloudWatch Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#dashboards:name=$APP_NAME-dashboard"
echo ""
echo "⚠️  Important:"
echo "   1. Update your DNS to point $DOMAIN_NAME to the CloudFront distribution"
echo "   2. Change the default admin password after first login"
echo "   3. Configure Planning Center API credentials when ready"
echo ""
echo "✅ Development deployment completed!"
