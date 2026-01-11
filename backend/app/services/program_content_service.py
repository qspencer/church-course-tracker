"""
Program Content Management Service

This service handles program content management including modules (categories),
content items (lessons), and organization.
"""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.program import Program
from app.models.program_content import ProgramContent, ProgramModule
from app.schemas.program_content import (
    ProgramContentCreate,
    ProgramContentUpdate,
    ProgramModuleCreate,
    ProgramModuleUpdate,
)


class ProgramContentService:
    """Service for managing program content (modules and content items)"""

    def __init__(self, db: Session):
        self.db = db

    # Program Module Management

    def create_module(
        self, module_data: ProgramModuleCreate, user_id: int
    ) -> ProgramModule:
        """Create a new program module (category)"""
        # Verify program exists
        program = (
            self.db.query(Program).filter(Program.id == module_data.program_id).first()
        )
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Program not found"
            )

        # Create module
        db_module = ProgramModule(
            **module_data.model_dump(), created_by=user_id, updated_by=user_id
        )

        self.db.add(db_module)
        self.db.commit()
        self.db.refresh(db_module)

        return db_module

    def get_modules(self, program_id: int) -> List[ProgramModule]:
        """Get all modules for a program"""
        return (
            self.db.query(ProgramModule)
            .filter(ProgramModule.program_id == program_id)
            .order_by(ProgramModule.order_index)
            .all()
        )

    def get_module(self, module_id: int) -> Optional[ProgramModule]:
        """Get a specific module"""
        return (
            self.db.query(ProgramModule).filter(ProgramModule.id == module_id).first()
        )

    def update_module(
        self, module_id: int, module_data: ProgramModuleUpdate, user_id: int
    ) -> Optional[ProgramModule]:
        """Update a program module"""
        db_module = self.get_module(module_id)
        if not db_module:
            return None

        # Update fields
        update_data = module_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_module, field, value)

        db_module.updated_by = user_id
        db_module.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(db_module)

        return db_module

    def delete_module(self, module_id: int, user_id: int) -> bool:
        """Delete a program module"""
        db_module = self.get_module(module_id)
        if not db_module:
            return False

        self.db.delete(db_module)
        self.db.commit()

        return True

    # Program Content Management

    def create_content(
        self, content_data: ProgramContentCreate, user_id: int
    ) -> ProgramContent:
        """Create new program content (lesson)"""
        # Verify program exists
        program = (
            self.db.query(Program)
            .filter(Program.id == content_data.program_id)
            .first()
        )
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Program not found"
            )

        # Verify module exists if specified
        if content_data.module_id:
            module = self.get_module(content_data.module_id)
            if not module:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
                )
            # Verify module belongs to the same program
            if module.program_id != content_data.program_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Module does not belong to this program",
                )

        # Create content
        db_content = ProgramContent(
            **content_data.model_dump(),
            created_by=user_id,
            updated_by=user_id,
        )

        self.db.add(db_content)
        self.db.commit()
        self.db.refresh(db_content)

        return db_content

    def get_content(
        self, program_id: int, module_id: Optional[int] = None
    ) -> List[ProgramContent]:
        """Get content for a program, optionally filtered by module"""
        query = self.db.query(ProgramContent).filter(
            ProgramContent.program_id == program_id
        )

        if module_id:
            query = query.filter(ProgramContent.module_id == module_id)

        return query.order_by(ProgramContent.order_index).all()

    def get_content_item(self, content_id: int) -> Optional[ProgramContent]:
        """Get a specific content item"""
        return (
            self.db.query(ProgramContent)
            .filter(ProgramContent.id == content_id)
            .first()
        )

    def update_content(
        self, content_id: int, content_data: ProgramContentUpdate, user_id: int
    ) -> Optional[ProgramContent]:
        """Update program content"""
        db_content = self.get_content_item(content_id)
        if not db_content:
            return None

        # Verify module exists if specified and belongs to same program
        if content_data.module_id is not None:
            if content_data.module_id:
                module = self.get_module(content_data.module_id)
                if not module:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
                    )
                if module.program_id != db_content.program_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Module does not belong to this program",
                    )

        # Update fields
        update_data = content_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_content, field, value)

        db_content.updated_by = user_id
        db_content.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(db_content)

        return db_content

    def delete_content(self, content_id: int, user_id: int) -> bool:
        """Delete program content"""
        db_content = self.get_content_item(content_id)
        if not db_content:
            return False

        self.db.delete(db_content)
        self.db.commit()

        return True


