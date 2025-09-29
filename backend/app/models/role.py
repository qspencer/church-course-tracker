"""
Role SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Role(Base):
    """Role model for system roles"""
    
    __tablename__ = "role"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, nullable=True)  # Array of permissions
    is_active = Column(Boolean, default=True, nullable=False)
    
    # CSV source tracking
    data_source = Column(String(20), nullable=True)  # 'csv', 'api', 'manual', etc.
    csv_loaded_at = Column(DateTime(timezone=True), nullable=True)  # When loaded from CSV
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    people_role = relationship("PeopleRole", back_populates="role", cascade="all, delete-orphan")
