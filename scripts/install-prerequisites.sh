#!/bin/bash

# Prerequisites Installation Script for AWS Deployment
echo "🔧 Installing prerequisites for AWS deployment..."

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    echo "✅ Running with elevated privileges"
else
    echo "⚠️  This script requires sudo privileges to install packages"
    echo "Please run: sudo ./scripts/install-prerequisites.sh"
    exit 1
fi

# Update package list
echo "📦 Updating package list..."
apt update

# Install AWS CLI
echo "☁️  Installing AWS CLI..."
apt install -y awscli

# Install Terraform
echo "🏗️  Installing Terraform..."
apt install -y terraform

# Install Docker
echo "🐳 Installing Docker..."
apt install -y docker.io

# Start Docker service
echo "🚀 Starting Docker service..."
systemctl start docker
systemctl enable docker

# Add current user to docker group
echo "👤 Adding user to docker group..."
usermod -aG docker $SUDO_USER

# Install Node.js (for frontend builds)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
apt install -y python3-pip python3-venv

# Verify installations
echo "✅ Verifying installations..."
echo "AWS CLI version:"
aws --version

echo "Terraform version:"
terraform --version

echo "Docker version:"
docker --version

echo "Node.js version:"
node --version

echo "Python version:"
python3 --version

echo "🎉 Prerequisites installation completed!"
echo ""
echo "📝 Next steps:"
echo "1. Configure AWS CLI: aws configure"
echo "2. Log out and log back in to use Docker without sudo"
echo "3. Run: ./scripts/setup-dev-deployment.sh"
