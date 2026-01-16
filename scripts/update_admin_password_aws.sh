#!/bin/bash
# Script to update the admin user password in AWS deployment to Matthew778*

set -e

echo "🔐 Updating Admin User Password in AWS Deployment"
echo "=================================================="
echo ""
echo "This script will update the admin user password to: Matthew778*"
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

echo "📋 Options to update the password:"
echo ""
echo "Option 1: Update via API (Recommended)"
echo "  This uses the update_admin_via_api.py script:"
echo "  python3 scripts/update_admin_via_api.py"
echo ""
echo "Option 2: Update directly in database"
echo "  This uses the update_aws_admin_user.py script:"
echo "  python3 scripts/update_aws_admin_user.py"
echo ""
echo "Option 3: Update via ECS task"
echo "  This runs a command in the ECS container:"
echo "  See scripts/update_admin_ecs.py"
echo ""

read -p "Which method would you like to use? (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Updating via API..."
        python3 "$(dirname "$0")/update_admin_via_api.py"
        ;;
    2)
        echo ""
        echo "🚀 Updating directly in database..."
        python3 "$(dirname "$0")/update_aws_admin_user.py"
        ;;
    3)
        echo ""
        echo "🚀 Updating via ECS..."
        python3 "$(dirname "$0")/update_admin_ecs.py"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "✅ Password update completed!"
echo ""
echo "🔐 New credentials:"
echo "   Username: Admin"
echo "   Password: Matthew778*"
echo ""
echo "You can now log in to the AWS deployment with these credentials."
