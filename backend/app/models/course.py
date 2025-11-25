"""
Course SQLAlchemy model (Maps to Planning Center Events)
"""

from sqlalchemy import (JSON, Boolean, Column, Date, DateTime, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Course(Base):
    """Course model - Master Course (Content definition, prerequisites, modules)
    
    This is the "Master Course" that defines content, prerequisites, and structure.
    Multiple CourseInstances (Course Offerings) can be created from this master course.
    """

    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    duration_weeks = Column(Integer, nullable=True)
    prerequisites = Column(JSON, nullable=True)  # List of prerequisite course IDs
    
    # Course attributes
    instructors = Column(JSON, nullable=True)  # List of user IDs (integers) and/or "TBD" string
    locations = Column(JSON, nullable=True)  # List of location strings
    delivery_modes = Column(JSON, nullable=True)  # List of delivery mode strings (e.g., "In-person", "Online", "Hybrid")
    
    # Planning Center mapping (template/event series - not specific instance)
    planning_center_event_template_id = Column(
        String(50), nullable=True, index=True
    )  # Template/Series ID from Planning Center
    
    # Legacy fields - kept for backward compatibility during migration
    # These will be moved to CourseInstance
    planning_center_event_id = Column(
        String(50), unique=True, index=True, nullable=True
    )  # DEPRECATED - Use CourseInstance.planning_center_event_id
    planning_center_event_name = Column(String(200), nullable=True)  # DEPRECATED
    event_start_date = Column(DateTime(timezone=True), nullable=True)  # DEPRECATED
    event_end_date = Column(DateTime(timezone=True), nullable=True)  # DEPRECATED
    max_capacity = Column(Integer, nullable=True)  # DEPRECATED
    current_registrations = Column(Integer, default=0, nullable=False)  # DEPRECATED
    
    is_active = Column(Boolean, default=True, nullable=False)

    # Content settings
    content_unlock_mode = Column(
        String(20), default="immediate", nullable=False
    )  # 'immediate' or 'progressive'
    max_file_size_mb = Column(
        Integer, default=1024, nullable=False
    )  # Configurable file size limit

    # CSV source tracking
    data_source = Column(String(20), nullable=True)  # 'csv', 'api', 'manual', etc.
    csv_loaded_at = Column(
        DateTime(timezone=True), nullable=True
    )  # When loaded from CSV

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by], lazy="select")
    updated_by_user = relationship("User", foreign_keys=[updated_by], lazy="select")
    course_enrollments = relationship(
        "CourseEnrollment", back_populates="course", cascade="all, delete-orphan"
    )
    content = relationship(
        "Content", back_populates="course", cascade="all, delete-orphan"
    )  # Legacy content model
    course_content = relationship(
        "CourseContent", back_populates="course", cascade="all, delete-orphan"
    )  # New content model
    modules = relationship(
        "CourseModule", back_populates="course", cascade="all, delete-orphan"
    )
    course_role = relationship(
        "CourseRole", back_populates="course", cascade="all, delete-orphan"
    )
    course_instances = relationship(
        "CourseInstance", back_populates="course", cascade="all, delete-orphan"
    )
    certification_courses = relationship(
        "Certification",
        secondary="certification_required_courses",
        back_populates="required_courses",
    )
