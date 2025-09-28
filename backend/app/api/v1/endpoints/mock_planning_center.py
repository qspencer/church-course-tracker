"""
Mock Planning Center API Endpoints
Provides mock Planning Center API responses for development and testing
"""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.mock_planning_center_service import MockPlanningCenterService

router = APIRouter()

# Initialize mock service
mock_service = MockPlanningCenterService()


@router.get("/test-connection")
async def test_mock_connection():
    """Test connection to mock Planning Center API"""
    try:
        is_connected = await mock_service.test_connection()
        return {
            "status": "success",
            "message": "Successfully connected to mock Planning Center API",
            "connected": is_connected,
            "mock_data_summary": mock_service.get_mock_data_summary()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Mock connection test failed: {str(e)}",
            "connected": False
        }


@router.get("/people")
async def get_mock_people(
    per_page: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get people from mock Planning Center API"""
    try:
        result = await mock_service.get_people(limit=per_page, offset=offset)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch mock people: {str(e)}"
        )


@router.get("/people/{person_id}")
async def get_mock_person(person_id: str):
    """Get a specific person from mock Planning Center API"""
    try:
        result = await mock_service.get_person(person_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch mock person: {str(e)}"
        )


@router.get("/events")
async def get_mock_events(
    per_page: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get events from mock Planning Center API"""
    try:
        result = await mock_service.get_events(limit=per_page, offset=offset)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch mock events: {str(e)}"
        )


@router.get("/events/{event_id}")
async def get_mock_event(event_id: str):
    """Get a specific event from mock Planning Center API"""
    try:
        result = await mock_service.get_event(event_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch mock event: {str(e)}"
        )


@router.get("/events/{event_id}/registrations")
async def get_mock_event_registrations(
    event_id: str,
    per_page: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get registrations for a specific event"""
    try:
        result = await mock_service.get_event_registrations(event_id, limit=per_page, offset=offset)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch mock event registrations: {str(e)}"
        )


@router.get("/people/{person_id}/registrations")
async def get_mock_person_registrations(
    person_id: str,
    per_page: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get registrations for a specific person"""
    try:
        result = await mock_service.get_person_registrations(person_id, limit=per_page, offset=offset)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch mock person registrations: {str(e)}"
        )


@router.post("/events/{event_id}/registrations")
async def create_mock_registration(
    event_id: str,
    person_id: str,
    notes: Optional[str] = None
):
    """Create a new registration"""
    try:
        result = await mock_service.create_registration(
            event_id=event_id,
            person_id=person_id,
            notes=notes
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create mock registration: {str(e)}"
        )


@router.put("/registrations/{registration_id}")
async def update_mock_registration(
    registration_id: str,
    status: Optional[str] = None,
    notes: Optional[str] = None
):
    """Update an existing registration"""
    try:
        update_data = {}
        if status is not None:
            update_data["status"] = status
        if notes is not None:
            update_data["notes"] = notes
        
        result = await mock_service.update_registration(registration_id, **update_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update mock registration: {str(e)}"
        )


@router.delete("/registrations/{registration_id}")
async def delete_mock_registration(registration_id: str):
    """Delete a registration"""
    try:
        result = await mock_service.delete_registration(registration_id)
        return {"success": result, "message": "Registration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete mock registration: {str(e)}"
        )


@router.get("/mock-data/summary")
async def get_mock_data_summary():
    """Get summary of mock data for debugging"""
    try:
        summary = mock_service.get_mock_data_summary()
        return {
            "status": "success",
            "data": summary
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get mock data summary: {str(e)}"
        )


@router.get("/mock-data/reset")
async def reset_mock_data():
    """Reset mock data to initial state"""
    try:
        # Reinitialize the mock service to reset data
        global mock_service
        mock_service = MockPlanningCenterService()
        return {
            "status": "success",
            "message": "Mock data reset successfully",
            "data": mock_service.get_mock_data_summary()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset mock data: {str(e)}"
        )
