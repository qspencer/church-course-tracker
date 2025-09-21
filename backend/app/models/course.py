"""
Course SQLAlchemy model (Maps to Planning Center Events)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Course(Base):
    """Course model - Maps to Planning Center Events"""
    
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    duration_weeks = Column(Integer, nullable=True)
    prerequisites = Column(JSON, nullable=True)  # List of prerequisite course IDs
    planning_center_event_id = Column(String(50), unique=True, index=True, nullable=True)
    planning_center_event_name = Column(String(200), nullable=True)
    event_start_date = Column(DateTime(timezone=True), nullable=True)
    event_end_date = Column(DateTime(timezone=True), nullable=True)
    max_capacity = Column(Integer, nullable=True)
    current_registrations = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    course_enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")
    content = relationship("Content", back_populates="course", cascade="all, delete-orphan")
    course_role = relationship("CourseRole", back_populates="course", cascade="all, delete-orphan")
    certification_courses = relationship("Certification", secondary="certification_required_courses", back_populates="required_courses")
