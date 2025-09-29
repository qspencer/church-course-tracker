"""
People SQLAlchemy model (from Planning Center)
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class People(Base):
    """People model for church members from Planning Center"""
    
    __tablename__ = "people"
    
    id = Column(Integer, primary_key=True, index=True)
    planning_center_id = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    address1 = Column(String(255), nullable=True)
    address2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    zip = Column(String(20), nullable=True)
    household_id = Column(String(50), nullable=True)
    household_name = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True, default="active")
    join_date = Column(Date, nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # CSV source tracking
    data_source = Column(String(20), nullable=True)  # 'csv', 'api', 'manual', etc.
    csv_loaded_at = Column(DateTime(timezone=True), nullable=True)  # When loaded from CSV
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)
    
    # Relationships
    course_enrollments = relationship("CourseEnrollment", back_populates="people", cascade="all, delete-orphan")
    people_campus = relationship("PeopleCampus", back_populates="people", cascade="all, delete-orphan")
    people_role = relationship("PeopleRole", back_populates="people", cascade="all, delete-orphan")
    course_role = relationship("CourseRole", back_populates="people", cascade="all, delete-orphan")
    certification_progress = relationship("CertificationProgress", back_populates="people", cascade="all, delete-orphan")
