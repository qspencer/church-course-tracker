"""
PeopleCampus SQLAlchemy model
"""

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class PeopleCampus(Base):
    """PeopleCampus model for people assigned to campuses"""

    __tablename__ = "people_campus"

    # No index=True on this PK: it is already indexed as the primary key, and
    # SQLAlchemy's auto-name ix_people_campus_id collided with the index that
    # people.campus_id (index=True) generates - a database-global name clash
    # that made Base.metadata.create_all() fail on the first test of each run.
    id = Column(Integer, primary_key=True)
    people_id = Column(Integer, ForeignKey("people.id"), nullable=False, index=True)
    campus_id = Column(Integer, ForeignKey("campus.id"), nullable=False, index=True)
    assigned_date = Column(Date, nullable=False)
    unassigned_date = Column(Date, nullable=True)  # When assignment ended (NULL = current)
    is_primary = Column(Boolean, default=False, nullable=False)  # Deprecated - kept for historical data
    is_active = Column(Boolean, default=True, nullable=False)  # FALSE if unassigned_date is set
    notes = Column(Text, nullable=True)  # Reason for change
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)

    # Relationships
    people = relationship("People", back_populates="people_campus")
    campus = relationship("Campus", back_populates="people_campus")
