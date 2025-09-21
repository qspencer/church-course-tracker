"""
CourseEnrollment SQLAlchemy model (Maps to Planning Center Registrations)
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CourseEnrollment(Base):
    """CourseEnrollment model - Maps to Planning Center Registrations"""
    
    __tablename__ = "course_enrollment"
    
    id = Column(Integer, primary_key=True, index=True)
    people_id = Column(Integer, ForeignKey("people.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    planning_center_registration_id = Column(String(50), unique=True, index=True, nullable=True)
    enrollment_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="enrolled", nullable=False)  # enrolled, in_progress, completed, dropped
    progress_percentage = Column(Float, default=0.0, nullable=False)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    dependency_override = Column(Boolean, default=False, nullable=False)
    dependency_override_by = Column(Integer, nullable=True)
    planning_center_synced = Column(Boolean, default=False, nullable=False)
    registration_status = Column(String(20), nullable=True)  # registered, cancelled, waitlisted - from PC
    registration_notes = Column(Text, nullable=True)  # from PC registration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    people = relationship("People", back_populates="course_enrollments")
    course = relationship("Course", back_populates="course_enrollments")
    content_completion = relationship("ContentCompletion", back_populates="course_enrollment", cascade="all, delete-orphan")
