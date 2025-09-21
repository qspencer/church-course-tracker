"""
Certification SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Association table for many-to-many relationship between Certification and Course
certification_required_courses = Table(
    'certification_required_courses',
    Base.metadata,
    Column('certification_id', Integer, ForeignKey('certification.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True)
)


class Certification(Base):
    """Certification model for multi-course certifications"""
    
    __tablename__ = "certification"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    required_courses = Column(JSON, nullable=True)  # Array of course IDs (legacy)
    validity_months = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    required_courses = relationship("Course", secondary=certification_required_courses, back_populates="certification_courses")
    certification_progress = relationship("CertificationProgress", back_populates="certification", cascade="all, delete-orphan")
