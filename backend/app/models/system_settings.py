"""
System Settings SQLAlchemy model
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class SystemSettings(Base):
    """System Settings model for storing application configuration"""

    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, index=True)  # 'system', 'planning_center', 'security', 'backup'
    data_type = Column(String(20), nullable=False)  # 'string', 'integer', 'boolean', 'json'
    description = Column(Text, nullable=True)
    is_sensitive = Column(Boolean, default=False, nullable=False)  # For passwords/secrets
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)  # User ID who last updated
