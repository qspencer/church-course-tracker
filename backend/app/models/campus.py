"""
Campus SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Campus(Base):
    """Campus model for church locations"""
    
    __tablename__ = "campus"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    planning_center_location_id = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # CSV source tracking
    data_source = Column(String(20), nullable=True)  # 'csv', 'api', 'manual', etc.
    csv_loaded_at = Column(DateTime(timezone=True), nullable=True)  # When loaded from CSV
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    people_campus = relationship("PeopleCampus", back_populates="campus", cascade="all, delete-orphan")
