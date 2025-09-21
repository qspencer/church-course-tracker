"""
CourseRole SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CourseRole(Base):
    """CourseRole model for course-specific roles"""
    
    __tablename__ = "course_role"
    
    id = Column(Integer, primary_key=True, index=True)
    people_id = Column(Integer, ForeignKey("people.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    role_type = Column(String(50), nullable=False)  # teacher, student, assistant, observer
    assigned_date = Column(Date, nullable=False)
    assigned_by = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    people = relationship("People", back_populates="course_role")
    course = relationship("Course", back_populates="course_role")
