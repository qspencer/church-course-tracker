#!/bin/bash

# Development Deployment Setup for apps.eastgate.church (without Docker check)
set -e

echo "🚀 Setting up development deployment for apps.eastgate.church"
echo "=========================================================="
echo ""

# Configuration
DOMAIN_NAME="apps.eastgate.church"
AWS_REGION="us-east-1"
APP_NAME="church-course-tracker"
ENVIRONMENT="development"
BUDGET_LIMIT=75

echo "📋 Configuration:"
echo "   Domain: $DOMAIN_NAME"
echo "   AWS Region: $AWS_REGION"
echo "   Environment: $ENVIRONMENT"
echo "   Budget Limit: \$$BUDGET_LIMIT/month"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please run: sudo ./scripts/install-prerequisites.sh"
    exit 1
fi

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please run: sudo ./scripts/install-prerequisites.sh"
    exit 1
fi

# Check Docker (skipped for now)
echo "⚠️  Docker check skipped - will be needed for application deployment"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please run: sudo ./scripts/install-prerequisites.sh"
    exit 1
fi

echo "✅ Prerequisites check completed!"

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured."
    echo "Please run: aws configure"
    echo "You'll need:"
    echo "  - AWS Access Key ID"
    echo "  - AWS Secret Access Key"
    echo "  - Default region: $AWS_REGION"
    echo "  - Default output format: json"
    exit 1
fi

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ AWS credentials configured for account: $AWS_ACCOUNT_ID"

# Create development Terraform configuration
echo "📝 Creating development Terraform configuration..."
cat > infrastructure/terraform.tfvars << EOF
# Development Configuration for apps.eastgate.church
aws_region = "$AWS_REGION"
app_name = "$APP_NAME"
environment = "$ENVIRONMENT"
domain_name = "$DOMAIN_NAME"
certificate_arn = ""  # Will be created automatically

# Cost-optimized settings for development
min_capacity = 1
max_capacity = 3
cpu_target_value = 80
memory_target_value = 85

# Database settings
db_password = "$(openssl rand -base64 32)"
EOF

echo "✅ Terraform configuration created!"

# Create development environment file
echo "📝 Creating development environment configuration..."
cat > backend/.env.development << EOF
# Development Environment Configuration
APP_NAME="Church Course Tracker"
ENVIRONMENT="development"
DEBUG=true
SECRET_KEY="$(openssl rand -base64 32)"

# Database (will be updated after RDS creation)
DATABASE_URL="sqlite:///./data/church_course_tracker.db"

# Mock Planning Center API (for development)
USE_MOCK_PLANNING_CENTER=true
PLANNING_CENTER_APP_ID=""
PLANNING_CENTER_SECRET=""

# AWS Configuration (will be updated after deployment)
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_S3_BUCKET=""
AWS_REGION="$AWS_REGION"

# CORS for development
ALLOWED_ORIGINS="https://$DOMAIN_NAME,http://localhost:4200,http://localhost:3000"

# Logging
LOG_LEVEL="DEBUG"
EOF

echo "✅ Development environment configuration created!"

# Create frontend development environment
echo "📝 Creating frontend development environment..."
cat > frontend/church-course-tracker/src/environments/environment.dev.ts << EOF
export const environment = {
  production: false,
  apiUrl: 'https://api.$DOMAIN_NAME/api/v1',
  appName: 'Church Course Tracker',
  version: '1.0.0',
  enableAnalytics: false,
  enableErrorReporting: false,
  logLevel: 'debug'
};
EOF

echo "✅ Frontend development environment created!"

# Initialize Terraform
echo "🔧 Initializing Terraform..."
cd infrastructure
terraform init

# Validate Terraform configuration
echo "✅ Validating Terraform configuration..."
terraform validate

# Plan infrastructure
echo "📋 Planning infrastructure deployment..."
terraform plan -out=tfplan

echo ""
echo "💰 Estimated monthly cost: ~$45-55 (within your $BUDGET_LIMIT budget)"
echo "🏗️  Resources to be created:"
echo "   - VPC with public/private subnets"
echo "   - RDS PostgreSQL (db.t3.micro)"
echo "   - ECS Fargate cluster (1-3 tasks)"
echo "   - Application Load Balancer"
echo "   - S3 buckets for static assets and uploads"
echo "   - CloudFront CDN"
echo "   - Route 53 hosted zone for $DOMAIN_NAME"
echo "   - SSL certificate via ACM"
echo ""

# Ask for confirmation
read -p "Do you want to proceed with the deployment? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    echo "❌ Deployment cancelled."
    exit 1
fi

# Apply infrastructure
echo "🚀 Deploying infrastructure..."
terraform apply tfplan

# Get outputs
echo "📊 Infrastructure deployed successfully!"
echo ""
echo "🔗 Application URLs:"
echo "   Frontend: https://$DOMAIN_NAME"
echo "   API: https://api.$DOMAIN_NAME"
echo ""

# Get database endpoint
DATABASE_ENDPOINT=$(terraform output -raw database_endpoint)
echo "🗄️ Database: $DATABASE_ENDPOINT"

# Update environment files with actual values
echo "📝 Updating environment files with deployment values..."
cd ..

# Update backend environment
cat > backend/.env.development << EOF
# Development Environment Configuration
APP_NAME="Church Course Tracker"
ENVIRONMENT="development"
DEBUG=true
SECRET_KEY="$(openssl rand -base64 32)"

# Database (RDS PostgreSQL)
DATABASE_URL="postgresql://postgres:$(grep db_password infrastructure/terraform.tfvars | cut -d'"' -f2)@$DATABASE_ENDPOINT:5432/church_course_tracker"

# Mock Planning Center API (for development)
USE_MOCK_PLANNING_CENTER=true
PLANNING_CENTER_APP_ID=""
PLANNING_CENTER_SECRET=""

# AWS Configuration
AWS_ACCESS_KEY_ID="$(aws configure get aws_access_key_id)"
AWS_SECRET_ACCESS_KEY="$(aws configure get aws_secret_access_key)"
AWS_S3_BUCKET="$(terraform -chdir=infrastructure output -raw s3_uploads_bucket)"
AWS_REGION="$AWS_REGION"

# CORS for development
ALLOWED_ORIGINS="https://$DOMAIN_NAME,http://localhost:4200,http://localhost:3000"

# Logging
LOG_LEVEL="DEBUG"
EOF

echo "✅ Environment files updated!"

echo ""
echo "🎉 Development deployment setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Update your DNS to point $DOMAIN_NAME to the CloudFront distribution"
echo "2. Install Docker and run: ./scripts/deploy-dev-application.sh"
echo "3. Test the application at: https://$DOMAIN_NAME"
echo ""
echo "🔐 Default admin credentials:"
echo "   Username: Admin"
echo "   Email: course.tracker.admin@eastgate.church"
echo "   Password: Matthew778*"