"""
Content SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Content(Base):
    """Content model for course content/modules"""
    
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content_type_id = Column(Integer, ForeignKey("content_type.id"), nullable=False, index=True)
    order_sequence = Column(Integer, nullable=False, default=0)
    file_path = Column(String(500), nullable=True)
    url = Column(String(500), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    is_required = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    course = relationship("Course", back_populates="content")
    content_type = relationship("ContentType", back_populates="content")
    content_completion = relationship("ContentCompletion", back_populates="content", cascade="all, delete-orphan")
