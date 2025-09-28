"""
Content Management Service

This service handles course content management including file uploads,
content organization, access tracking, and audit logging.
"""

import os
import uuid
import mimetypes
from typing import List, Optional, Dict, Any, BinaryIO
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from fastapi import UploadFile, HTTPException, status
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from app.models.course_content import (
    CourseModule, CourseContent, ContentAccessLog, ContentAuditLog,
    ContentType, StorageType
)
from app.models.course import Course
from app.models.user import User
from app.schemas.course_content import (
    CourseModuleCreate, CourseModuleUpdate,
    CourseContentCreate, CourseContentUpdate,
    ContentAccessLogCreate, ContentAuditLogCreate
)
from app.core.config import settings


class ContentService:
    """Service for managing course content"""
    
    def __init__(self, db: Session):
        self.db = db
        self.s3_client = None
        self._init_s3_client()
    
    def _init_s3_client(self):
        """Initialize S3 client if credentials are available"""
        if not BOTO3_AVAILABLE:
            print("Warning: boto3 not available, S3 functionality disabled")
            return
            
        if (hasattr(settings, 'AWS_ACCESS_KEY_ID') and 
            hasattr(settings, 'AWS_SECRET_ACCESS_KEY') and
            hasattr(settings, 'AWS_S3_BUCKET')):
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=getattr(settings, 'AWS_REGION', 'us-east-1')
                )
            except Exception as e:
                print(f"Warning: Could not initialize S3 client: {e}")
    
    # Course Module Management
    
    def create_module(self, module_data: CourseModuleCreate, user_id: int) -> CourseModule:
        """Create a new course module"""
        # Verify course exists
        course = self.db.query(Course).filter(Course.id == module_data.course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Create module
        db_module = CourseModule(
            **module_data.dict(),
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(db_module)
        self.db.commit()
        self.db.refresh(db_module)
        
        # Log audit trail (only for content, not modules)
        # Modules don't have content_id, so we skip audit logging for now
        # TODO: Implement separate module audit logging if needed
        
        return db_module
    
    def get_modules(self, course_id: int) -> List[CourseModule]:
        """Get all modules for a course"""
        return self.db.query(CourseModule).filter(
            CourseModule.course_id == course_id
        ).order_by(CourseModule.order_index).all()
    
    def get_module(self, module_id: int) -> Optional[CourseModule]:
        """Get a specific module"""
        return self.db.query(CourseModule).filter(CourseModule.id == module_id).first()
    
    def update_module(self, module_id: int, module_data: CourseModuleUpdate, user_id: int) -> Optional[CourseModule]:
        """Update a course module"""
        db_module = self.get_module(module_id)
        if not db_module:
            return None
        
        # Store old values for audit
        old_values = {
            "title": db_module.title,
            "description": db_module.description,
            "order_index": db_module.order_index,
            "is_active": db_module.is_active
        }
        
        # Update fields
        update_data = module_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_module, field, value)
        
        db_module.updated_by = user_id
        db_module.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_module)
        
        # Log audit trail
        self._log_audit(
            content_id=None,
            user_id=user_id,
            action="update",
            change_summary=f"Updated module: {db_module.title}",
            old_values=old_values,
            new_values=update_data
        )
        
        return db_module
    
    def delete_module(self, module_id: int, user_id: int) -> bool:
        """Delete a course module"""
        db_module = self.get_module(module_id)
        if not db_module:
            return False
        
        # Store old values for audit
        old_values = {
            "title": db_module.title,
            "description": db_module.description,
            "course_id": db_module.course_id
        }
        
        self.db.delete(db_module)
        self.db.commit()
        
        # Log audit trail
        self._log_audit(
            content_id=None,
            user_id=user_id,
            action="delete",
            change_summary=f"Deleted module: {db_module.title}",
            old_values=old_values
        )
        
        return True
    
    # Course Content Management
    
    def create_content(self, content_data: CourseContentCreate, user_id: int) -> CourseContent:
        """Create new course content"""
        # Verify course exists
        course = self.db.query(Course).filter(Course.id == content_data.course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Verify module exists if specified
        if content_data.module_id:
            module = self.get_module(content_data.module_id)
            if not module:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Module not found"
                )
        
        # Determine storage type based on content type
        storage_type = self._determine_storage_type(content_data)
        
        # Create content
        db_content = CourseContent(
            **content_data.dict(),
            storage_type=storage_type,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(db_content)
        self.db.commit()
        self.db.refresh(db_content)
        
        # Log audit trail
        self._log_audit(
            content_id=db_content.id,
            user_id=user_id,
            action="create",
            change_summary=f"Created content: {content_data.title}",
            new_values=content_data.dict()
        )
        
        return db_content
    
    def upload_file(self, content_id: int, file: UploadFile, user_id: int) -> Dict[str, Any]:
        """Upload a file for course content"""
        content = self.db.query(CourseContent).filter(CourseContent.id == content_id).first()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Check file size
        file_size = 0
        file_content = file.file.read()
        file_size = len(file_content)
        file.file.seek(0)  # Reset file pointer
        
        max_size = content.course.max_file_size_mb * 1024 * 1024  # Convert MB to bytes
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {content.course.max_file_size_mb}MB"
            )
        
        # Determine storage type based on file size
        storage_type = StorageType.DATABASE if file_size < 10 * 1024 * 1024 else StorageType.S3  # 10MB threshold
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Store file
        if storage_type == StorageType.DATABASE:
            file_path = self._store_file_in_database(unique_filename, file_content)
        else:
            file_path = self._store_file_in_s3(unique_filename, file_content, file.content_type)
        
        # Update content record
        content.file_name = file.filename
        content.file_size = file_size
        content.file_path = file_path
        content.mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        content.storage_type = storage_type
        content.updated_by = user_id
        content.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(content)
        
        # Log audit trail
        self._log_audit(
            content_id=content_id,
            user_id=user_id,
            action="update",
            change_summary=f"Uploaded file: {file.filename}",
            new_values={
                "file_name": file.filename,
                "file_size": file_size,
                "file_path": file_path,
                "mime_type": file.content_type
            }
        )
        
        return {
            "content_id": content_id,
            "file_path": file_path,
            "file_size": file_size,
            "storage_type": storage_type,
            "message": "File uploaded successfully"
        }
    
    def get_content(self, course_id: int, module_id: Optional[int] = None) -> List[CourseContent]:
        """Get content for a course, optionally filtered by module"""
        query = self.db.query(CourseContent).filter(CourseContent.course_id == course_id)
        
        if module_id:
            query = query.filter(CourseContent.module_id == module_id)
        
        return query.order_by(CourseContent.order_index).all()
    
    def get_content_item(self, content_id: int) -> Optional[CourseContent]:
        """Get a specific content item"""
        return self.db.query(CourseContent).filter(CourseContent.id == content_id).first()
    
    def update_content(self, content_id: int, content_data: CourseContentUpdate, user_id: int) -> Optional[CourseContent]:
        """Update course content"""
        db_content = self.get_content_item(content_id)
        if not db_content:
            return None
        
        # Store old values for audit
        old_values = {
            "title": db_content.title,
            "description": db_content.description,
            "module_id": db_content.module_id,
            "order_index": db_content.order_index,
            "is_active": db_content.is_active
        }
        
        # Update fields
        update_data = content_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_content, field, value)
        
        db_content.updated_by = user_id
        db_content.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_content)
        
        # Log audit trail
        self._log_audit(
            content_id=content_id,
            user_id=user_id,
            action="update",
            change_summary=f"Updated content: {db_content.title}",
            old_values=old_values,
            new_values=update_data
        )
        
        return db_content
    
    def delete_content(self, content_id: int, user_id: int) -> bool:
        """Delete course content"""
        db_content = self.get_content_item(content_id)
        if not db_content:
            return False
        
        # Store old values for audit
        old_values = {
            "title": db_content.title,
            "description": db_content.description,
            "course_id": db_content.course_id,
            "file_path": db_content.file_path
        }
        
        # Delete associated file if it exists
        if db_content.file_path:
            self._delete_file(db_content.file_path, db_content.storage_type)
        
        self.db.delete(db_content)
        self.db.commit()
        
        # Log audit trail
        self._log_audit(
            content_id=content_id,
            user_id=user_id,
            action="delete",
            change_summary=f"Deleted content: {db_content.title}",
            old_values=old_values
        )
        
        return True
    
    def download_content(self, content_id: int, user_id: int, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Download course content"""
        content = self.get_content_item(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Log access
        self._log_access(
            content_id=content_id,
            user_id=user_id,
            access_type="download",
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Increment download count
        content.download_count += 1
        self.db.commit()
        
        # Get file content
        if content.storage_type == StorageType.DATABASE:
            file_content = self._get_file_from_database(content.file_path)
        elif content.storage_type == StorageType.S3:
            file_content = self._get_file_from_s3(content.file_path)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot download external content"
            )
        
        return {
            "content": file_content,
            "filename": content.file_name,
            "mime_type": content.mime_type,
            "file_size": content.file_size
        }
    
    # Access Tracking
    
    def log_content_access(self, access_data: ContentAccessLogCreate) -> ContentAccessLog:
        """Log content access"""
        db_access = ContentAccessLog(**access_data.dict())
        self.db.add(db_access)
        self.db.commit()
        self.db.refresh(db_access)
        return db_access
    
    def get_content_access_logs(self, content_id: int, limit: int = 100) -> List[ContentAccessLog]:
        """Get access logs for content"""
        return self.db.query(ContentAccessLog).filter(
            ContentAccessLog.content_id == content_id
        ).order_by(desc(ContentAccessLog.access_timestamp)).limit(limit).all()
    
    def get_user_content_progress(self, user_id: int, course_id: int) -> Dict[str, Any]:
        """Get user's content access progress for a course"""
        # Get all content for the course
        content_items = self.get_content(course_id)
        content_ids = [item.id for item in content_items]
        
        # Get access logs for this user and course content
        access_logs = self.db.query(ContentAccessLog).filter(
            and_(
                ContentAccessLog.user_id == user_id,
                ContentAccessLog.content_id.in_(content_ids)
            )
        ).all()
        
        # Organize by content
        progress = {}
        for content in content_items:
            content_logs = [log for log in access_logs if log.content_id == content.id]
            if content_logs:
                latest_log = max(content_logs, key=lambda x: x.access_timestamp)
                progress[content.id] = {
                    "content_title": content.title,
                    "last_accessed": latest_log.access_timestamp,
                    "access_type": latest_log.access_type,
                    "progress_percentage": latest_log.progress_percentage or 0,
                    "time_spent": latest_log.time_spent or 0
                }
            else:
                progress[content.id] = {
                    "content_title": content.title,
                    "last_accessed": None,
                    "access_type": None,
                    "progress_percentage": 0,
                    "time_spent": 0
                }
        
        return progress
    
    # Audit Trail
    
    def get_audit_logs(self, content_id: int, limit: int = 100) -> List[ContentAuditLog]:
        """Get audit logs for content"""
        return self.db.query(ContentAuditLog).filter(
            ContentAuditLog.content_id == content_id
        ).order_by(desc(ContentAuditLog.change_timestamp)).limit(limit).all()
    
    # Helper Methods
    
    def _determine_storage_type(self, content_data: CourseContentCreate) -> StorageType:
        """Determine storage type based on content type"""
        if content_data.content_type in [ContentType.EXTERNAL_LINK, ContentType.EMBEDDED]:
            return StorageType.EXTERNAL
        elif content_data.file_size and content_data.file_size > 10 * 1024 * 1024:  # 10MB
            return StorageType.S3
        else:
            return StorageType.DATABASE
    
    def _store_file_in_database(self, filename: str, file_content: bytes) -> str:
        """Store file in database (for small files)"""
        # For now, we'll store in a files directory
        # In production, you might want to store in a dedicated file storage table
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return file_path
    
    def _store_file_in_s3(self, filename: str, file_content: bytes, content_type: str) -> str:
        """Store file in S3"""
        if not self.s3_client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3 storage not configured"
            )
        
        bucket_name = settings.AWS_S3_BUCKET
        s3_key = f"course-content/{filename}"
        
        try:
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type
            )
            return s3_key
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload to S3: {str(e)}"
            )
    
    def _get_file_from_database(self, file_path: str) -> bytes:
        """Get file content from database storage"""
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        with open(file_path, "rb") as f:
            return f.read()
    
    def _get_file_from_s3(self, s3_key: str) -> bytes:
        """Get file content from S3"""
        if not self.s3_client:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="S3 storage not configured"
            )
        
        try:
            response = self.s3_client.get_object(
                Bucket=settings.AWS_S3_BUCKET,
                Key=s3_key
            )
            return response['Body'].read()
        except ClientError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found in S3: {str(e)}"
            )
    
    def _delete_file(self, file_path: str, storage_type: StorageType):
        """Delete file from storage"""
        if storage_type == StorageType.DATABASE:
            if os.path.exists(file_path):
                os.remove(file_path)
        elif storage_type == StorageType.S3 and self.s3_client:
            try:
                self.s3_client.delete_object(
                    Bucket=settings.AWS_S3_BUCKET,
                    Key=file_path
                )
            except ClientError:
                pass  # Ignore errors when deleting
    
    def _log_access(self, content_id: int, user_id: int, access_type: str, 
                   ip_address: str = None, user_agent: str = None):
        """Log content access"""
        access_log = ContentAccessLog(
            content_id=content_id,
            user_id=user_id,
            access_type=access_type,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(access_log)
        self.db.commit()
    
    def _log_audit(self, content_id: Optional[int], user_id: int, action: str,
                  change_summary: str, old_values: Dict = None, new_values: Dict = None):
        """Log audit trail"""
        audit_log = ContentAuditLog(
            content_id=content_id,
            user_id=user_id,
            action=action,
            change_summary=change_summary,
            old_values=old_values,
            new_values=new_values
        )
        self.db.add(audit_log)
        self.db.commit()
