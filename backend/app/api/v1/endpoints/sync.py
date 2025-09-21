"""
Planning Center synchronization endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.sync import SyncStatus, SyncResponse
from app.services.sync_service import SyncService

router = APIRouter()


@router.post("/members", response_model=SyncResponse)
async def sync_members(
    db: Session = Depends(get_db)
):
    """Sync members from Planning Center"""
    sync_service = SyncService(db)
    try:
        result = await sync_service.sync_members()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )


@router.get("/status", response_model=SyncStatus)
async def get_sync_status(
    db: Session = Depends(get_db)
):
    """Get current sync status"""
    sync_service = SyncService(db)
    return sync_service.get_sync_status()


@router.post("/test-connection")
async def test_planning_center_connection():
    """Test connection to Planning Center API"""
    sync_service = SyncService(None)  # No DB needed for connection test
    try:
        success = await sync_service.test_connection()
        if success:
            return {"status": "success", "message": "Connection successful"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Connection failed"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection test failed: {str(e)}"
        )
