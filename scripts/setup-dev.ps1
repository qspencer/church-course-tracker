# Church Course Tracker - Development Setup Script (PowerShell)
# This script sets up the development environment for the project

param(
    [switch]$SkipDocker
)

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🚀 Setting up Church Course Tracker development environment..." -ForegroundColor Green

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if required tools are installed
function Test-Requirements {
    Write-Status "Checking requirements..."
    
    # Check Node.js
    try {
        $nodeVersion = node --version
        $nodeMajorVersion = [int]($nodeVersion -replace 'v(\d+)\..*', '$1')
        if ($nodeMajorVersion -lt 18) {
            Write-Error "Node.js version 18+ is required. Current version: $nodeVersion"
            exit 1
        }
        Write-Status "Node.js version: $nodeVersion ✅"
    }
    catch {
        Write-Error "Node.js is not installed. Please install Node.js 18+ and try again."
        exit 1
    }
    
    # Check Python
    try {
        $pythonVersion = python --version
        $pythonMajorMinor = [version]($pythonVersion -replace 'Python (\d+\.\d+)\..*', '$1')
        $requiredVersion = [version]"3.11"
        if ($pythonMajorMinor -lt $requiredVersion) {
            Write-Error "Python 3.11+ is required. Current version: $pythonVersion"
            exit 1
        }
        Write-Status "Python version: $pythonVersion ✅"
    }
    catch {
        Write-Error "Python 3 is not installed. Please install Python 3.11+ and try again."
        exit 1
    }
    
    # Check Docker (optional)
    try {
        docker --version | Out-Null
        Write-Status "Docker is available ✅"
    }
    catch {
        if (-not $SkipDocker) {
            Write-Warning "Docker is not installed. Docker is optional but recommended for development."
        }
    }
    
    Write-Status "Requirements check completed ✅"
}

# Setup backend
function Setup-Backend {
    Write-Status "Setting up backend..."
    
    Set-Location backend
    
    # Create virtual environment
    if (-not (Test-Path "venv")) {
        Write-Status "Creating Python virtual environment..."
        python -m venv venv
    }
    
    # Activate virtual environment
    Write-Status "Activating virtual environment..."
    & ".\venv\Scripts\Activate.ps1"
    
    # Install dependencies
    Write-Status "Installing Python dependencies..."
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if (-not (Test-Path ".env")) {
        Write-Status "Creating .env file..."
        Copy-Item "env.example" ".env"
        Write-Warning "Please edit .env file with your configuration"
    }
    
    # Create data directory
    if (-not (Test-Path "data")) {
        New-Item -ItemType Directory -Path "data" | Out-Null
    }
    
    # Run database migrations
    Write-Status "Running database migrations..."
    alembic upgrade head
    
    Set-Location ..
    Write-Status "Backend setup completed ✅"
}

# Setup frontend
function Setup-Frontend {
    Write-Status "Setting up frontend..."
    
    Set-Location "frontend\church-course-tracker"
    
    # Install dependencies
    Write-Status "Installing Node.js dependencies..."
    npm install
    
    Set-Location ..\..
    Write-Status "Frontend setup completed ✅"
}

# Setup Docker (optional)
function Setup-Docker {
    if (-not $SkipDocker) {
        try {
            docker --version | Out-Null
            Write-Status "Setting up Docker development environment..."
            
            Set-Location docker
            
            # Create necessary directories
            if (-not (Test-Path "ssl")) {
                New-Item -ItemType Directory -Path "ssl" | Out-Null
            }
            
            Set-Location ..
            Write-Status "Docker setup completed ✅"
            Write-Warning "To start the development environment with Docker, run:"
            Write-Warning "docker-compose -f docker/docker-compose.dev.yml up --build"
        }
        catch {
            Write-Warning "Docker not available, skipping Docker setup"
        }
    }
}

# Main setup function
function Main {
    Write-Status "Starting Church Course Tracker development setup..."
    
    Test-Requirements
    Setup-Backend
    Setup-Frontend
    Setup-Docker
    
    Write-Host ""
    Write-Status "🎉 Development environment setup completed!"
    Write-Host ""
    Write-Status "Next steps:"
    Write-Host "1. Edit backend\.env with your configuration"
    Write-Host "2. Start the backend: cd backend && .\venv\Scripts\Activate.ps1 && uvicorn main:app --reload"
    Write-Host "3. Start the frontend: cd frontend\church-course-tracker && npm start"
    Write-Host "4. Access the application at http://localhost:4200"
    Write-Host ""
    Write-Status "For Docker development:"
    Write-Host "docker-compose -f docker/docker-compose.dev.yml up --build"
    Write-Host ""
    Write-Status "Happy coding! 🚀"
}

# Run main function
Main
