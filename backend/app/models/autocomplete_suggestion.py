"""
Autocomplete Suggestion model for storing user-entered values for auto-complete functionality
"""

from sqlalchemy import Column, Integer, String, DateTime, Index
from sqlalchemy.sql import func

from app.core.database import Base


class AutocompleteSuggestion(Base):
    """Model for storing autocomplete suggestions for various field types"""

    __tablename__ = "autocomplete_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    field_type = Column(String(50), nullable=False, index=True)  # e.g., 'location', 'delivery_mode'
    value = Column(String(200), nullable=False, index=True)  # The actual suggestion value
    usage_count = Column(Integer, default=1, nullable=False)  # Track how often it's used
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        Index('ix_autocomplete_suggestions_field_type_value', 'field_type', 'value', unique=True),
    )

