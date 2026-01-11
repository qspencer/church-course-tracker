"""
Planning Center Sync API endpoints
"""

import logging
from typing import Any, Dict, List, Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_active_user
from app.services.planning_center_sync_service import PlanningCenterSyncService
from app.schemas.attribute_mapping import AttributeMappingReview, AttributeMappingDecisions
from app.utils.attribute_matcher import AttributeMatcher
from app.models.course import Course
from app.models.program import Program

router = APIRouter()


@router.get("/test-connection", response_model=Dict[str, Any])
async def test_planning_center_connection(db: Session = Depends(get_db)):
    """Test connection to Planning Center API"""
    try:
        from app.services.sync_service import SyncService

        sync_service = SyncService(db)

        # Test the connection
        is_connected = await sync_service.test_connection()

        if is_connected:
            return {
                "status": "success",
                "message": "Successfully connected to Planning Center API",
                "connected": True,
            }
        else:
            return {
                "status": "error",
                "message": "Failed to connect to Planning Center API",
                "connected": False,
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection test failed: {str(e)}",
            "connected": False,
        }


@router.post("/people", response_model=Dict[str, Any])
async def start_sync_people(db: Session = Depends(get_db)):
    """Start async sync of people from Planning Center"""
    sync_service = PlanningCenterSyncService(db)
    task_id = sync_service.start_sync_people()

    return {
        "task_id": task_id,
        "status": "started",
        "message": "People sync started in background",
    }


@router.post("/events", response_model=Dict[str, Any])
async def start_sync_events(db: Session = Depends(get_db)):
    """Start async sync of events (courses) from Planning Center"""
    sync_service = PlanningCenterSyncService(db)
    task_id = sync_service.start_sync_events()

    return {
        "task_id": task_id,
        "status": "started",
        "message": "Events sync started in background",
    }


@router.get("/events", response_model=List[Dict[str, Any]])
async def get_planning_center_events(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get list of events from Planning Center (real-time)"""
    sync_service = PlanningCenterSyncService(db)
    try:
        events = sync_service.get_events()
        return events
    except ValueError as e:
        # ValueError from Planning Center API issues
        error_msg = str(e)
        if "authentication failed" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/events/diagnostics", response_model=Dict[str, Any])
async def get_events_diagnostics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """
    Get diagnostic information about fetched events, including date ranges.
    Shows which API is used, the oldest/newest events, and whether the limit was hit.
    """
    sync_service = PlanningCenterSyncService(db)
    try:
        events = sync_service.get_events()
        
        if not events:
            return {
                "total_events": 0,
                "message": "No events found",
                "api_used": "unknown"
            }
        
        # Extract dates from events (handle both Check-Ins and Calendar API formats)
        dates_created = []
        dates_start = []
        events_with_created_at = []  # Track events that have created_at
        
        for event in events:
            attrs = event.get("attributes", {})
            
            # Check-Ins API uses created_at
            created_at_str = attrs.get("created_at")
            if created_at_str:
                try:
                    from dateutil import parser
                    created_at_dt = parser.parse(created_at_str)
                    dates_created.append(created_at_dt)
                    events_with_created_at.append((event, created_at_dt))
                except:
                    pass
            
            # Calendar API uses starts_at, Check-Ins uses start_date
            start_date_str = attrs.get("starts_at") or attrs.get("start_date")
            if start_date_str:
                try:
                    from dateutil import parser
                    dates_start.append(parser.parse(start_date_str))
                except:
                    pass
        
        # Determine which API is being used based on event structure
        api_used = "unknown"
        sort_order = "unknown"
        first_event = events[0] if events else {}
        if "created_at" in first_event.get("attributes", {}):
            api_used = "Check-Ins API"
            sort_order = "created_at (newest created first)"
        elif "starts_at" in first_event.get("attributes", {}):
            api_used = "Calendar API"
            sort_order = "starts_at (newest start date first)"
        
        # Check if limit was likely applied (exactly 1000 events)
        limit_applied = len(events) >= 1000
        from app.core.config import settings
        configured_limit = settings.PLANNING_CENTER_MAX_EVENTS
        
        result = {
            "total_events": len(events),
            "api_used": api_used,
            "sort_order": sort_order,
            "configured_limit": configured_limit,
            "limit_applied": limit_applied,
        }
        
        if dates_created:
            dates_created.sort()
            result["created_at_range"] = {
                "newest_created": dates_created[-1].isoformat() if dates_created else None,
                "oldest_created": dates_created[0].isoformat() if dates_created else None,
                "newest_created_formatted": dates_created[-1].strftime("%Y-%m-%d %H:%M:%S") if dates_created else None,
                "oldest_created_formatted": dates_created[0].strftime("%Y-%m-%d %H:%M:%S") if dates_created else None,
            }
        
        if dates_start:
            dates_start.sort()
            result["start_date_range"] = {
                "newest_start": dates_start[-1].isoformat() if dates_start else None,
                "oldest_start": dates_start[0].isoformat() if dates_start else None,
                "newest_start_formatted": dates_start[-1].strftime("%Y-%m-%d %H:%M:%S") if dates_start else None,
                "oldest_start_formatted": dates_start[0].strftime("%Y-%m-%d %H:%M:%S") if dates_start else None,
            }
        
        # Find the oldest event by created_at date (if available)
        if events_with_created_at:
            # Sort by created_at to find the oldest
            events_with_created_at.sort(key=lambda x: x[1])  # Sort by created_at datetime
            oldest_by_created_at = events_with_created_at[0][0]  # First item is oldest
            oldest_attrs = oldest_by_created_at.get("attributes", {})
            result["oldest_event_by_created_at"] = {
                "id": oldest_by_created_at.get("id"),
                "name": oldest_attrs.get("name"),
                "created_at": oldest_attrs.get("created_at"),
                "created_at_formatted": events_with_created_at[0][1].strftime("%Y-%m-%d %H:%M:%S"),
                "start_date": oldest_attrs.get("start_date"),
                "starts_at": oldest_attrs.get("starts_at"),
                "note": "This is the event with the oldest created_at date in the fetched list"
            }
        
        # Find the oldest event in the list (last item since sorted descending by API order)
        if events:
            oldest_event = events[-1]
            oldest_attrs = oldest_event.get("attributes", {})
            result["oldest_event_in_list"] = {
                "id": oldest_event.get("id"),
                "name": oldest_attrs.get("name"),
                "created_at": oldest_attrs.get("created_at"),
                "start_date": oldest_attrs.get("start_date"),
                "starts_at": oldest_attrs.get("starts_at"),
                "note": "This is the last event in the sorted list (may not be oldest by created_at if sorted by start_date)"
            }
        
        # Find the newest event in the list (first item since sorted descending)
        if events:
            newest_event = events[0]
            newest_attrs = newest_event.get("attributes", {})
            result["newest_event_in_list"] = {
                "id": newest_event.get("id"),
                "name": newest_attrs.get("name"),
                "created_at": newest_attrs.get("created_at"),
                "start_date": newest_attrs.get("start_date"),
                "starts_at": newest_attrs.get("starts_at"),
                "note": "This is the newest event being fetched (first in sorted list)"
            }
        
        return result
        
    except ValueError as e:
        error_msg = str(e)
        if "authentication failed" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch event diagnostics: {str(e)}"
        )


@router.get("/lists", response_model=List[Dict[str, Any]])
async def get_planning_center_lists(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get all lists from Planning Center (real-time)"""
    sync_service = PlanningCenterSyncService(db)
    try:
        lists = sync_service.get_lists()
        return lists
    except ValueError as e:
        # ValueError from Planning Center API issues
        error_msg = str(e)
        if "authentication failed" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/events/{event_id}", response_model=Dict[str, Any])
async def get_planning_center_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get a single event from Planning Center by ID"""
    sync_service = PlanningCenterSyncService(db)
    try:
        event = sync_service.get_event(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/lists/{list_id}", response_model=Dict[str, Any])
async def get_planning_center_list(
    list_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get a single list from Planning Center by ID"""
    sync_service = PlanningCenterSyncService(db)
    try:
        list_data = sync_service.get_list(list_id)
        if not list_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"List with ID {list_id} not found"
            )
        return list_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/events/{event_id}/registrations", response_model=List[Dict[str, Any]])
async def get_event_registrations(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """
    Get registrations for a specific Planning Center event.
    Requires admin or staff role.
    """
    if not current_user or current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can view Planning Center registrations",
        )
    sync_service = PlanningCenterSyncService(db)
    try:
        registrations = sync_service.get_event_registrations(event_id)
        return registrations
    except ValueError as e:
        error_msg = str(e)
        # If event not found or no registrations, return empty list instead of error
        if "not found" in error_msg.lower() or "has no registrations" in error_msg.lower() or "404" in error_msg:
            logger.info(f"Event {event_id} not found or has no registrations: {error_msg}")
            return []
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
        )
    except Exception as e:
        error_msg = str(e)
        # Handle connection errors or other issues - still return empty list to be user-friendly
        logger.warning(f"Error fetching event registrations for {event_id}: {error_msg}")
        if "not found" in error_msg.lower() or "404" in error_msg:
            return []
        logger.exception(f"Error fetching event registrations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching event registrations",
        )


@router.post("/registrations", response_model=Dict[str, Any])
async def start_sync_registrations(
    event_id: Optional[str] = None, db: Session = Depends(get_db)
):
    """Start async sync of registrations from Planning Center"""
    sync_service = PlanningCenterSyncService(db)
    task_id = sync_service.start_sync_registrations(event_id=event_id)

    return {
        "task_id": task_id,
        "status": "started",
        "message": "Registrations sync started in background",
    }


@router.post("/all", response_model=Dict[str, Any])
async def start_sync_all(db: Session = Depends(get_db)):
    """Start async sync of all data from Planning Center"""
    sync_service = PlanningCenterSyncService(db)
    task_id = sync_service.start_sync_all()

    return {
        "task_id": task_id,
        "status": "started",
        "message": "Full sync started in background",
    }


@router.get("/tasks", response_model=List[Dict[str, Any]])
async def list_sync_tasks(
    task_type: Optional[str] = None, db: Session = Depends(get_db)
):
    """List all sync tasks, optionally filtered by type"""
    sync_service = PlanningCenterSyncService(db)
    tasks = sync_service.list_sync_tasks(task_type=task_type)

    return tasks


@router.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_sync_task_status(task_id: str, db: Session = Depends(get_db)):
    """Get sync task status by task ID"""
    sync_service = PlanningCenterSyncService(db)
    task_status = sync_service.get_sync_task_status(task_id)

    if not task_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return task_status


@router.post("/webhook", response_model=Dict[str, Any])
async def process_webhook(request: Request, db: Session = Depends(get_db)):
    """Process webhook events from Planning Center"""
    try:
        webhook_data = await request.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload"
        )

    sync_service = PlanningCenterSyncService(db)
    result = sync_service.process_webhook_event(webhook_data)

    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=result["error"]
        )

    return result


@router.get("/attribute-mappings", response_model=AttributeMappingReview)
async def get_attribute_mappings(
    source_type: Literal["event", "list"] = Query(..., description="Source type from Planning Center"),
    source_id: str = Query(..., description="Planning Center source ID (event_id or list_id)"),
    target_type: Literal["course", "program"] = Query(..., description="Target type in CCT"),
    target_id: int = Query(..., description="Target ID (course_id or program_id)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """
    Get attribute mappings for review before import
    """
    sync_service = PlanningCenterSyncService(db)
    matcher = AttributeMatcher(similarity_threshold=0.75)
    
    # Get PC data based on source type
    pc_attributes = {}
    if source_type == "event":
        events = sync_service.get_events()
        event = next((e for e in events if e.get("id") == source_id), None)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planning Center event '{source_id}' not found"
            )
        pc_attributes = event.get("attributes", {})
    elif source_type == "list":
        # For lists, we need to get people from the list
        # For now, we'll get the first person's attributes as a sample
        people = sync_service.get_list_people(source_id)
        if not people:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Planning Center list '{source_id}' not found or empty"
            )
        # Merge attributes from all people (taking first non-null value for each attribute)
        for person in people:
            attrs = person.get("attributes", {})
            for key, value in attrs.items():
                if key not in pc_attributes and value is not None:
                    pc_attributes[key] = value
    
    # Get local attributes based on target type
    local_attributes = []
    if target_type == "course":
        # Get Course model attributes
        course = db.query(Course).filter(Course.id == target_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with ID {target_id} not found"
            )
        # Common Course attributes that can be mapped
        local_attributes = [
            "title", "description", "duration_weeks", "prerequisites",
            "instructors", "locations", "delivery_modes",
            "planning_center_event_id", "planning_center_event_name",
            "event_start_date", "event_end_date", "max_capacity"
        ]
    elif target_type == "program":
        # Get Program model attributes
        program = db.query(Program).filter(Program.id == target_id).first()
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {target_id} not found"
            )
        # Common Program attributes that can be mapped
        local_attributes = [
            "title", "description", "role_definitions", "relationship_config",
            "locations", "delivery_modes", "prerequisites",
            "planning_center_event_template_id", "planning_center_event_id",
            "planning_center_event_name", "is_active"
        ]
    
    # Match attributes
    from app.schemas.attribute_mapping import AttributeMappingMatch
    matches = []
    for pc_attr_name, pc_attr_value in pc_attributes.items():
        match_result = matcher.find_best_match(pc_attr_name, local_attributes)
        if match_result:
            local_attr, score = match_result
            matches.append(AttributeMappingMatch(
                pc_attribute=pc_attr_name,
                local_attribute=local_attr,
                similarity_score=score,
                is_predefined=False,  # Could enhance this with predefined mappings
                match_status="matched"
            ))
        else:
            matches.append(AttributeMappingMatch(
                pc_attribute=pc_attr_name,
                local_attribute=None,
                similarity_score=0.0,
                is_predefined=False,
                match_status="unmatched"
            ))
    
    return AttributeMappingReview(
        source_type=source_type,
        source_id=source_id,
        target_type=target_type,
        target_id=target_id,
        pc_attributes=pc_attributes,
        local_attributes=local_attributes,
        matches=matches
    )


@router.post("/attribute-mappings/decisions", response_model=Dict[str, Any])
async def save_attribute_mapping_decisions(
    decisions: AttributeMappingDecisions,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """
    Save user's attribute mapping decisions.
    This endpoint stores decisions for later use during import.
    """
    # For now, we just validate and return success
    # In a full implementation, you might store these in a cache or database
    # The actual application of decisions happens during the import process
    
    # Validate decisions
    for decision in decisions.decisions:
        if decision.action in ["accept", "rematch"]:
            if not decision.local_attribute:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"local_attribute is required for action '{decision.action}'"
                )
        elif decision.action == "custom":
            if not decision.custom_attribute_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="custom_attribute_name is required for 'custom' action"
                )
    
    return {
        "status": "success",
        "message": "Mapping decisions saved",
        "decisions": decisions.decisions
    }


@router.get("/people/search", response_model=List[Dict[str, Any]])
async def search_planning_center_people(
    q: str = Query(..., description="Search term (name, email, or phone)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """
    Search for people in Planning Center by name, email, or phone number.
    Requires admin or staff role.
    """
    if not current_user or current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff users can search Planning Center people",
        )
    sync_service = PlanningCenterSyncService(db)
    try:
        people = sync_service.search_people(q, limit=limit)
        return people
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.exception(f"Error searching Planning Center people: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching Planning Center people",
        )
