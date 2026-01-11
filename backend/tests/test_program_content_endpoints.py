"""
Tests for program content API endpoints
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from app.models.program import Program
from app.models.program_content import ProgramModule, ProgramContent
from app.schemas.program_content import (
    ProgramModuleCreate, ProgramContentCreate
)


class TestProgramContentEndpoints:
    """Test program content API endpoints"""
    
    def test_create_program_module_success(self, client: TestClient, admin_token, db_session):
        """Test creating a program module (category) successfully"""
        # Create a program first
        program = Program(
            title="Test Program",
            description="Test Description",
            is_active=True
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)
        
        # Setup
        module_data = {
            "program_id": program.id,
            "title": "Category 1",
            "description": "First category",
            "order_index": 1
        }
        
        # Execute
        response = client.post(
            "/api/v1/program-content/modules/",
            json=module_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Verify
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Category 1"
        assert data["description"] == "First category"
        assert data["order_index"] == 1
        assert data["is_active"] is True
        assert data["program_id"] == program.id
    
    def test_create_program_module_unauthorized(self, client: TestClient):
        """Test creating a program module without authentication"""
        module_data = {
            "program_id": 1,
            "title": "Category 1",
            "order_index": 1
        }
        
        response = client.post("/api/v1/program-content/modules/", json=module_data)
        
        assert response.status_code == 401
    
    def test_get_program_modules(self, client: TestClient, admin_token, db_session):
        """Test getting program modules"""
        # Create a program and module
        program = Program(
            title="Test Program",
            description="Test Description",
            is_active=True
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)
        
        module = ProgramModule(
            program_id=program.id,
            title="Category 1",
            order_index=1
        )
        db_session.add(module)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/program-content/modules/{program.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["title"] == "Category 1"
    
    def test_get_program_module(self, client: TestClient, admin_token, db_session):
        """Test getting a specific program module"""
        # Create a program and module
        program = Program(
            title="Test Program",
            description="Test Description",
            is_active=True
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)
        
        module = ProgramModule(
            program_id=program.id,
            title="Category 1",
            order_index=1
        )
        db_session.add(module)
        db_session.commit()
        db_session.refresh(module)
        
        response = client.get(
            f"/api/v1/program-content/modules/single/{module.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == module.id
        assert data["title"] == "Category 1"
    
    def test_update_program_module(self, client: TestClient, admin_token, db_session):
        """Test updating a program module"""
        # Create a program and module
        program = Program(
            title="Test Program",
            description="Test Description",
            is_active=True
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)
        
        module = ProgramModule(
            program_id=program.id,
            title="Category 1",
            order_index=1
        )
        db_session.add(module)
        db_session.commit()
        db_session.refresh(module)
        
        update_data = {
            "title": "Updated Category",
            "order_index": 2
        }
        
        response = client.put(
            f"/api/v1/program-content/modules/{module.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Category"
        assert data["order_index"] == 2
    
    def test_delete_program_module(self, client: TestClient, admin_token, db_session):
        """Test deleting a program module"""
        # Create a program and module
        program = Program(
            title="Test Program",
            description="Test Description",
            is_active=True
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)
        
        module = ProgramModule(
            program_id=program.id,
            title="Category 1",
            order_index=1
        )
        db_session.add(module)
        db_session.commit()
        db_session.refresh(module)
        
        response = client.delete(
            f"/api/v1/program-content/modules/{module.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 204
        
        # Verify it's deleted
        deleted_module = db_session.query(ProgramModule).filter(ProgramModule.id == module.id).first()
        assert deleted_module is None
    
    def test_create_program_content_success(self, client: TestClient, admin_token, db_session):
        """Test creating program content (lesson) successfully"""
        # Create a program first
        program = Program(
            title="Test Program",
            description="Test Description",
            is_active=True
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)
        
        # Setup
        content_data = {
            "program_id": program.id,
            "title": "Lesson 1",
            "description": "First lesson",
            "content_type": "document",
            "order_index": 1
        }
        
        # Execute
        response = client.post(
            "/api/v1/program-content/",
            json=content_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Verify
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Lesson 1"
        assert data["description"] == "First lesson"
        assert data["order_index"] == 1
        assert data["program_id"] == program.id
    
    def test_create_program_content_with_module(self, client: TestClient, admin_token, db_session):
        """Test creating program content with a module (category)"""
        # Create a program and module
        program = Program(
            title="Test Program",
            description="Test Description",
            is_active=True
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)
        
        module = ProgramModule(
            program_id=program.id,
            title="Category 1",
            order_index=1
        )
        db_session.add(module)
        db_session.commit()
        db_session.refresh(module)
        
        # Create content linked to module
        content_data = {
            "program_id": program.id,
            "module_id": module.id,
            "title": "Lesson 1",
            "content_type": "document",
            "order_index": 1
        }
        
        response = client.post(
            "/api/v1/program-content/",
            json=content_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["module_id"] == module.id
        assert data["title"] == "Lesson 1"
    
    def test_get_program_content(self, client: TestClient, admin_token, db_session):
        """Test getting program content"""
        # Create a program and content
        program = Program(
            title="Test Program",
            description="Test Description",
            is_active=True
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)
        
        content = ProgramContent(
            program_id=program.id,
            title="Lesson 1",
            content_type="document",
            order_index=1
        )
        db_session.add(content)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/program-content/program/{program.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["title"] == "Lesson 1"
    
    def test_get_program_content_filtered_by_module(self, client: TestClient, admin_token, db_session):
        """Test getting program content filtered by module"""
        # Create a program, module, and content
        program = Program(
            title="Test Program",
            description="Test Description",
            is_active=True
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)
        
        module = ProgramModule(
            program_id=program.id,
            title="Category 1",
            order_index=1
        )
        db_session.add(module)
        db_session.commit()
        db_session.refresh(module)
        
        content = ProgramContent(
            program_id=program.id,
            module_id=module.id,
            title="Lesson 1",
            content_type="document",
            order_index=1
        )
        db_session.add(content)
        db_session.commit()
        
        response = client.get(
            f"/api/v1/program-content/program/{program.id}",
            params={"module_id": module.id},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["module_id"] == module.id
    
    def test_update_program_content(self, client: TestClient, admin_token, db_session):
        """Test updating program content"""
        # Create a program and content
        program = Program(
            title="Test Program",
            description="Test Description",
            is_active=True
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)
        
        content = ProgramContent(
            program_id=program.id,
            title="Lesson 1",
            content_type="document",
            order_index=1
        )
        db_session.add(content)
        db_session.commit()
        db_session.refresh(content)
        
        update_data = {
            "title": "Updated Lesson",
            "order_index": 2
        }
        
        response = client.put(
            f"/api/v1/program-content/{content.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Lesson"
        assert data["order_index"] == 2
    
    def test_delete_program_content(self, client: TestClient, admin_token, db_session):
        """Test deleting program content"""
        # Create a program and content
        program = Program(
            title="Test Program",
            description="Test Description",
            is_active=True
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)
        
        content = ProgramContent(
            program_id=program.id,
            title="Lesson 1",
            content_type="document",
            order_index=1
        )
        db_session.add(content)
        db_session.commit()
        db_session.refresh(content)
        
        response = client.delete(
            f"/api/v1/program-content/{content.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 204
        
        # Verify it's deleted
        deleted_content = db_session.query(ProgramContent).filter(ProgramContent.id == content.id).first()
        assert deleted_content is None
    
    def test_program_not_found(self, client: TestClient, admin_token):
        """Test getting modules for non-existent program"""
        response = client.get(
            "/api/v1/program-content/modules/99999",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Should return 404 or empty list
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 0


