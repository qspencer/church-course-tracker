"""
CourseEnrollment SQLAlchemy model (Maps to Planning Center Registrations)
"""

from sqlalchemy import (Boolean, Column, Date, DateTime, Float, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class CourseEnrollment(Base):
    """CourseEnrollment model - Maps to Planning Center Registrations"""

    __tablename__ = "course_enrollment"

    id = Column(Integer, primary_key=True, index=True)
    people_id = Column(Integer, ForeignKey("people.id"), nullable=False, index=True)
    course_instance_id = Column(Integer, ForeignKey("course_instances.id"), nullable=True, index=True)
    
    # Legacy field - kept for backward compatibility during migration
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True, index=True)  # DEPRECATED - Use course_instance_id
    
    # Teacher assignment for discipleship tracking
    assigned_teacher_id = Column(Integer, ForeignKey("course_instance_teachers.id"), nullable=True, index=True)
    
    planning_center_registration_id = Column(
        String(50), unique=True, index=True, nullable=True
    )
    enrollment_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(
        String(20), default="enrolled", nullable=False
    )  # enrolled, in_progress, completed, dropped
    progress_percentage = Column(Float, default=0.0, nullable=False)
    completion_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    dependency_override = Column(Boolean, default=False, nullable=False)
    dependency_override_by = Column(Integer, nullable=True)
    planning_center_synced = Column(Boolean, default=False, nullable=False)
    registration_status = Column(
        String(20), nullable=True
    )  # registered, cancelled, waitlisted - from PC
    registration_notes = Column(Text, nullable=True)  # from PC registration

    # CSV source tracking
    data_source = Column(String(20), nullable=True)  # 'csv', 'api', 'manual', etc.
    csv_loaded_at = Column(
        DateTime(timezone=True), nullable=True
    )  # When loaded from CSV

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    # Relationships
    people = relationship("People", back_populates="course_enrollments")
    course_instance = relationship("CourseInstance", back_populates="enrollments", lazy="select")
    course = relationship("Course", foreign_keys=[course_id])  # Legacy relationship
    assigned_teacher = relationship(
        "CourseInstanceTeacher",
        foreign_keys=[assigned_teacher_id],
        back_populates="assigned_students"
    )
    content_completion = relationship(
        "ContentCompletion",
        back_populates="course_enrollment",
        cascade="all, delete-orphan",
    )
