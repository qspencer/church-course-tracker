#!/bin/bash

# Script to update RDS security group to allow local access
# This script adds your current IP address to the RDS security group

set -e

echo "🔐 Updating RDS Security Group for Local Access"
echo "================================================"

# Get current public IP address
CURRENT_IP=$(curl -s https://checkip.amazonaws.com)
echo "📍 Your current public IP: $CURRENT_IP"

# RDS security group ID (from Terraform output)
RDS_SG_ID="sg-0a1b2c3d4e5f67890"  # This will be the actual SG ID from your deployment

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

echo "🔍 Finding RDS security group..."

# Find the RDS security group
RDS_SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=*rds*" \
    --query 'SecurityGroups[0].GroupId' \
    --output text)

if [ "$RDS_SG_ID" = "None" ] || [ -z "$RDS_SG_ID" ]; then
    echo "❌ Could not find RDS security group. Please check your AWS deployment."
    exit 1
fi

echo "✅ Found RDS security group: $RDS_SG_ID"

# Add rule to allow PostgreSQL access from current IP
echo "🔧 Adding inbound rule for PostgreSQL access..."

aws ec2 authorize-security-group-ingress \
    --group-id "$RDS_SG_ID" \
    --protocol tcp \
    --port 5432 \
    --cidr "$CURRENT_IP/32" \
    --output table

echo "✅ Security group updated successfully!"
echo ""
echo "📝 You can now connect to the RDS database using:"
echo "   Host: church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com"
echo "   Port: 5432"
echo "   Database: church_course_tracker"
echo "   Username: postgres"
echo "   Password: [your-db-password]"
echo ""
echo "⚠️  Remember to remove this rule when you're done for security!"
