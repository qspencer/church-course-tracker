#!/bin/bash

# Quick Deploy Script for Church Course Tracker
# This script automates the entire deployment process

set -e

echo "🚀 Church Course Tracker - Quick AWS Deployment"
echo "=============================================="
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    echo "📖 Install from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform is not installed. Please install it first."
    echo "📖 Install from: https://developer.hashicorp.com/terraform/downloads"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install it first."
    echo "📖 Install from: https://www.docker.com/get-started"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install it first."
    echo "📖 Install from: https://nodejs.org/"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first."
    echo "📖 Install from: https://www.python.org/"
    exit 1
fi

echo "✅ All prerequisites are installed!"

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ AWS credentials configured for account: $AWS_ACCOUNT_ID"

# Get user input
echo ""
echo "📝 Configuration Setup"
echo "====================="
echo ""

# Get AWS region
read -p "Enter AWS region (default: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

# Get domain name
read -p "Enter your domain name (optional, leave blank for ALB DNS): " DOMAIN_NAME

# Get database password
read -s -p "Enter database password: " DB_PASSWORD
echo ""

# Get email for alerts
read -p "Enter email for CloudWatch alerts: " ALERT_EMAIL

# Create terraform.tfvars
echo "📝 Creating Terraform configuration..."
cat > infrastructure/terraform.tfvars << EOF
aws_region = "$AWS_REGION"
app_name = "church-course-tracker"
environment = "production"
db_password = "$DB_PASSWORD"
domain_name = "$DOMAIN_NAME"
alert_email = "$ALERT_EMAIL"
EOF

echo "✅ Terraform configuration created!"

# Deploy infrastructure
echo ""
echo "🏗️ Deploying infrastructure..."
echo "=============================="
echo "⚠️  This will create AWS resources that may incur costs (~$57/month)"
echo ""
read -p "Do you want to proceed? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    echo "❌ Deployment cancelled."
    exit 1
fi

cd infrastructure
terraform init
terraform plan -out=tfplan
terraform apply tfplan
cd ..

echo "✅ Infrastructure deployed successfully!"

# Get outputs
ALB_DNS=$(cd infrastructure && terraform output -raw alb_dns_name)
CLOUDFRONT_DOMAIN=$(cd infrastructure && terraform output -raw cloudfront_domain)
DATABASE_ENDPOINT=$(cd infrastructure && terraform output -raw database_endpoint)

echo ""
echo "📊 Deployment Summary"
echo "====================="
echo "🌐 Application URL: https://$CLOUDFRONT_DOMAIN"
echo "🔗 API URL: http://$ALB_DNS"
echo "🗄️ Database: $DATABASE_ENDPOINT"
echo ""

# Deploy application
echo "🚀 Deploying application..."
echo "==========================="

# Build and push backend image
echo "📦 Building backend image..."
cd backend
docker build -f Dockerfile.prod -t church-course-tracker-backend:latest .
cd ..

# Get ECR repository URL
ECR_REPOSITORY=$(cd infrastructure && terraform output -raw ecr_repository_url)

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY

# Tag and push image
docker tag church-course-tracker-backend:latest $ECR_REPOSITORY:latest
docker push $ECR_REPOSITORY:latest

echo "✅ Backend image pushed to ECR!"

# Build and deploy frontend
echo "🌐 Building and deploying frontend..."
cd frontend/church-course-tracker
npm ci
npm run build --configuration=production

# Get S3 bucket name
S3_BUCKET=$(cd ../../infrastructure && terraform output -raw s3_static_bucket)

# Sync to S3
aws s3 sync dist/church-course-tracker/ s3://$S3_BUCKET --delete

echo "✅ Frontend deployed to S3!"

# Update ECS service
echo "🔄 Updating ECS service..."
aws ecs update-service \
    --cluster church-course-tracker-cluster \
    --service church-course-tracker-service \
    --force-new-deployment \
    --region $AWS_REGION

# Wait for service to be stable
echo "⏳ Waiting for service to be stable..."
aws ecs wait services-stable \
    --cluster church-course-tracker-cluster \
    --services church-course-tracker-service \
    --region $AWS_REGION

echo "✅ ECS service updated!"

# Run database migrations
echo "🗄️ Running database migrations..."
TASK_ARN=$(aws ecs list-tasks --cluster church-course-tracker-cluster --service-name church-course-tracker-service --region $AWS_REGION --query 'taskArns[0]' --output text)

if [ "$TASK_ARN" != "None" ] && [ "$TASK_ARN" != "" ]; then
    aws ecs execute-command \
        --cluster church-course-tracker-cluster \
        --task $TASK_ARN \
        --container backend \
        --command "alembic upgrade head" \
        --interactive \
        --region $AWS_REGION
fi

echo "✅ Database migrations completed!"

# Final summary
echo ""
echo "🎉 Deployment Completed Successfully!"
echo "===================================="
echo ""
echo "🔗 Your application is now live at:"
echo "   Frontend: https://$CLOUDFRONT_DOMAIN"
echo "   API: http://$ALB_DNS"
echo ""
echo "🔐 Default admin credentials:"
echo "   Username: Admin"
echo "   Email: course.tracker.admin@eastgate.church"
echo "   Password: Matthew778*"
echo ""
echo "⚠️  Important:"
echo "   1. Change the default admin password after first login"
echo "   2. Update your domain DNS to point to the CloudFront distribution"
echo "   3. Configure Planning Center API credentials in AWS Secrets Manager"
echo ""
echo "📊 Monitoring:"
echo "   CloudWatch Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=$AWS_REGION#dashboards:name=church-course-tracker-dashboard"
echo ""
echo "✅ Deployment completed successfully!"
