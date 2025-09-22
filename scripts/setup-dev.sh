#!/bin/bash

# Church Course Tracker - Development Setup Script
# This script sets up the development environment for the project

set -e  # Exit on any error

echo "🚀 Setting up Church Course Tracker development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ and try again."
        exit 1
    fi
    
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version 18+ is required. Current version: $(node --version)"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.11+ and try again."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$(echo "$PYTHON_VERSION < 3.11" | bc -l)" -eq 1 ]; then
        print_error "Python 3.11+ is required. Current version: $(python3 --version)"
        exit 1
    fi
    
    # Check Docker (optional)
    if ! command -v docker &> /dev/null; then
        print_warning "Docker is not installed. Docker is optional but recommended for development."
    fi
    
    print_status "Requirements check completed ✅"
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file..."
        cp env.example .env
        print_warning "Please edit .env file with your configuration"
    fi
    
    # Create data directory
    mkdir -p data
    
    # Run database migrations
    print_status "Running database migrations..."
    alembic upgrade head
    
    cd ..
    print_status "Backend setup completed ✅"
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd frontend/church-course-tracker
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    # Create environment file if it doesn't exist
    if [ ! -f "src/environments/environment.ts" ]; then
        print_status "Environment file already exists"
    fi
    
    cd ../..
    print_status "Frontend setup completed ✅"
}

# Setup Docker (optional)
setup_docker() {
    if command -v docker &> /dev/null; then
        print_status "Setting up Docker development environment..."
        
        cd docker
        
        # Create necessary directories
        mkdir -p ssl
        
        print_status "Docker setup completed ✅"
        print_warning "To start the development environment with Docker, run:"
        print_warning "docker-compose -f docker/docker-compose.dev.yml up --build"
        
        cd ..
    else
        print_warning "Docker not available, skipping Docker setup"
    fi
}

# Main setup function
main() {
    print_status "Starting Church Course Tracker development setup..."
    
    check_requirements
    setup_backend
    setup_frontend
    setup_docker
    
    echo ""
    print_status "🎉 Development environment setup completed!"
    echo ""
    print_status "Next steps:"
    echo "1. Edit backend/.env with your configuration"
    echo "2. Start the backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
    echo "3. Start the frontend: cd frontend/church-course-tracker && npm start"
    echo "4. Access the application at http://localhost:4200"
    echo ""
    print_status "For Docker development:"
    echo "docker-compose -f docker/docker-compose.dev.yml up --build"
    echo ""
    print_status "Happy coding! 🚀"
}

# Run main function
main
