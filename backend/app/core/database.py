"""
Database configuration and session management with connection pooling
"""

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Database connection configuration
def get_engine_config():
    """Get database engine configuration based on environment"""
    config = {
        "echo": settings.DATABASE_ECHO,
        "pool_pre_ping": True,
    }
    
    if "sqlite" in settings.DATABASE_URL:
        # SQLite configuration
        config.update({
            "connect_args": {"check_same_thread": False},
        })
    else:
        # PostgreSQL/MySQL configuration with connection pooling
        try:
            config.update({
                "poolclass": QueuePool,
                "pool_size": settings.DATABASE_POOL_SIZE,
                "max_overflow": settings.DATABASE_MAX_OVERFLOW,
                "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
                "pool_recycle": settings.DATABASE_POOL_RECYCLE,
                "pool_pre_ping": True,
            })
        except (ValueError, TypeError) as e:
            logger.warning(f"Database pool configuration error: {e}. Using defaults.")
            config.update({
                "pool_pre_ping": True,
            })
    
    return config

# Create database engine with optimized configuration
engine = create_engine(
    settings.DATABASE_URL,
    **get_engine_config()
)

# Add connection event listeners for monitoring
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite pragmas for better performance"""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Set synchronous mode for better performance
        cursor.execute("PRAGMA synchronous=NORMAL")
        # Set cache size
        cursor.execute("PRAGMA cache_size=10000")
        # Set temp store to memory
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()

@event.listens_for(engine, "connect")
def set_postgresql_settings(dbapi_connection, connection_record):
    """Set PostgreSQL settings for better performance"""
    if "postgresql" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        # Set statement timeout
        cursor.execute("SET statement_timeout = '30s'")
        # Set lock timeout
        cursor.execute("SET lock_timeout = '10s'")
        # Set idle transaction timeout
        cursor.execute("SET idle_in_transaction_session_timeout = '60s'")
        cursor.close()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
