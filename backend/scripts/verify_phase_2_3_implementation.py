#!/usr/bin/env python3
"""
Verification script for Phase 2 and Phase 3 implementation
Checks database schema and verifies migrations were applied
"""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Database URL - use environment variable or default to local SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/church_course_tracker.db")

def check_table_exists(engine, table_name):
    """Check if a table exists"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def check_foreign_key(engine, table_name, fk_name):
    """Check if a foreign key exists"""
    with engine.connect() as conn:
        result = conn.execute(text(f"PRAGMA foreign_key_list({table_name})"))
        fks = result.fetchall()
        # SQLite returns foreign keys as rows
        # Check if any FK matches our expected name pattern
        return any(fk_name.lower() in str(fk).lower() for fk in fks)

def main():
    """Verify Phase 2 and Phase 3 implementation"""
    print("🔍 Verifying Phase 2 and Phase 3 Implementation")
    print("=" * 60)
    print(f"Database: {DATABASE_URL}")
    print()
    
    # Create engine
    try:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False
    
    print("✅ Database connection successful")
    print()
    
    all_passed = True
    
    # Phase 2: Campus 1:M Relationship
    print("📋 Phase 2: Campus 1:M Relationship")
    print("-" * 60)
    
    # Check people table has campus_id
    if check_column_exists(engine, "people", "campus_id"):
        print("✅ people.campus_id column exists")
    else:
        print("❌ people.campus_id column NOT found")
        all_passed = False
    
    # Check people table has campus_assigned_date
    if check_column_exists(engine, "people", "campus_assigned_date"):
        print("✅ people.campus_assigned_date column exists")
    else:
        print("❌ people.campus_assigned_date column NOT found")
        all_passed = False
    
    # Check people_campus table has unassigned_date
    if check_table_exists(engine, "people_campus"):
        if check_column_exists(engine, "people_campus", "unassigned_date"):
            print("✅ people_campus.unassigned_date column exists")
        else:
            print("❌ people_campus.unassigned_date column NOT found")
            all_passed = False
    else:
        print("⚠️  people_campus table not found (may not exist yet)")
    
    print()
    
    # Phase 3: Course Offerings Architecture
    print("📋 Phase 3: Course Offerings Architecture")
    print("-" * 60)
    
    # Check course_instances table exists
    if check_table_exists(engine, "course_instances"):
        print("✅ course_instances table exists")
        
        # Check key columns
        required_columns = [
            "id", "course_id", "instance_name", "start_date", "end_date",
            "is_active", "enrollment_open"
        ]
        for col in required_columns:
            if check_column_exists(engine, "course_instances", col):
                print(f"  ✅ course_instances.{col} exists")
            else:
                print(f"  ❌ course_instances.{col} NOT found")
                all_passed = False
    else:
        print("❌ course_instances table NOT found")
        all_passed = False
    
    # Check course_instance_teachers table exists
    if check_table_exists(engine, "course_instance_teachers"):
        print("✅ course_instance_teachers table exists")
        
        # Check key columns
        required_columns = [
            "id", "course_instance_id", "people_id", "role_type",
            "assigned_date", "is_primary", "is_active"
        ]
        for col in required_columns:
            if check_column_exists(engine, "course_instance_teachers", col):
                print(f"  ✅ course_instance_teachers.{col} exists")
            else:
                print(f"  ❌ course_instance_teachers.{col} NOT found")
                all_passed = False
    else:
        print("❌ course_instance_teachers table NOT found")
        all_passed = False
    
    # Check course_enrollment has new columns
    if check_table_exists(engine, "course_enrollment"):
        print("✅ course_enrollment table exists")
        
        if check_column_exists(engine, "course_enrollment", "course_instance_id"):
            print("  ✅ course_enrollment.course_instance_id exists")
        else:
            print("  ❌ course_enrollment.course_instance_id NOT found")
            all_passed = False
        
        if check_column_exists(engine, "course_enrollment", "assigned_teacher_id"):
            print("  ✅ course_enrollment.assigned_teacher_id exists")
        else:
            print("  ❌ course_enrollment.assigned_teacher_id NOT found")
            all_passed = False
    else:
        print("⚠️  course_enrollment table not found (may have different name)")
    
    print()
    
    # Check indexes
    print("📋 Checking Indexes")
    print("-" * 60)
    
    with engine.connect() as conn:
        # Check people.campus_id index
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='people' AND sql LIKE '%campus_id%'"))
        indexes = result.fetchall()
        if indexes:
            print("✅ Index on people.campus_id exists")
        else:
            print("⚠️  Index on people.campus_id not found (may be created automatically)")
        
        # Check course_instances indexes
        result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='course_instances'"))
        indexes = result.fetchall()
        if indexes:
            print(f"✅ Found {len(indexes)} index(es) on course_instances table")
        else:
            print("⚠️  No indexes found on course_instances table")
    
    print()
    print("=" * 60)
    
    if all_passed:
        print("✅ All Phase 2 and Phase 3 schema checks PASSED!")
        print()
        print("📝 Next Steps:")
        print("  1. Run API endpoint tests")
        print("  2. Test course instance CRUD operations")
        print("  3. Verify data migration (if applicable)")
        return True
    else:
        print("❌ Some schema checks FAILED")
        print()
        print("📝 Action Required:")
        print("  1. Run database migrations: alembic upgrade head")
        print("  2. Verify migration files are correct")
        print("  3. Check database connection")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

