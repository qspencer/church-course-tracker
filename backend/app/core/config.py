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
    ALLOWED_HOSTS: List[str] = ["*"]  # Configure properly for production
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/church_course_tracker.db"
    DATABASE_ECHO: bool = False
    
    # Planning Center API
    PLANNING_CENTER_API_URL: str = "https://api.planningcenteronline.com"
    PLANNING_CENTER_APP_ID: Optional[str] = None
    PLANNING_CENTER_SECRET: Optional[str] = None
    
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
