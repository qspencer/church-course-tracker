"""
Enhanced CSV Data Loader with Source Tracking

This module provides enhanced functionality to load test data from CSV files
with source tracking, allowing selective removal of only CSV-loaded data.
"""

import csv
import os
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.course import Course
from app.models.course_content import CourseModule, CourseContent, ContentType, StorageType
from app.models.member import People
from app.models.campus import Campus
from app.models.role import Role
from app.models.course_role import CourseRole
from app.models.enrollment import CourseEnrollment
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


class EnhancedCSVDataLoader:
    """Enhanced CSV loader with source tracking and selective clearing"""
    
    def __init__(self, data_dir: str = "data/csv"):
        self.data_dir = data_dir
        self.csv_timestamp = datetime.now(timezone.utc)
    
    def load_all_data(self, db: Session, force_reload: bool = False) -> Dict[str, int]:
        """
        Load all CSV data into the database with source tracking
        
        Args:
            db: Database session
            force_reload: If True, reload data even if it already exists
            
        Returns:
            Dictionary with counts of loaded records by type
        """
        results = {}
        
        try:
            # Load data in dependency order with source tracking
            results['campuses'] = self._load_campuses(db, force_reload)
            results['roles'] = self._load_roles(db, force_reload)
            results['users'] = self._load_users(db, force_reload)
            results['people'] = self._load_people(db, force_reload)
            results['courses'] = self._load_courses(db, force_reload)
            results['modules'] = self._load_modules(db, force_reload)
            results['content'] = self._load_content(db, force_reload)
            results['enrollments'] = self._load_enrollments(db, force_reload)
            
            db.commit()
            logger.info(f"Successfully loaded CSV data: {results}")
            return results
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading CSV data: {e}")
            raise
    
    def clear_csv_data_only(self, db: Session) -> Dict[str, int]:
        """
        Clear only CSV-loaded data, preserving user-entered data
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with counts of deleted records by type
        """
        results = {}
        
        try:
            # Delete in reverse dependency order, only CSV-loaded data
            results['enrollments'] = self._clear_csv_enrollments(db)
            results['content'] = self._clear_csv_content(db)
            results['modules'] = self._clear_csv_modules(db)
            results['courses'] = self._clear_csv_courses(db)
            results['people'] = self._clear_csv_people(db)
            results['users'] = self._clear_csv_users(db)
            results['campuses'] = self._clear_csv_campuses(db)
            results['roles'] = self._clear_csv_roles(db)
            
            db.commit()
            logger.info(f"Successfully cleared CSV data: {results}")
            return results
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error clearing CSV data: {e}")
            raise
    
    def get_csv_data_summary(self, db: Session) -> Dict[str, int]:
        """
        Get summary of CSV-loaded data only
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with counts of CSV-loaded records by type
        """
        return {
            'csv_campuses': db.query(Campus).filter(Campus.data_source == 'csv').count(),
            'csv_roles': db.query(Role).filter(Role.data_source == 'csv').count(),
            'csv_users': db.query(User).filter(User.data_source == 'csv').count(),
            'csv_people': db.query(People).filter(People.data_source == 'csv').count(),
            'csv_courses': db.query(Course).filter(Course.data_source == 'csv').count(),
            'csv_modules': db.query(CourseModule).filter(CourseModule.data_source == 'csv').count(),
            'csv_content': db.query(CourseContent).filter(CourseContent.data_source == 'csv').count(),
            'csv_enrollments': db.query(CourseEnrollment).filter(CourseEnrollment.data_source == 'csv').count(),
        }
    
    def _load_campuses(self, db: Session, force_reload: bool) -> int:
        """Load campuses with source tracking"""
        csv_file = os.path.join(self.data_dir, "campuses.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(Campus).filter(Campus.data_source == 'csv').first():
            logger.info("CSV campuses already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                campus = Campus(
                    name=row['name'],
                    address=row.get('address', ''),
                    phone=row.get('phone', ''),
                    email=row.get('email', ''),
                    is_active=row.get('is_active', 'true').lower() == 'true',
                    data_source='csv',
                    csv_loaded_at=self.csv_timestamp
                )
                db.add(campus)
                count += 1
        
        logger.info(f"✅ Loaded {count} campuses from CSV")
        return count
    
    def _load_roles(self, db: Session, force_reload: bool) -> int:
        """Load roles with source tracking"""
        csv_file = os.path.join(self.data_dir, "roles.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(Role).filter(Role.data_source == 'csv').first():
            logger.info("CSV roles already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                role = Role(
                    name=row['name'],
                    description=row.get('description', ''),
                    permissions=row.get('permissions', '[]'),
                    is_active=row.get('is_active', 'true').lower() == 'true',
                    data_source='csv',
                    csv_loaded_at=self.csv_timestamp
                )
                db.add(role)
                count += 1
        
        logger.info(f"✅ Loaded {count} roles from CSV")
        return count
    
    def _load_users(self, db: Session, force_reload: bool) -> int:
        """Load users with source tracking"""
        csv_file = os.path.join(self.data_dir, "users.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(User).filter(User.data_source == 'csv').first():
            logger.info("CSV users already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user = User(
                    username=row['username'],
                    email=row['email'],
                    full_name=row['full_name'],
                    hashed_password=get_password_hash(row['password']),
                    role=row.get('role', 'staff'),
                    is_active=row.get('is_active', 'true').lower() == 'true',
                    data_source='csv',
                    csv_loaded_at=self.csv_timestamp
                )
                db.add(user)
                count += 1
        
        logger.info(f"✅ Loaded {count} users from CSV")
        return count
    
    def _load_people(self, db: Session, force_reload: bool) -> int:
        """Load people with source tracking"""
        csv_file = os.path.join(self.data_dir, "people.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(People).filter(People.data_source == 'csv').first():
            logger.info("CSV people already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                people = People(
                    planning_center_id=f"pc_{row['first_name'].lower()}_{row['last_name'].lower()}",  # Generate ID
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    email=row['email'],
                    phone=row.get('phone', ''),
                    date_of_birth=None,  # Not in CSV
                    gender='',  # Not in CSV
                    address1=row.get('address', ''),
                    city=row.get('city', ''),
                    state=row.get('state', ''),
                    zip=row.get('zip_code', ''),
                    household_id='',  # Not in CSV
                    household_name='',  # Not in CSV
                    status='active',
                    join_date=None,  # Not in CSV
                    is_active=row.get('is_active', 'true').lower() == 'true',
                    data_source='csv',
                    csv_loaded_at=self.csv_timestamp
                )
                db.add(people)
                count += 1
        
        logger.info(f"✅ Loaded {count} people from CSV")
        return count
    
    def _load_courses(self, db: Session, force_reload: bool) -> int:
        """Load courses with source tracking"""
        csv_file = os.path.join(self.data_dir, "courses.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(Course).filter(Course.data_source == 'csv').first():
            logger.info("CSV courses already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                course = Course(
                    title=row['title'],
                    description=row.get('description', ''),
                    duration_weeks=int(row.get('duration_weeks', 0)) if row.get('duration_weeks') else None,
                    max_capacity=int(row.get('max_capacity', 0)) if row.get('max_capacity') else None,
                    is_active=row.get('is_active', 'true').lower() == 'true',
                    data_source='csv',
                    csv_loaded_at=self.csv_timestamp
                )
                db.add(course)
                count += 1
        
        logger.info(f"✅ Loaded {count} courses from CSV")
        return count
    
    def _load_modules(self, db: Session, force_reload: bool) -> int:
        """Load modules with source tracking"""
        csv_file = os.path.join(self.data_dir, "modules.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(CourseModule).filter(CourseModule.data_source == 'csv').first():
            logger.info("CSV modules already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Find course by title
                course = db.query(Course).filter(Course.title == row['course_title']).first()
                if not course:
                    logger.warning(f"Course not found: {row['course_title']}")
                    continue
                
                module = CourseModule(
                    course_id=course.id,
                    title=row['title'],
                    description=row.get('description', ''),
                    order_index=int(row.get('order_index', 1)),
                    data_source='csv',
                    csv_loaded_at=self.csv_timestamp
                )
                db.add(module)
                count += 1
        
        logger.info(f"✅ Loaded {count} modules from CSV")
        return count
    
    def _load_content(self, db: Session, force_reload: bool) -> int:
        """Load content with source tracking"""
        csv_file = os.path.join(self.data_dir, "content.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(CourseContent).filter(CourseContent.data_source == 'csv').first():
            logger.info("CSV content already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Find course by title
                course = db.query(Course).filter(Course.title == row['course_title']).first()
                if not course:
                    logger.warning(f"Course not found: {row['course_title']}")
                    continue
                
                # Find module by title if specified
                module = None
                if row.get('module_title'):
                    module = db.query(CourseModule).filter(
                        CourseModule.course_id == course.id,
                        CourseModule.title == row['module_title']
                    ).first()
                
                content = CourseContent(
                    course_id=course.id,
                    module_id=module.id if module else None,
                    title=row['title'],
                    content_type=row.get('content_type', 'document'),
                    storage_type=row.get('storage_type', 'database'),
                    order_index=int(row.get('order_index', 1)),
                    data_source='csv',
                    csv_loaded_at=self.csv_timestamp
                )
                db.add(content)
                count += 1
        
        logger.info(f"✅ Loaded {count} content from CSV")
        return count
    
    def _load_enrollments(self, db: Session, force_reload: bool) -> int:
        """Load enrollments with source tracking"""
        csv_file = os.path.join(self.data_dir, "enrollments.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(CourseEnrollment).filter(CourseEnrollment.data_source == 'csv').first():
            logger.info("CSV enrollments already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Find course by title
                course = db.query(Course).filter(Course.title == row['course_title']).first()
                if not course:
                    logger.warning(f"Course not found: {row['course_title']}")
                    continue
                
                # Find person by name
                person = db.query(People).filter(
                    People.first_name == row['first_name'],
                    People.last_name == row['last_name']
                ).first()
                if not person:
                    logger.warning(f"Person not found: {row['first_name']} {row['last_name']}")
                    continue
                
                enrollment = CourseEnrollment(
                    people_id=person.id,
                    course_id=course.id,
                    enrollment_date=datetime.now(timezone.utc),
                    status=row.get('status', 'enrolled'),
                    progress_percentage=0.0,
                    planning_center_synced=False,
                    registration_status='registered',
                    data_source='csv',
                    csv_loaded_at=self.csv_timestamp
                )
                db.add(enrollment)
                count += 1
        
        logger.info(f"✅ Loaded {count} enrollments from CSV")
        return count
    
    # Clear methods for CSV data only
    def _clear_csv_enrollments(self, db: Session) -> int:
        """Clear only CSV-loaded enrollments"""
        count = db.query(CourseEnrollment).filter(CourseEnrollment.data_source == 'csv').count()
        db.query(CourseEnrollment).filter(CourseEnrollment.data_source == 'csv').delete()
        logger.info(f"🗑️ Cleared {count} CSV enrollments")
        return count
    
    def _clear_csv_content(self, db: Session) -> int:
        """Clear only CSV-loaded content"""
        count = db.query(CourseContent).filter(CourseContent.data_source == 'csv').count()
        db.query(CourseContent).filter(CourseContent.data_source == 'csv').delete()
        logger.info(f"🗑️ Cleared {count} CSV content")
        return count
    
    def _clear_csv_modules(self, db: Session) -> int:
        """Clear only CSV-loaded modules"""
        count = db.query(CourseModule).filter(CourseModule.data_source == 'csv').count()
        db.query(CourseModule).filter(CourseModule.data_source == 'csv').delete()
        logger.info(f"🗑️ Cleared {count} CSV modules")
        return count
    
    def _clear_csv_courses(self, db: Session) -> int:
        """Clear only CSV-loaded courses"""
        count = db.query(Course).filter(Course.data_source == 'csv').count()
        db.query(Course).filter(Course.data_source == 'csv').delete()
        logger.info(f"🗑️ Cleared {count} CSV courses")
        return count
    
    def _clear_csv_people(self, db: Session) -> int:
        """Clear only CSV-loaded people"""
        count = db.query(People).filter(People.data_source == 'csv').count()
        db.query(People).filter(People.data_source == 'csv').delete()
        logger.info(f"🗑️ Cleared {count} CSV people")
        return count
    
    def _clear_csv_users(self, db: Session) -> int:
        """Clear only CSV-loaded users"""
        count = db.query(User).filter(User.data_source == 'csv').count()
        db.query(User).filter(User.data_source == 'csv').delete()
        logger.info(f"🗑️ Cleared {count} CSV users")
        return count
    
    def _clear_csv_campuses(self, db: Session) -> int:
        """Clear only CSV-loaded campuses"""
        count = db.query(Campus).filter(Campus.data_source == 'csv').count()
        db.query(Campus).filter(Campus.data_source == 'csv').delete()
        logger.info(f"🗑️ Cleared {count} CSV campuses")
        return count
    
    def _clear_csv_roles(self, db: Session) -> int:
        """Clear only CSV-loaded roles"""
        count = db.query(Role).filter(Role.data_source == 'csv').count()
        db.query(Role).filter(Role.data_source == 'csv').delete()
        logger.info(f"🗑️ Cleared {count} CSV roles")
        return count


def load_csv_data_on_startup_enhanced(force_reload: bool = None):
    """
    Load CSV data when the application starts up (enhanced version)
    """
    try:
        from app.core.config import settings
        
        if not settings.LOAD_CSV_DATA:
            logger.info("CSV data loading is disabled")
            return
        
        data_dir = settings.CSV_DATA_DIR
        if not os.path.exists(data_dir):
            logger.warning(f"CSV data directory not found: {data_dir}")
            return
        
        if force_reload is None:
            force_reload = settings.FORCE_RELOAD_CSV
        
        loader = EnhancedCSVDataLoader(data_dir)
        db = next(get_db())
        
        try:
            results = loader.load_all_data(db, force_reload)
            logger.info(f"Successfully loaded CSV data: {results}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error loading CSV data on startup: {e}")


def clear_csv_data_only():
    """
    Clear only CSV-loaded data, preserving user-entered data
    """
    try:
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            loader = EnhancedCSVDataLoader()
            results = loader.clear_csv_data_only(db)
            print(f"✅ Cleared CSV data: {results}")
            return results
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error clearing CSV data: {e}")
        raise


def get_csv_data_summary():
    """
    Get summary of CSV-loaded data only
    """
    try:
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            loader = EnhancedCSVDataLoader()
            results = loader.get_csv_data_summary(db)
            return results
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error getting CSV data summary: {e}")
        return {}
