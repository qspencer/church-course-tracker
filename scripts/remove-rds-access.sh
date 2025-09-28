#!/bin/bash

# Script to remove RDS access from your IP address
# This script removes the security group rule that allows your IP to access RDS

set -e

echo "🔐 Removing RDS Access from Your IP"
echo "===================================="

# Get current public IP
CURRENT_IP=$(curl -s https://checkip.amazonaws.com)
echo "📍 Your current public IP: $CURRENT_IP"

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
    --output text 2>/dev/null)

if [ "$RDS_SG_ID" = "None" ] || [ -z "$RDS_SG_ID" ]; then
    echo "❌ Could not find RDS security group."
    exit 1
fi

echo "✅ Found RDS security group: $RDS_SG_ID"

# Check if rule exists
EXISTING_RULE=$(aws ec2 describe-security-groups \
    --group-ids "$RDS_SG_ID" \
    --query "SecurityGroups[0].IpPermissions[?FromPort==\`5432\` && IpRanges[?CidrIp==\`$CURRENT_IP/32\`]]" \
    --output text 2>/dev/null)

if [ -z "$EXISTING_RULE" ]; then
    echo "ℹ️  No rule found for your IP address. Nothing to remove."
    exit 0
fi

echo "🔧 Removing security group rule..."

# Remove the rule
aws ec2 revoke-security-group-ingress \
    --group-id "$RDS_SG_ID" \
    --protocol tcp \
    --port 5432 \
    --cidr "$CURRENT_IP/32"

echo "✅ Successfully removed access rule for your IP address"
echo "🔒 RDS database is now secure and not accessible from your local machine"
