"""
CourseInstance SQLAlchemy model (Course Offering)
Represents a specific offering of a Master Course with dates, schedule, and teachers
"""

from sqlalchemy import (JSON, Boolean, Column, Date, DateTime, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class CourseInstance(Base):
    """CourseInstance model - Specific offering of a Master Course (Course Offering)"""

    __tablename__ = "course_instances"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    instance_name = Column(String(200), nullable=False)  # e.g., "Fall 2024 - Session A"
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    schedule = Column(JSON, nullable=True)  # Optional: {"day_of_week": "Monday", "time": "19:00", "frequency": "weekly"}
    max_capacity = Column(Integer, nullable=True)
    current_enrollments = Column(Integer, default=0, nullable=False)
    
    # Planning Center mapping (specific event)
    planning_center_event_id = Column(String(50), unique=True, index=True, nullable=True)
    planning_center_event_name = Column(String(200), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    enrollment_open = Column(Boolean, default=True, nullable=False)
    enrollment_deadline = Column(DateTime(timezone=True), nullable=True)
    
    # Location
    campus_id = Column(Integer, ForeignKey("campus.id"), nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    course = relationship("Course", back_populates="course_instances")
    campus = relationship("Campus", foreign_keys=[campus_id])
    teachers = relationship(
        "CourseInstanceTeacher", back_populates="course_instance", cascade="all, delete-orphan"
    )
    enrollments = relationship(
        "CourseEnrollment", back_populates="course_instance", cascade="all, delete-orphan"
    )
    created_by_user = relationship("User", foreign_keys=[created_by], lazy="select")
    updated_by_user = relationship("User", foreign_keys=[updated_by], lazy="select")


class CourseInstanceTeacher(Base):
    """Teacher/Mentor for a Course Instance"""

    __tablename__ = "course_instance_teachers"

    id = Column(Integer, primary_key=True, index=True)
    course_instance_id = Column(Integer, ForeignKey("course_instances.id"), nullable=False, index=True)
    people_id = Column(Integer, ForeignKey("people.id"), nullable=False, index=True)
    role_type = Column(
        String(50), nullable=False
    )  # 'teacher', 'mentor', 'assistant', 'co-teacher'
    assigned_date = Column(Date, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)  # Primary teacher/mentor
    max_students = Column(Integer, nullable=True)  # For 1:1 discipleship tracking
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    course_instance = relationship("CourseInstance", back_populates="teachers")
    people = relationship("People", back_populates="teaching_instances")
    assigned_students = relationship(
        "CourseEnrollment",
        foreign_keys="CourseEnrollment.assigned_teacher_id",
        back_populates="assigned_teacher"
    )
    created_by_user = relationship("User", foreign_keys=[created_by], lazy="select")
    updated_by_user = relationship("User", foreign_keys=[updated_by], lazy="select")

