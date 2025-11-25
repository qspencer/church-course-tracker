"""
Program Models

This module defines the database models for program management,
including programs, participants, pairings, sessions, and progress tracking.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (JSON, Boolean, Column, DateTime, Enum, Float, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Program(Base):
    """Program model - Ongoing mentoring/discipleship programs"""

    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Flexible role system - JSON array of role definitions
    # Example: [
    #   {"name": "Mentor", "min_participants": 1, "max_participants": 1, "is_primary": true},
    #   {"name": "Mentee", "min_participants": 1, "max_participants": 3, "is_primary": false}
    # ]
    role_definitions = Column(JSON, nullable=True)  # Made nullable to match migration
    
    # Relationship configuration - JSON object
    # Example: {
    #   "allow_multiple_secondary": true,
    #   "max_secondary_per_primary": 3,
    #   "require_pairing": true,
    #   "progress_calculation": "content_based" | "session_based" | "custom"
    # }
    relationship_config = Column(JSON, nullable=True, default=lambda: {
        "allow_multiple_secondary": True,
        "max_secondary_per_primary": None,  # None = unlimited
        "require_pairing": True,
        "progress_calculation": "content_based"
    })
    
    # Optional attributes (same as courses)
    locations = Column(JSON, nullable=True)  # List of location strings
    delivery_modes = Column(JSON, nullable=True)  # List of delivery mode strings
    prerequisites = Column(JSON, nullable=True)  # List of prerequisite program/course IDs
    
    # Planning Center integration
    planning_center_event_template_id = Column(String(50), nullable=True, index=True)
    planning_center_event_id = Column(String(50), nullable=True, index=True)
    planning_center_event_name = Column(String(200), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    
    # CSV source tracking
    data_source = Column(String(20), nullable=True)
    csv_loaded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by], lazy="select")
    updated_by_user = relationship("User", foreign_keys=[updated_by], lazy="select")
    program_admins = relationship(
        "ProgramAdmin", back_populates="program", cascade="all, delete-orphan"
    )
    program_participants = relationship(
        "ProgramParticipant", back_populates="program", cascade="all, delete-orphan"
    )
    program_modules = relationship(
        "ProgramModule", back_populates="program", cascade="all, delete-orphan"
    )
    program_content = relationship(
        "ProgramContent", back_populates="program", cascade="all, delete-orphan"
    )
    program_pairings = relationship(
        "ProgramPairing", back_populates="program", cascade="all, delete-orphan"
    )
    program_sessions = relationship(
        "ProgramSession", back_populates="program", cascade="all, delete-orphan"
    )


class ProgramAdmin(Base):
    """Program administrators who can manage pairings and participants"""

    __tablename__ = "program_admins"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Permissions (for future expansion)
    can_manage_participants = Column(Boolean, default=True, nullable=False)
    can_manage_pairings = Column(Boolean, default=True, nullable=False)
    can_manage_content = Column(Boolean, default=True, nullable=False)
    can_manage_admins = Column(Boolean, default=False, nullable=False)  # Only some admins can manage other admins
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    program = relationship("Program", back_populates="program_admins")
    user = relationship("User", foreign_keys=[user_id])
    created_by_user = relationship("User", foreign_keys=[created_by])


class ProgramParticipant(Base):
    """People participating in a program with a specific role"""

    __tablename__ = "program_participants"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    people_id = Column(Integer, ForeignKey("people.id"), nullable=False, index=True)
    
    role_name = Column(String(100), nullable=False)  # Must match role_definitions in Program
    
    start_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)  # Nullable for active participants
    status = Column(
        String(20), default="active", nullable=False
    )  # "active", "paused", "completed", "ended"
    
    notes = Column(Text, nullable=True)
    
    # Progress summary
    progress_percentage = Column(Float, default=0.0, nullable=False)  # 0-100
    last_activity_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    program = relationship("Program", back_populates="program_participants")
    people = relationship("People")
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    # Pairings where this participant is primary
    primary_pairings = relationship(
        "ProgramPairing",
        foreign_keys="ProgramPairing.primary_participant_id",
        back_populates="primary_participant"
    )
    # Pairings where this participant is secondary
    secondary_pairings = relationship(
        "ProgramPairing",
        foreign_keys="ProgramPairing.secondary_participant_id",
        back_populates="secondary_participant"
    )
    program_progress = relationship(
        "ProgramProgress", back_populates="participant", cascade="all, delete-orphan"
    )


class ProgramPairing(Base):
    """Explicit pairing between participants (e.g., Mentor-Mentee relationship)"""

    __tablename__ = "program_pairings"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False, index=True)
    
    primary_participant_id = Column(
        Integer, ForeignKey("program_participants.id"), nullable=False, index=True
    )
    secondary_participant_id = Column(
        Integer, ForeignKey("program_participants.id"), nullable=False, index=True
    )
    
    # Relationship details
    start_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)  # Nullable for active pairings
    status = Column(
        String(20), default="active", nullable=False
    )  # "active", "paused", "completed", "ended"
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Program admin
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    program = relationship("Program", back_populates="program_pairings")
    primary_participant = relationship(
        "ProgramParticipant",
        foreign_keys=[primary_participant_id],
        back_populates="primary_pairings"
    )
    secondary_participant = relationship(
        "ProgramParticipant",
        foreign_keys=[secondary_participant_id],
        back_populates="secondary_pairings"
    )
    created_by_user = relationship("User", foreign_keys=[created_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    program_sessions = relationship(
        "ProgramSession", back_populates="pairing", cascade="all, delete-orphan"
    )
