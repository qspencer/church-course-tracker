"""
Service for managing autocomplete suggestions
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.models.autocomplete_suggestion import AutocompleteSuggestion as AutocompleteSuggestionModel
from app.schemas.autocomplete_suggestion import AutocompleteSuggestionCreate, AutocompleteSuggestionUpdate
from app.services.audit_service import AuditService


class AutocompleteSuggestionService:
    """Service for managing autocomplete suggestions"""

    def __init__(self, db: Session):
        self.db = db

    def get_suggestions(self, field_type: str, limit: int = 50) -> List[AutocompleteSuggestionModel]:
        """Get suggestions for a specific field type, ordered by usage count"""
        return (
            self.db.query(AutocompleteSuggestionModel)
            .filter(AutocompleteSuggestionModel.field_type == field_type)
            .order_by(AutocompleteSuggestionModel.usage_count.desc(), AutocompleteSuggestionModel.value.asc())
            .limit(limit)
            .all()
        )

    def get_suggestion_values(self, field_type: str, limit: int = 50) -> List[str]:
        """Get just the values (strings) for a field type"""
        suggestions = self.get_suggestions(field_type, limit)
        return [s.value for s in suggestions]

    def add_or_increment_suggestion(self, field_type: str, value: str) -> AutocompleteSuggestionModel:
        """Add a new suggestion or increment usage count if it exists"""
        # Normalize the value (trim whitespace, etc.)
        normalized_value = value.strip()
        
        # Check if suggestion already exists
        existing = (
            self.db.query(AutocompleteSuggestionModel)
            .filter(
                AutocompleteSuggestionModel.field_type == field_type,
                AutocompleteSuggestionModel.value == normalized_value
            )
            .first()
        )

        if existing:
            # Increment usage count
            existing.usage_count += 1
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new suggestion
            new_suggestion = AutocompleteSuggestionModel(
                field_type=field_type,
                value=normalized_value,
                usage_count=1
            )
            self.db.add(new_suggestion)
            self.db.commit()
            self.db.refresh(new_suggestion)
            AuditService(self.db).log_change(
                table_name=AutocompleteSuggestionModel.__tablename__,
                record_id=new_suggestion.id,
                action="insert",
                new_values={"field_type": field_type, "value": normalized_value},
                changed_by=None  # System-generated
            )
            return new_suggestion

    def add_suggestions_batch(self, field_type: str, values: List[str]) -> List[AutocompleteSuggestionModel]:
        """Add multiple suggestions at once"""
        results = []
        for value in values:
            if value and value.strip():
                suggestion = self.add_or_increment_suggestion(field_type, value)
                results.append(suggestion)
        return results

    def delete_suggestion(self, suggestion_id: int) -> bool:
        """Delete a suggestion"""
        suggestion = self.db.query(AutocompleteSuggestionModel).filter(
            AutocompleteSuggestionModel.id == suggestion_id
        ).first()
        
        if not suggestion:
            return False
        
        self.db.delete(suggestion)
        self.db.commit()
        AuditService(self.db).log_change(
            table_name=AutocompleteSuggestionModel.__tablename__,
            record_id=suggestion_id,
            action="delete",
            old_values={"field_type": suggestion.field_type, "value": suggestion.value},
            changed_by=None
        )
        return True

