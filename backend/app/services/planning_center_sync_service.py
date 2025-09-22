"""
Planning Center Sync Service
"""

import httpx
import asyncio
import uuid
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

from app.core.config import settings
from app.services.people_service import PeopleService
from app.services.course_service import CourseService
from app.services.enrollment_service import CourseEnrollmentService
from app.models.planning_center_sync_log import PlanningCenterSyncLog
from app.models.planning_center_webhook_events import PlanningCenterWebhookEvents
from app.models.planning_center_events_cache import PlanningCenterEventsCache
from app.models.planning_center_registrations_cache import PlanningCenterRegistrationsCache

# Global task storage for tracking async operations
sync_tasks = {}


class PlanningCenterSyncService:
    """Service for syncing data with Planning Center"""
    
    def __init__(self, db: Session):
        self.db = db
        self.people_service = PeopleService(db)
        self.course_service = CourseService(db)
        self.enrollment_service = CourseEnrollmentService(db)
        self.base_url = "https://api.planningcenteronline.com"
        self.headers = self._get_auth_headers()
    
    def _get_db_session(self):
        """Get a new database session for background tasks"""
        from app.core.database import SessionLocal
        return SessionLocal()
    
    def _get_auth_headers(self) -> dict:
        """Get authentication headers for Planning Center API"""
        if not settings.PLANNING_CENTER_APP_ID or not settings.PLANNING_CENTER_SECRET:
            raise ValueError("Planning Center credentials not configured. Please set PLANNING_CENTER_APP_ID and PLANNING_CENTER_SECRET.")
        
        # Use HTTP Basic Authentication for Personal Access Tokens
        import base64
        credentials = f"{settings.PLANNING_CENTER_APP_ID}:{settings.PLANNING_CENTER_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
    
    def _create_sync_task(self, task_type: str, task_id: str = None) -> str:
        """Create a new sync task entry"""
        if task_id is None:
            task_id = str(uuid.uuid4())
        
        sync_tasks[task_id] = {
            "task_type": task_type,
            "status": "pending",
            "started_at": datetime.utcnow(),
            "progress": 0,
            "message": "Task queued",
            "result": None,
            "error": None
        }
        return task_id
    
    def _update_sync_task(self, task_id: str, **kwargs):
        """Update sync task status"""
        if task_id in sync_tasks:
            sync_tasks[task_id].update(kwargs)
    
    def get_sync_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get sync task status"""
        return sync_tasks.get(task_id)
    
    def list_sync_tasks(self, task_type: str = None) -> List[Dict[str, Any]]:
        """List all sync tasks, optionally filtered by type"""
        tasks = list(sync_tasks.values())
        if task_type:
            tasks = [task for task in tasks if task.get("task_type") == task_type]
        return tasks
    
    def start_sync_people(self, updated_by: Optional[int] = None) -> str:
        """Start async sync of people from Planning Center"""
        task_id = self._create_sync_task("sync_people")
        
        # Start background task
        def run_sync():
            asyncio.run(self._sync_people_background(task_id, updated_by))
        
        thread = threading.Thread(target=run_sync, daemon=True)
        thread.start()
        
        return task_id
    
    def start_sync_events(self, updated_by: Optional[int] = None) -> str:
        """Start async sync of events from Planning Center"""
        task_id = self._create_sync_task("sync_events")
        
        # Start background task
        def run_sync():
            asyncio.run(self._sync_events_background(task_id, updated_by))
        
        thread = threading.Thread(target=run_sync, daemon=True)
        thread.start()
        
        return task_id
    
    def start_sync_registrations(self, event_id: Optional[str] = None, updated_by: Optional[int] = None) -> str:
        """Start async sync of registrations from Planning Center"""
        task_id = self._create_sync_task("sync_registrations")
        
        # Start background task
        def run_sync():
            asyncio.run(self._sync_registrations_background(task_id, event_id, updated_by))
        
        thread = threading.Thread(target=run_sync, daemon=True)
        thread.start()
        
        return task_id
    
    def start_sync_all(self, updated_by: Optional[int] = None) -> str:
        """Start async sync of all data from Planning Center"""
        task_id = self._create_sync_task("sync_all")
        
        # Start background task
        def run_sync():
            asyncio.run(self._sync_all_background(task_id, updated_by))
        
        thread = threading.Thread(target=run_sync, daemon=True)
        thread.start()
        
        return task_id
    
    async def _sync_people_background(self, task_id: str, updated_by: Optional[int] = None):
        """Background sync of people from Planning Center"""
        db = self._get_db_session()
        try:
            self._update_sync_task(task_id, status="running", message="Starting people sync...")
            
            sync_log = PlanningCenterSyncLog(
                sync_type="people",
                sync_direction="from_pc",
                started_at=datetime.utcnow(),
                created_by=updated_by
            )
            db.add(sync_log)
            db.commit()
            
            async with httpx.AsyncClient() as client:
                # Get all people from Planning Center
                self._update_sync_task(task_id, progress=10, message="Fetching people from Planning Center...")
                response = await client.get(
                    f"{self.base_url}/people/v2/people",
                    headers=self.headers,
                    params={"per_page": 100}
                )
                response.raise_for_status()
                
                people_data = response.json()
                records_processed = 0
                records_successful = 0
                records_failed = 0
                errors = []
                
                total_records = len(people_data.get("data", []))
                self._update_sync_task(task_id, progress=20, message=f"Processing {total_records} people...")
                
                for i, person_data in enumerate(people_data.get("data", [])):
                    records_processed += 1
                    try:
                        people_service = PeopleService(db)
                        people_service.sync_from_planning_center(
                            person_data, updated_by=updated_by
                        )
                        records_successful += 1
                    except Exception as e:
                        records_failed += 1
                        errors.append(f"Person {person_data.get('id')}: {str(e)}")
                    
                    # Update progress
                    progress = 20 + int((i + 1) / total_records * 70)
                    self._update_sync_task(task_id, progress=progress, 
                                         message=f"Processed {i + 1}/{total_records} people")
                
                # Update sync log
                sync_log.records_processed = records_processed
                sync_log.records_successful = records_successful
                sync_log.records_failed = records_failed
                sync_log.completed_at = datetime.utcnow()
                if errors:
                    sync_log.error_details = {"errors": errors}
                
                db.commit()
                
                result = {
                    "status": "success",
                    "records_processed": records_processed,
                    "records_successful": records_successful,
                    "records_failed": records_failed,
                    "errors": errors
                }
                
                self._update_sync_task(task_id, status="completed", progress=100, 
                                     message="People sync completed successfully", result=result)
                
        except Exception as e:
            self._update_sync_task(task_id, status="failed", 
                                 message=f"People sync failed: {str(e)}", error=str(e))
            if 'sync_log' in locals():
                sync_log.completed_at = datetime.utcnow()
                sync_log.error_details = {"error": str(e)}
                db.commit()
        finally:
            db.close()
    
    async def _sync_events_background(self, task_id: str, updated_by: Optional[int] = None):
        """Background sync of events from Planning Center"""
        db = self._get_db_session()
        try:
            self._update_sync_task(task_id, status="running", message="Starting events sync...")
            
            sync_log = PlanningCenterSyncLog(
                sync_type="events",
                sync_direction="from_pc",
                started_at=datetime.utcnow(),
                created_by=updated_by
            )
            db.add(sync_log)
            db.commit()
            
            async with httpx.AsyncClient() as client:
                # Get all events from Planning Center
                self._update_sync_task(task_id, progress=10, message="Fetching events from Planning Center...")
                response = await client.get(
                    f"{self.base_url}/events/v2/events",
                    headers=self.headers,
                    params={"per_page": 100}
                )
                response.raise_for_status()
                
                events_data = response.json()
                records_processed = 0
                records_successful = 0
                records_failed = 0
                errors = []
                
                total_records = len(events_data.get("data", []))
                self._update_sync_task(task_id, progress=20, message=f"Processing {total_records} events...")
                
                for i, event_data in enumerate(events_data.get("data", [])):
                    records_processed += 1
                    try:
                        # Cache event data
                        self._cache_event_data(db, event_data)
                        
                        # Sync course
                        course_service = CourseService(db)
                        course_service.sync_from_planning_center(
                            event_data, updated_by=updated_by
                        )
                        records_successful += 1
                    except Exception as e:
                        records_failed += 1
                        errors.append(f"Event {event_data.get('id')}: {str(e)}")
                    
                    # Update progress
                    progress = 20 + int((i + 1) / total_records * 70)
                    self._update_sync_task(task_id, progress=progress, 
                                         message=f"Processed {i + 1}/{total_records} events")
                
                # Update sync log
                sync_log.records_processed = records_processed
                sync_log.records_successful = records_successful
                sync_log.records_failed = records_failed
                sync_log.completed_at = datetime.utcnow()
                if errors:
                    sync_log.error_details = {"errors": errors}
                
                db.commit()
                
                result = {
                    "status": "success",
                    "records_processed": records_processed,
                    "records_successful": records_successful,
                    "records_failed": records_failed,
                    "errors": errors
                }
                
                self._update_sync_task(task_id, status="completed", progress=100, 
                                     message="Events sync completed successfully", result=result)
                
        except Exception as e:
            self._update_sync_task(task_id, status="failed", 
                                 message=f"Events sync failed: {str(e)}", error=str(e))
            if 'sync_log' in locals():
                sync_log.completed_at = datetime.utcnow()
                sync_log.error_details = {"error": str(e)}
                db.commit()
        finally:
            db.close()
    
    async def _sync_registrations_background(self, task_id: str, event_id: Optional[str] = None, updated_by: Optional[int] = None):
        """Background sync of registrations from Planning Center"""
        db = self._get_db_session()
        try:
            self._update_sync_task(task_id, status="running", message="Starting registrations sync...")
            
            sync_log = PlanningCenterSyncLog(
                sync_type="registrations",
                sync_direction="from_pc",
                started_at=datetime.utcnow(),
                created_by=updated_by
            )
            db.add(sync_log)
            db.commit()
            
            async with httpx.AsyncClient() as client:
                records_processed = 0
                records_successful = 0
                records_failed = 0
                errors = []
                
                if event_id:
                    # Sync registrations for specific event
                    self._update_sync_task(task_id, progress=10, message=f"Fetching registrations for event {event_id}...")
                    response = await client.get(
                        f"{self.base_url}/events/v2/events/{event_id}/registrations",
                        headers=self.headers,
                        params={"per_page": 100}
                    )
                    response.raise_for_status()
                    registrations_data = response.json()
                    
                    total_records = len(registrations_data.get("data", []))
                    self._update_sync_task(task_id, progress=20, message=f"Processing {total_records} registrations...")
                    
                    for i, registration_data in enumerate(registrations_data.get("data", [])):
                        records_processed += 1
                        try:
                            # Cache registration data
                            self._cache_registration_data(db, registration_data)
                            
                            # Sync enrollment
                            enrollment_service = CourseEnrollmentService(db)
                            enrollment_service.sync_from_planning_center(
                                registration_data, updated_by=updated_by
                            )
                            records_successful += 1
                        except Exception as e:
                            records_failed += 1
                            errors.append(f"Registration {registration_data.get('id')}: {str(e)}")
                        
                        # Update progress
                        progress = 20 + int((i + 1) / total_records * 70)
                        self._update_sync_task(task_id, progress=progress, 
                                             message=f"Processed {i + 1}/{total_records} registrations")
                else:
                    # Sync all registrations (this could be expensive)
                    self._update_sync_task(task_id, progress=10, message="Fetching all events for registration sync...")
                    events_response = await client.get(
                        f"{self.base_url}/events/v2/events",
                        headers=self.headers,
                        params={"per_page": 100}
                    )
                    events_response.raise_for_status()
                    events_data = events_response.json()
                    
                    total_events = len(events_data.get("data", []))
                    self._update_sync_task(task_id, progress=20, message=f"Processing registrations for {total_events} events...")
                    
                    for event_idx, event_data in enumerate(events_data.get("data", [])):
                        event_id = event_data.get("id")
                        registrations_response = await client.get(
                            f"{self.base_url}/events/v2/events/{event_id}/registrations",
                            headers=self.headers,
                            params={"per_page": 100}
                        )
                        registrations_response.raise_for_status()
                        registrations_data = registrations_response.json()
                        
                        for registration_data in registrations_data.get("data", []):
                            records_processed += 1
                            try:
                                # Cache registration data
                                self._cache_registration_data(db, registration_data)
                                
                                # Sync enrollment
                                enrollment_service = CourseEnrollmentService(db)
                                enrollment_service.sync_from_planning_center(
                                    registration_data, updated_by=updated_by
                                )
                                records_successful += 1
                            except Exception as e:
                                records_failed += 1
                                errors.append(f"Registration {registration_data.get('id')}: {str(e)}")
                        
                        # Update progress
                        progress = 20 + int((event_idx + 1) / total_events * 70)
                        self._update_sync_task(task_id, progress=progress, 
                                             message=f"Processed {event_idx + 1}/{total_events} events")
                
                # Update sync log
                sync_log.records_processed = records_processed
                sync_log.records_successful = records_successful
                sync_log.records_failed = records_failed
                sync_log.completed_at = datetime.utcnow()
                if errors:
                    sync_log.error_details = {"errors": errors}
                
                db.commit()
                
                result = {
                    "status": "success",
                    "records_processed": records_processed,
                    "records_successful": records_successful,
                    "records_failed": records_failed,
                    "errors": errors
                }
                
                self._update_sync_task(task_id, status="completed", progress=100, 
                                     message="Registrations sync completed successfully", result=result)
                
        except Exception as e:
            self._update_sync_task(task_id, status="failed", 
                                 message=f"Registrations sync failed: {str(e)}", error=str(e))
            if 'sync_log' in locals():
                sync_log.completed_at = datetime.utcnow()
                sync_log.error_details = {"error": str(e)}
                db.commit()
        finally:
            db.close()
    
    async def _sync_all_background(self, task_id: str, updated_by: Optional[int] = None):
        """Background sync of all data from Planning Center"""
        try:
            self._update_sync_task(task_id, status="running", message="Starting full sync...")
            
            # Sync in order: people, events, then registrations
            self._update_sync_task(task_id, progress=10, message="Starting people sync...")
            people_task_id = self._create_sync_task("sync_people")
            await self._sync_people_background(people_task_id, updated_by)
            
            self._update_sync_task(task_id, progress=40, message="Starting events sync...")
            events_task_id = self._create_sync_task("sync_events")
            await self._sync_events_background(events_task_id, updated_by)
            
            self._update_sync_task(task_id, progress=70, message="Starting registrations sync...")
            registrations_task_id = self._create_sync_task("sync_registrations")
            await self._sync_registrations_background(registrations_task_id, None, updated_by)
            
            # Get results from individual syncs
            people_result = self.get_sync_task_status(people_task_id)
            events_result = self.get_sync_task_status(events_task_id)
            registrations_result = self.get_sync_task_status(registrations_task_id)
            
            result = {
                "people": people_result.get("result") if people_result else None,
                "events": events_result.get("result") if events_result else None,
                "registrations": registrations_result.get("result") if registrations_result else None
            }
            
            self._update_sync_task(task_id, status="completed", progress=100, 
                                 message="Full sync completed successfully", result=result)
            
        except Exception as e:
            self._update_sync_task(task_id, status="failed", 
                                 message=f"Full sync failed: {str(e)}", error=str(e))
    
    # Keep the original sync methods for backward compatibility
    async def sync_people(self, updated_by: Optional[int] = None) -> Dict[str, Any]:
        """Sync people from Planning Center"""
        sync_log = PlanningCenterSyncLog(
            sync_type="people",
            sync_direction="from_pc",
            started_at=datetime.utcnow(),
            created_by=updated_by
        )
        self.db.add(sync_log)
        self.db.commit()
        
        try:
            async with httpx.AsyncClient() as client:
                # Get all people from Planning Center
                response = await client.get(
                    f"{self.base_url}/people/v2/people",
                    headers=self.headers,
                    params={"per_page": 100}
                )
                response.raise_for_status()
                
                people_data = response.json()
                records_processed = 0
                records_successful = 0
                records_failed = 0
                errors = []
                
                for person_data in people_data.get("data", []):
                    records_processed += 1
                    try:
                        self.people_service.sync_from_planning_center(
                            person_data, updated_by=updated_by
                        )
                        records_successful += 1
                    except Exception as e:
                        records_failed += 1
                        errors.append(f"Person {person_data.get('id')}: {str(e)}")
                
                # Update sync log
                sync_log.records_processed = records_processed
                sync_log.records_successful = records_successful
                sync_log.records_failed = records_failed
                sync_log.completed_at = datetime.utcnow()
                if errors:
                    sync_log.error_details = {"errors": errors}
                
                self.db.commit()
                
                return {
                    "status": "success",
                    "records_processed": records_processed,
                    "records_successful": records_successful,
                    "records_failed": records_failed,
                    "errors": errors
                }
                
        except Exception as e:
            sync_log.completed_at = datetime.utcnow()
            sync_log.error_details = {"error": str(e)}
            self.db.commit()
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def sync_events(self, updated_by: Optional[int] = None) -> Dict[str, Any]:
        """Sync events (courses) from Planning Center"""
        sync_log = PlanningCenterSyncLog(
            sync_type="events",
            sync_direction="from_pc",
            started_at=datetime.utcnow(),
            created_by=updated_by
        )
        self.db.add(sync_log)
        self.db.commit()
        
        try:
            async with httpx.AsyncClient() as client:
                # Get all events from Planning Center
                response = await client.get(
                    f"{self.base_url}/events/v2/events",
                    headers=self.headers,
                    params={"per_page": 100}
                )
                response.raise_for_status()
                
                events_data = response.json()
                records_processed = 0
                records_successful = 0
                records_failed = 0
                errors = []
                
                for event_data in events_data.get("data", []):
                    records_processed += 1
                    try:
                        # Cache event data
                        self._cache_event_data(event_data)
                        
                        # Sync course
                        self.course_service.sync_from_planning_center(
                            event_data, updated_by=updated_by
                        )
                        records_successful += 1
                    except Exception as e:
                        records_failed += 1
                        errors.append(f"Event {event_data.get('id')}: {str(e)}")
                
                # Update sync log
                sync_log.records_processed = records_processed
                sync_log.records_successful = records_successful
                sync_log.records_failed = records_failed
                sync_log.completed_at = datetime.utcnow()
                if errors:
                    sync_log.error_details = {"errors": errors}
                
                self.db.commit()
                
                return {
                    "status": "success",
                    "records_processed": records_processed,
                    "records_successful": records_successful,
                    "records_failed": records_failed,
                    "errors": errors
                }
                
        except Exception as e:
            sync_log.completed_at = datetime.utcnow()
            sync_log.error_details = {"error": str(e)}
            self.db.commit()
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def sync_registrations(self, event_id: Optional[str] = None, updated_by: Optional[int] = None) -> Dict[str, Any]:
        """Sync registrations from Planning Center"""
        sync_log = PlanningCenterSyncLog(
            sync_type="registrations",
            sync_direction="from_pc",
            started_at=datetime.utcnow(),
            created_by=updated_by
        )
        self.db.add(sync_log)
        self.db.commit()
        
        try:
            async with httpx.AsyncClient() as client:
                records_processed = 0
                records_successful = 0
                records_failed = 0
                errors = []
                
                if event_id:
                    # Sync registrations for specific event
                    response = await client.get(
                        f"{self.base_url}/events/v2/events/{event_id}/registrations",
                        headers=self.headers,
                        params={"per_page": 100}
                    )
                    response.raise_for_status()
                    registrations_data = response.json()
                    
                    for registration_data in registrations_data.get("data", []):
                        records_processed += 1
                        try:
                            # Cache registration data
                            self._cache_registration_data(registration_data)
                            
                            # Sync enrollment
                            self.enrollment_service.sync_from_planning_center(
                                registration_data, updated_by=updated_by
                            )
                            records_successful += 1
                        except Exception as e:
                            records_failed += 1
                            errors.append(f"Registration {registration_data.get('id')}: {str(e)}")
                else:
                    # Sync all registrations (this could be expensive)
                    # Get all events first, then get registrations for each
                    events_response = await client.get(
                        f"{self.base_url}/events/v2/events",
                        headers=self.headers,
                        params={"per_page": 100}
                    )
                    events_response.raise_for_status()
                    events_data = events_response.json()
                    
                    for event_data in events_data.get("data", []):
                        event_id = event_data.get("id")
                        registrations_response = await client.get(
                            f"{self.base_url}/events/v2/events/{event_id}/registrations",
                            headers=self.headers,
                            params={"per_page": 100}
                        )
                        registrations_response.raise_for_status()
                        registrations_data = registrations_response.json()
                        
                        for registration_data in registrations_data.get("data", []):
                            records_processed += 1
                            try:
                                # Cache registration data
                                self._cache_registration_data(registration_data)
                                
                                # Sync enrollment
                                self.enrollment_service.sync_from_planning_center(
                                    registration_data, updated_by=updated_by
                                )
                                records_successful += 1
                            except Exception as e:
                                records_failed += 1
                                errors.append(f"Registration {registration_data.get('id')}: {str(e)}")
                
                # Update sync log
                sync_log.records_processed = records_processed
                sync_log.records_successful = records_successful
                sync_log.records_failed = records_failed
                sync_log.completed_at = datetime.utcnow()
                if errors:
                    sync_log.error_details = {"errors": errors}
                
                self.db.commit()
                
                return {
                    "status": "success",
                    "records_processed": records_processed,
                    "records_successful": records_successful,
                    "records_failed": records_failed,
                    "errors": errors
                }
                
        except Exception as e:
            sync_log.completed_at = datetime.utcnow()
            sync_log.error_details = {"error": str(e)}
            self.db.commit()
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _cache_event_data(self, db: Session, event_data: Dict[str, Any]):
        """Cache event data from Planning Center"""
        pc_event_id = event_data.get("id")
        
        # Check if already cached
        existing_cache = db.query(PlanningCenterEventsCache).filter(
            PlanningCenterEventsCache.planning_center_event_id == pc_event_id
        ).first()
        
        if existing_cache:
            # Update existing cache
            existing_cache.event_name = event_data.get("name")
            existing_cache.event_description = event_data.get("description")
            existing_cache.start_date = event_data.get("start_date")
            existing_cache.end_date = event_data.get("end_date")
            existing_cache.max_capacity = event_data.get("max_capacity")
            existing_cache.current_registrations_count = event_data.get("current_registrations", 0)
            existing_cache.registration_deadline = event_data.get("registration_deadline")
            existing_cache.event_status = event_data.get("status")
            existing_cache.last_synced_at = datetime.utcnow()
            existing_cache.updated_at = datetime.utcnow()
        else:
            # Create new cache entry
            cache_entry = PlanningCenterEventsCache(
                planning_center_event_id=pc_event_id,
                event_name=event_data.get("name"),
                event_description=event_data.get("description"),
                start_date=event_data.get("start_date"),
                end_date=event_data.get("end_date"),
                max_capacity=event_data.get("max_capacity"),
                current_registrations_count=event_data.get("current_registrations", 0),
                registration_deadline=event_data.get("registration_deadline"),
                event_status=event_data.get("status"),
                last_synced_at=datetime.utcnow()
            )
            db.add(cache_entry)
        
        db.commit()
    
    def _cache_registration_data(self, db: Session, registration_data: Dict[str, Any]):
        """Cache registration data from Planning Center"""
        pc_registration_id = registration_data.get("id")
        
        # Check if already cached
        existing_cache = db.query(PlanningCenterRegistrationsCache).filter(
            PlanningCenterRegistrationsCache.planning_center_registration_id == pc_registration_id
        ).first()
        
        if existing_cache:
            # Update existing cache
            existing_cache.registration_status = registration_data.get("status")
            existing_cache.registration_date = registration_data.get("created_at")
            existing_cache.registration_notes = registration_data.get("notes")
            existing_cache.custom_field_responses = registration_data.get("custom_field_responses")
            existing_cache.last_synced_at = datetime.utcnow()
            existing_cache.updated_at = datetime.utcnow()
        else:
            # Create new cache entry
            cache_entry = PlanningCenterRegistrationsCache(
                planning_center_registration_id=pc_registration_id,
                planning_center_event_id=registration_data.get("event_id"),
                planning_center_person_id=registration_data.get("person_id"),
                registration_status=registration_data.get("status"),
                registration_date=registration_data.get("created_at"),
                registration_notes=registration_data.get("notes"),
                custom_field_responses=registration_data.get("custom_field_responses"),
                last_synced_at=datetime.utcnow()
            )
            db.add(cache_entry)
        
        db.commit()
    
    def process_webhook_event(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook event from Planning Center"""
        try:
            # Store webhook event
            webhook_event = PlanningCenterWebhookEvents(
                event_type=webhook_data.get("event_type"),
                planning_center_id=webhook_data.get("id"),
                payload=webhook_data
            )
            self.db.add(webhook_event)
            self.db.commit()
            
            # Process based on event type
            event_type = webhook_data.get("event_type")
            if event_type == "person.created" or event_type == "person.updated":
                # Sync person data
                asyncio.create_task(self.sync_people())
            elif event_type == "event.created" or event_type == "event.updated":
                # Sync event data
                asyncio.create_task(self.sync_events())
            elif event_type == "registration.created" or event_type == "registration.updated":
                # Sync registration data
                event_id = webhook_data.get("event_id")
                asyncio.create_task(self.sync_registrations(event_id=event_id))
            
            # Mark webhook as processed
            webhook_event.processed = True
            webhook_event.processed_at = datetime.utcnow()
            self.db.commit()
            
            return {"status": "success", "message": "Webhook processed successfully"}
            
        except Exception as e:
            # Mark webhook as failed
            if 'webhook_event' in locals():
                webhook_event.processed = True
                webhook_event.processed_at = datetime.utcnow()
                webhook_event.error_message = str(e)
                self.db.commit()
            
            return {"status": "error", "error": str(e)}
