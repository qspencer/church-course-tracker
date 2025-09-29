"""
CSV Data Loader for Church Course Tracker

This module provides functionality to load test data from CSV files
into the database when the application starts up.
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


class CSVDataLoader:
    """Loads test data from CSV files into the database"""
    
    def __init__(self, data_dir: str = "data/csv"):
        self.data_dir = data_dir
        self.loaded_data = {
            'users': [],
            'courses': [],
            'modules': [],
            'content': [],
            'people': [],
            'campuses': [],
            'roles': [],
            'enrollments': []
        }
    
    def load_all_data(self, db: Session, force_reload: bool = False) -> Dict[str, int]:
        """
        Load all CSV data into the database
        
        Args:
            db: Database session
            force_reload: If True, reload data even if it already exists
            
        Returns:
            Dictionary with counts of loaded records by type
        """
        results = {}
        
        try:
            # Load data in dependency order
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
    
    def _load_campuses(self, db: Session, force_reload: bool = False) -> int:
        """Load campuses from CSV"""
        csv_file = os.path.join(self.data_dir, "campuses.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(Campus).count() > 0:
            logger.info("Campuses already exist, skipping load")
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
                    is_active=row.get('is_active', 'true').lower() == 'true'
                )
                db.add(campus)
                count += 1
        
        return count
    
    def _load_roles(self, db: Session, force_reload: bool = False) -> int:
        """Load roles from CSV"""
        csv_file = os.path.join(self.data_dir, "roles.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(Role).count() > 0:
            logger.info("Roles already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                role = Role(
                    name=row['name'],
                    description=row.get('description', ''),
                    permissions=row.get('permissions', ''),
                    is_active=row.get('is_active', 'true').lower() == 'true'
                )
                db.add(role)
                count += 1
        
        return count
    
    def _load_users(self, db: Session, force_reload: bool = False) -> int:
        """Load users from CSV"""
        csv_file = os.path.join(self.data_dir, "users.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(User).count() > 0:
            logger.info("Users already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Get role by name
                role = db.query(Role).filter(Role.name == row['role']).first()
                if not role:
                    logger.warning(f"Role not found: {row['role']}")
                    continue
                
                user = User(
                    username=row['username'],
                    email=row['email'],
                    hashed_password=get_password_hash(row['password']),
                    full_name=row.get('full_name', ''),
                    role=row['role'],
                    is_active=row.get('is_active', 'true').lower() == 'true',
                    created_at=datetime.now(timezone.utc)
                )
                db.add(user)
                count += 1
        
        return count
    
    def _load_people(self, db: Session, force_reload: bool = False) -> int:
        """Load people from CSV"""
        csv_file = os.path.join(self.data_dir, "people.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(People).count() > 0:
            logger.info("People already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Get campus by name
                campus = db.query(Campus).filter(Campus.name == row.get('campus', '')).first()
                
                person = People(
                    planning_center_id=f"csv_{row['first_name'].lower()}_{row['last_name'].lower()}",
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    email=row.get('email', ''),
                    phone=row.get('phone', ''),
                    address1=row.get('address', ''),
                    city=row.get('city', ''),
                    state=row.get('state', ''),
                    zip=row.get('zip_code', ''),
                    is_active=row.get('is_active', 'true').lower() == 'true'
                )
                db.add(person)
                count += 1
        
        return count
    
    def _load_courses(self, db: Session, force_reload: bool = False) -> int:
        """Load courses from CSV"""
        csv_file = os.path.join(self.data_dir, "courses.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(Course).count() > 0:
            logger.info("Courses already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                course = Course(
                    title=row['title'],
                    description=row.get('description', ''),
                    duration_weeks=int(row.get('duration_weeks', 4)),
                    max_capacity=int(row.get('max_capacity', 50)),
                    is_active=row.get('is_active', 'true').lower() == 'true',
                    created_at=datetime.now(timezone.utc)
                )
                db.add(course)
                count += 1
        
        return count
    
    def _load_modules(self, db: Session, force_reload: bool = False) -> int:
        """Load course modules from CSV"""
        csv_file = os.path.join(self.data_dir, "modules.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(CourseModule).count() > 0:
            logger.info("Modules already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Get course by title
                course = db.query(Course).filter(Course.title == row['course_title']).first()
                if not course:
                    logger.warning(f"Course not found: {row['course_title']}")
                    continue
                
                module = CourseModule(
                    course_id=course.id,
                    title=row['title'],
                    description=row.get('description', ''),
                    order_index=int(row.get('order_index', 1)),
                    is_active=row.get('is_active', 'true').lower() == 'true',
                    created_at=datetime.now(timezone.utc)
                )
                db.add(module)
                count += 1
        
        return count
    
    def _load_content(self, db: Session, force_reload: bool = False) -> int:
        """Load course content from CSV"""
        csv_file = os.path.join(self.data_dir, "content.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(CourseContent).count() > 0:
            logger.info("Content already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Get course and module
                course = db.query(Course).filter(Course.title == row['course_title']).first()
                module = None
                if row.get('module_title'):
                    module = db.query(CourseModule).filter(
                        CourseModule.title == row['module_title'],
                        CourseModule.course_id == course.id if course else None
                    ).first()
                
                if not course:
                    logger.warning(f"Course not found: {row['course_title']}")
                    continue
                
                content = CourseContent(
                    course_id=course.id,
                    module_id=module.id if module else None,
                    title=row['title'],
                    description=row.get('description', ''),
                    content_type=ContentType(row.get('content_type', 'document')),
                    storage_type=StorageType(row.get('storage_type', 'database')),
                    order_index=int(row.get('order_index', 1)),
                    is_active=row.get('is_active', 'true').lower() == 'true',
                    created_at=datetime.now(timezone.utc)
                )
                db.add(content)
                count += 1
        
        return count
    
    def _load_enrollments(self, db: Session, force_reload: bool = False) -> int:
        """Load course enrollments from CSV"""
        csv_file = os.path.join(self.data_dir, "enrollments.csv")
        if not os.path.exists(csv_file):
            logger.warning(f"CSV file not found: {csv_file}")
            return 0
        
        if not force_reload and db.query(CourseEnrollment).count() > 0:
            logger.info("Enrollments already exist, skipping load")
            return 0
        
        count = 0
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Get course and person
                course = db.query(Course).filter(Course.title == row['course_title']).first()
                person = db.query(People).filter(
                    People.first_name == row['first_name'],
                    People.last_name == row['last_name']
                ).first()
                
                if not course or not person:
                    logger.warning(f"Course or person not found: {row['course_title']}, {row['first_name']} {row['last_name']}")
                    continue
                
                enrollment = CourseEnrollment(
                    course_id=course.id,
                    people_id=person.id,
                    enrollment_date=datetime.now(timezone.utc),
                    status=row.get('status', 'enrolled'),
                    completion_date=None
                )
                db.add(enrollment)
                count += 1
        
        return count


def load_csv_data_on_startup(force_reload: bool = None):
    """
    Load CSV data when the application starts up
    
    Args:
        force_reload: If True, reload data even if it already exists
    """
    try:
        from app.core.config import settings
        
        # Check if CSV loading is enabled
        if not settings.LOAD_CSV_DATA:
            logger.info("CSV data loading is disabled")
            return
        
        data_dir = settings.CSV_DATA_DIR
        if not os.path.exists(data_dir):
            logger.warning(f"CSV data directory not found: {data_dir}")
            return
        
        # Use force_reload from settings if not provided
        if force_reload is None:
            force_reload = settings.FORCE_RELOAD_CSV
        
        # Load data
        loader = CSVDataLoader(data_dir)
        db = next(get_db())
        
        try:
            results = loader.load_all_data(db, force_reload)
            logger.info(f"CSV data loading completed: {results}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error loading CSV data on startup: {e}")


def create_sample_csv_files(data_dir: str = "data/csv"):
    """
    Create sample CSV files with test data
    
    Args:
        data_dir: Directory to create CSV files in
    """
    os.makedirs(data_dir, exist_ok=True)
    
    # Create campuses CSV
    with open(os.path.join(data_dir, "campuses.csv"), 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['name', 'address', 'phone', 'email', 'is_active'])
        writer.writerow(['Main Campus', '123 Church St, Anytown, CA 12345', '555-1234', 'main@church.com', 'true'])
        writer.writerow(['North Campus', '456 North Ave, Anytown, CA 12346', '555-5678', 'north@church.com', 'true'])
        writer.writerow(['South Campus', '789 South Blvd, Anytown, CA 12347', '555-9012', 'south@church.com', 'true'])
    
    # Create roles CSV
    with open(os.path.join(data_dir, "roles.csv"), 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['name', 'description', 'permissions', 'is_active'])
        writer.writerow(['admin', 'System Administrator', 'all', 'true'])
        writer.writerow(['staff', 'Church Staff', 'manage_courses,manage_users', 'true'])
        writer.writerow(['viewer', 'Course Viewer', 'view_courses', 'true'])
    
    # Create users CSV
    with open(os.path.join(data_dir, "users.csv"), 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['username', 'email', 'password', 'full_name', 'role', 'is_active'])
        writer.writerow(['admin', 'admin@church.com', 'admin123', 'Administrator', 'admin', 'true'])
        writer.writerow(['staff', 'staff@church.com', 'staff123', 'Church Staff', 'staff', 'true'])
        writer.writerow(['viewer', 'viewer@church.com', 'viewer123', 'Course Viewer', 'viewer', 'true'])
        writer.writerow(['pastor', 'pastor@church.com', 'pastor123', 'Pastor John', 'admin', 'true'])
    
    # Create people CSV
    with open(os.path.join(data_dir, "people.csv"), 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'state', 'zip_code', 'campus', 'is_active'])
        writer.writerow(['John', 'Doe', 'john@example.com', '555-0001', '123 Main St', 'Anytown', 'CA', '12345', 'Main Campus', 'true'])
        writer.writerow(['Jane', 'Smith', 'jane@example.com', '555-0002', '456 Oak Ave', 'Anytown', 'CA', '12345', 'Main Campus', 'true'])
        writer.writerow(['Bob', 'Johnson', 'bob@example.com', '555-0003', '789 Pine St', 'Anytown', 'CA', '12345', 'North Campus', 'true'])
        writer.writerow(['Alice', 'Brown', 'alice@example.com', '555-0004', '321 Elm St', 'Anytown', 'CA', '12345', 'South Campus', 'true'])
        writer.writerow(['Charlie', 'Wilson', 'charlie@example.com', '555-0005', '654 Maple Ave', 'Anytown', 'CA', '12345', 'Main Campus', 'true'])
    
    # Create courses CSV
    with open(os.path.join(data_dir, "courses.csv"), 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['title', 'description', 'duration_weeks', 'max_capacity', 'is_active'])
        writer.writerow(['Introduction to Faith', 'A foundational course on Christian faith and beliefs', '6', '30', 'true'])
        writer.writerow(['Bible Study Methods', 'Learn how to study and interpret the Bible effectively', '8', '25', 'true'])
        writer.writerow(['Church History', 'Explore the history of Christianity and the church', '10', '20', 'true'])
        writer.writerow(['Christian Ethics', 'Understanding moral principles from a Christian perspective', '6', '25', 'true'])
        writer.writerow(['Worship and Music', 'The role of music and worship in Christian life', '4', '15', 'true'])
    
    # Create modules CSV
    with open(os.path.join(data_dir, "modules.csv"), 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['course_title', 'title', 'description', 'order_index', 'is_active'])
        writer.writerow(['Introduction to Faith', 'What is Faith?', 'Understanding the concept of faith in Christianity', '1', 'true'])
        writer.writerow(['Introduction to Faith', 'The Trinity', 'Exploring the Father, Son, and Holy Spirit', '2', 'true'])
        writer.writerow(['Introduction to Faith', 'Salvation', 'Understanding salvation and grace', '3', 'true'])
        writer.writerow(['Bible Study Methods', 'Reading the Bible', 'How to read and understand biblical texts', '1', 'true'])
        writer.writerow(['Bible Study Methods', 'Interpretation', 'Methods for interpreting scripture', '2', 'true'])
        writer.writerow(['Bible Study Methods', 'Application', 'Applying biblical teachings to daily life', '3', 'true'])
    
    # Create content CSV
    with open(os.path.join(data_dir, "content.csv"), 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['course_title', 'module_title', 'title', 'description', 'content_type', 'storage_type', 'order_index', 'is_active'])
        writer.writerow(['Introduction to Faith', 'What is Faith?', 'Faith Definition Video', 'A video explaining the definition of faith', 'video', 'database', '1', 'true'])
        writer.writerow(['Introduction to Faith', 'What is Faith?', 'Faith Study Guide', 'A comprehensive study guide on faith', 'document', 'database', '2', 'true'])
        writer.writerow(['Introduction to Faith', 'The Trinity', 'Trinity Explained', 'Understanding the concept of the Trinity', 'document', 'database', '1', 'true'])
        writer.writerow(['Introduction to Faith', 'The Trinity', 'Trinity Audio Lesson', 'An audio lesson on the Trinity', 'audio', 'database', '2', 'true'])
        writer.writerow(['Bible Study Methods', 'Reading the Bible', 'Bible Reading Guide', 'A guide to effective Bible reading', 'document', 'database', '1', 'true'])
        writer.writerow(['Bible Study Methods', 'Reading the Bible', 'Bible Study Video', 'Video tutorial on Bible study methods', 'video', 'database', '2', 'true'])
    
    # Create enrollments CSV
    with open(os.path.join(data_dir, "enrollments.csv"), 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['course_title', 'first_name', 'last_name', 'status', 'is_active'])
        writer.writerow(['Introduction to Faith', 'John', 'Doe', 'enrolled', 'true'])
        writer.writerow(['Introduction to Faith', 'Jane', 'Smith', 'enrolled', 'true'])
        writer.writerow(['Bible Study Methods', 'John', 'Doe', 'enrolled', 'true'])
        writer.writerow(['Bible Study Methods', 'Bob', 'Johnson', 'enrolled', 'true'])
        writer.writerow(['Church History', 'Alice', 'Brown', 'enrolled', 'true'])
        writer.writerow(['Christian Ethics', 'Charlie', 'Wilson', 'enrolled', 'true'])
    
    logger.info(f"Sample CSV files created in {data_dir}")


if __name__ == "__main__":
    # Create sample CSV files
    create_sample_csv_files()
    print("Sample CSV files created successfully!")
