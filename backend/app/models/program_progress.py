"""
Program Progress and Session SQLAlchemy models

Flexible progress tracking for programs including sessions and milestones.
"""

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, JSON,
                        String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ProgramSession(Base):
    """Logs meetings/sessions between participants"""
    
    __tablename__ = "program_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    pairing_id = Column(
        Integer, ForeignKey("program_pairings.id"), nullable=True, index=True
    )  # Optional - could be group session
    
    # Session details
    session_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    location = Column(String(255), nullable=True)
    session_type = Column(
        String(50), nullable=True
    )  # "in_person", "online", "phone", "video_call", etc.
    
    # Participants who attended
    participant_ids = Column(JSON, nullable=True)  # List of ProgramParticipant IDs
    
    # Session content/topics
    topics_covered = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Progress tracking
    content_completed = Column(JSON, nullable=True)  # List of ProgramContent IDs completed
    milestones_achieved = Column(JSON, nullable=True)  # List of milestone names/IDs
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who logged the session
    
    # Relationships
    program = relationship("Program", back_populates="program_sessions")
    pairing = relationship("ProgramPairing", back_populates="program_sessions")
    created_by_user = relationship("User", foreign_keys=[created_by], lazy="select")
    program_progress = relationship(
        "ProgramProgress",
        foreign_keys="ProgramProgress.session_id",
        back_populates="session"
    )


class ProgramProgress(Base):
    """Flexible progress tracking for programs"""
    
    __tablename__ = "program_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    participant_id = Column(
        Integer, ForeignKey("program_participants.id"), nullable=False, index=True
    )
    
    # Progress type
    progress_type = Column(
        String(50), nullable=False
    )  # "content_completion", "session_completion", "milestone"
    
    # Content completion (if progress_type is "content_completion")
    content_id = Column(
        Integer, ForeignKey("program_content.id"), nullable=True, index=True
    )
    completion_date = Column(DateTime(timezone=True), nullable=True)
    completion_percentage = Column(Integer, nullable=True)  # 0-100
    
    # Session completion (if progress_type is "session_completion")
    session_id = Column(
        Integer, ForeignKey("program_sessions.id"), nullable=True, index=True
    )
    
    # Milestone (if progress_type is "milestone")
    milestone_name = Column(String(200), nullable=True)
    milestone_description = Column(Text, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    program = relationship("Program")
    participant = relationship("ProgramParticipant", back_populates="program_progress")
    content = relationship("ProgramContent", foreign_keys=[content_id], back_populates="program_progress")
    session = relationship("ProgramSession", back_populates="program_progress")
    created_by_user = relationship("User", foreign_keys=[created_by], lazy="select")

