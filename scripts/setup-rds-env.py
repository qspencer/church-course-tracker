#!/usr/bin/env python3
"""
Setup script for connecting to AWS RDS database from local development
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RDS configuration
RDS_ENDPOINT = "church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com"
RDS_PORT = "5432"
DB_NAME = "church_course_tracker"
DB_USER = "postgres"

def setup_rds_environment():
    """Set up environment variables for RDS connection"""
    logger.info("🔧 Setting up RDS environment...")
    
    # Get database password from user
    db_password = input("Enter RDS database password: ").strip()
    
    if not db_password:
        logger.error("❌ Database password is required")
        sys.exit(1)
    
    # Set environment variables
    os.environ["ENVIRONMENT"] = "development"
    os.environ["DATABASE_URL"] = f"postgresql://{DB_USER}:{db_password}@{RDS_ENDPOINT}:{RDS_PORT}/{DB_NAME}"
    os.environ["SECRET_KEY"] = "dev-secret-key-for-local-development-only"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "120"
    os.environ["DEBUG"] = "true"
    os.environ["ALLOWED_ORIGINS"] = "http://localhost:4200,http://127.0.0.1:4200"
    
    logger.info("✅ Environment variables set for RDS connection")
    logger.info(f"📍 Database URL: postgresql://{DB_USER}:***@{RDS_ENDPOINT}:{RDS_PORT}/{DB_NAME}")


def test_database_connection():
    """Test database connection"""
    logger.info("🧪 Testing database connection...")
    
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            
            if test_value == 1:
                logger.info("✅ Database connection successful!")
                return True
            else:
                logger.error("❌ Database connection test failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def run_migrations():
    """Run database migrations"""
    logger.info("🗄️  Running database migrations...")
    
    try:
        result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Database migrations completed successfully")
            return True
        else:
            logger.error(f"❌ Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        return False


def run_database_optimization():
    """Run database optimization"""
    logger.info("⚡ Running database optimization...")
    
    try:
        result = subprocess.run([sys.executable, "scripts/optimize_database.py"], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Database optimization completed successfully")
            return True
        else:
            logger.error(f"❌ Optimization failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Optimization error: {e}")
        return False


def main():
    """Main setup function"""
    logger.info("🚀 Setting up RDS connection for local development...")
    
    try:
        # Set up environment
        setup_rds_environment()
        
        # Test connection
        if not test_database_connection():
            logger.error("❌ Database connection failed. Please check:")
            logger.error("  1. Security group allows your IP")
            logger.error("  2. RDS instance is running")
            logger.error("  3. Database credentials are correct")
            sys.exit(1)
        
        # Run migrations
        if not run_migrations():
            logger.error("❌ Setup failed at migration step")
            sys.exit(1)
        
        # Run optimization
        if not run_database_optimization():
            logger.error("❌ Setup failed at optimization step")
            sys.exit(1)
        
        logger.info("✅ RDS setup completed successfully!")
        logger.info("🎉 You can now run the application with: uvicorn main:app --reload")
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
