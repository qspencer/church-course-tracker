"""
PeopleRole SQLAlchemy model
"""

from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PeopleRole(Base):
    """PeopleRole model for people's system roles"""
    
    __tablename__ = "people_role"
    
    id = Column(Integer, primary_key=True, index=True)
    people_id = Column(Integer, ForeignKey("people.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False, index=True)
    assigned_date = Column(Date, nullable=False)
    assigned_by = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    people = relationship("People", back_populates="people_role")
    role = relationship("Role", back_populates="people_role")
