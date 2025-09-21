"""
PlanningCenterRegistrationsCache SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class PlanningCenterRegistrationsCache(Base):
    """PlanningCenterRegistrationsCache model for cached PC Registrations data"""
    
    __tablename__ = "planning_center_registrations_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    planning_center_registration_id = Column(String(50), unique=True, index=True, nullable=False)
    planning_center_event_id = Column(String(50), nullable=False, index=True)
    planning_center_person_id = Column(String(50), nullable=False, index=True)
    registration_status = Column(String(50), nullable=True)  # registered, cancelled, waitlisted
    registration_date = Column(DateTime(timezone=True), nullable=True)
    registration_notes = Column(Text, nullable=True)
    custom_field_responses = Column(JSON, nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
