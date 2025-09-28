#!/bin/bash

# User-level Prerequisites Installation Script
echo "🔧 Installing prerequisites for AWS deployment (user-level)..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  This script is designed for user-level installation"
    echo "Please run without sudo: ./scripts/install-prerequisites-user.sh"
    exit 1
fi

# Install AWS CLI via pip (user-level)
echo "☁️  Installing AWS CLI..."
if ! command -v aws &> /dev/null; then
    pip3 install --user awscli
    echo "✅ AWS CLI installed"
else
    echo "✅ AWS CLI already installed"
fi

# Install Terraform via snap (if available)
echo "🏗️  Installing Terraform..."
if ! command -v terraform &> /dev/null; then
    if command -v snap &> /dev/null; then
        echo "Installing Terraform via snap..."
        snap install terraform --classic
    else
        echo "❌ Snap not available. Please install Terraform manually:"
        echo "   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip"
        echo "   unzip terraform_1.6.0_linux_amd64.zip"
        echo "   sudo mv terraform /usr/local/bin/"
        exit 1
    fi
else
    echo "✅ Terraform already installed"
fi

# Install Docker via snap (if available)
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    if command -v snap &> /dev/null; then
        echo "Installing Docker via snap..."
        snap install docker
    else
        echo "❌ Snap not available. Please install Docker manually:"
        echo "   sudo apt update && sudo apt install docker.io"
        echo "   sudo usermod -aG docker $USER"
        echo "   (logout and login again)"
        exit 1
    fi
else
    echo "✅ Docker already installed"
fi

# Install Node.js via snap (if available)
echo "📦 Installing Node.js..."
if ! command -v node &> /dev/null; then
    if command -v snap &> /dev/null; then
        echo "Installing Node.js via snap..."
        snap install node --classic
    else
        echo "❌ Snap not available. Please install Node.js manually:"
        echo "   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -"
        echo "   sudo apt install -y nodejs"
        exit 1
    fi
else
    echo "✅ Node.js already installed"
fi

# Verify installations
echo "✅ Verifying installations..."
echo "AWS CLI version:"
aws --version 2>/dev/null || echo "❌ AWS CLI not working"

echo "Terraform version:"
terraform --version 2>/dev/null || echo "❌ Terraform not working"

echo "Docker version:"
docker --version 2>/dev/null || echo "❌ Docker not working"

echo "Node.js version:"
node --version 2>/dev/null || echo "❌ Node.js not working"

echo "Python version:"
python3 --version 2>/dev/null || echo "❌ Python3 not working"

echo "🎉 Prerequisites installation completed!"
echo ""
echo "📝 Next steps:"
echo "1. Configure AWS CLI: aws configure"
echo "2. If Docker was installed, logout and login again to use without sudo"
echo "3. Run: ./scripts/setup-dev-deployment.sh"
