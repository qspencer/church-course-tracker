"""
CertificationProgress SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CertificationProgress(Base):
    """CertificationProgress model for certification tracking"""
    
    __tablename__ = "certification_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    people_id = Column(Integer, ForeignKey("people.id"), nullable=False, index=True)
    certification_id = Column(Integer, ForeignKey("certification.id"), nullable=False, index=True)
    started_date = Column(Date, nullable=False)
    completed_date = Column(Date, nullable=True)
    status = Column(String(20), default="in_progress", nullable=False)  # in_progress, completed, expired
    expires_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    people = relationship("People", back_populates="certification_progress")
    certification = relationship("Certification", back_populates="certification_progress")
