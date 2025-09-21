"""
Planning Center sync service
"""

import httpx
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.config import settings
from app.schemas.sync import SyncResponse, SyncStatus
from app.models.member import Member as MemberModel


class SyncService:
    """Service for Planning Center synchronization"""
    
    def __init__(self, db: Optional[Session]):
        self.db = db
        self.api_url = settings.PLANNING_CENTER_API_URL
        self.app_id = settings.PLANNING_CENTER_APP_ID
        self.secret = settings.PLANNING_CENTER_SECRET
    
    async def test_connection(self) -> bool:
        """Test connection to Planning Center API"""
        try:
            async with httpx.AsyncClient() as client:
                headers = self._get_auth_headers()
                response = await client.get(
                    f"{self.api_url}/people/v2/people",
                    headers=headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception:
            return False
    
    async def sync_members(self) -> SyncResponse:
        """Sync members from Planning Center"""
        if not self.db:
            raise ValueError("Database session required for sync")
        
        try:
            async with httpx.AsyncClient() as client:
                headers = self._get_auth_headers()
                
                # Fetch people from Planning Center
                response = await client.get(
                    f"{self.api_url}/people/v2/people",
                    headers=headers,
                    params={"per_page": 100}
                )
                response.raise_for_status()
                
                data = response.json()
                people = data.get("data", [])
                
                synced_count = 0
                for person in people:
                    if await self._sync_person(person):
                        synced_count += 1
                
                return SyncResponse(
                    success=True,
                    records_synced=synced_count,
                    message=f"Successfully synced {synced_count} members",
                    sync_time=datetime.utcnow()
                )
                
        except Exception as e:
            return SyncResponse(
                success=False,
                records_synced=0,
                message=f"Sync failed: {str(e)}",
                sync_time=datetime.utcnow()
            )
    
    async def _sync_person(self, person_data: dict) -> bool:
        """Sync a single person from Planning Center"""
        try:
            person_id = person_data.get("id")
            attributes = person_data.get("attributes", {})
            
            # Check if member already exists
            existing_member = self.db.query(MemberModel).filter(
                MemberModel.planning_center_id == person_id
            ).first()
            
            if existing_member:
                # Update existing member
                existing_member.first_name = attributes.get("first_name", "")
                existing_member.last_name = attributes.get("last_name", "")
                existing_member.email = attributes.get("email", "")
                existing_member.phone = attributes.get("phone", "")
                existing_member.updated_at = datetime.utcnow()
            else:
                # Create new member
                new_member = MemberModel(
                    planning_center_id=person_id,
                    first_name=attributes.get("first_name", ""),
                    last_name=attributes.get("last_name", ""),
                    email=attributes.get("email", ""),
                    phone=attributes.get("phone", ""),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(new_member)
            
            self.db.commit()
            return True
            
        except Exception:
            self.db.rollback()
            return False
    
    def get_sync_status(self) -> SyncStatus:
        """Get current sync status"""
        # This would typically be stored in a sync status table
        return SyncStatus(
            last_sync=None,
            status="idle",
            records_synced=0
        )
    
    def _get_auth_headers(self) -> dict:
        """Get authentication headers for Planning Center API"""
        # This is a placeholder - implement proper OAuth or API key auth
        return {
            "Authorization": f"Bearer {self.secret}",
            "Content-Type": "application/json"
        }
