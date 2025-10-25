#!/bin/bash

# Landing Page Deployment Script
# This script helps deploy the landing page to various hosting services

set -e

echo "🚀 Landing Page Deployment Script"
echo "=================================="

# Check if required files exist
if [ ! -f "index.html" ]; then
    echo "❌ Error: index.html not found"
    exit 1
fi

if [ ! -f "styles.css" ]; then
    echo "❌ Error: styles.css not found"
    exit 1
fi

if [ ! -f "script.js" ]; then
    echo "❌ Error: script.js not found"
    exit 1
fi

echo "✅ All required files found"

# Function to deploy to AWS S3
deploy_s3() {
    echo "📦 Deploying to AWS S3..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        echo "❌ AWS CLI not found. Please install it first."
        exit 1
    fi
    
    # Check if bucket name is provided
    if [ -z "$S3_BUCKET" ]; then
        echo "❌ Please set S3_BUCKET environment variable"
        echo "Example: export S3_BUCKET=quentinspencer.com"
        exit 1
    fi
    
    # Sync files to S3
    aws s3 sync . s3://$S3_BUCKET --delete --exclude "*.sh" --exclude "README.md" --exclude ".git/*"
    
    # Set proper content types
    aws s3 cp index.html s3://$S3_BUCKET/index.html --content-type "text/html"
    aws s3 cp styles.css s3://$S3_BUCKET/styles.css --content-type "text/css"
    aws s3 cp script.js s3://$S3_BUCKET/script.js --content-type "application/javascript"
    
    echo "✅ Deployment to S3 completed"
    echo "🌐 Website available at: https://$S3_BUCKET"
}

# Function to deploy to Netlify
deploy_netlify() {
    echo "📦 Deploying to Netlify..."
    
    # Check if Netlify CLI is installed
    if ! command -v netlify &> /dev/null; then
        echo "❌ Netlify CLI not found. Please install it first."
        echo "Run: npm install -g netlify-cli"
        exit 1
    fi
    
    # Deploy to Netlify
    netlify deploy --prod --dir .
    
    echo "✅ Deployment to Netlify completed"
}

# Function to create a deployment package
create_package() {
    echo "📦 Creating deployment package..."
    
    PACKAGE_NAME="landing-page-$(date +%Y%m%d-%H%M%S).zip"
    
    # Create zip file excluding unnecessary files
    zip -r $PACKAGE_NAME . -x "*.sh" "README.md" ".git/*" "*.zip"
    
    echo "✅ Package created: $PACKAGE_NAME"
    echo "📁 Upload this file to your hosting service"
}

# Function to validate files
validate() {
    echo "🔍 Validating files..."
    
    # Check HTML syntax
    if command -v tidy &> /dev/null; then
        tidy -q -e index.html
        echo "✅ HTML validation passed"
    else
        echo "⚠️  HTML Tidy not found, skipping HTML validation"
    fi
    
    # Check if all links are working (basic check)
    echo "🔗 Checking internal links..."
    
    # Check if all referenced files exist
    if [ -f "styles.css" ] && [ -f "script.js" ]; then
        echo "✅ All referenced files exist"
    else
        echo "❌ Some referenced files are missing"
        exit 1
    fi
    
    echo "✅ Validation completed"
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  s3          Deploy to AWS S3"
    echo "  netlify     Deploy to Netlify"
    echo "  package     Create deployment package"
    echo "  validate    Validate files"
    echo "  help        Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  S3_BUCKET   S3 bucket name for deployment"
    echo ""
    echo "Examples:"
    echo "  $0 validate"
    echo "  S3_BUCKET=quentinspencer.com $0 s3"
    echo "  $0 netlify"
    echo "  $0 package"
}

# Main script logic
case "${1:-help}" in
    s3)
        validate
        deploy_s3
        ;;
    netlify)
        validate
        deploy_netlify
        ;;
    package)
        validate
        create_package
        ;;
    validate)
        validate
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Unknown option: $1"
        show_help
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment process completed!"
