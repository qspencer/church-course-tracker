"""
Planning Center Sync API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List

from app.core.database import get_db
from app.services.planning_center_sync_service import PlanningCenterSyncService

router = APIRouter()


@router.get("/test-connection", response_model=Dict[str, Any])
async def test_planning_center_connection(
    db: Session = Depends(get_db)
):
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
                "connected": True
            }
        else:
            return {
                "status": "error",
                "message": "Failed to connect to Planning Center API",
                "connected": False
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection test failed: {str(e)}",
            "connected": False
        }


@router.post("/people", response_model=Dict[str, Any])
async def start_sync_people(
    db: Session = Depends(get_db)
):
    """Start async sync of people from Planning Center"""
    sync_service = PlanningCenterSyncService(db)
    task_id = sync_service.start_sync_people()
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": "People sync started in background"
    }


@router.post("/events", response_model=Dict[str, Any])
async def start_sync_events(
    db: Session = Depends(get_db)
):
    """Start async sync of events (courses) from Planning Center"""
    sync_service = PlanningCenterSyncService(db)
    task_id = sync_service.start_sync_events()
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Events sync started in background"
    }


@router.post("/registrations", response_model=Dict[str, Any])
async def start_sync_registrations(
    event_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Start async sync of registrations from Planning Center"""
    sync_service = PlanningCenterSyncService(db)
    task_id = sync_service.start_sync_registrations(event_id=event_id)
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Registrations sync started in background"
    }


@router.post("/all", response_model=Dict[str, Any])
async def start_sync_all(
    db: Session = Depends(get_db)
):
    """Start async sync of all data from Planning Center"""
    sync_service = PlanningCenterSyncService(db)
    task_id = sync_service.start_sync_all()
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Full sync started in background"
    }


@router.get("/tasks", response_model=List[Dict[str, Any]])
async def list_sync_tasks(
    task_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all sync tasks, optionally filtered by type"""
    sync_service = PlanningCenterSyncService(db)
    tasks = sync_service.list_sync_tasks(task_type=task_type)
    
    return tasks


@router.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_sync_task_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Get sync task status by task ID"""
    sync_service = PlanningCenterSyncService(db)
    task_status = sync_service.get_sync_task_status(task_id)
    
    if not task_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task_status


@router.post("/webhook", response_model=Dict[str, Any])
async def process_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Process webhook events from Planning Center"""
    try:
        webhook_data = await request.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    sync_service = PlanningCenterSyncService(db)
    result = sync_service.process_webhook_event(webhook_data)
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return result
