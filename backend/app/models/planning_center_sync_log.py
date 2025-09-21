"""
PlanningCenterSyncLog SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class PlanningCenterSyncLog(Base):
    """PlanningCenterSyncLog model for sync tracking"""
    
    __tablename__ = "planning_center_sync_log"
    
    id = Column(Integer, primary_key=True, index=True)
    sync_type = Column(String(50), nullable=False)  # people, events, registrations, custom_fields
    sync_direction = Column(String(20), nullable=False)  # from_pc, to_pc
    records_processed = Column(Integer, default=0, nullable=False)
    records_successful = Column(Integer, default=0, nullable=False)
    records_failed = Column(Integer, default=0, nullable=False)
    error_details = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, nullable=True)
