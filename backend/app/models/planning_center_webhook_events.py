"""
PlanningCenterWebhookEvents SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class PlanningCenterWebhookEvents(Base):
    """PlanningCenterWebhookEvents model for webhook tracking"""
    
    __tablename__ = "planning_center_webhook_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)  # person.created, event.created, registration.created, etc.
    planning_center_id = Column(String(50), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    processed = Column(Boolean, default=False, nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
