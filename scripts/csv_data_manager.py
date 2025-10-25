#!/usr/bin/env python3
"""
CSV Data Manager for Church Course Tracker

This script provides utilities to manage CSV test data for the application.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.csv_loader import CSVDataLoader, create_sample_csv_files, load_csv_data_on_startup
from app.core.enhanced_csv_loader import EnhancedCSVDataLoader, clear_csv_data_only, get_csv_data_summary
from app.core.database import get_db
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_data():
    """Create sample CSV files with test data"""
    data_dir = settings.CSV_DATA_DIR
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"Creating sample CSV files in {data_dir}...")
    create_sample_csv_files(data_dir)
    print("✅ Sample CSV files created successfully!")
    
    # List created files
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    print(f"\nCreated {len(csv_files)} CSV files:")
    for file in sorted(csv_files):
        print(f"  - {file}")


def load_data_to_database(force_reload=False):
    """Load CSV data into the database"""
    print("Loading CSV data into database...")
    
    try:
        loader = CSVDataLoader(settings.CSV_DATA_DIR)
        db = next(get_db())
        
        try:
            results = loader.load_all_data(db, force_reload)
            print("✅ CSV data loaded successfully!")
            print("\nLoaded records:")
            for data_type, count in results.items():
                print(f"  - {data_type}: {count} records")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error loading CSV data: {e}")
        return False
    
    return True


def clear_database():
    """Clear all data from the database (WARNING: This will delete all data!)"""
    print("⚠️  WARNING: This will delete ALL data from the database!")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    try:
        from app.models.user import User
        from app.models.role import Role
        from app.models.campus import Campus
        from app.models.member import People
        from app.models.course import Course
        from app.models.course_content import CourseModule, CourseContent
        from app.models.enrollment import CourseEnrollment
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            # Delete in reverse dependency order
            db.query(CourseEnrollment).delete()
            db.query(CourseContent).delete()
            db.query(CourseModule).delete()
            db.query(Course).delete()
            db.query(People).delete()
            db.query(User).delete()
            db.query(Campus).delete()
            db.query(Role).delete()
            
            db.commit()
            print("✅ Database cleared successfully!")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error clearing database: {e}")


def show_data_summary():
    """Show summary of data in the database"""
    try:
        from app.models.user import User
        from app.models.role import Role
        from app.models.campus import Campus
        from app.models.member import People
        from app.models.course import Course
        from app.models.course_content import CourseModule, CourseContent
        from app.models.enrollment import CourseEnrollment
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            print("Database Data Summary:")
            print("=" * 50)
            
            # Count records
            counts = {
                'Users': db.query(User).count(),
                'Roles': db.query(Role).count(),
                'Campuses': db.query(Campus).count(),
                'People': db.query(People).count(),
                'Courses': db.query(Course).count(),
                'Modules': db.query(CourseModule).count(),
                'Content': db.query(CourseContent).count(),
                'Enrollments': db.query(CourseEnrollment).count()
            }
            
            for data_type, count in counts.items():
                print(f"  {data_type}: {count} records")
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error getting data summary: {e}")


def show_csv_data_summary():
    """Show summary of CSV-loaded data only"""
    try:
        results = get_csv_data_summary()
        print("\n📊 CSV Data Summary (CSV-loaded data only):")
        print("=" * 50)
        print(f"  CSV Users: {results.get('csv_users', 0)}")
        print(f"  CSV Courses: {results.get('csv_courses', 0)}")
        print(f"  CSV Modules: {results.get('csv_modules', 0)}")
        print(f"  CSV Content: {results.get('csv_content', 0)}")
        print(f"  CSV People: {results.get('csv_people', 0)}")
        print(f"  CSV Campuses: {results.get('csv_campuses', 0)}")
        print(f"  CSV Roles: {results.get('csv_roles', 0)}")
        print(f"  CSV Enrollments: {results.get('csv_enrollments', 0)}")
        
        total_csv = sum(results.values())
        if total_csv > 0:
            print(f"\n✅ Total CSV-loaded records: {total_csv}")
            print("💡 Use 'clear-csv' command to remove only CSV data")
        else:
            print("\n📝 No CSV data found in database")
    except Exception as e:
        print(f"❌ Error getting CSV data summary: {e}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="CSV Data Manager for Church Course Tracker")
    parser.add_argument('command', choices=['create', 'load', 'clear', 'summary', 'full-setup', 'clear-csv', 'csv-summary'], 
                       help='Command to execute')
    parser.add_argument('--force', action='store_true', 
                       help='Force reload data even if it already exists')
    parser.add_argument('--data-dir', default=None,
                       help='CSV data directory (overrides config)')
    
    args = parser.parse_args()
    
    # Override data directory if provided
    if args.data_dir:
        settings.CSV_DATA_DIR = args.data_dir
    
    print(f"CSV Data Manager - {args.command.upper()}")
    print(f"Data directory: {settings.CSV_DATA_DIR}")
    print("-" * 50)
    
    if args.command == 'create':
        create_sample_data()
        
    elif args.command == 'load':
        load_data_to_database(force_reload=args.force)
        
    elif args.command == 'clear':
        clear_database()
        
    elif args.command == 'summary':
        show_data_summary()
        
    elif args.command == 'full-setup':
        print("Setting up complete test environment...")
        create_sample_data()
        if load_data_to_database(force_reload=args.force):
            show_data_summary()
            print("\n🎉 Full setup completed successfully!")
            print("\nYou can now start the application with CSV data loading enabled.")
            print("Set LOAD_CSV_DATA=true in your environment variables.")
    
    elif args.command == 'clear-csv':
        clear_csv_data_only()
        
    elif args.command == 'csv-summary':
        show_csv_data_summary()


if __name__ == "__main__":
    main()
