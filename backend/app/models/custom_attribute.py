"""
Custom Attribute Model

Stores custom attributes imported from Planning Center that don't map to standard CCT fields.
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class CustomAttribute(Base):
    """Custom attribute model for storing Planning Center attributes that don't map to standard fields"""

    __tablename__ = "custom_attributes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Entity reference - which entity this attribute belongs to
    entity_type = Column(String(50), nullable=False, index=True)  # 'person', 'course', 'program', 'enrollment', 'program_participant'
    entity_id = Column(Integer, nullable=False, index=True)  # ID of the entity
    
    # Attribute details
    attribute_name = Column(String(200), nullable=False, index=True)  # The custom attribute name (from user input)
    pc_attribute_name = Column(String(200), nullable=True)  # Original Planning Center attribute name
    attribute_value = Column(Text, nullable=True)  # The actual value (stored as text, can be JSON stringified for complex types)
    attribute_type = Column(String(50), nullable=True)  # 'string', 'number', 'boolean', 'date', 'json'
    
    # Metadata
    source = Column(String(50), default='planning_center', nullable=False)  # 'planning_center', 'manual', etc.
    planning_center_source_id = Column(String(50), nullable=True, index=True)  # PC event/list ID where this came from
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by], lazy="select")
    updated_by_user = relationship("User", foreign_keys=[updated_by], lazy="select")
    
    # Composite index for efficient lookups
    __table_args__ = (
        {'extend_existing': True},
    )

