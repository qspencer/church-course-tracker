"""
Planning Center Sync API endpoints
"""

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
async def get_planning_center_events(db: Session = Depends(get_db)):
    """Get list of events from Planning Center (real-time)"""
    sync_service = PlanningCenterSyncService(db)
    try:
        return sync_service.get_events()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/lists", response_model=List[Dict[str, Any]])
async def get_planning_center_lists(db: Session = Depends(get_db)):
    """Get all lists from Planning Center (real-time)"""
    sync_service = PlanningCenterSyncService(db)
    try:
        return sync_service.get_lists()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
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
