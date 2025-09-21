"""
People API endpoints (from Planning Center)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.people import People, PeopleCreate, PeopleUpdate
from app.services.people_service import PeopleService

router = APIRouter()


@router.get("/", response_model=List[People])
async def get_people(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all people with pagination and optional filtering"""
    people_service = PeopleService(db)
    return people_service.get_people(skip=skip, limit=limit, is_active=is_active)


@router.get("/{person_id}", response_model=People)
async def get_person(
    person_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific person by ID"""
    people_service = PeopleService(db)
    person = people_service.get_person(person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    return person


@router.get("/pc-id/{pc_id}", response_model=People)
async def get_person_by_pc_id(
    pc_id: str,
    db: Session = Depends(get_db)
):
    """Get a person by Planning Center ID"""
    people_service = PeopleService(db)
    person = people_service.get_person_by_pc_id(pc_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found for Planning Center ID"
        )
    return person


@router.get("/search/{search_term}", response_model=List[People])
async def search_people(
    search_term: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Search people by name or email"""
    people_service = PeopleService(db)
    return people_service.search_people(search_term, limit=limit)


@router.post("/", response_model=People, status_code=status.HTTP_201_CREATED)
async def create_person(
    person: PeopleCreate,
    db: Session = Depends(get_db)
):
    """Create a new person"""
    people_service = PeopleService(db)
    return people_service.create_person(person)


@router.put("/{person_id}", response_model=People)
async def update_person(
    person_id: int,
    person_update: PeopleUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing person"""
    people_service = PeopleService(db)
    person = people_service.update_person(person_id, person_update)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    return person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    person_id: int,
    db: Session = Depends(get_db)
):
    """Delete a person"""
    people_service = PeopleService(db)
    success = people_service.delete_person(person_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
