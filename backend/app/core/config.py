"""
Application configuration settings with secure environment variable management
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import secrets
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings with secure defaults"""
    
    # Application
    APP_NAME: str = "Church Course Tracker"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))  # 2 hours default
    
    # CORS - Secure configuration
    ALLOWED_HOSTS: List[str] = [
        "localhost:8000",
        "127.0.0.1:8000",
        "localhost:4200",
        "127.0.0.1:4200",
        "church-course-tracker-alb-776928604.us-east-1.elb.amazonaws.com",
        "apps.quentinspencer.com",
        "apps.eastgate.church",
        "10.0.0.0/8",  # Allow internal AWS network
        "172.16.0.0/12",  # Allow internal AWS network
        "192.168.0.0/16"  # Allow internal AWS network
    ]
    ALLOWED_ORIGINS: List[str] = [
        "https://apps.quentinspencer.com",
        "https://apps.eastgate.church"
    ]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/church_course_tracker.db")
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"
    
    # Database Connection Pooling (PostgreSQL/MySQL only)
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    DATABASE_POOL_TIMEOUT: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
    DATABASE_POOL_RECYCLE: int = int(os.getenv("DATABASE_POOL_RECYCLE", "3600"))
    
    # CSV Data Loading
    LOAD_CSV_DATA: bool = os.getenv("LOAD_CSV_DATA", "false").lower() == "true"
    CSV_DATA_DIR: str = os.getenv("CSV_DATA_DIR", "data/csv")
    FORCE_RELOAD_CSV: bool = os.getenv("FORCE_RELOAD_CSV", "false").lower() == "true"
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET: Optional[str] = os.getenv("AWS_S3_BUCKET")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Planning Center API
    PLANNING_CENTER_API_URL: str = os.getenv("PLANNING_CENTER_API_URL", "https://api.planningcenteronline.com")
    PLANNING_CENTER_APP_ID: Optional[str] = os.getenv("PLANNING_CENTER_APP_ID")
    PLANNING_CENTER_SECRET: Optional[str] = os.getenv("PLANNING_CENTER_SECRET")
    PLANNING_CENTER_ACCESS_TOKEN: Optional[str] = os.getenv("PLANNING_CENTER_ACCESS_TOKEN")
    
    # Mock Planning Center API (for development)
    USE_MOCK_PLANNING_CENTER: bool = os.getenv("USE_MOCK_PLANNING_CENTER", "true").lower() == "true"
    
    # Security
    ALGORITHM: str = "HS256"
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    # File uploads
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB default
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf", "text/plain", "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse ALLOWED_ORIGINS from environment variable if provided
        if os.getenv("ALLOWED_ORIGINS"):
            origins_str = os.getenv("ALLOWED_ORIGINS")
            if origins_str:
                self.ALLOWED_ORIGINS = [origin.strip() for origin in origins_str.split(",")]
        self._validate_security_settings()
    
    def _validate_security_settings(self):
        """Validate critical security settings"""
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "your-secret-key-change-in-production":
                raise ValueError("SECRET_KEY must be set in production environment")
            
            if "*" in self.ALLOWED_HOSTS:
                logger.warning("Wildcard (*) in ALLOWED_HOSTS is not recommended for production")
            
            if not self.ALLOWED_ORIGINS:
                raise ValueError("ALLOWED_ORIGINS must be configured for production")
            
            if self.DEBUG:
                logger.warning("DEBUG mode is enabled in production - this is not recommended")
        
        # Validate secret key strength
        if len(self.SECRET_KEY) < 32:
            logger.warning("SECRET_KEY should be at least 32 characters long")
        
        # Validate token expiration
        if self.ACCESS_TOKEN_EXPIRE_MINUTES > 1440:  # 24 hours
            logger.warning("ACCESS_TOKEN_EXPIRE_MINUTES is very long - consider shorter expiration")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
