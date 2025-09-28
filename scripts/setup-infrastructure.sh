#!/bin/bash

# Infrastructure Setup Script for Church Course Tracker
set -e

echo "🏗️ Setting up AWS infrastructure for Church Course Tracker..."

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform is not installed. Please install it first."
    echo "📖 Install from: https://developer.hashicorp.com/terraform/downloads"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    echo "📖 Install from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📍 AWS Account: $AWS_ACCOUNT_ID"

# Navigate to infrastructure directory
cd infrastructure

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "⚠️  terraform.tfvars not found. Creating from example..."
    cp terraform.tfvars.example terraform.tfvars
    echo "📝 Please edit terraform.tfvars with your values before continuing."
    echo "🔑 You'll need to set a secure database password."
    exit 1
fi

# Validate Terraform configuration
echo "✅ Validating Terraform configuration..."
terraform validate

# Plan infrastructure
echo "📋 Planning infrastructure deployment..."
terraform plan -out=tfplan

# Ask for confirmation
echo ""
echo "🚨 This will create AWS resources that may incur costs."
echo "💰 Estimated monthly cost: ~$57"
echo ""
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
echo "   Frontend: $(terraform output -raw application_url)"
echo "   API: $(terraform output -raw api_url)"
echo ""
echo "📈 Monitoring:"
echo "   CloudWatch Dashboard: $(terraform output -raw cloudwatch_dashboard_url)"
echo ""
echo "🗄️ Database:"
echo "   Endpoint: $(terraform output -raw database_endpoint)"
echo ""
echo "📦 Next steps:"
echo "   1. Update your domain DNS to point to the CloudFront distribution"
echo "   2. Run './scripts/deploy-aws.sh' to deploy the application"
echo "   3. Configure your Planning Center API credentials in AWS Secrets Manager"

# Clean up plan file
rm -f tfplan

echo "✅ Infrastructure setup completed!"
