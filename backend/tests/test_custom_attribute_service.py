"""
Tests for Custom Attribute Service
"""

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.custom_attribute_service import CustomAttributeService
from app.models.custom_attribute import CustomAttribute
from app.models.member import People


class TestCustomAttributeService:
    """Test custom attribute service operations"""
    
    def test_create_custom_attribute(self, db_session):
        """Test creating a custom attribute"""
        # Create a person first
        person = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(person)
        db_session.commit()
        
        service = CustomAttributeService(db_session)
        custom_attr = service.create_custom_attribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="discipler_name",
            attribute_value="Jane Smith",
            pc_attribute_name="Discipler Name",
            attribute_type="string",
            created_by=1
        )
        
        assert custom_attr.id is not None
        assert custom_attr.entity_type == "person"
        assert custom_attr.entity_id == person.id
        assert custom_attr.attribute_name == "discipler_name"
        assert custom_attr.attribute_value == "Jane Smith"
        assert custom_attr.pc_attribute_name == "Discipler Name"
        assert custom_attr.attribute_type == "string"
        assert custom_attr.source == "planning_center"
        assert custom_attr.created_by == 1
    
    def test_get_custom_attributes(self, db_session):
        """Test getting all custom attributes for an entity"""
        # Create a person
        person = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(person)
        db_session.commit()
        
        service = CustomAttributeService(db_session)
        
        # Create multiple custom attributes
        attr1 = service.create_custom_attribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="discipler_name",
            attribute_value="Jane Smith"
        )
        attr2 = service.create_custom_attribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="testimony_entered",
            attribute_value="true",
            attribute_type="boolean"
        )
        
        # Get all attributes for this person
        attributes = service.get_custom_attributes("person", person.id)
        
        assert len(attributes) == 2
        assert attr1.id in [a.id for a in attributes]
        assert attr2.id in [a.id for a in attributes]
    
    def test_get_custom_attribute(self, db_session):
        """Test getting a specific custom attribute"""
        person = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(person)
        db_session.commit()
        
        service = CustomAttributeService(db_session)
        created = service.create_custom_attribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="discipler_name",
            attribute_value="Jane Smith"
        )
        
        retrieved = service.get_custom_attribute(
            "person",
            person.id,
            "discipler_name"
        )
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.attribute_value == "Jane Smith"
    
    def test_update_custom_attribute(self, db_session):
        """Test updating a custom attribute"""
        person = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(person)
        db_session.commit()
        
        service = CustomAttributeService(db_session)
        created = service.create_custom_attribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="discipler_name",
            attribute_value="Jane Smith"
        )
        
        updated = service.update_custom_attribute(
            "person",
            person.id,
            "discipler_name",
            "John Doe",
            updated_by=2
        )
        
        assert updated is not None
        assert updated.attribute_value == "John Doe"
        assert updated.updated_by == 2
    
    def test_delete_custom_attribute(self, db_session):
        """Test deleting a custom attribute"""
        person = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(person)
        db_session.commit()
        
        service = CustomAttributeService(db_session)
        created = service.create_custom_attribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="discipler_name",
            attribute_value="Jane Smith"
        )
        
        deleted = service.delete_custom_attribute(
            "person",
            person.id,
            "discipler_name"
        )
        
        assert deleted is True
        
        # Verify it's gone
        retrieved = service.get_custom_attribute(
            "person",
            person.id,
            "discipler_name"
        )
        assert retrieved is None
    
    def test_apply_attribute_mappings(self, db_session):
        """Test applying attribute mappings to create custom attributes"""
        person = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(person)
        db_session.commit()
        
        service = CustomAttributeService(db_session)
        
        pc_attributes = {
            "first_name": "John",
            "Discipler Name": "Jane Smith",
            "Testimony Entered?": "Yes",
            "Date Life on Life Discipleship Started": "2024-01-15"
        }
        
        mapping_decisions = [
            {
                "pc_attribute": "first_name",
                "action": "accept",
                "local_attribute": "first_name"
            },
            {
                "pc_attribute": "Discipler Name",
                "action": "custom",
                "custom_attribute_name": "discipler_name"
            },
            {
                "pc_attribute": "Testimony Entered?",
                "action": "custom",
                "custom_attribute_name": "testimony_entered"
            },
            {
                "pc_attribute": "Date Life on Life Discipleship Started",
                "action": "ignore"
            }
        ]
        
        result = service.apply_attribute_mappings(
            pc_attributes=pc_attributes,
            mapping_decisions=mapping_decisions,
            entity_type="person",
            entity_id=person.id,
            planning_center_source_id="pc_list_123",
            created_by=1
        )
        
        # Check mapped attributes
        assert "first_name" in result["mapped_attributes"]
        assert result["mapped_attributes"]["first_name"] == "John"
        
        # Check custom attributes were created
        assert len(result["custom_attributes_created"]) == 2
        
        custom_attrs = service.get_custom_attributes("person", person.id)
        assert len(custom_attrs) == 2
        
        # Verify custom attribute values
        discipler_attr = service.get_custom_attribute("person", person.id, "discipler_name")
        assert discipler_attr is not None
        assert discipler_attr.attribute_value == "Jane Smith"
        assert discipler_attr.pc_attribute_name == "Discipler Name"
        
        testimony_attr = service.get_custom_attribute("person", person.id, "testimony_entered")
        assert testimony_attr is not None
        assert testimony_attr.attribute_value == "Yes"
    
    def test_infer_attribute_type(self, db_session):
        """Test automatic attribute type inference"""
        person = People(
            planning_center_id="pc_123",
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db_session.add(person)
        db_session.commit()
        
        service = CustomAttributeService(db_session)
        
        # Test string
        attr1 = service.create_custom_attribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="test_string",
            attribute_value="Some text"
        )
        assert attr1.attribute_type == "string"
        
        # Test number
        attr2 = service.create_custom_attribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="test_number",
            attribute_value=42
        )
        assert attr2.attribute_type == "number"
        
        # Test boolean
        attr3 = service.create_custom_attribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="test_boolean",
            attribute_value=True
        )
        assert attr3.attribute_type == "boolean"
        
        # Test date
        attr4 = service.create_custom_attribute(
            entity_type="person",
            entity_id=person.id,
            attribute_name="test_date",
            attribute_value="2024-01-15"
        )
        assert attr4.attribute_type == "date"

