#!/usr/bin/env python3
"""
Local development setup script for Church Course Tracker
This script sets up a local development environment with SQLite
"""

import os
import sys
import subprocess
import logging

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_local_environment():
    """Set up local development environment"""
    logger.info("🔧 Setting up local development environment...")
    
    # Set environment variables for local development
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DATABASE_URL"] = "sqlite:///./data/church_course_tracker.db"
    os.environ["SECRET_KEY"] = "dev-secret-key-for-local-development-only"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "120"
    os.environ["DEBUG"] = "true"
    os.environ["ALLOWED_ORIGINS"] = "http://localhost:4200,http://127.0.0.1:4200"
    
    logger.info("✅ Environment variables set for local development")


def create_database_directory():
    """Create database directory if it doesn't exist"""
    logger.info("📁 Creating database directory...")
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    logger.info(f"✅ Database directory created: {data_dir}")


def run_migrations():
    """Run database migrations"""
    logger.info("🗄️  Running database migrations...")
    
    try:
        # Change to backend directory
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        os.chdir(backend_dir)
        
        # Run alembic upgrade
        result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Database migrations completed successfully")
        else:
            logger.error(f"❌ Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        return False
    
    return True


def run_database_optimization():
    """Run database optimization"""
    logger.info("⚡ Running database optimization...")
    
    try:
        # Change to backend directory
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        os.chdir(backend_dir)
        
        # Run optimization script
        result = subprocess.run([sys.executable, "scripts/optimize_database.py"], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Database optimization completed successfully")
            logger.info(result.stdout)
        else:
            logger.error(f"❌ Optimization failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Optimization error: {e}")
        return False
    
    return True


def create_admin_user():
    """Create default admin user"""
    logger.info("👤 Creating default admin user...")
    
    try:
        # Change to backend directory
        backend_dir = os.path.dirname(os.path.dirname(__file__))
        os.chdir(backend_dir)
        
        # Run admin user creation script
        result = subprocess.run([sys.executable, "create_default_admin.py"], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Admin user created successfully")
            logger.info("📝 Admin credentials: admin / admin123")
        else:
            logger.error(f"❌ Admin user creation failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Admin user creation error: {e}")
        return False
    
    return True


def main():
    """Main setup function"""
    logger.info("🚀 Starting local development setup...")
    
    try:
        # Set up environment
        setup_local_environment()
        
        # Create database directory
        create_database_directory()
        
        # Run migrations
        if not run_migrations():
            logger.error("❌ Setup failed at migration step")
            sys.exit(1)
        
        # Run database optimization
        if not run_database_optimization():
            logger.error("❌ Setup failed at optimization step")
            sys.exit(1)
        
        # Create admin user
        if not create_admin_user():
            logger.error("❌ Setup failed at admin user creation step")
            sys.exit(1)
        
        logger.info("✅ Local development setup completed successfully!")
        logger.info("🎉 You can now run the application with: uvicorn main:app --reload")
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
