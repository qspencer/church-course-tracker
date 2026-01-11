"""
People API endpoints (from Planning Center)
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.enrollment import CourseEnrollment
from app.schemas.people import People, PeopleCreate, PeopleUpdate
from app.services.enrollment_service import CourseEnrollmentService
from app.services.people_service import PeopleService
from app.services.planning_center_sync_service import PlanningCenterSyncService
from app.api.v1.endpoints.auth import get_current_active_user
from pydantic import BaseModel
import httpx
import logging

router = APIRouter()


@router.get("", response_model=List[People])
@router.get("/", response_model=List[People])
async def get_people(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """Get all people with pagination and optional filtering"""
    people_service = PeopleService(db)
    return people_service.get_people(skip=skip, limit=limit, is_active=is_active)


@router.get("/{person_id}", response_model=People)
async def get_person(person_id: int, db: Session = Depends(get_db)):
    """Get a specific person by ID"""
    people_service = PeopleService(db)
    person = people_service.get_person(person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    return person


@router.get("/pc-id/{pc_id}", response_model=People)
async def get_person_by_pc_id(pc_id: str, db: Session = Depends(get_db)):
    """Get a person by Planning Center ID"""
    people_service = PeopleService(db)
    person = people_service.get_person_by_pc_id(pc_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found for Planning Center ID",
        )
    return person


@router.get("/search/{search_term}", response_model=List[People])
async def search_people(
    search_term: str, limit: int = 50, db: Session = Depends(get_db)
):
    """Search people by name or email"""
    people_service = PeopleService(db)
    return people_service.search_people(search_term, limit=limit)


@router.post("", response_model=People, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=People, status_code=status.HTTP_201_CREATED)
async def create_person(person: PeopleCreate, db: Session = Depends(get_db)):
    """Create a new person"""
    people_service = PeopleService(db)
    return people_service.create_person(person)


@router.put("/{person_id}", response_model=People)
async def update_person(
    person_id: int, person_update: PeopleUpdate, db: Session = Depends(get_db)
):
    """Update an existing person"""
    people_service = PeopleService(db)
    person = people_service.update_person(person_id, person_update)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    return person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(person_id: int, db: Session = Depends(get_db)):
    """Delete a person"""
    people_service = PeopleService(db)
    success = people_service.delete_person(person_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )


@router.get("/{person_id}/enrollments", response_model=List[CourseEnrollment])
async def get_person_enrollments(person_id: int, db: Session = Depends(get_db)):
    """Get all enrollments for a specific person"""
    # Verify person exists
    people_service = PeopleService(db)
    person = people_service.get_person(person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Person not found"
        )
    
    # Get enrollments for this person
    enrollment_service = CourseEnrollmentService(db)
    enrollments = enrollment_service.get_enrollments(people_id=person_id)
    return enrollments


class ImportMemberFromPCRequest(BaseModel):
    planning_center_person_id: str


@router.post("/import-from-pc", response_model=People)
async def import_member_from_planning_center(
    request: ImportMemberFromPCRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Import a member from Planning Center by person ID"""
    logger = logging.getLogger(__name__)
    sync_service = PlanningCenterSyncService(db)
    people_service = PeopleService(db)
    
    try:
        # Fetch the person data from Planning Center with emails and phone numbers included
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"https://api.planningcenteronline.com/people/v2/people/{request.planning_center_person_id}",
                headers=sync_service.headers,
                params={"include": "emails,phone_numbers"}
            )
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Person not found in Planning Center"
                )
            
            response.raise_for_status()
            data = response.json()
            person_data = data.get("data")
            included = data.get("included", [])
            
            if not person_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Person data not found in Planning Center response"
                )
        
        # Process included emails and phone numbers and attach to person_data
        # This matches the logic in PlanningCenterSyncService._attach_included_data
        emails_by_id = {}
        phones_by_id = {}
        
        for item in included:
            item_type = item.get("type")
            item_id = item.get("id")
            attrs = item.get("attributes", {})
            
            if item_type == "Email":
                emails_by_id[item_id] = attrs.get("address", "")
            elif item_type == "PhoneNumber":
                phones_by_id[item_id] = attrs.get("number", "")
        
        # Attach emails and phone numbers to person attributes
        relationships = person_data.get("relationships", {})
        person_attrs = person_data.get("attributes", {})
        
        # Get email addresses
        email_data = relationships.get("emails", {}).get("data", [])
        emails = []
        for email_ref in email_data:
            email_id = email_ref.get("id")
            if email_id in emails_by_id:
                emails.append(emails_by_id[email_id])
        
        # Get phone numbers
        phone_data = relationships.get("phone_numbers", {}).get("data", [])
        phone_numbers = []
        for phone_ref in phone_data:
            phone_id = phone_ref.get("id")
            if phone_id in phones_by_id:
                phone_numbers.append(phones_by_id[phone_id])
        
        # Attach to person attributes for sync_from_planning_center to use
        if emails:
            person_attrs["email"] = emails[0]  # Primary email
            person_attrs["emails"] = emails  # All emails
            logger.info(f"Attached email to person: {emails[0]} (total: {len(emails)})")
        else:
            logger.warning(f"No emails found for person {request.planning_center_person_id}")
            
        if phone_numbers:
            person_attrs["phone_number"] = phone_numbers[0]  # Primary phone
            person_attrs["phone_numbers"] = phone_numbers  # All phone numbers
            logger.info(f"Attached phone to person: {phone_numbers[0]} (total: {len(phone_numbers)})")
        else:
            logger.warning(f"No phone numbers found for person {request.planning_center_person_id}")
        
        # Sync/create member from Planning Center person data
        member = people_service.sync_from_planning_center(
            person_data,
            updated_by=current_user["id"]
        )
        
        return member
        
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Planning Center API error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching person from Planning Center: {e.response.status_code}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error importing member from Planning Center: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to import member from Planning Center: {str(e)}"
        )
