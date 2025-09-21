"""
PeopleCampus SQLAlchemy model
"""

from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PeopleCampus(Base):
    """PeopleCampus model for people assigned to campuses"""
    
    __tablename__ = "people_campus"
    
    id = Column(Integer, primary_key=True, index=True)
    people_id = Column(Integer, ForeignKey("people.id"), nullable=False, index=True)
    campus_id = Column(Integer, ForeignKey("campus.id"), nullable=False, index=True)
    assigned_date = Column(Date, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    people = relationship("People", back_populates="people_campus")
    campus = relationship("Campus", back_populates="people_campus")
