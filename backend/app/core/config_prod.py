"""
Production configuration settings for AWS deployment
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class ProductionSettings(BaseSettings):
    """Production settings optimized for AWS"""
    
    # Application
    APP_NAME: str = "Church Course Tracker"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS - Update with your domain
    ALLOWED_HOSTS: List[str] = [
        "your-domain.com",
        "api.your-domain.com",
        "*.amazonaws.com"
    ]
    ALLOWED_ORIGINS: List[str] = [
        "https://your-domain.com",
        "https://www.your-domain.com"
    ]
    
    # Database - RDS PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@rds-endpoint:5432/church_course_tracker")
    DATABASE_ECHO: bool = False
    
    # Planning Center API
    PLANNING_CENTER_API_URL: str = "https://api.planningcenteronline.com"
    PLANNING_CENTER_APP_ID: Optional[str] = os.getenv("PLANNING_CENTER_APP_ID")
    PLANNING_CENTER_SECRET: Optional[str] = os.getenv("PLANNING_CENTER_SECRET")
    PLANNING_CENTER_ACCESS_TOKEN: Optional[str] = os.getenv("PLANNING_CENTER_ACCESS_TOKEN")
    
    # Security
    ALGORITHM: str = "HS256"
    
    # File uploads - S3
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR: str = "/tmp/uploads"  # Temporary local storage
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET: Optional[str] = os.getenv("AWS_S3_BUCKET")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env.production"
        case_sensitive = True


# Create production settings instance
settings = ProductionSettings()
