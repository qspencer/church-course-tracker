"""
API endpoints for autocomplete suggestions
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.autocomplete_suggestion import AutocompleteSuggestion
from app.services.autocomplete_suggestion_service import AutocompleteSuggestionService

router = APIRouter()


@router.get("/{field_type}", response_model=List[str])
async def get_suggestions(
    field_type: str,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of suggestions to return"),
    db: Session = Depends(get_db)
):
    """
    Get autocomplete suggestions for a specific field type
    
    Supported field types:
    - 'location': Location suggestions
    - 'delivery_mode': Delivery mode suggestions
    """
    service = AutocompleteSuggestionService(db)
    return service.get_suggestion_values(field_type, limit)


@router.post("/{field_type}", response_model=AutocompleteSuggestion)
async def add_suggestion(
    field_type: str,
    value: str = Query(..., description="The suggestion value to add"),
    db: Session = Depends(get_db)
):
    """
    Add or increment a suggestion for a field type
    If the suggestion already exists, its usage count is incremented
    """
    service = AutocompleteSuggestionService(db)
    return service.add_or_increment_suggestion(field_type, value)


@router.post("/{field_type}/batch", response_model=List[AutocompleteSuggestion])
async def add_suggestions_batch(
    field_type: str,
    values: List[str],
    db: Session = Depends(get_db)
):
    """
    Add multiple suggestions at once for a field type
    """
    service = AutocompleteSuggestionService(db)
    return service.add_suggestions_batch(field_type, values)

