"""
PlanningCenterEventsCache SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class PlanningCenterEventsCache(Base):
    """PlanningCenterEventsCache model for cached PC Events data"""
    
    __tablename__ = "planning_center_events_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    planning_center_event_id = Column(String(50), unique=True, index=True, nullable=False)
    event_name = Column(String(200), nullable=False)
    event_description = Column(Text, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    max_capacity = Column(Integer, nullable=True)
    current_registrations_count = Column(Integer, default=0, nullable=False)
    registration_deadline = Column(DateTime(timezone=True), nullable=True)
    event_status = Column(String(50), nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
