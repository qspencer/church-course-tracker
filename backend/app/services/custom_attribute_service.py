"""
Custom Attribute Service

Service for managing custom attributes imported from Planning Center.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.custom_attribute import CustomAttribute as CustomAttributeModel
from datetime import datetime, timezone


class CustomAttributeService:
    """Service for custom attribute operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_custom_attribute(
        self,
        entity_type: str,
        entity_id: int,
        attribute_name: str,
        attribute_value: Any,
        pc_attribute_name: Optional[str] = None,
        attribute_type: Optional[str] = None,
        source: str = 'planning_center',
        planning_center_source_id: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> CustomAttributeModel:
        """Create a new custom attribute"""
        
        # Determine attribute type if not provided
        if attribute_type is None:
            attribute_type = self._infer_attribute_type(attribute_value)
        
        # Convert value to string for storage
        value_str = self._value_to_string(attribute_value, attribute_type)
        
        custom_attr = CustomAttributeModel(
            entity_type=entity_type,
            entity_id=entity_id,
            attribute_name=attribute_name,
            pc_attribute_name=pc_attribute_name,
            attribute_value=value_str,
            attribute_type=attribute_type,
            source=source,
            planning_center_source_id=planning_center_source_id,
            created_by=created_by
        )
        
        self.db.add(custom_attr)
        self.db.commit()
        self.db.refresh(custom_attr)
        return custom_attr

    def get_custom_attributes(
        self,
        entity_type: str,
        entity_id: int
    ) -> List[CustomAttributeModel]:
        """Get all custom attributes for an entity"""
        return (
            self.db.query(CustomAttributeModel)
            .filter(
                and_(
                    CustomAttributeModel.entity_type == entity_type,
                    CustomAttributeModel.entity_id == entity_id
                )
            )
            .all()
        )

    def get_custom_attribute(
        self,
        entity_type: str,
        entity_id: int,
        attribute_name: str
    ) -> Optional[CustomAttributeModel]:
        """Get a specific custom attribute"""
        return (
            self.db.query(CustomAttributeModel)
            .filter(
                and_(
                    CustomAttributeModel.entity_type == entity_type,
                    CustomAttributeModel.entity_id == entity_id,
                    CustomAttributeModel.attribute_name == attribute_name
                )
            )
            .first()
        )

    def get_custom_attribute_by_id(
        self,
        attribute_id: int
    ) -> Optional[CustomAttributeModel]:
        """Get a custom attribute by ID"""
        return (
            self.db.query(CustomAttributeModel)
            .filter(CustomAttributeModel.id == attribute_id)
            .first()
        )

    def update_custom_attribute(
        self,
        entity_type: str,
        entity_id: int,
        attribute_name: str,
        attribute_value: Any,
        updated_by: Optional[int] = None
    ) -> Optional[CustomAttributeModel]:
        """Update an existing custom attribute"""
        custom_attr = self.get_custom_attribute(entity_type, entity_id, attribute_name)
        if not custom_attr:
            return None
        
        attribute_type = self._infer_attribute_type(attribute_value)
        value_str = self._value_to_string(attribute_value, attribute_type)
        
        custom_attr.attribute_value = value_str
        custom_attr.attribute_type = attribute_type
        custom_attr.updated_at = datetime.now(timezone.utc)
        custom_attr.updated_by = updated_by
        
        self.db.commit()
        self.db.refresh(custom_attr)
        return custom_attr

    def delete_custom_attribute(
        self,
        entity_type: str,
        entity_id: int,
        attribute_name: str
    ) -> bool:
        """Delete a custom attribute"""
        custom_attr = self.get_custom_attribute(entity_type, entity_id, attribute_name)
        if not custom_attr:
            return False
        
        self.db.delete(custom_attr)
        self.db.commit()
        return True

    def _infer_attribute_type(self, value: Any) -> str:
        """Infer the attribute type from the value"""
        if value is None:
            return 'string'
        if isinstance(value, bool):
            return 'boolean'
        if isinstance(value, (int, float)):
            return 'number'
        if isinstance(value, (dict, list)):
            return 'json'
        if isinstance(value, datetime) or (isinstance(value, str) and self._is_date_string(value)):
            return 'date'
        return 'string'

    def _is_date_string(self, value: str) -> bool:
        """Check if a string looks like a date"""
        import re
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'^\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'^\d{4}-\d{2}-\d{2}T',  # ISO datetime
        ]
        return any(re.match(pattern, value) for pattern in date_patterns)

    def _value_to_string(self, value: Any, attribute_type: str) -> str:
        """Convert value to string for storage"""
        if value is None:
            return ''
        if attribute_type == 'json':
            import json
            return json.dumps(value)
        if attribute_type == 'date' and isinstance(value, datetime):
            return value.isoformat()
        return str(value)

    def apply_attribute_mappings(
        self,
        pc_attributes: Dict[str, Any],
        mapping_decisions: List[Dict[str, Any]],
        entity_type: str,
        entity_id: int,
        planning_center_source_id: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Apply attribute mapping decisions to PC attributes
        
        Returns:
            Dictionary with:
            - 'mapped_attributes': Attributes mapped to standard fields
            - 'custom_attributes_created': List of created custom attributes
        """
        mapped_attributes = {}
        custom_attributes_created = []
        
        # Build a decision lookup
        decisions_by_pc_attr = {
            decision['pc_attribute']: decision
            for decision in mapping_decisions
        }
        
        for pc_attr, pc_value in pc_attributes.items():
            if pc_attr not in decisions_by_pc_attr:
                # No decision made, skip it
                continue
            
            decision = decisions_by_pc_attr[pc_attr]
            action = decision.get('action')
            
            if action == 'accept' or action == 'rematch':
                # Map to standard field
                local_attr = decision.get('local_attribute')
                if local_attr:
                    mapped_attributes[local_attr] = pc_value
            elif action == 'custom':
                # Save as custom attribute
                custom_name = decision.get('custom_attribute_name')
                if custom_name:
                    custom_attr = self.create_custom_attribute(
                        entity_type=entity_type,
                        entity_id=entity_id,
                        attribute_name=custom_name,
                        attribute_value=pc_value,
                        pc_attribute_name=pc_attr,
                        planning_center_source_id=planning_center_source_id,
                        created_by=created_by
                    )
                    custom_attributes_created.append(custom_attr)
            # 'ignore' action - do nothing
        
        return {
            'mapped_attributes': mapped_attributes,
            'custom_attributes_created': custom_attributes_created
        }

