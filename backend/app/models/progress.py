"""
ContentCompletion SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ContentCompletion(Base):
    """ContentCompletion model for content-level progress tracking"""
    
    __tablename__ = "content_completion"
    
    id = Column(Integer, primary_key=True, index=True)
    course_enrollment_id = Column(Integer, ForeignKey("course_enrollment.id"), nullable=False, index=True)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    time_spent_minutes = Column(Integer, nullable=True)
    score = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    course_enrollment = relationship("CourseEnrollment", back_populates="content_completion")
    content = relationship("Content", back_populates="content_completion")
