"""
Planning Center Sync Service
"""

import asyncio
import logging
import re
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from dateutil import parser
import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    PlanningCenterAPIError,
    PlanningCenterAuthenticationError,
    PlanningCenterRateLimitError,
    PlanningCenterNotFoundError,
)

logger = logging.getLogger(__name__)
from app.models.planning_center_events_cache import PlanningCenterEventsCache
from app.models.planning_center_registrations_cache import \
    PlanningCenterRegistrationsCache
from app.models.planning_center_sync_log import PlanningCenterSyncLog
from app.models.planning_center_webhook_events import \
    PlanningCenterWebhookEvents
from app.services.course_service import CourseService
from app.services.enrollment_service import CourseEnrollmentService
from app.services.people_service import PeopleService

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

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not date_str:
            return None
        try:
            return parser.parse(date_str)
        except (ValueError, TypeError):
            return None

    def _get_db_session(self):
        """Get a new database session for background tasks"""
        from app.core.database import SessionLocal

        return SessionLocal()

    def _get_auth_headers(self) -> dict:
        """Get authentication headers for Planning Center API"""
        if not settings.PLANNING_CENTER_APP_ID or not settings.PLANNING_CENTER_SECRET:
            raise ValueError(
                "Planning Center credentials not configured. Please set PLANNING_CENTER_APP_ID and PLANNING_CENTER_SECRET."
            )

        # Use HTTP Basic Authentication for Personal Access Tokens
        import base64

        credentials = (
            f"{settings.PLANNING_CENTER_APP_ID}:{settings.PLANNING_CENTER_SECRET}"
        )
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }

    def _create_sync_task(self, task_type: str, task_id: str = None) -> str:
        """Create a new sync task entry"""
        if task_id is None:
            task_id = str(uuid.uuid4())

        sync_tasks[task_id] = {
            "task_type": task_type,
            "status": "pending",
            "started_at": datetime.now(timezone.utc),
            "progress": 0,
            "message": "Task queued",
            "result": None,
            "error": None,
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
            try:
                asyncio.run(self._sync_people_background(task_id, updated_by))
                logger.info(f"Background sync {task_id} completed")
            except Exception as e:
                logger.error(f"Background sync {task_id} encountered fatal error: {e}", exc_info=True)
                try:
                    self._update_sync_task(task_id, status="failed", message=f"Fatal error: {str(e)}")
                except Exception as db_error:
                    logger.error(f"Failed to update task status: {db_error}", exc_info=True)

        thread = threading.Thread(target=run_sync, daemon=False)
        thread.start()

        return task_id

    def start_sync_events(self, updated_by: Optional[int] = None) -> str:
        """Start async sync of events from Planning Center"""
        task_id = self._create_sync_task("sync_events")

        # Start background task
        def run_sync():
            try:
                asyncio.run(self._sync_events_background(task_id, updated_by))
                logger.info(f"Background sync {task_id} completed")
            except Exception as e:
                logger.error(f"Background sync {task_id} encountered fatal error: {e}", exc_info=True)
                try:
                    self._update_sync_task(task_id, status="failed", message=f"Fatal error: {str(e)}")
                except Exception as db_error:
                    logger.error(f"Failed to update task status: {db_error}", exc_info=True)

        thread = threading.Thread(target=run_sync, daemon=False)
        thread.start()

        return task_id

    def start_sync_registrations(
        self, event_id: Optional[str] = None, updated_by: Optional[int] = None
    ) -> str:
        """Start async sync of registrations from Planning Center"""
        task_id = self._create_sync_task("sync_registrations")

        # Start background task
        def run_sync():
            try:
                asyncio.run(
                    self._sync_registrations_background(task_id, event_id, updated_by)
                )
                logger.info(f"Background sync {task_id} completed")
            except Exception as e:
                logger.error(f"Background sync {task_id} encountered fatal error: {e}", exc_info=True)
                try:
                    self._update_sync_task(task_id, status="failed", message=f"Fatal error: {str(e)}")
                except Exception as db_error:
                    logger.error(f"Failed to update task status: {db_error}", exc_info=True)

        thread = threading.Thread(target=run_sync, daemon=False)
        thread.start()

        return task_id

    def start_sync_all(self, updated_by: Optional[int] = None) -> str:
        """Start async sync of all data from Planning Center"""
        task_id = self._create_sync_task("sync_all")

        # Start background task
        def run_sync():
            try:
                asyncio.run(self._sync_all_background(task_id, updated_by))
                logger.info(f"Background sync {task_id} completed")
            except Exception as e:
                logger.error(f"Background sync {task_id} encountered fatal error: {e}", exc_info=True)
                try:
                    self._update_sync_task(task_id, status="failed", message=f"Fatal error: {str(e)}")
                except Exception as db_error:
                    logger.error(f"Failed to update task status: {db_error}", exc_info=True)

        thread = threading.Thread(target=run_sync, daemon=True)
        thread.start()

        return task_id

    async def _sync_people_background(
        self, task_id: str, updated_by: Optional[int] = None
    ):
        """Background sync of people from Planning Center"""
        db = self._get_db_session()
        try:
            self._update_sync_task(
                task_id, status="running", message="Starting people sync..."
            )

            sync_log = PlanningCenterSyncLog(
                sync_type="people",
                sync_direction="from_pc",
                started_at=datetime.now(timezone.utc),
                created_by=updated_by,
            )
            db.add(sync_log)
            db.commit()

            async with httpx.AsyncClient() as client:
                # Get all people from Planning Center
                self._update_sync_task(
                    task_id,
                    progress=10,
                    message="Fetching people from Planning Center...",
                )
                try:
                    response = await client.get(
                        f"{self.base_url}/people/v2/people",
                        headers=self.headers,
                        params={"per_page": 100},
                    )
                    response.raise_for_status()
                    people_data = response.json()
                except httpx.TimeoutException:
                    logger.warning(f"Request timed out: {self.base_url}/people/v2/people")
                    raise PlanningCenterAPIError("Request timed out", status_code=504)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 401:
                        raise PlanningCenterAuthenticationError("Authentication failed", status_code=401)
                    elif e.response.status_code == 429:
                        raise PlanningCenterRateLimitError("Rate limit exceeded", status_code=429)
                    elif e.response.status_code == 404:
                        raise PlanningCenterNotFoundError("Resource not found", status_code=404)
                    else:
                        logger.error(f"HTTP error {e.response.status_code}: {e}")
                        raise PlanningCenterAPIError(f"HTTP {e.response.status_code}", status_code=e.response.status_code)
                except httpx.ConnectError as e:
                    logger.error(f"Connection error: {e}")
                    raise PlanningCenterAPIError("Cannot connect to Planning Center")
                except ValueError as e:  # JSON decode errors
                    logger.error(f"Invalid JSON response: {e}")
                    raise PlanningCenterAPIError("Invalid response format")
                records_processed = 0
                records_successful = 0
                records_failed = 0
                errors = []

                total_records = len(people_data.get("data", []))
                self._update_sync_task(
                    task_id,
                    progress=20,
                    message=f"Processing {total_records} people...",
                )

                for i, person_data in enumerate(people_data.get("data", [])):
                    records_processed += 1
                    try:
                        # Sync to People table
                        people_service = PeopleService(db)
                        people_service.sync_from_planning_center(
                            person_data, updated_by=updated_by
                        )
                        
                        # Also create user if person has email and is a leader/instructor
                        attrs = person_data.get("attributes", {})
                        email = attrs.get("email")
                        # Check if person is a leader or has instructor role
                        # You can customize this logic based on your Planning Center setup
                        is_leader = attrs.get("status") == "leader" or attrs.get("leader") == True
                        # For now, create users for all people with emails
                        # You can add more filtering logic here
                        if email:
                            from app.services.user_service import UserService
                            user_service = UserService(db)
                            # Only create users for leaders/instructors, or all if you want
                            # For now, we'll create users for people with emails
                            # You can add role-based filtering here
                            user_service.create_user_from_planning_center(
                                person_data, 
                                default_role="instructor" if is_leader else "staff",
                                created_by=updated_by
                            )
                        
                        records_successful += 1
                    except Exception as e:
                        records_failed += 1
                        errors.append(f"Person {person_data.get('id')}: {str(e)}")

                    # Update progress
                    progress = 20 + int((i + 1) / total_records * 70)
                    self._update_sync_task(
                        task_id,
                        progress=progress,
                        message=f"Processed {i + 1}/{total_records} people",
                    )

                # Update sync log
                sync_log.records_processed = records_processed
                sync_log.records_successful = records_successful
                sync_log.records_failed = records_failed
                sync_log.completed_at = datetime.now(timezone.utc)
                if errors:
                    sync_log.error_details = {"errors": errors}

                db.commit()

                result = {
                    "status": "success",
                    "records_processed": records_processed,
                    "records_successful": records_successful,
                    "records_failed": records_failed,
                    "errors": errors,
                }

                self._update_sync_task(
                    task_id,
                    status="completed",
                    progress=100,
                    message="People sync completed successfully",
                    result=result,
                )

        except Exception as e:
            self._update_sync_task(
                task_id,
                status="failed",
                message=f"People sync failed: {str(e)}",
                error=str(e),
            )
            if "sync_log" in locals():
                sync_log.completed_at = datetime.now(timezone.utc)
                sync_log.error_details = {"error": str(e)}
                db.commit()
        finally:
            db.close()

    async def _sync_events_background(
        self, task_id: str, updated_by: Optional[int] = None
    ):
        """Background sync of events from Planning Center"""
        db = self._get_db_session()
        try:
            self._update_sync_task(
                task_id, status="running", message="Starting events sync..."
            )

            sync_log = PlanningCenterSyncLog(
                sync_type="events",
                sync_direction="from_pc",
                started_at=datetime.now(timezone.utc),
                created_by=updated_by,
            )
            db.add(sync_log)
            db.commit()

            async with httpx.AsyncClient() as client:
                # Get all events from Planning Center
                self._update_sync_task(
                    task_id,
                    progress=10,
                    message="Fetching events from Planning Center...",
                )
                try:
                    response = await client.get(
                        f"{self.base_url}/events/v2/events",
                        headers=self.headers,
                        params={"per_page": 100},
                    )
                    response.raise_for_status()
                    events_data = response.json()
                except httpx.TimeoutException:
                    logger.warning(f"Request timed out: {self.base_url}/events/v2/events")
                    raise PlanningCenterAPIError("Request timed out", status_code=504)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 401:
                        raise PlanningCenterAuthenticationError("Authentication failed", status_code=401)
                    elif e.response.status_code == 429:
                        raise PlanningCenterRateLimitError("Rate limit exceeded", status_code=429)
                    elif e.response.status_code == 404:
                        raise PlanningCenterNotFoundError("Resource not found", status_code=404)
                    else:
                        logger.error(f"HTTP error {e.response.status_code}: {e}")
                        raise PlanningCenterAPIError(f"HTTP {e.response.status_code}", status_code=e.response.status_code)
                except httpx.ConnectError as e:
                    logger.error(f"Connection error: {e}")
                    raise PlanningCenterAPIError("Cannot connect to Planning Center")
                except ValueError as e:  # JSON decode errors
                    logger.error(f"Invalid JSON response: {e}")
                    raise PlanningCenterAPIError("Invalid response format")
                records_processed = 0
                records_successful = 0
                records_failed = 0
                errors = []

                total_records = len(events_data.get("data", []))
                self._update_sync_task(
                    task_id,
                    progress=20,
                    message=f"Processing {total_records} events...",
                )

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
                    self._update_sync_task(
                        task_id,
                        progress=progress,
                        message=f"Processed {i + 1}/{total_records} events",
                    )

                # Update sync log
                sync_log.records_processed = records_processed
                sync_log.records_successful = records_successful
                sync_log.records_failed = records_failed
                sync_log.completed_at = datetime.now(timezone.utc)
                if errors:
                    sync_log.error_details = {"errors": errors}

                db.commit()

                result = {
                    "status": "success",
                    "records_processed": records_processed,
                    "records_successful": records_successful,
                    "records_failed": records_failed,
                    "errors": errors,
                }

                self._update_sync_task(
                    task_id,
                    status="completed",
                    progress=100,
                    message="Events sync completed successfully",
                    result=result,
                )

        except Exception as e:
            self._update_sync_task(
                task_id,
                status="failed",
                message=f"Events sync failed: {str(e)}",
                error=str(e),
            )
            if "sync_log" in locals():
                sync_log.completed_at = datetime.now(timezone.utc)
                sync_log.error_details = {"error": str(e)}
                db.commit()
        finally:
            db.close()

    async def _sync_registrations_background(
        self,
        task_id: str,
        event_id: Optional[str] = None,
        updated_by: Optional[int] = None,
    ):
        """Background sync of registrations from Planning Center"""
        db = self._get_db_session()
        try:
            self._update_sync_task(
                task_id, status="running", message="Starting registrations sync..."
            )

            sync_log = PlanningCenterSyncLog(
                sync_type="registrations",
                sync_direction="from_pc",
                started_at=datetime.now(timezone.utc),
                created_by=updated_by,
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
                    self._update_sync_task(
                        task_id,
                        progress=10,
                        message=f"Fetching registrations for event {event_id}...",
                    )
                    try:
                        response = await client.get(
                            f"{self.base_url}/events/v2/events/{event_id}/registrations",
                            headers=self.headers,
                            params={"per_page": 100},
                        )
                        response.raise_for_status()
                        registrations_data = response.json()
                    except httpx.TimeoutException:
                        logger.warning(f"Request timed out: event {event_id} registrations")
                        raise PlanningCenterAPIError("Request timed out", status_code=504)
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 401:
                            raise PlanningCenterAuthenticationError("Authentication failed", status_code=401)
                        elif e.response.status_code == 429:
                            raise PlanningCenterRateLimitError("Rate limit exceeded", status_code=429)
                        elif e.response.status_code == 404:
                            raise PlanningCenterNotFoundError("Resource not found", status_code=404)
                        else:
                            logger.error(f"HTTP error {e.response.status_code}: {e}")
                            raise PlanningCenterAPIError(f"HTTP {e.response.status_code}", status_code=e.response.status_code)
                    except httpx.ConnectError as e:
                        logger.error(f"Connection error: {e}")
                        raise PlanningCenterAPIError("Cannot connect to Planning Center")
                    except ValueError as e:  # JSON decode errors
                        logger.error(f"Invalid JSON response: {e}")
                        raise PlanningCenterAPIError("Invalid response format")

                    total_records = len(registrations_data.get("data", []))
                    self._update_sync_task(
                        task_id,
                        progress=20,
                        message=f"Processing {total_records} registrations...",
                    )

                    for i, registration_data in enumerate(
                        registrations_data.get("data", [])
                    ):
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
                            errors.append(
                                f"Registration {registration_data.get('id')}: {str(e)}"
                            )

                        # Update progress
                        progress = 20 + int((i + 1) / total_records * 70)
                        self._update_sync_task(
                            task_id,
                            progress=progress,
                            message=f"Processed {i + 1}/{total_records} registrations",
                        )
                else:
                    # Sync all registrations (this could be expensive)
                    self._update_sync_task(
                        task_id,
                        progress=10,
                        message="Fetching all events for registration sync...",
                    )
                    try:
                        events_response = await client.get(
                            f"{self.base_url}/events/v2/events",
                            headers=self.headers,
                            params={"per_page": 100},
                        )
                        events_response.raise_for_status()
                        events_data = events_response.json()
                    except httpx.TimeoutException:
                        logger.warning(f"Request timed out: fetching events")
                        raise PlanningCenterAPIError("Request timed out", status_code=504)
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 401:
                            raise PlanningCenterAuthenticationError("Authentication failed", status_code=401)
                        elif e.response.status_code == 429:
                            raise PlanningCenterRateLimitError("Rate limit exceeded", status_code=429)
                        elif e.response.status_code == 404:
                            raise PlanningCenterNotFoundError("Resource not found", status_code=404)
                        else:
                            logger.error(f"HTTP error {e.response.status_code}: {e}")
                            raise PlanningCenterAPIError(f"HTTP {e.response.status_code}", status_code=e.response.status_code)
                    except httpx.ConnectError as e:
                        logger.error(f"Connection error: {e}")
                        raise PlanningCenterAPIError("Cannot connect to Planning Center")
                    except ValueError as e:  # JSON decode errors
                        logger.error(f"Invalid JSON response: {e}")
                        raise PlanningCenterAPIError("Invalid response format")

                    total_events = len(events_data.get("data", []))
                    self._update_sync_task(
                        task_id,
                        progress=20,
                        message=f"Processing registrations for {total_events} events...",
                    )

                    for event_idx, event_data in enumerate(events_data.get("data", [])):
                        event_id = event_data.get("id")
                        try:
                            registrations_response = await client.get(
                                f"{self.base_url}/events/v2/events/{event_id}/registrations",
                                headers=self.headers,
                                params={"per_page": 100},
                            )
                            registrations_response.raise_for_status()
                            registrations_data = registrations_response.json()
                        except httpx.TimeoutException:
                            logger.warning(f"Request timed out: event {event_id} registrations")
                            raise PlanningCenterAPIError("Request timed out", status_code=504)
                        except httpx.HTTPStatusError as e:
                            if e.response.status_code == 401:
                                raise PlanningCenterAuthenticationError("Authentication failed", status_code=401)
                            elif e.response.status_code == 429:
                                raise PlanningCenterRateLimitError("Rate limit exceeded", status_code=429)
                            elif e.response.status_code == 404:
                                raise PlanningCenterNotFoundError("Resource not found", status_code=404)
                            else:
                                logger.error(f"HTTP error {e.response.status_code}: {e}")
                                raise PlanningCenterAPIError(f"HTTP {e.response.status_code}", status_code=e.response.status_code)
                        except httpx.ConnectError as e:
                            logger.error(f"Connection error: {e}")
                            raise PlanningCenterAPIError("Cannot connect to Planning Center")
                        except ValueError as e:  # JSON decode errors
                            logger.error(f"Invalid JSON response: {e}")
                            raise PlanningCenterAPIError("Invalid response format")

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
                                errors.append(
                                    f"Registration {registration_data.get('id')}: {str(e)}"
                                )

                        # Update progress
                        progress = 20 + int((event_idx + 1) / total_events * 70)
                        self._update_sync_task(
                            task_id,
                            progress=progress,
                            message=f"Processed {event_idx + 1}/{total_events} events",
                        )

                # Update sync log
                sync_log.records_processed = records_processed
                sync_log.records_successful = records_successful
                sync_log.records_failed = records_failed
                sync_log.completed_at = datetime.now(timezone.utc)
                if errors:
                    sync_log.error_details = {"errors": errors}

                db.commit()

                result = {
                    "status": "success",
                    "records_processed": records_processed,
                    "records_successful": records_successful,
                    "records_failed": records_failed,
                    "errors": errors,
                }

                self._update_sync_task(
                    task_id,
                    status="completed",
                    progress=100,
                    message="Registrations sync completed successfully",
                    result=result,
                )

        except Exception as e:
            self._update_sync_task(
                task_id,
                status="failed",
                message=f"Registrations sync failed: {str(e)}",
                error=str(e),
            )
            if "sync_log" in locals():
                sync_log.completed_at = datetime.now(timezone.utc)
                sync_log.error_details = {"error": str(e)}
                db.commit()
        finally:
            db.close()

    async def _sync_all_background(
        self, task_id: str, updated_by: Optional[int] = None
    ):
        """Background sync of all data from Planning Center"""
        try:
            self._update_sync_task(
                task_id, status="running", message="Starting full sync..."
            )

            # Sync in order: people, events, then registrations
            self._update_sync_task(
                task_id, progress=10, message="Starting people sync..."
            )
            people_task_id = self._create_sync_task("sync_people")
            await self._sync_people_background(people_task_id, updated_by)

            self._update_sync_task(
                task_id, progress=40, message="Starting events sync..."
            )
            events_task_id = self._create_sync_task("sync_events")
            await self._sync_events_background(events_task_id, updated_by)

            self._update_sync_task(
                task_id, progress=70, message="Starting registrations sync..."
            )
            registrations_task_id = self._create_sync_task("sync_registrations")
            await self._sync_registrations_background(
                registrations_task_id, None, updated_by
            )

            # Get results from individual syncs
            people_result = self.get_sync_task_status(people_task_id)
            events_result = self.get_sync_task_status(events_task_id)
            registrations_result = self.get_sync_task_status(registrations_task_id)

            result = {
                "people": people_result.get("result") if people_result else None,
                "events": events_result.get("result") if events_result else None,
                "registrations": (
                    registrations_result.get("result") if registrations_result else None
                ),
            }

            self._update_sync_task(
                task_id,
                status="completed",
                progress=100,
                message="Full sync completed successfully",
                result=result,
            )

        except Exception as e:
            self._update_sync_task(
                task_id,
                status="failed",
                message=f"Full sync failed: {str(e)}",
                error=str(e),
            )

    # Keep the original sync methods for backward compatibility
    async def sync_people(self, updated_by: Optional[int] = None) -> Dict[str, Any]:
        """Sync people from Planning Center"""
        sync_log = PlanningCenterSyncLog(
            sync_type="people",
            sync_direction="from_pc",
            started_at=datetime.now(timezone.utc),
            created_by=updated_by,
        )
        self.db.add(sync_log)
        self.db.commit()

        try:
            async with httpx.AsyncClient() as client:
                # Get all people from Planning Center
                try:
                    response = await client.get(
                        f"{self.base_url}/people/v2/people",
                        headers=self.headers,
                        params={"per_page": 100},
                    )
                    response.raise_for_status()
                    people_data = response.json()
                except httpx.TimeoutException:
                    logger.warning(f"Request timed out: {self.base_url}/people/v2/people")
                    raise PlanningCenterAPIError("Request timed out", status_code=504)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 401:
                        raise PlanningCenterAuthenticationError("Authentication failed", status_code=401)
                    elif e.response.status_code == 429:
                        raise PlanningCenterRateLimitError("Rate limit exceeded", status_code=429)
                    elif e.response.status_code == 404:
                        raise PlanningCenterNotFoundError("Resource not found", status_code=404)
                    else:
                        logger.error(f"HTTP error {e.response.status_code}: {e}")
                        raise PlanningCenterAPIError(f"HTTP {e.response.status_code}", status_code=e.response.status_code)
                except httpx.ConnectError as e:
                    logger.error(f"Connection error: {e}")
                    raise PlanningCenterAPIError("Cannot connect to Planning Center")
                except ValueError as e:  # JSON decode errors
                    logger.error(f"Invalid JSON response: {e}")
                    raise PlanningCenterAPIError("Invalid response format")
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
                sync_log.completed_at = datetime.now(timezone.utc)
                if errors:
                    sync_log.error_details = {"errors": errors}

                self.db.commit()

                return {
                    "status": "success",
                    "records_processed": records_processed,
                    "records_successful": records_successful,
                    "records_failed": records_failed,
                    "errors": errors,
                }

        except Exception as e:
            sync_log.completed_at = datetime.now(timezone.utc)
            sync_log.error_details = {"error": str(e)}
            self.db.commit()

            return {"status": "error", "error": str(e)}

    async def sync_events(self, updated_by: Optional[int] = None) -> Dict[str, Any]:
        """Sync events (courses) from Planning Center"""
        sync_log = PlanningCenterSyncLog(
            sync_type="events",
            sync_direction="from_pc",
            started_at=datetime.now(timezone.utc),
            created_by=updated_by,
        )
        self.db.add(sync_log)
        self.db.commit()

        try:
            async with httpx.AsyncClient() as client:
                # Get all events from Planning Center
                try:
                    response = await client.get(
                        f"{self.base_url}/events/v2/events",
                        headers=self.headers,
                        params={"per_page": 100},
                    )
                    response.raise_for_status()
                    events_data = response.json()
                except httpx.TimeoutException:
                    logger.warning(f"Request timed out: {self.base_url}/events/v2/events")
                    raise PlanningCenterAPIError("Request timed out", status_code=504)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 401:
                        raise PlanningCenterAuthenticationError("Authentication failed", status_code=401)
                    elif e.response.status_code == 429:
                        raise PlanningCenterRateLimitError("Rate limit exceeded", status_code=429)
                    elif e.response.status_code == 404:
                        raise PlanningCenterNotFoundError("Resource not found", status_code=404)
                    else:
                        logger.error(f"HTTP error {e.response.status_code}: {e}")
                        raise PlanningCenterAPIError(f"HTTP {e.response.status_code}", status_code=e.response.status_code)
                except httpx.ConnectError as e:
                    logger.error(f"Connection error: {e}")
                    raise PlanningCenterAPIError("Cannot connect to Planning Center")
                except ValueError as e:  # JSON decode errors
                    logger.error(f"Invalid JSON response: {e}")
                    raise PlanningCenterAPIError("Invalid response format")
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
                sync_log.completed_at = datetime.now(timezone.utc)
                if errors:
                    sync_log.error_details = {"errors": errors}

                self.db.commit()

                return {
                    "status": "success",
                    "records_processed": records_processed,
                    "records_successful": records_successful,
                    "records_failed": records_failed,
                    "errors": errors,
                }

        except Exception as e:
            sync_log.completed_at = datetime.now(timezone.utc)
            sync_log.error_details = {"error": str(e)}
            self.db.commit()

            return {"status": "error", "error": str(e)}

    def get_events(self) -> List[Dict[str, Any]]:
        """
        Get events from Planning Center (synchronous)
        
        Uses cache if available and fresh, otherwise fetches from API.
        Tries Check-Ins API first, falls back to Calendar API if Check-Ins is not available.
        
        Returns:
            List of event dictionaries from Planning Center API
        """
        import httpx
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Check cache first
        cache_ttl_minutes = settings.PLANNING_CENTER_CACHE_TTL_MINUTES
        if cache_ttl_minutes > 0:
            cached_events = self._get_cached_events(cache_ttl_minutes)
            if cached_events is not None:
                logger.info(f"Returning {len(cached_events)} events from cache")
                return cached_events
        
        # Cache miss or stale - fetch from API
        try:
            with httpx.Client(timeout=30.0) as client:
                events = []
                per_page = 100
                offset = 0
                api_source = None  # Track which API we used
                
                # Try Check-Ins API first
                try:
                    response = client.get(
                        f"{self.base_url}/check-ins/v2/events",
                        headers=self.headers,
                        params={"per_page": per_page, "offset": offset, "order": "-created_at"},
                    )
                    
                    # If 404, try Calendar API as fallback
                    if response.status_code == 404:
                        logger.info("Check-Ins API returned 404, trying Calendar API as fallback")
                        events = self._get_events_from_calendar(client)
                        api_source = "calendar"
                    # If 401, the token doesn't have Check-Ins access - try Calendar API
                    elif response.status_code == 401:
                        logger.info("Check-Ins API returned 401 (no access), trying Calendar API as fallback")
                        events = self._get_events_from_calendar(client)
                        api_source = "calendar"
                    else:
                        response.raise_for_status()
                        data = response.json()
                        
                        page_events = data.get("data", [])
                        if not page_events:
                            # If no events from Check-Ins, try Calendar as fallback
                            logger.info("No events from Check-Ins API, trying Calendar API as fallback")
                            events = self._get_events_from_calendar(client)
                            api_source = "calendar"
                        else:
                            events.extend(page_events)
                            api_source = "checkins"
                            
                            # Check if there are more pages
                            if len(page_events) < per_page:
                                pass  # No more pages
                            else:
                                offset += per_page
                                
                                # Continue paginating up to configured limit
                                max_events = settings.PLANNING_CENTER_MAX_EVENTS
                                while len(events) < max_events:
                                    response = client.get(
                                        f"{self.base_url}/check-ins/v2/events",
                                        headers=self.headers,
                                        params={"per_page": per_page, "offset": offset, "order": "-created_at"},
                                    )
                                    response.raise_for_status()
                                    data = response.json()
                                    page_events = data.get("data", [])
                                    if not page_events:
                                        break
                                    events.extend(page_events)
                                    if len(page_events) < per_page:
                                        break
                                    offset += per_page
                    
                    # Update cache after fetching
                    if cache_ttl_minutes > 0 and events:
                        logger.info(f"Caching {len(events)} events from {api_source or 'API'}")
                        self._update_events_cache(events)
                    
                    return events
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in [401, 404]:
                        logger.info(f"Check-Ins API error {e.response.status_code}, trying Calendar API as fallback")
                        events = self._get_events_from_calendar(client)
                        # Update cache if we got events from Calendar API
                        if cache_ttl_minutes > 0 and events:
                            logger.info(f"Caching {len(events)} events from Calendar API fallback")
                            self._update_events_cache(events)
                        return events
                    raise
        except httpx.TimeoutException:
            logger.warning("Request timed out while fetching events")
            raise PlanningCenterAPIError("Request timed out", status_code=504)
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {e}")
            raise PlanningCenterAPIError("Cannot connect to Planning Center")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise PlanningCenterAPIError(f"Request failed: {str(e)}")
        except ValueError as e:  # JSON decode errors
            logger.error(f"Invalid JSON response: {e}")
            raise PlanningCenterAPIError("Invalid response format")
        except Exception as e:
            logger.error(f"Unexpected error fetching events: {e}", exc_info=True)
            raise

    def _get_events_from_calendar(self, client) -> List[Dict[str, Any]]:
        """
        Get events from Calendar API as fallback when Check-Ins API is not available
        
        Args:
            client: httpx.Client instance
            
        Returns:
            List of event dictionaries from Calendar API
        """
        import logging
        logger = logging.getLogger(__name__)
        
        events = []
        per_page = 100
        offset = 0
        
        try:
            while True:
                response = client.get(
                    f"{self.base_url}/calendar/v2/events",
                    headers=self.headers,
                    params={"per_page": per_page, "offset": offset, "order": "-starts_at"},
                )
                
                if response.status_code == 401:
                    error_detail = "Unknown error"
                    try:
                        error_data = response.json()
                        error_detail = error_data.get("errors", [{}])[0].get("detail", str(response.text))
                    except (ValueError, KeyError, IndexError) as e:
                        logger.debug(f"Could not parse error JSON from Planning Center response: {e}")
                        error_detail = str(response.text)
                    raise ValueError(f"Planning Center API authentication failed. Please check your PLANNING_CENTER_APP_ID and PLANNING_CENTER_SECRET credentials. Error: {error_detail}")
                
                if response.status_code == 404:
                    logger.warning("Calendar API also returned 404")
                    return []
                
                response.raise_for_status()
                data = response.json()
                
                page_events = data.get("data", [])
                if not page_events:
                    break
                
                events.extend(page_events)
                
                # Check if there are more pages
                if len(page_events) < per_page:
                    break
                
                offset += per_page
                
                # Limit to configured maximum events to avoid timeouts
                max_events = settings.PLANNING_CENTER_MAX_EVENTS
                if len(events) >= max_events:
                    break
            
            logger.info(f"Retrieved {len(events)} events from Calendar API")
            return events
        except httpx.TimeoutException:
            logger.warning("Request timed out while fetching events from Calendar API")
            raise PlanningCenterAPIError("Request timed out", status_code=504)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                error_detail = "Unknown error"
                try:
                    error_data = e.response.json()
                    error_detail = error_data.get("errors", [{}])[0].get("detail", str(e.response.text))
                except (ValueError, KeyError, IndexError) as json_error:
                    logger.debug(f"Could not parse error JSON from Planning Center response: {json_error}")
                    error_detail = str(e.response.text)
                logger.error(f"Planning Center API authentication failed (401): {error_detail}")
                raise PlanningCenterAuthenticationError(f"Authentication failed: {error_detail}", status_code=401)
            elif e.response.status_code == 429:
                raise PlanningCenterRateLimitError("Rate limit exceeded", status_code=429)
            elif e.response.status_code == 404:
                logger.warning("Calendar API returned 404")
                raise PlanningCenterNotFoundError("Resource not found", status_code=404)
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                raise PlanningCenterAPIError(f"HTTP {e.response.status_code}", status_code=e.response.status_code)
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {e}")
            raise PlanningCenterAPIError("Cannot connect to Planning Center")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise PlanningCenterAPIError(f"Request failed: {str(e)}")
        except ValueError as e:  # JSON decode errors
            logger.error(f"Invalid JSON response: {e}")
            raise PlanningCenterAPIError("Invalid response format")
        except Exception as e:
            logger.error(f"Unexpected error fetching events from Calendar API: {e}", exc_info=True)
            raise

    def get_lists(self) -> List[Dict[str, Any]]:
        """
        Get all lists from Planning Center People (synchronous)
        
        Returns:
            List of list dictionaries from Planning Center API
        """
        import httpx
        
        try:
            with httpx.Client(timeout=30.0) as client:
                lists = []
                per_page = 100
                offset = 0
                
                while True:
                    response = client.get(
                        f"{self.base_url}/people/v2/lists",
                        headers=self.headers,
                        params={"per_page": per_page, "offset": offset, "order": "name"},
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    page_lists = data.get("data", [])
                    if not page_lists:
                        break
                    
                    lists.extend(page_lists)
                    
                    # Check if there are more pages
                    if len(page_lists) < per_page:
                        break
                    
                    offset += per_page
                
                return lists
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Planning Center API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"Failed to connect to Planning Center API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error fetching lists: {str(e)}")

    def get_list_people(self, list_id: str) -> List[Dict[str, Any]]:
        """
        Get people from a Planning Center List (synchronous)
        
        Args:
            list_id: Planning Center list ID
        
        Returns:
            List of person dictionaries from Planning Center API
        """
        import httpx
        
        try:
            with httpx.Client(timeout=30.0) as client:
                people = []
                per_page = 100
                offset = 0
                
                while True:
                    response = client.get(
                        f"{self.base_url}/people/v2/lists/{list_id}/people",
                        headers=self.headers,
                        params={"per_page": per_page, "offset": offset},
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    page_people = data.get("data", [])
                    if not page_people:
                        break
                    
                    people.extend(page_people)
                    
                    # Check if there are more pages
                    if len(page_people) < per_page:
                        break
                    
                    offset += per_page
                
                return people
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Planning Center API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"Failed to connect to Planning Center API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error fetching list people: {str(e)}")

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single event from Planning Center by ID (synchronous)
        Tries Check-Ins API first, falls back to Calendar API if needed.
        
        Args:
            event_id: Planning Center event ID
            
        Returns:
            Event dictionary from Planning Center API or None if not found
        """
        import httpx
        
        # Try Check-Ins API first
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.base_url}/check-ins/v2/events/{event_id}",
                    headers=self.headers,
                )
                
                if response.status_code == 404:
                    # Try Calendar API as fallback
                    return self._get_event_from_calendar(event_id)
                    
                response.raise_for_status()
                data = response.json()
                
                return data.get("data")
        except httpx.TimeoutException:
            logger.warning(f"Request timed out: event {event_id}")
            raise PlanningCenterAPIError("Request timed out", status_code=504)
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (401, 404):
                # Try Calendar API as fallback
                return self._get_event_from_calendar(event_id)
            elif e.response.status_code == 429:
                raise PlanningCenterRateLimitError("Rate limit exceeded", status_code=429)
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                raise PlanningCenterAPIError(f"HTTP {e.response.status_code}", status_code=e.response.status_code)
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {e}")
            raise PlanningCenterAPIError("Cannot connect to Planning Center")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise PlanningCenterAPIError(f"Request failed: {str(e)}")
        except ValueError as e:  # JSON decode errors
            logger.error(f"Invalid JSON response: {e}")
            raise PlanningCenterAPIError("Invalid response format")
        except Exception as e:
            logger.error(f"Unexpected error fetching event: {e}", exc_info=True)
            raise

    def _get_event_from_calendar(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single event from Calendar API (fallback method)
        
        Args:
            event_id: Planning Center event ID
            
        Returns:
            Event dictionary from Calendar API or None if not found
        """
        import httpx
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.base_url}/calendar/v2/events/{event_id}",
                    headers=self.headers,
                )
                
                if response.status_code == 404:
                    return None
                    
                response.raise_for_status()
                data = response.json()
                
                return data.get("data")
        except httpx.TimeoutException:
            logger.warning(f"Request timed out: calendar event {event_id}")
            raise PlanningCenterAPIError("Request timed out", status_code=504)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            elif e.response.status_code == 401:
                raise PlanningCenterAuthenticationError("Authentication failed", status_code=401)
            elif e.response.status_code == 429:
                raise PlanningCenterRateLimitError("Rate limit exceeded", status_code=429)
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                raise PlanningCenterAPIError(f"HTTP {e.response.status_code}", status_code=e.response.status_code)
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {e}")
            raise PlanningCenterAPIError("Cannot connect to Planning Center")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise PlanningCenterAPIError(f"Request failed: {str(e)}")
        except ValueError as e:  # JSON decode errors
            logger.error(f"Invalid JSON response: {e}")
            raise PlanningCenterAPIError("Invalid response format")
        except Exception as e:
            logger.error(f"Unexpected error fetching event from Calendar API: {e}", exc_info=True)
            raise

    def search_people(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for people in Planning Center by name, email, or phone number.
        Uses Planning Center API's where parameter for efficient server-side filtering
        and paginates through results to search across all people.
        
        Args:
            search_term: Search term (name, email, or phone)
            limit: Maximum number of results to return
            
        Returns:
            List of person dictionaries from Planning Center API
        """
        import httpx
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            with httpx.Client(timeout=60.0) as client:  # Increased timeout for pagination
                filtered_people = []
                search_lower = search_term.lower().strip()
                
                # Clean search term for phone number matching (remove non-digits)
                phone_digits = re.sub(r'\D', '', search_term)
                
                # Planning Center API v2 supports 'where' parameter for filtering
                # We'll try multiple where clauses to search across name, email, and phone
                # Since Planning Center doesn't support OR conditions in where, we'll make
                # multiple requests and combine results, or paginate and filter client-side
                
                # Strategy: Use where parameter for name search (most common), then
                # paginate through additional results and filter client-side for email/phone
                per_page = 100  # Planning Center max per_page
                max_pages = 10  # Limit to 1000 people max to avoid timeout
                page = 1
                
                # First, try searching by name using where parameter
                # Split search term into potential first/last name parts
                name_parts = search_lower.split()
                first_name_search = name_parts[0] if name_parts else search_lower
                last_name_search = name_parts[-1] if len(name_parts) > 1 else None
                
                # Try searching by first name
                params = {
                    "per_page": per_page,
                    "where[first_name]": first_name_search,
                    "include": "emails,phone_numbers"
                }
                
                response = client.get(
                    f"{self.base_url}/people/v2/people",
                    headers=self.headers,
                    params=params,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    people = data.get("data", [])
                    included = data.get("included", [])
                    
                    # Process included emails and phone numbers
                    people_with_included = self._attach_included_data(people, included)
                    
                    # Filter and add matching people
                    for person in people_with_included:
                        if len(filtered_people) >= limit:
                            break
                        if self._person_matches_search(person, search_lower, phone_digits):
                            filtered_people.append(person)
                
                # If we haven't found enough results, try searching by last name
                if len(filtered_people) < limit and last_name_search:
                    params = {
                        "per_page": per_page,
                        "where[last_name]": last_name_search,
                        "include": "emails,phone_numbers"
                    }
                    
                    response = client.get(
                        f"{self.base_url}/people/v2/people",
                        headers=self.headers,
                        params=params,
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        people = data.get("data", [])
                        included = data.get("included", [])
                        
                        # Process included emails and phone numbers
                        people_with_included = self._attach_included_data(people, included)
                        
                        # Filter and add matching people (avoid duplicates)
                        existing_ids = {p.get("id") for p in filtered_people}
                        for person in people_with_included:
                            if len(filtered_people) >= limit:
                                break
                            if person.get("id") not in existing_ids:
                                if self._person_matches_search(person, search_lower, phone_digits):
                                    filtered_people.append(person)
                                    existing_ids.add(person.get("id"))
                
                # If still not enough results, paginate through all people and filter client-side
                # This ensures we search across ALL people, not just those matching the where clause
                if len(filtered_people) < limit:
                    page = 1
                    existing_ids = {p.get("id") for p in filtered_people}
                    
                    while len(filtered_people) < limit and page <= max_pages:
                        params = {
                            "per_page": per_page,
                            "page": page,
                            "include": "emails,phone_numbers"
                        }
                        
                        response = client.get(
                            f"{self.base_url}/people/v2/people",
                            headers=self.headers,
                            params=params,
                        )
                        
                        if response.status_code != 200:
                            break
                            
                        data = response.json()
                        people = data.get("data", [])
                        included = data.get("included", [])
                        
                        if not people:  # No more results
                            break
                        
                        # Process included emails and phone numbers
                        people_with_included = self._attach_included_data(people, included)
                        
                        # Filter people by search term
                        for person in people_with_included:
                            if len(filtered_people) >= limit:
                                break
                            if person.get("id") not in existing_ids:
                                if self._person_matches_search(person, search_lower, phone_digits):
                                    filtered_people.append(person)
                                    existing_ids.add(person.get("id"))
                        
                        # Check if there are more pages
                        meta = data.get("meta", {})
                        if page >= meta.get("total_pages", page):
                            break
                            
                        page += 1
                
                return filtered_people[:limit]

        except httpx.TimeoutException:
            logger.warning("Request timed out while searching people")
            raise PlanningCenterAPIError("Request timed out", status_code=504)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            elif e.response.status_code == 401:
                raise PlanningCenterAuthenticationError("Authentication failed", status_code=401)
            elif e.response.status_code == 429:
                raise PlanningCenterRateLimitError("Rate limit exceeded", status_code=429)
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                raise PlanningCenterAPIError(f"HTTP {e.response.status_code}", status_code=e.response.status_code)
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {e}")
            raise PlanningCenterAPIError("Cannot connect to Planning Center")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise PlanningCenterAPIError(f"Request failed: {str(e)}")
        except ValueError as e:  # JSON decode errors
            logger.error(f"Invalid JSON response: {e}")
            raise PlanningCenterAPIError("Invalid response format")
        except Exception as e:
            logger.error(f"Unexpected error searching people: {e}", exc_info=True)
            raise
    
    def _attach_included_data(self, people: List[Dict[str, Any]], included: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Attach included emails and phone numbers to person records.
        
        Args:
            people: List of person dictionaries from Planning Center API
            included: List of included resources (emails, phone_numbers) from API response
            
        Returns:
            List of person dictionaries with emails and phone_numbers attached
        """
        # Build maps of included resources by ID
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
        
        # Attach emails and phone numbers to people
        for person in people:
            relationships = person.get("relationships", {})
            
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
            
            # Attach to person attributes for easy access
            attrs = person.get("attributes", {})
            if emails:
                # Use primary email (first one) as the main email
                attrs["email"] = emails[0]
                attrs["emails"] = emails  # Store all emails
            if phone_numbers:
                # Use primary phone (first one) as the main phone
                attrs["phone_number"] = phone_numbers[0]
                attrs["phone_numbers"] = phone_numbers  # Store all phone numbers
        
        return people
    
    def _person_matches_search(self, person: Dict[str, Any], search_lower: str, phone_digits: str) -> bool:
        """
        Check if a person matches the search term in name, email, or phone.
        Now checks included emails and phone_numbers from relationships.
        
        Args:
            person: Person dictionary from Planning Center API (with included data attached)
            search_lower: Lowercase search term
            phone_digits: Search term with only digits (for phone matching)
            
        Returns:
            True if person matches search criteria
        """
        attrs = person.get("attributes", {})
        
        # Check name
        first_name = (attrs.get("first_name") or "").lower()
        last_name = (attrs.get("last_name") or "").lower()
        full_name = f"{first_name} {last_name}".strip()
        
        if search_lower in full_name or search_lower in first_name or search_lower in last_name:
            return True
        
        # Check email - check both the main email and all emails from included data
        email = (attrs.get("email") or "").lower()
        if search_lower in email:
            return True
        
        # Check all emails if available
        emails = attrs.get("emails", [])
        for email_addr in emails:
            if search_lower in str(email_addr).lower():
                return True
        
        # Check phone numbers - check both the main phone and all phones from included data
        phone_number = (attrs.get("phone_number") or "").lower()
        if phone_number:
            phone_number_digits = re.sub(r'\D', '', str(phone_number))
            if phone_digits and phone_digits in phone_number_digits:
                return True
            if search_lower in phone_number:
                return True
        
        # Check all phone numbers if available
        phone_numbers = attrs.get("phone_numbers", [])
        for phone in phone_numbers:
            if not phone:
                continue
            phone_digits_only = re.sub(r'\D', '', str(phone))
            if phone_digits and phone_digits in phone_digits_only:
                return True
            if search_lower in str(phone).lower():
                return True
        
        # Also check legacy phone fields in attributes (for backward compatibility)
        legacy_phone_fields = [
            attrs.get("mobile_carrier", ""),
            attrs.get("home_phone", ""),
            attrs.get("work_phone", ""),
        ]
        
        for phone_field in legacy_phone_fields:
            if not phone_field:
                continue
            phone_field_digits = re.sub(r'\D', '', str(phone_field))
            if phone_digits and phone_digits in phone_field_digits:
                return True
            if search_lower in str(phone_field).lower():
                return True
        
        return False
    
    def get_list(self, list_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single list from Planning Center by ID (synchronous)
        
        Args:
            list_id: Planning Center list ID
            
        Returns:
            List dictionary from Planning Center API or None if not found
        """
        import httpx
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.base_url}/people/v2/lists/{list_id}",
                    headers=self.headers,
                )
                
                if response.status_code == 404:
                    return None
                    
                response.raise_for_status()
                data = response.json()

                return data.get("data")
        except httpx.TimeoutException:
            logger.warning(f"Request timed out while fetching list {list_id}")
            raise PlanningCenterAPIError("Request timed out", status_code=504)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            elif e.response.status_code == 401:
                raise PlanningCenterAuthenticationError("Authentication failed", status_code=401)
            elif e.response.status_code == 429:
                raise PlanningCenterRateLimitError("Rate limit exceeded", status_code=429)
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                raise PlanningCenterAPIError(f"HTTP {e.response.status_code}", status_code=e.response.status_code)
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {e}")
            raise PlanningCenterAPIError("Cannot connect to Planning Center")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise PlanningCenterAPIError(f"Request failed: {str(e)}")
        except ValueError as e:  # JSON decode errors
            logger.error(f"Invalid JSON response: {e}")
            raise PlanningCenterAPIError("Invalid response format")
        except Exception as e:
            logger.error(f"Unexpected error fetching list: {e}", exc_info=True)
            raise

    def get_event_registrations(self, event_id: str) -> List[Dict[str, Any]]:
        """
        Get registrations for a specific Planning Center event (synchronous).
        Includes person data for each registration.
        
        Args:
            event_id: Planning Center event ID
        
        Returns:
            List of registration dictionaries from Planning Center API with person data attached
        """
        import httpx
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            with httpx.Client(timeout=60.0) as client:
                # First, fetch the event to see its structure and check for registration_url
                logger.info(f"Fetching event '{event_id}' from Calendar API to check structure")
                
                # Fetch the event from Calendar API with relationships and included data
                try:
                    response = client.get(
                        f"{self.base_url}/calendar/v2/events/{event_id}",
                        headers=self.headers,
                        params={
                            "include": "event_instances.signups.person"
                        }
                    )
                    if response.status_code == 200:
                        event_json = response.json()
                        event_data = event_json.get("data", {})
                        event_attrs = event_data.get("attributes", {})
                        logger.info(f"Event '{event_id}' found in Calendar API: {event_attrs.get('name', 'Unknown')}")
                        registration_url = event_attrs.get('registration_url', '')
                        logger.info(f"Event has registration_url: {registration_url}")
                        
                        # Extract registration event ID from registration_url if present
                        registration_event_id = None
                        if registration_url:
                            # Extract ID from URL like: .../registrations/events/3070694
                            import re
                            match = re.search(r'/registrations/events/(\d+)', registration_url)
                            if match:
                                registration_event_id = match.group(1)
                                logger.info(f"Extracted registration event ID '{registration_event_id}' from registration_url")
                        
                        # Check included data for signups
                        all_included = event_json.get("included", [])
                        logger.info(f"Found {len(all_included)} included items in event response")
                        
                        # Log what types of items are in included data
                        included_types = {}
                        for item in all_included:
                            item_type = item.get("type", "Unknown")
                            included_types[item_type] = included_types.get(item_type, 0) + 1
                        logger.info(f"Included data types: {included_types}")
                        
                        # Find all signups from included data
                        signups_by_instance = {}
                        instances_by_id = {}
                        
                        # First, identify event instances
                        for item in all_included:
                            if item.get("type") == "EventInstance":
                                instances_by_id[item.get("id")] = item
                        
                        logger.info(f"Found {len(instances_by_id)} event instances in included data")
                        
                        # If no instances in included data, try fetching them explicitly
                        if not instances_by_id:
                            logger.info(f"No event instances in included data, fetching event instances separately")
                            try:
                                instances_response = client.get(
                                    f"{self.base_url}/calendar/v2/events/{event_id}/event_instances",
                                    headers=self.headers,
                                    params={"per_page": 100, "include": "signups.person"}
                                )
                                if instances_response.status_code == 200:
                                    instances_data = instances_response.json()
                                    instance_list = instances_data.get("data", [])
                                    instances_included = instances_data.get("included", [])
                                    logger.info(f"Found {len(instance_list)} event instances via separate API call")
                                    
                                    # Log first event instance structure to understand what data is available
                                    if instance_list:
                                        first_instance = instance_list[0]
                                        instance_attrs = first_instance.get("attributes", {})
                                        instance_relationships = first_instance.get("relationships", {})
                                        logger.info(f"Sample event instance ID: {first_instance.get('id')}")
                                        logger.info(f"Sample event instance attributes: {list(instance_attrs.keys())}")
                                        logger.info(f"Sample event instance relationships: {list(instance_relationships.keys())}")
                                        # Check for signup/registration-related attributes
                                        if "signup_count" in instance_attrs:
                                            logger.info(f"Event instance has signup_count: {instance_attrs.get('signup_count')}")
                                        if "registration_count" in instance_attrs:
                                            logger.info(f"Event instance has registration_count: {instance_attrs.get('registration_count')}")
                                    
                                    # Add instances to our map
                                    for instance in instance_list:
                                        instances_by_id[instance.get("id")] = instance
                                    
                                    # Add included data (signups and people) to all_included
                                    all_included.extend(instances_included)
                                    logger.info(f"Added {len(instances_included)} items to included data from event instances")
                                    
                                    # Log what types of items were included
                                    if instances_included:
                                        included_types = {}
                                        for item in instances_included:
                                            item_type = item.get("type", "Unknown")
                                            included_types[item_type] = included_types.get(item_type, 0) + 1
                                        logger.info(f"Included data types from event instances: {included_types}")
                                else:
                                    logger.info(f"Event instances API returned {instances_response.status_code}")
                            except Exception as e:
                                logger.warning(f"Error fetching event instances: {str(e)}")
                        
                        # Then, find signups and link them to instances
                        signups = []
                        for item in all_included:
                            if item.get("type") == "Signup":
                                signups.append(item)
                                # Find which instance this signup belongs to
                                signup_relationships = item.get("relationships", {})
                                instance_rel = signup_relationships.get("event_instance", {}).get("data", {})
                                instance_id = instance_rel.get("id")
                                if instance_id:
                                    if instance_id not in signups_by_instance:
                                        signups_by_instance[instance_id] = []
                                    signups_by_instance[instance_id].append(item)
                        
                        logger.info(f"Found {len(signups)} signups in included data for event '{event_id}'")
                        
                        # If we have a registration_event_id from registration_url, try using it as a signup ID FIRST
                        # The registration_url ID is likely the specific signup we want, not a general event ID
                        if registration_event_id and registration_event_id != event_id and not signups:
                            logger.info(f"Trying registration_event_id '{registration_event_id}' as a direct signup ID FIRST (from registration_url)")
                            try:
                                # Try the registration_event_id as a direct signup ID
                                signup_response = client.get(
                                    f"{self.base_url}/registrations/v2/signups/{registration_event_id}",
                                    headers=self.headers,
                                    timeout=10.0
                                )
                                if signup_response.status_code == 200:
                                    logger.info(f"Found signup with ID '{registration_event_id}', now fetching its registrations")
                                    try:
                                        # Fetch all registrations with pagination
                                        all_reg_list = []
                                        all_people_by_id = {}
                                        all_included = []  # Store all included data (people, registrants, etc.)
                                        per_page = 100
                                        offset = 0
                                        
                                        while True:
                                            reg_response = client.get(
                                                f"{self.base_url}/registrations/v2/signups/{registration_event_id}/registrations",
                                                headers=self.headers,
                                                params={
                                                    "per_page": per_page,
                                                    "offset": offset,
                                                    "include": "registrant_contact,registrants.person",
                                                    "include_archived": "true"
                                                },
                                                timeout=10.0
                                            )
                                            if reg_response.status_code == 200:
                                                reg_data = reg_response.json()
                                                page_reg_list = reg_data.get("data", [])
                                                page_included = reg_data.get("included", [])
                                                
                                                # Check pagination metadata
                                                meta = reg_data.get("meta", {})
                                                links = reg_data.get("links", {})
                                                total_count = meta.get("total_count", len(page_reg_list))
                                                
                                                logger.info(f"Page {offset // per_page + 1}: Found {len(page_reg_list)} registrations (total_count from meta: {total_count})")
                                                logger.info(f"Pagination metadata: meta={meta}, links={links}")
                                                
                                                # Log included data types
                                                included_types = {}
                                                for item in page_included:
                                                    item_type = item.get("type")
                                                    included_types[item_type] = included_types.get(item_type, 0) + 1
                                                logger.info(f"Included data types in page {offset // per_page + 1}: {included_types}")
                                                
                                                # Add to our lists
                                                all_reg_list.extend(page_reg_list)
                                                
                                                # Build people map and collect all included data (across all pages)
                                                for item in page_included:
                                                    item_type = item.get("type")
                                                    item_id = item.get("id")
                                                    
                                                    # Store all included items
                                                    all_included.append(item)
                                                    
                                                    # Build people map
                                                    if item_type == "Person":
                                                        all_people_by_id[item_id] = item
                                                    
                                                    # Also check for Registrant objects that might contain person references
                                                    if item_type == "Registrant":
                                                        logger.info(f"Found Registrant object in included data: {item_id}, relationships: {list(item.get('relationships', {}).keys())}")
                                                        # Store registrants for later lookup
                                                        if "registrants_by_id" not in locals():
                                                            registrants_by_id = {}
                                                        registrants_by_id[item_id] = item
                                                
                                                # Log what types of included data we're getting
                                                included_types_summary = {}
                                                for item in page_included:
                                                    item_type = item.get("type")
                                                    included_types_summary[item_type] = included_types_summary.get(item_type, 0) + 1
                                                logger.info(f"Included data summary for page {offset // per_page + 1}: {included_types_summary}")
                                                
                                                # Check if there are more pages
                                                if links.get("next"):
                                                    offset += per_page
                                                    logger.info(f"More pages available, fetching next page (offset: {offset})")
                                                elif len(page_reg_list) < per_page:
                                                    # No more pages if we got fewer than per_page results
                                                    break
                                                elif len(all_reg_list) >= total_count if total_count else False:
                                                    # We've got all registrations
                                                    break
                                                else:
                                                    # Try next page
                                                    offset += per_page
                                                    if offset > 1000:  # Safety limit
                                                        logger.warning(f"Reached safety limit of 1000 registrations, stopping pagination")
                                                        break
                                            else:
                                                break
                                        
                                                logger.info(f"Found {len(all_reg_list)} total registrations for signup ID {registration_event_id} (from registration_url, across all pages)")
                                                
                                                # Log all registration IDs to compare with user's expected list
                                                registration_ids = [reg.get("id") for reg in all_reg_list]
                                                logger.info(f"All registration IDs returned by API: {sorted(registration_ids)}")
                                        
                                        if all_reg_list:
                                            # Process all registrations
                                            all_registrations = []
                                            
                                            for reg in all_reg_list:
                                                reg_id = reg.get("id")
                                                reg_attrs = reg.get("attributes", {})
                                                reg_relationships = reg.get("relationships", {})
                                                
                                                logger.info(f"Processing registration {reg_id}, relationships keys: {list(reg_relationships.keys())}")
                                                
                                                # Check if registration has any additional person-related data in attributes
                                                selection = reg_attrs.get("selection", "") or reg_attrs.get("name", "")
                                                logger.info(f"Registration {reg_id}: selection='{selection}', created_at='{reg_attrs.get('created_at')}', status='{reg_attrs.get('status')}'")
                                                
                                                # Log full registration structure for first few to understand the data model
                                                if len(all_registrations) < 2:
                                                    import json
                                                    logger.info(f"Full registration {reg_id} structure (first 2000 chars): {json.dumps(reg, indent=2, default=str)[:2000]}")
                                                
                                                # Try to fetch registrants separately for this registration
                                                # Planning Center: a registration can have multiple registrants (e.g., wife + husband)
                                                registrants_list = []
                                                
                                                # Try endpoint under signup path
                                                try:
                                                    registrants_response = client.get(
                                                        f"{self.base_url}/registrations/v2/signups/{registration_event_id}/registrations/{reg_id}/registrants",
                                                        headers=self.headers,
                                                        params={
                                                            "include": "person",
                                                            "include_archived": "true"
                                                        },
                                                        timeout=10.0
                                                    )
                                                    if registrants_response.status_code == 200:
                                                        registrants_data = registrants_response.json()
                                                        registrants_list = registrants_data.get("data", [])
                                                        registrants_included = registrants_data.get("included", [])
                                                        
                                                        # Add registrant people to our people map
                                                        for item in registrants_included:
                                                            if item.get("type") == "Person":
                                                                all_people_by_id[item.get("id")] = item
                                                        
                                                        logger.info(f"Registration {reg_id}: fetched {len(registrants_list)} registrants via signup-based endpoint")
                                                except Exception as e:
                                                    logger.debug(f"Signup-based registrants endpoint failed for {reg_id}: {str(e)}")
                                                
                                                # If that didn't work, try the direct registration endpoint (even though it returned 404 before)
                                                if not registrants_list:
                                                    try:
                                                        registrants_response = client.get(
                                                            f"{self.base_url}/registrations/v2/registrations/{reg_id}/registrants",
                                                            headers=self.headers,
                                                            params={
                                                                "include": "person",
                                                                "include_archived": "true"
                                                            },
                                                            timeout=10.0
                                                        )
                                                        if registrants_response.status_code == 200:
                                                            registrants_data = registrants_response.json()
                                                            registrants_list = registrants_data.get("data", [])
                                                            registrants_included = registrants_data.get("included", [])
                                                            
                                                            # Add registrant people to our people map
                                                            for item in registrants_included:
                                                                if item.get("type") == "Person":
                                                                    all_people_by_id[item.get("id")] = item
                                                            
                                                            logger.info(f"Registration {reg_id}: fetched {len(registrants_list)} registrants via direct endpoint")
                                                    except Exception as e:
                                                        logger.debug(f"Direct registrants endpoint failed for {reg_id}: {str(e)}")
                                                
                                                # If we still don't have registrants, fall back to registrant_contact (at least 1 person)
                                                if not registrants_list:
                                                    contact_data = reg_relationships.get("registrant_contact", {}).get("data", {})
                                                    if contact_data:
                                                        registrants_list = [{"type": "Person", "id": contact_data.get("id")}]
                                                        logger.info(f"Registration {reg_id}: falling back to registrant_contact (only 1 person)")
                                                
                                                # Process each registrant as a separate enrollment
                                                for registrant_ref in registrants_list:
                                                    registrant_id = registrant_ref.get("id")
                                                    
                                                    # Find the registrant person in included data
                                                    person = None
                                                    
                                                    # Check if registrant_ref is a Person object
                                                    if registrant_ref.get("type") == "Person":
                                                        if registrant_id in all_people_by_id:
                                                            person = all_people_by_id[registrant_id]
                                                    else:
                                                        # It's a Registrant object, get the person from its relationship
                                                        registrant_relationships = registrant_ref.get("relationships", {})
                                                        person_ref = registrant_relationships.get("person", {}).get("data", {})
                                                        person_id = person_ref.get("id") if person_ref else registrant_id
                                                        
                                                        if person_id and person_id in all_people_by_id:
                                                            person = all_people_by_id[person_id]
                                                        else:
                                                            # Try direct lookup by ID (might be a person ID)
                                                            if registrant_id in all_people_by_id:
                                                                person = all_people_by_id[registrant_id]
                                                    
                                                    # Create a registration record for this registrant
                                                    registration = {
                                                        "type": "Registration",
                                                        "id": f"{reg.get('id')}-{registrant_id}",  # Unique ID for each registrant
                                                        "attributes": {
                                                            "status": "registered",
                                                            "created_at": reg_attrs.get("created_at"),
                                                            "notes": ""
                                                        },
                                                        "relationships": {
                                                            "registration": {"data": {"id": reg.get("id"), "type": "Registration"}}
                                                        }
                                                    }
                                                    
                                                    if person:
                                                        person_attrs = person.get("attributes", {})
                                                        registration_attrs = registration.get("attributes", {})
                                                        
                                                        first_name = person_attrs.get("first_name", "")
                                                        last_name = person_attrs.get("last_name", "")
                                                        if first_name or last_name:
                                                            registration_attrs["person_name"] = f"{first_name} {last_name}".strip()
                                                            registration_attrs["first_name"] = first_name
                                                            registration_attrs["last_name"] = last_name
                                                        
                                                        email = person_attrs.get("email") or (person_attrs.get("emails", [{}])[0].get("address") if person_attrs.get("emails") else None)
                                                        if email:
                                                            registration_attrs["email"] = email
                                                        
                                                        # Store person ID in relationships for enrollment service
                                                        registration["relationships"]["person"] = {"data": {"id": person.get("id"), "type": "Person"}}
                                                    
                                                    all_registrations.append(registration)
                                            
                                            logger.info(f"Returning {len(all_registrations)} registrations from signup ID {registration_event_id}")
                                            return all_registrations
                                        elif reg_response.status_code == 404:
                                            logger.info(f"No registrations found for signup ID {registration_event_id} (404)")
                                        else:
                                            logger.warning(f"Unexpected status {reg_response.status_code} when fetching registrations for signup ID {registration_event_id}")
                                    except Exception as e:
                                        logger.warning(f"Error fetching registrations for signup ID {registration_event_id}: {str(e)}")
                                elif signup_response.status_code == 404:
                                    logger.info(f"Registration event ID '{registration_event_id}' is not a valid signup ID (404)")
                                else:
                                    logger.warning(f"Unexpected status {signup_response.status_code} when checking signup ID {registration_event_id}")
                            except httpx.TimeoutException:
                                logger.warning(f"Timeout trying registration_event_id as signup ID")
                            except Exception as e:
                                logger.warning(f"Error trying registration_event_id as signup ID: {str(e)}")
                        else:
                            logger.info(f"No registration_event_id available to try as signup ID")
                        
                        if signups:
                            # Convert signups to registration-like format
                            all_registrations = []
                            
                            # Build map of person data
                            people_by_id = {}
                            for item in all_included:
                                if item.get("type") == "Person":
                                    people_by_id[item.get("id")] = item
                            
                            for signup in signups:
                                signup_attrs = signup.get("attributes", {})
                                signup_relationships = signup.get("relationships", {})
                                
                                # Map signup to registration format
                                registration = {
                                    "type": "Registration",
                                    "id": signup.get("id"),
                                    "attributes": {
                                        "status": signup_attrs.get("status", "registered"),
                                        "created_at": signup_attrs.get("created_at"),
                                        "notes": signup_attrs.get("notes", "")
                                    },
                                    "relationships": signup_relationships
                                }
                                
                                # Attach person data if available
                                person_data = signup_relationships.get("person", {}).get("data", {})
                                person_id = person_data.get("id") if person_data else None
                                
                                if person_id and person_id in people_by_id:
                                    person = people_by_id[person_id]
                                    person_attrs = person.get("attributes", {})
                                    registration_attrs = registration.get("attributes", {})
                                    
                                    first_name = person_attrs.get("first_name", "")
                                    last_name = person_attrs.get("last_name", "")
                                    if first_name or last_name:
                                        registration_attrs["person_name"] = f"{first_name} {last_name}".strip()
                                        registration_attrs["first_name"] = first_name
                                        registration_attrs["last_name"] = last_name
                                    
                                    email = person_attrs.get("email") or (person_attrs.get("emails", [{}])[0].get("address") if person_attrs.get("emails") else None)
                                    if email:
                                        registration_attrs["email"] = email
                                
                                all_registrations.append(registration)
                            
                            logger.info(f"Returning {len(all_registrations)} signups/registrations for Calendar event '{event_id}'")
                            return all_registrations
                        else:
                            logger.info(f"No signups found in included data, will try fetching from event instances")
                            
                            # If we found a registration event ID from registration_url, try using that
                            if registration_event_id and registration_event_id != event_id:
                                logger.info(f"Trying Registrations API with event ID from registration_url: {registration_event_id}")
                                
                                # Try as path parameter first
                                try:
                                    reg_response = client.get(
                                        f"{self.base_url}/registrations/v2/events/{registration_event_id}/registrations",
                                        headers=self.headers,
                                        params={
                                            "per_page": 100,
                                            "offset": 0,
                                            "include": "person"
                                        }
                                    )
                                    if reg_response.status_code == 200:
                                        logger.info(f"Successfully fetched registrations using path parameter for event ID {registration_event_id}")
                                except Exception as e:
                                    logger.warning(f"Error trying Registrations API with path parameter: {str(e)}")
                                    reg_response = None
                                
                                # If that didn't work, try querying by event_id filter
                                if not reg_response or reg_response.status_code != 200:
                                    logger.info(f"Trying Registrations API query with event_id filter: {registration_event_id}")
                                    try:
                                        reg_response = client.get(
                                            f"{self.base_url}/registrations/v2/registrations",
                                            headers=self.headers,
                                            params={
                                                "per_page": 100,
                                                "offset": 0,
                                                "include": "person,event",
                                                "where[event_id]": registration_event_id,
                                                "include_archived": "true"
                                            }
                                        )
                                        if reg_response.status_code == 200:
                                            logger.info(f"Successfully fetched registrations using query filter for event ID {registration_event_id}")
                                    except Exception as e:
                                        logger.warning(f"Error trying Registrations API with query filter: {str(e)}")
                                        reg_response = None
                                
                                # Try Events API with the registration event ID
                                if not reg_response or reg_response.status_code != 200:
                                    logger.info(f"Trying Events API with registration event ID: {registration_event_id}")
                                    try:
                                        reg_response = client.get(
                                            f"{self.base_url}/events/v2/events/{registration_event_id}/registrations",
                                            headers=self.headers,
                                            params={
                                                "per_page": 100,
                                                "offset": 0,
                                                "include": "person",
                                                "include_archived": "true"
                                            }
                                        )
                                        if reg_response.status_code == 200:
                                            logger.info(f"Successfully fetched registrations from Events API for event ID {registration_event_id}")
                                    except Exception as e:
                                        logger.warning(f"Error trying Events API: {str(e)}")
                                        reg_response = None
                                
                                if reg_response and reg_response.status_code == 200:
                                    reg_data = reg_response.json()
                                    reg_list = reg_data.get("data", [])
                                    reg_included = reg_data.get("included", [])
                                    logger.info(f"Found {len(reg_list)} registrations using registration event ID {registration_event_id}")
                                    
                                    if reg_list:
                                        # Process registrations
                                        all_registrations = []
                                        people_by_id = {}
                                        
                                        for item in reg_included:
                                            if item.get("type") == "Person":
                                                people_by_id[item.get("id")] = item
                                        
                                        for reg in reg_list:
                                            reg_attrs = reg.get("attributes", {})
                                            reg_relationships = reg.get("relationships", {})
                                            
                                            registration = {
                                                "type": "Registration",
                                                "id": reg.get("id"),
                                                "attributes": {
                                                    "status": reg_attrs.get("status", "registered"),
                                                    "created_at": reg_attrs.get("created_at"),
                                                    "notes": reg_attrs.get("notes", "")
                                                },
                                                "relationships": reg_relationships
                                            }
                                            
                                            person_data = reg_relationships.get("person", {}).get("data", {})
                                            person_id = person_data.get("id") if person_data else None
                                            
                                            if person_id and person_id in people_by_id:
                                                person = people_by_id[person_id]
                                                person_attrs = person.get("attributes", {})
                                                registration_attrs = registration.get("attributes", {})
                                                
                                                first_name = person_attrs.get("first_name", "")
                                                last_name = person_attrs.get("last_name", "")
                                                if first_name or last_name:
                                                    registration_attrs["person_name"] = f"{first_name} {last_name}".strip()
                                                    registration_attrs["first_name"] = first_name
                                                    registration_attrs["last_name"] = last_name
                                                
                                                email = person_attrs.get("email") or (person_attrs.get("emails", [{}])[0].get("address") if person_attrs.get("emails") else None)
                                                if email:
                                                    registration_attrs["email"] = email
                                            
                                            all_registrations.append(registration)
                                        
                                        logger.info(f"Returning {len(all_registrations)} registrations from Registrations API")
                                        return all_registrations
                                else:
                                    if reg_response:
                                        logger.info(f"Registrations API returned {reg_response.status_code} for event ID {registration_event_id}")
                            
                            # If no signups in included data, try fetching from event instances directly
                            # Limit to first 3 instances to prevent hanging, break early if we find signups
                            instances_checked = 0
                            max_instances_to_check = 3
                            for instance_id, instance in list(instances_by_id.items())[:max_instances_to_check]:
                                instances_checked += 1
                                logger.info(f"Fetching signups from event instance {instance_id} ({instances_checked}/{min(len(instances_by_id), max_instances_to_check)})")
                                try:
                                    signup_response = client.get(
                                        f"{self.base_url}/calendar/v2/event_instances/{instance_id}/signups",
                                        headers=self.headers,
                                        params={
                                            "per_page": 100,
                                            "offset": 0,
                                            "include": "person"
                                        },
                                        timeout=10.0  # Add timeout to prevent hanging
                                    )
                                    if signup_response.status_code == 200:
                                        signups_data = signup_response.json()
                                        page_signups = signups_data.get("data", [])
                                        page_included = signups_data.get("included", [])
                                        
                                        if page_signups:
                                            # Process and return signups
                                            all_registrations = []
                                            people_by_id = {}
                                            
                                            for item in page_included:
                                                if item.get("type") == "Person":
                                                    people_by_id[item.get("id")] = item
                                            
                                            for signup in page_signups:
                                                signup_attrs = signup.get("attributes", {})
                                                signup_relationships = signup.get("relationships", {})
                                                
                                                registration = {
                                                    "type": "Registration",
                                                    "id": signup.get("id"),
                                                    "attributes": {
                                                        "status": signup_attrs.get("status", "registered"),
                                                        "created_at": signup_attrs.get("created_at"),
                                                        "notes": signup_attrs.get("notes", "")
                                                    },
                                                    "relationships": signup_relationships
                                                }
                                                
                                                person_data = signup_relationships.get("person", {}).get("data", {})
                                                person_id = person_data.get("id") if person_data else None
                                                
                                                if person_id and person_id in people_by_id:
                                                    person = people_by_id[person_id]
                                                    person_attrs = person.get("attributes", {})
                                                    registration_attrs = registration.get("attributes", {})
                                                    
                                                    first_name = person_attrs.get("first_name", "")
                                                    last_name = person_attrs.get("last_name", "")
                                                    if first_name or last_name:
                                                        registration_attrs["person_name"] = f"{first_name} {last_name}".strip()
                                                        registration_attrs["first_name"] = first_name
                                                        registration_attrs["last_name"] = last_name
                                                    
                                                    email = person_attrs.get("email") or (person_attrs.get("emails", [{}])[0].get("address") if person_attrs.get("emails") else None)
                                                    if email:
                                                        registration_attrs["email"] = email
                                                
                                                all_registrations.append(registration)
                                            
                                            logger.info(f"Returning {len(all_registrations)} signups from event instance {instance_id}")
                                            return all_registrations
                                    elif signup_response.status_code == 404:
                                        logger.info(f"No signups found for event instance {instance_id} (404)")
                                    else:
                                        logger.warning(f"Unexpected status {signup_response.status_code} when fetching signups for instance {instance_id}")
                                except httpx.TimeoutException:
                                    logger.warning(f"Timeout fetching signups from event instance {instance_id}")
                                except Exception as e:
                                    logger.warning(f"Error fetching signups from event instance {instance_id}: {str(e)}")
                            
                            logger.info(f"Checked {instances_checked} event instances, no signups found")
                            
                            # Skip querying all signups - we already tried the registration_event_id as a direct signup ID above
                            # Don't query all signups as it returns too many (927 from 100 signups)
                            # The registration_event_id from registration_url is the specific signup we want
                            logger.info(f"Skipping query for all signups (would return too many). The registration_event_id approach should have already been tried.")
                    elif response.status_code == 404:
                        logger.info(f"Event '{event_id}' not found in Calendar API")
                    else:
                        logger.warning(f"Error fetching event '{event_id}' from Calendar API: {response.status_code}")
                except Exception as e:
                    logger.warning(f"Error checking Calendar event '{event_id}': {str(e)}")
                
                # Continue with original registration fetch logic
                all_registrations = []
                all_included = []
                per_page = 100
                offset = 0
                
                # Try Check-Ins API first (registrations are typically from Check-Ins events)
                try:
                    while True:
                        response = client.get(
                            f"{self.base_url}/check-ins/v2/events/{event_id}/event_times",
                            headers=self.headers,
                            params={
                                "per_page": per_page,
                                "offset": offset,
                                "include": "event_time_registrations.person",
                                "include_archived": "true"
                            },
                        )
                        if response.status_code == 404 or response.status_code == 401:
                            # Check-Ins API not available, fall back to Events API
                            break
                        response.raise_for_status()
                        data = response.json()
                        
                        event_times = data.get("data", [])
                        page_included = data.get("included", [])
                        
                        if not event_times:
                            break
                        
                        # Extract registrations from event times
                        registrations_by_id = {}
                        for item in page_included:
                            if item.get("type") == "EventTimeRegistration":
                                registrations_by_id[item.get("id")] = item
                        
                        for event_time in event_times:
                            relationships = event_time.get("relationships", {})
                            registrations_rel = relationships.get("event_time_registrations", {})
                            registrations_data = registrations_rel.get("data", [])
                            
                            for reg_ref in registrations_data:
                                reg_id = reg_ref.get("id")
                                if reg_id in registrations_by_id:
                                    all_registrations.append(registrations_by_id[reg_id])
                        
                        all_included.extend(page_included)
                        
                        if len(event_times) < per_page:
                            break
                        
                        offset += per_page
                    
                    # If we got registrations from Check-Ins, process and return them
                    if all_registrations:
                        # Build map of person data by ID
                        people_by_id = {}
                        for item in all_included:
                            if item.get("type") == "Person":
                                people_by_id[item.get("id")] = item
                        
                        # Attach person data to registrations
                        for registration in all_registrations:
                            relationships = registration.get("relationships", {})
                            person_data = relationships.get("person", {}).get("data")
                            
                            if person_data and person_data.get("id") in people_by_id:
                                person = people_by_id[person_data.get("id")]
                                person_attrs = person.get("attributes", {})
                                registration_attrs = registration.get("attributes", {})
                                
                                first_name = person_attrs.get("first_name", "")
                                last_name = person_attrs.get("last_name", "")
                                if first_name or last_name:
                                    registration_attrs["person_name"] = f"{first_name} {last_name}".strip()
                                    registration_attrs["first_name"] = first_name
                                    registration_attrs["last_name"] = last_name
                                
                                email = person_attrs.get("email") or (person_attrs.get("emails", [{}])[0].get("address") if person_attrs.get("emails") else None)
                                if email:
                                    registration_attrs["email"] = email
                        
                        return all_registrations
                    
                    # Reset for Events API fallback
                    all_registrations = []
                    all_included = []
                    offset = 0
                except httpx.HTTPStatusError as checkins_error:
                    # Check-Ins API failed, will try Events API below
                    if checkins_error.response.status_code not in [404, 401]:
                        raise
                
                # Try Events API
                try:
                    while True:
                        response = client.get(
                            f"{self.base_url}/events/v2/events/{event_id}/registrations",
                            headers=self.headers,
                            params={
                                "per_page": per_page,
                                "offset": offset,
                                "include": "person",
                                "include_archived": "true"
                            },
                        )
                        # Handle 404 immediately - event not found or has no registrations
                        if response.status_code == 404:
                            logger.info(f"Planning Center event '{event_id}' not found in Events API (404)")
                            break
                        # Handle 401 - no access to this API
                        if response.status_code == 401:
                            logger.info(f"Planning Center Events API returned 401 for event '{event_id}'")
                            break
                        response.raise_for_status()
                        data = response.json()
                        
                        page_registrations = data.get("data", [])
                        page_included = data.get("included", [])
                        
                        if not page_registrations:
                            break
                        
                        all_registrations.extend(page_registrations)
                        all_included.extend(page_included)
                        
                        # Check if there are more pages
                        if len(page_registrations) < per_page:
                            break
                        
                        offset += per_page
                    
                    # If we got registrations from Events API, process and return them
                    if all_registrations:
                        # Build map of person data by ID
                        people_by_id = {}
                        for item in all_included:
                            if item.get("type") == "Person":
                                people_by_id[item.get("id")] = item
                        
                        # Attach person data to registrations
                        for registration in all_registrations:
                            relationships = registration.get("relationships", {})
                            person_data = relationships.get("person", {}).get("data")
                            
                            if person_data and person_data.get("id") in people_by_id:
                                # Attach person attributes to registration for easier access
                                person = people_by_id[person_data.get("id")]
                                person_attrs = person.get("attributes", {})
                                registration_attrs = registration.get("attributes", {})
                                
                                # Add person name and email to registration attributes
                                first_name = person_attrs.get("first_name", "")
                                last_name = person_attrs.get("last_name", "")
                                if first_name or last_name:
                                    registration_attrs["person_name"] = f"{first_name} {last_name}".strip()
                                    registration_attrs["first_name"] = first_name
                                    registration_attrs["last_name"] = last_name
                                
                                email = person_attrs.get("email") or (person_attrs.get("emails", [{}])[0].get("address") if person_attrs.get("emails") else None)
                                if email:
                                    registration_attrs["email"] = email
                        
                        return all_registrations
                except httpx.HTTPStatusError as events_error:
                    # Events API failed, will try Registrations API below
                    if events_error.response.status_code not in [404, 401]:
                        raise
                
                # Reset for Registrations API fallback (new public API)
                all_registrations = []
                all_included = []
                offset = 0
                
                # Try new Registrations API (public API as of June 2025)
                logger.info(f"Trying Registrations API for event '{event_id}'")
                try:
                    while True:
                        response = client.get(
                            f"{self.base_url}/registrations/v2/events/{event_id}/registrations",
                            headers=self.headers,
                            params={
                                "per_page": per_page,
                                "offset": offset,
                                "include": "person",
                                "include_archived": "true"
                            },
                        )
                        # Handle 404 immediately - event not found or has no registrations
                        if response.status_code == 404:
                            logger.info(f"Planning Center event '{event_id}' not found in Registrations API (404)")
                            break
                        # Handle 401 - no access to this API
                        if response.status_code == 401:
                            logger.info(f"Planning Center Registrations API returned 401 for event '{event_id}'")
                            break
                        response.raise_for_status()
                        data = response.json()
                        
                        page_registrations = data.get("data", [])
                        page_included = data.get("included", [])
                        
                        if not page_registrations:
                            break
                        
                        all_registrations.extend(page_registrations)
                        all_included.extend(page_included)
                        
                        # Check if there are more pages
                        if len(page_registrations) < per_page:
                            break
                        
                        offset += per_page
                    
                    # If we got registrations from Registrations API, process and return them
                    if all_registrations:
                        # Build map of person data by ID
                        people_by_id = {}
                        for item in all_included:
                            if item.get("type") == "Person":
                                people_by_id[item.get("id")] = item
                        
                        # Attach person data to registrations
                        for registration in all_registrations:
                            relationships = registration.get("relationships", {})
                            person_data = relationships.get("person", {}).get("data")
                            
                            if person_data and person_data.get("id") in people_by_id:
                                # Attach person attributes to registration for easier access
                                person = people_by_id[person_data.get("id")]
                                person_attrs = person.get("attributes", {})
                                registration_attrs = registration.get("attributes", {})
                                
                                # Add person name and email to registration attributes
                                first_name = person_attrs.get("first_name", "")
                                last_name = person_attrs.get("last_name", "")
                                if first_name or last_name:
                                    registration_attrs["person_name"] = f"{first_name} {last_name}".strip()
                                    registration_attrs["first_name"] = first_name
                                    registration_attrs["last_name"] = last_name
                                
                                email = person_attrs.get("email") or (person_attrs.get("emails", [{}])[0].get("address") if person_attrs.get("emails") else None)
                                if email:
                                    registration_attrs["email"] = email
                        
                        return all_registrations
                except httpx.HTTPStatusError as reg_error:
                    # Registrations API failed
                    if reg_error.response.status_code not in [404, 401]:
                        raise
                
                # Try Calendar API registrations endpoint as last resort
                logger.info(f"Trying Calendar API registrations for event '{event_id}'")
                all_registrations = []
                all_included = []
                offset = 0
                
                try:
                    while True:
                        response = client.get(
                            f"{self.base_url}/calendar/v2/events/{event_id}/registrations",
                            headers=self.headers,
                            params={
                                "per_page": per_page,
                                "offset": offset,
                                "include": "person",
                                "include_archived": "true"
                            },
                        )
                        # Handle 404 - break and continue to direct query method
                        if response.status_code == 404:
                            logger.info(f"Planning Center event '{event_id}' not found in Calendar API or has no registrations (404)")
                            break
                        # Handle 401 - break and continue to direct query method
                        if response.status_code == 401:
                            logger.info(f"Planning Center Calendar API returned 401 for event '{event_id}'")
                            break
                        response.raise_for_status()
                        data = response.json()
                        
                        page_registrations = data.get("data", [])
                        page_included = data.get("included", [])
                        
                        if not page_registrations:
                            break
                        
                        all_registrations.extend(page_registrations)
                        all_included.extend(page_included)
                        
                        # Check if there are more pages
                        if len(page_registrations) < per_page:
                            break
                        
                        offset += per_page
                    
                    # Build map of person data by ID
                    people_by_id = {}
                    for item in all_included:
                        if item.get("type") == "Person":
                            people_by_id[item.get("id")] = item
                    
                    # Attach person data to registrations
                    for registration in all_registrations:
                        relationships = registration.get("relationships", {})
                        person_data = relationships.get("person", {}).get("data")
                        
                        if person_data and person_data.get("id") in people_by_id:
                            # Attach person attributes to registration for easier access
                            person = people_by_id[person_data.get("id")]
                            person_attrs = person.get("attributes", {})
                            registration_attrs = registration.get("attributes", {})
                            
                            # Add person name and email to registration attributes
                            first_name = person_attrs.get("first_name", "")
                            last_name = person_attrs.get("last_name", "")
                            if first_name or last_name:
                                registration_attrs["person_name"] = f"{first_name} {last_name}".strip()
                                registration_attrs["first_name"] = first_name
                                registration_attrs["last_name"] = last_name
                            
                            email = person_attrs.get("email") or (person_attrs.get("emails", [{}])[0].get("address") if person_attrs.get("emails") else None)
                            if email:
                                registration_attrs["email"] = email
                    
                    # Only return if we actually got registrations
                    if all_registrations:
                        return all_registrations
                    # Otherwise continue to direct query method below
                except httpx.HTTPStatusError as cal_error:
                    # Calendar API failed - continue to direct query method
                    if cal_error.response.status_code in [404, 401]:
                        logger.info(f"Planning Center Calendar API returned {cal_error.response.status_code} for event '{event_id}'")
                        # Don't return here - continue to direct query method below
                    else:
                        raise
                
                # Try querying registrations directly by filtering by event_id (including archived)
                logger.info(f"Trying to query registrations directly by event_id '{event_id}' (including archived)")
                all_registrations = []
                all_included = []
                offset = 0
                
                try:
                    # Try querying registrations API with where filter and various archived parameters
                    # Planning Center APIs may use different parameter names for archived items
                    archived_params = [
                        {"include_archived": "true"},
                        {"archived": "true"},
                        {"show_archived": "true"},
                        {"include_archived": "true", "archived": "true"}  # Try both
                    ]
                    
                    for archived_param_set in archived_params:
                        logger.info(f"Trying registrations query with params: {archived_param_set}")
                        offset = 0  # Reset offset for each parameter set
                        all_registrations = []
                        all_included = []
                        
                        while True:
                            params = {
                                "per_page": per_page,
                                "offset": offset,
                                "include": "person,event",
                                "where[event_id]": event_id
                            }
                            params.update(archived_param_set)
                            
                            response = client.get(
                                f"{self.base_url}/registrations/v2/registrations",
                                headers=self.headers,
                                params=params,
                            )
                            # Handle 404 - try next parameter set
                            if response.status_code == 404:
                                logger.info(f"No registrations found with params {archived_param_set} (404)")
                                break  # Break inner loop, try next parameter set
                            # Handle 401 - try next parameter set
                            if response.status_code == 401:
                                logger.info(f"Planning Center Registrations API returned 401 with params {archived_param_set}")
                                break  # Break inner loop, try next parameter set
                            response.raise_for_status()
                            data = response.json()
                            
                            page_registrations = data.get("data", [])
                            page_included = data.get("included", [])
                            
                            if not page_registrations:
                                break
                            
                            all_registrations.extend(page_registrations)
                            all_included.extend(page_included)
                            
                            # Check if there are more pages
                            if len(page_registrations) < per_page:
                                break
                            
                            offset += per_page
                        
                        # If we found registrations with this parameter set, process and return them
                        if all_registrations:
                            logger.info(f"Found {len(all_registrations)} registrations with params {archived_param_set}")
                            # Build map of person data by ID
                            people_by_id = {}
                            for item in all_included:
                                if item.get("type") == "Person":
                                    people_by_id[item.get("id")] = item
                            
                            # Attach person data to registrations
                            for registration in all_registrations:
                                relationships = registration.get("relationships", {})
                                person_data = relationships.get("person", {}).get("data")
                                
                                if person_data and person_data.get("id") in people_by_id:
                                    # Attach person attributes to registration for easier access
                                    person = people_by_id[person_data.get("id")]
                                    person_attrs = person.get("attributes", {})
                                    registration_attrs = registration.get("attributes", {})
                                    
                                    # Add person name and email to registration attributes
                                    first_name = person_attrs.get("first_name", "")
                                    last_name = person_attrs.get("last_name", "")
                                    if first_name or last_name:
                                        registration_attrs["person_name"] = f"{first_name} {last_name}".strip()
                                        registration_attrs["first_name"] = first_name
                                        registration_attrs["last_name"] = last_name
                                    
                                    email = person_attrs.get("email") or (person_attrs.get("emails", [{}])[0].get("address") if person_attrs.get("emails") else None)
                                    if email:
                                        registration_attrs["email"] = email
                            
                            logger.info(f"Returning {len(all_registrations)} registrations for event '{event_id}'")
                            return all_registrations
                except httpx.HTTPStatusError as query_error:
                    # Query API failed - log but don't raise
                    logger.warning(f"Failed to query registrations by event_id '{event_id}': {query_error.response.status_code}")
                    if query_error.response.status_code not in [404, 401]:
                        raise
                
                # Try querying without filter to see if API is accessible, then filter client-side
                logger.info(f"Trying to query all registrations (without filter) to verify API access")
                try:
                    # Try a simple query without filter to see if registrations API is accessible
                    response = client.get(
                        f"{self.base_url}/registrations/v2/registrations",
                        headers=self.headers,
                        params={
                            "per_page": 10,  # Just get a few to test
                            "offset": 0,
                            "include": "person,event",
                            "include_archived": "true"
                        },
                    )
                    if response.status_code == 200:
                        logger.info(f"Registrations API is accessible. Checking if event_id format matches...")
                        data = response.json()
                        sample_registrations = data.get("data", [])
                        if sample_registrations:
                            # Check a sample registration to see event_id format
                            sample = sample_registrations[0]
                            relationships = sample.get("relationships", {})
                            event_rel = relationships.get("event", {})
                            event_data_ref = event_rel.get("data", {})
                            sample_event_id = event_data_ref.get("id")
                            logger.info(f"Sample registration found. Event ID in registration: {sample_event_id} (type: {type(sample_event_id).__name__}), Looking for: {event_id} (type: {type(event_id).__name__})")
                    elif response.status_code in [401, 403]:
                        logger.warning(f"Registrations API returned {response.status_code} - may not have access to query registrations")
                    else:
                        logger.info(f"Registrations API returned {response.status_code}")
                except Exception as e:
                    logger.warning(f"Error testing registrations API access: {str(e)}")
                
                # No registrations found in any API
                logger.warning(f"No registrations found for event '{event_id}' in any Planning Center API endpoint")
                return []
        except httpx.TimeoutException:
            logger.warning(f"Request timed out while fetching registrations for event {event_id}")
            raise PlanningCenterAPIError("Request timed out", status_code=504)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # Event not found or has no registrations - return empty list
                logger.info(f"Planning Center event '{event_id}' not found or has no registrations (HTTP 404)")
                return []
            elif e.response.status_code == 401:
                # No access to registrations - return empty list
                logger.info(f"Planning Center event '{event_id}' - no access to registrations (HTTP 401)")
                return []
            elif e.response.status_code == 429:
                raise PlanningCenterRateLimitError("Rate limit exceeded", status_code=429)
            else:
                error_text = str(e.response.text) if e.response.text else str(e.response.status_code)
                logger.error(f"HTTP error {e.response.status_code}: {error_text}")
                raise PlanningCenterAPIError(f"HTTP {e.response.status_code}", status_code=e.response.status_code)
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {e}")
            raise PlanningCenterAPIError("Cannot connect to Planning Center")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise PlanningCenterAPIError(f"Request failed: {str(e)}")
        except ValueError as e:  # JSON decode errors
            logger.error(f"Invalid JSON response: {e}")
            raise PlanningCenterAPIError("Invalid response format")
        except Exception as e:
            logger.error(f"Unexpected error fetching registrations: {e}", exc_info=True)
            raise

    def _get_registrations_from_checkins(self, event_id: str) -> List[Dict[str, Any]]:
        """
        Get registrations from Planning Center Check-Ins API (fallback method).
        
        Args:
            event_id: Planning Center event ID
        
        Returns:
            List of registration dictionaries from Planning Center Check-Ins API
        """
        import httpx
        
        try:
            with httpx.Client(timeout=60.0) as client:
                all_registrations = []
                all_included = []
                per_page = 100
                offset = 0
                
                while True:
                    response = client.get(
                        f"{self.base_url}/check-ins/v2/events/{event_id}/event_times",
                        headers=self.headers,
                        params={
                            "per_page": per_page,
                            "offset": offset,
                            "include": "event_time_registrations.person"
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    event_times = data.get("data", [])
                    page_included = data.get("included", [])
                    
                    if not event_times:
                        break
                    
                    # Extract registrations from event times
                    for event_time in event_times:
                        relationships = event_time.get("relationships", {})
                        registrations_rel = relationships.get("event_time_registrations", {})
                        registrations_data = registrations_rel.get("data", [])
                        
                        # Build map of registrations by ID from included data
                        registrations_by_id = {}
                        for item in page_included:
                            if item.get("type") == "EventTimeRegistration":
                                registrations_by_id[item.get("id")] = item
                        
                        # Add registrations to our list
                        for reg_ref in registrations_data:
                            reg_id = reg_ref.get("id")
                            if reg_id in registrations_by_id:
                                all_registrations.append(registrations_by_id[reg_id])
                    
                    all_included.extend(page_included)
                    
                    # Check if there are more pages
                    if len(event_times) < per_page:
                        break
                    
                    offset += per_page
                
                # Build map of person data by ID
                people_by_id = {}
                for item in all_included:
                    if item.get("type") == "Person":
                        people_by_id[item.get("id")] = item
                
                # Attach person data to registrations
                for registration in all_registrations:
                    relationships = registration.get("relationships", {})
                    person_data = relationships.get("person", {}).get("data")
                    
                    if person_data and person_data.get("id") in people_by_id:
                        # Attach person attributes to registration for easier access
                        person = people_by_id[person_data.get("id")]
                        person_attrs = person.get("attributes", {})
                        registration_attrs = registration.get("attributes", {})
                        
                        # Add person name and email to registration attributes
                        first_name = person_attrs.get("first_name", "")
                        last_name = person_attrs.get("last_name", "")
                        if first_name or last_name:
                            registration_attrs["person_name"] = f"{first_name} {last_name}".strip()
                            registration_attrs["first_name"] = first_name
                            registration_attrs["last_name"] = last_name
                        
                        email = person_attrs.get("email") or (person_attrs.get("emails", [{}])[0].get("address") if person_attrs.get("emails") else None)
                        if email:
                            registration_attrs["email"] = email
                
                return all_registrations
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Planning Center event '{event_id}' not found in Check-Ins API")
            raise ValueError(f"Planning Center Check-Ins API error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"Failed to connect to Planning Center Check-Ins API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error fetching registrations from Check-Ins API: {str(e)}")

    async def sync_registrations(
        self, event_id: Optional[str] = None, updated_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """Sync registrations from Planning Center"""
        sync_log = PlanningCenterSyncLog(
            sync_type="registrations",
            sync_direction="from_pc",
            started_at=datetime.now(timezone.utc),
            created_by=updated_by,
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
                        params={"per_page": 100},
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
                            errors.append(
                                f"Registration {registration_data.get('id')}: {str(e)}"
                            )
                else:
                    # Sync all registrations (this could be expensive)
                    # Get all events first, then get registrations for each
                    events_response = await client.get(
                        f"{self.base_url}/events/v2/events",
                        headers=self.headers,
                        params={"per_page": 100},
                    )
                    events_response.raise_for_status()
                    events_data = events_response.json()

                    for event_data in events_data.get("data", []):
                        event_id = event_data.get("id")
                        registrations_response = await client.get(
                            f"{self.base_url}/events/v2/events/{event_id}/registrations",
                            headers=self.headers,
                            params={"per_page": 100},
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
                                errors.append(
                                    f"Registration {registration_data.get('id')}: {str(e)}"
                                )

                # Update sync log
                sync_log.records_processed = records_processed
                sync_log.records_successful = records_successful
                sync_log.records_failed = records_failed
                sync_log.completed_at = datetime.now(timezone.utc)
                if errors:
                    sync_log.error_details = {"errors": errors}

                self.db.commit()

                return {
                    "status": "success",
                    "records_processed": records_processed,
                    "records_successful": records_successful,
                    "records_failed": records_failed,
                    "errors": errors,
                }

        except Exception as e:
            sync_log.completed_at = datetime.now(timezone.utc)
            sync_log.error_details = {"error": str(e)}
            self.db.commit()

            return {"status": "error", "error": str(e)}

    def _get_cached_events(self, cache_ttl_minutes: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get events from cache if cache is fresh (within TTL)
        
        Args:
            cache_ttl_minutes: Cache TTL in minutes
            
        Returns:
            List of event dictionaries if cache is fresh, None otherwise
        """
        from datetime import timedelta, timezone
        from sqlalchemy import desc
        
        try:
            # Check the most recent cache entry's last_synced_at
            most_recent_cache = (
                self.db.query(PlanningCenterEventsCache)
                .order_by(desc(PlanningCenterEventsCache.last_synced_at))
                .first()
            )
            
            if not most_recent_cache or not most_recent_cache.last_synced_at:
                return None
            
            # Check if cache is still fresh
            # Handle timezone-aware comparison
            if most_recent_cache.last_synced_at.tzinfo is None:
                # If naive datetime, assume UTC
                cache_time = most_recent_cache.last_synced_at.replace(tzinfo=timezone.utc)
            else:
                cache_time = most_recent_cache.last_synced_at
            
            cache_age = datetime.now(timezone.utc) - cache_time
            if cache_age > timedelta(minutes=cache_ttl_minutes):
                return None
            
            # Cache is fresh - retrieve all cached events
            # Sort by start_date descending (most recent/future events first), then by last_synced_at
            # Use nullslast() to handle events without start_date
            from sqlalchemy import nullslast
            cached_entries = (
                self.db.query(PlanningCenterEventsCache)
                .order_by(
                    nullslast(desc(PlanningCenterEventsCache.start_date)),
                    desc(PlanningCenterEventsCache.last_synced_at)
                )
                .limit(settings.PLANNING_CENTER_MAX_EVENTS)
                .all()
            )
            
            if not cached_entries:
                return None
            
            # Reconstruct event dictionaries from cache in API format
            events = []
            for cache_entry in cached_entries:
                # Format dates for API response
                start_date_str = None
                end_date_str = None
                if cache_entry.start_date:
                    if cache_entry.start_date.tzinfo is None:
                        start_date_str = cache_entry.start_date.replace(tzinfo=timezone.utc).isoformat()
                    else:
                        start_date_str = cache_entry.start_date.isoformat()
                if cache_entry.end_date:
                    if cache_entry.end_date.tzinfo is None:
                        end_date_str = cache_entry.end_date.replace(tzinfo=timezone.utc).isoformat()
                    else:
                        end_date_str = cache_entry.end_date.isoformat()
                
                event = {
                    "id": cache_entry.planning_center_event_id,
                    "type": "event",
                    "attributes": {
                        "name": cache_entry.event_name,
                        "description": cache_entry.event_description,
                        "start_date": start_date_str,
                        "end_date": end_date_str,
                        "starts_at": start_date_str,
                        "ends_at": end_date_str,
                        "capacity": cache_entry.max_capacity,
                        "max_attendees": cache_entry.max_capacity,
                        "current_registrations_count": cache_entry.current_registrations_count,
                        "registration_deadline": cache_entry.registration_deadline.isoformat() if cache_entry.registration_deadline else None,
                        "status": cache_entry.event_status,
                    }
                }
                events.append(event)
            
            return events
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error retrieving cached events: {str(e)}")
            return None

    def _update_events_cache(self, events: List[Dict[str, Any]]) -> None:
        """
        Update the events cache with fresh data from API
        
        Args:
            events: List of event dictionaries from Planning Center API
        """
        try:
            for event in events:
                self._cache_event_data(self.db, event)
            
            self.db.commit()
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating events cache: {str(e)}")
            self.db.rollback()

    def _cache_event_data(self, db: Session, event_data: Dict[str, Any]):
        """Cache event data from Planning Center"""
        pc_event_id = event_data.get("id")
        attributes = event_data.get("attributes", {})
        
        # Helper to get value from attributes or direct (for flat structure compatibility)
        def get_val(key):
            return attributes.get(key) or event_data.get(key)
        
        # Handle both Check-Ins API (start_date/end_date) and Calendar API (starts_at/ends_at) formats
        start_date_val = get_val("start_date") or get_val("starts_at")
        end_date_val = get_val("end_date") or get_val("ends_at")

        # Check if already cached
        existing_cache = (
            db.query(PlanningCenterEventsCache)
            .filter(PlanningCenterEventsCache.planning_center_event_id == pc_event_id)
            .first()
        )

        if existing_cache:
            # Update existing cache
            existing_cache.event_name = get_val("name")
            existing_cache.event_description = get_val("description")
            existing_cache.start_date = self._parse_datetime(start_date_val)
            existing_cache.end_date = self._parse_datetime(end_date_val)
            existing_cache.max_capacity = get_val("max_capacity")
            existing_cache.current_registrations_count = get_val(
                "current_registrations_count"
            ) or get_val("current_registrations") or 0
            existing_cache.registration_deadline = self._parse_datetime(
                get_val("registration_deadline")
            )
            existing_cache.event_status = get_val("status")
            existing_cache.last_synced_at = datetime.now(timezone.utc)
            existing_cache.updated_at = datetime.now(timezone.utc)
        else:
            # Create new cache entry
            cache_entry = PlanningCenterEventsCache(
                planning_center_event_id=pc_event_id,
                event_name=get_val("name"),
                event_description=get_val("description"),
                start_date=self._parse_datetime(start_date_val),
                end_date=self._parse_datetime(end_date_val),
                max_capacity=get_val("max_capacity"),
                current_registrations_count=get_val("current_registrations_count") or get_val("current_registrations") or 0,
                registration_deadline=self._parse_datetime(
                    get_val("registration_deadline")
                ),
                event_status=get_val("status"),
                last_synced_at=datetime.now(timezone.utc),
            )
            db.add(cache_entry)

        db.commit()

    def _cache_registration_data(self, db: Session, registration_data: Dict[str, Any]):
        """Cache registration data from Planning Center"""
        pc_registration_id = registration_data.get("id")
        attributes = registration_data.get("attributes", {})
        relationships = registration_data.get("relationships", {})
        
        # Helper to get value from attributes or direct
        def get_val(key):
            return attributes.get(key) or registration_data.get(key)
            
        # Helper to get ID from relationships or direct
        def get_rel_id(key):
            if key in relationships and "data" in relationships[key]:
                return relationships[key]["data"].get("id")
            return registration_data.get(f"{key}_id") or registration_data.get(key)

        # Check if already cached
        existing_cache = (
            db.query(PlanningCenterRegistrationsCache)
            .filter(
                PlanningCenterRegistrationsCache.planning_center_registration_id
                == pc_registration_id
            )
            .first()
        )

        if existing_cache:
            # Update existing cache
            existing_cache.registration_status = get_val("status")
            existing_cache.registration_date = self._parse_datetime(
                get_val("created_at")
            )
            existing_cache.registration_notes = get_val("notes")
            existing_cache.custom_field_responses = get_val(
                "custom_field_responses"
            )
            existing_cache.last_synced_at = datetime.now(timezone.utc)
            existing_cache.updated_at = datetime.now(timezone.utc)
        else:
            # Create new cache entry
            cache_entry = PlanningCenterRegistrationsCache(
                planning_center_registration_id=pc_registration_id,
                planning_center_event_id=get_rel_id("event"),
                planning_center_person_id=get_rel_id("person"),
                registration_status=get_val("status"),
                registration_date=self._parse_datetime(
                    get_val("created_at")
                ),
                registration_notes=get_val("notes"),
                custom_field_responses=get_val("custom_field_responses"),
                last_synced_at=datetime.now(timezone.utc),
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
                payload=webhook_data,
            )
            self.db.add(webhook_event)
            self.db.commit()

            # Process based on event type
            event_type = webhook_data.get("event_type")
            if event_type == "person.created" or event_type == "person.updated":
                # Sync person data
                try:
                    asyncio.create_task(self.sync_people())
                except RuntimeError:
                    # No event loop running (e.g., in tests), skip async task creation
                    pass
            elif event_type == "event.created" or event_type == "event.updated":
                # Sync event data
                try:
                    asyncio.create_task(self.sync_events())
                except RuntimeError:
                    # No event loop running (e.g., in tests), skip async task creation
                    pass
            elif (
                event_type == "registration.created"
                or event_type == "registration.updated"
            ):
                # Sync registration data
                event_id = webhook_data.get("event_id")
                try:
                    asyncio.create_task(self.sync_registrations(event_id=event_id))
                except RuntimeError:
                    # No event loop running (e.g., in tests), skip async task creation
                    pass

            # Mark webhook as processed
            webhook_event.processed = True
            webhook_event.processed_at = datetime.now(timezone.utc)
            self.db.commit()

            return {"status": "success", "message": "Webhook processed successfully"}

        except Exception as e:
            # Mark webhook as failed
            if "webhook_event" in locals():
                webhook_event.processed = True
                webhook_event.processed_at = datetime.now(timezone.utc)
                webhook_event.error_message = str(e)
                self.db.commit()

            return {"status": "error", "error": str(e)}
