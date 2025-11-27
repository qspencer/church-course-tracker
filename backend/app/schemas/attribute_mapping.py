"""
Schemas for attribute mapping between Planning Center and local models
"""

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


class AttributeMappingMatch(BaseModel):
    """A single attribute match proposal"""
    pc_attribute: str = Field(..., description="Planning Center attribute name")
    local_attribute: Optional[str] = Field(None, description="Matched local attribute name")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score (0-1)")
    is_predefined: bool = Field(False, description="Whether this is a predefined mapping")
    match_status: Literal["matched", "unmatched"] = Field(..., description="Whether a match was found")


class AttributeMappingReview(BaseModel):
    """Attribute mappings for review"""
    source_type: Literal["event", "list"] = Field(..., description="Source type from Planning Center")
    source_id: str = Field(..., description="Planning Center source ID (event_id or list_id)")
    target_type: Literal["course", "program"] = Field(..., description="Target type in CCT")
    target_id: int = Field(..., description="Target ID (course_id or program_id)")
    pc_attributes: Dict[str, Any] = Field(..., description="All Planning Center attributes")
    local_attributes: List[str] = Field(..., description="Available local attribute names")
    matches: List[AttributeMappingMatch] = Field(..., description="Proposed attribute matches")


class AttributeMappingDecision(BaseModel):
    """User's decision for a single attribute"""
    pc_attribute: str = Field(..., description="Planning Center attribute name")
    action: Literal["accept", "rematch", "custom", "ignore"] = Field(..., description="User's chosen action")
    local_attribute: Optional[str] = Field(None, description="Local attribute name (for accept/rematch)")
    custom_attribute_name: Optional[str] = Field(None, description="Custom attribute name (for custom action)")


class AttributeMappingDecisions(BaseModel):
    """User's decisions for all attributes"""
    source_type: Literal["event", "list"] = Field(..., description="Source type")
    source_id: str = Field(..., description="Planning Center source ID")
    target_type: Literal["course", "program"] = Field(..., description="Target type")
    target_id: int = Field(..., description="Target ID")
    decisions: List[AttributeMappingDecision] = Field(..., description="User's mapping decisions")

