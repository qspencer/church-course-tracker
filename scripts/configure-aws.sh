#!/bin/bash

# AWS Configuration Script
echo "🔐 Configuring AWS CLI for deployment..."

# Check if AWS CLI is available
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please run the prerequisites installation first."
    exit 1
fi

echo "📋 You'll need the following AWS credentials:"
echo "   1. AWS Access Key ID"
echo "   2. AWS Secret Access Key"
echo "   3. Default region: us-east-1"
echo "   4. Default output format: json"
echo ""

echo "🔗 Get your credentials from:"
echo "   https://console.aws.amazon.com/iam/home#/security_credentials"
echo ""

# Check if already configured
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ AWS CLI is already configured!"
    aws sts get-caller-identity
    echo ""
    echo "Do you want to reconfigure? (y/n)"
    read -r response
    if [[ ! $response =~ ^[Yy]$ ]]; then
        echo "✅ Using existing AWS configuration."
        exit 0
    fi
fi

echo "🔧 Running AWS configuration..."
echo "Please enter your AWS credentials when prompted:"
echo ""

# Configure AWS CLI
aws configure

# Test the configuration
echo "🧪 Testing AWS configuration..."
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ AWS configuration successful!"
    echo ""
    echo "📊 Your AWS Account Information:"
    aws sts get-caller-identity
    echo ""
    echo "🎉 AWS CLI is ready for deployment!"
else
    echo "❌ AWS configuration failed. Please check your credentials."
    echo "💡 Make sure you have:"
    echo "   - Valid AWS Access Key ID"
    echo "   - Valid AWS Secret Access Key"
    echo "   - Proper IAM permissions for the services we'll use"
    exit 1
fi
