"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Church Course Tracker"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    ALLOWED_HOSTS: List[str] = [
        "localhost:8000",
        "127.0.0.1:8000",
        "localhost:4200",
        "127.0.0.1:4200",
        "*",
        "church-course-tracker-alb-776928604.us-east-1.elb.amazonaws.com",
        "apps.eastgate.church",
        "10.0.0.0/8",  # Allow internal AWS network
        "172.16.0.0/12",  # Allow internal AWS network
        "192.168.0.0/16"  # Allow internal AWS network
    ]
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://apps.quentinspencer.com",
        "https://apps.eastgate.church"
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/church_course_tracker.db"
    DATABASE_ECHO: bool = False
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # Planning Center API
    PLANNING_CENTER_API_URL: str = "https://api.planningcenteronline.com"
    PLANNING_CENTER_APP_ID: Optional[str] = None
    PLANNING_CENTER_SECRET: Optional[str] = None
    PLANNING_CENTER_ACCESS_TOKEN: Optional[str] = None
    
    # Mock Planning Center API (for development)
    USE_MOCK_PLANNING_CENTER: bool = True  # Set to False to use real API
    
    # Security
    ALGORITHM: str = "HS256"
    
    # File uploads
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
