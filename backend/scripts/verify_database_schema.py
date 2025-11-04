#!/usr/bin/env python3
"""
Comprehensive database schema verification script
Checks all model columns against the actual database schema
"""

import os
import sys
import psycopg2
from typing import Dict, List, Set

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define expected columns for each table based on models
# Format: {table_name: {column_name: {'type': 'VARCHAR(200)', 'nullable': True}}}
EXPECTED_COLUMNS = {
    'courses': {
        'id': {'type': 'INTEGER', 'nullable': False},
        'title': {'type': 'VARCHAR(200)', 'nullable': False},
        'description': {'type': 'TEXT', 'nullable': True},
        'duration_weeks': {'type': 'INTEGER', 'nullable': True},
        'prerequisites': {'type': 'JSON', 'nullable': True},
        'planning_center_event_id': {'type': 'VARCHAR(50)', 'nullable': True},
        'planning_center_event_name': {'type': 'VARCHAR(200)', 'nullable': True},
        'event_start_date': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'event_end_date': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'max_capacity': {'type': 'INTEGER', 'nullable': True},
        'current_registrations': {'type': 'INTEGER', 'nullable': False},
        'is_active': {'type': 'BOOLEAN', 'nullable': False},
        'content_unlock_mode': {'type': 'VARCHAR(20)', 'nullable': False},
        'max_file_size_mb': {'type': 'INTEGER', 'nullable': False},
        'data_source': {'type': 'VARCHAR(20)', 'nullable': True},
        'csv_loaded_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'updated_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'created_by': {'type': 'INTEGER', 'nullable': True},
        'updated_by': {'type': 'INTEGER', 'nullable': True},
    },
    'users': {
        'id': {'type': 'INTEGER', 'nullable': False},
        'username': {'type': 'VARCHAR(50)', 'nullable': True},
        'email': {'type': 'VARCHAR(255)', 'nullable': False},
        'full_name': {'type': 'VARCHAR(200)', 'nullable': False},
        'hashed_password': {'type': 'VARCHAR(255)', 'nullable': False},
        'role': {'type': 'VARCHAR(20)', 'nullable': False},
        'is_active': {'type': 'BOOLEAN', 'nullable': False},
        'data_source': {'type': 'VARCHAR(20)', 'nullable': True},
        'csv_loaded_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'updated_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'last_login': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
    },
    'people': {
        'id': {'type': 'INTEGER', 'nullable': False},
        'planning_center_id': {'type': 'VARCHAR(50)', 'nullable': False},
        'first_name': {'type': 'VARCHAR(100)', 'nullable': False},
        'last_name': {'type': 'VARCHAR(100)', 'nullable': False},
        'email': {'type': 'VARCHAR(255)', 'nullable': True},
        'phone': {'type': 'VARCHAR(20)', 'nullable': True},
        'date_of_birth': {'type': 'DATE', 'nullable': True},
        'gender': {'type': 'VARCHAR(10)', 'nullable': True},
        'address1': {'type': 'VARCHAR(255)', 'nullable': True},
        'address2': {'type': 'VARCHAR(255)', 'nullable': True},
        'city': {'type': 'VARCHAR(100)', 'nullable': True},
        'state': {'type': 'VARCHAR(50)', 'nullable': True},
        'zip': {'type': 'VARCHAR(20)', 'nullable': True},
        'household_id': {'type': 'VARCHAR(50)', 'nullable': True},
        'household_name': {'type': 'VARCHAR(255)', 'nullable': True},
        'status': {'type': 'VARCHAR(50)', 'nullable': True},
        'join_date': {'type': 'DATE', 'nullable': True},
        'last_synced_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'is_active': {'type': 'BOOLEAN', 'nullable': False},
        'data_source': {'type': 'VARCHAR(20)', 'nullable': True},
        'csv_loaded_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'updated_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'created_by': {'type': 'INTEGER', 'nullable': True},
        'updated_by': {'type': 'INTEGER', 'nullable': True},
    },
    'course_enrollment': {
        'id': {'type': 'INTEGER', 'nullable': False},
        'people_id': {'type': 'INTEGER', 'nullable': False},
        'course_id': {'type': 'INTEGER', 'nullable': False},
        'planning_center_registration_id': {'type': 'VARCHAR(50)', 'nullable': True},
        'enrollment_date': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'status': {'type': 'VARCHAR(20)', 'nullable': False},
        'progress_percentage': {'type': 'DOUBLE PRECISION', 'nullable': False},
        'completion_date': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'notes': {'type': 'TEXT', 'nullable': True},
        'dependency_override': {'type': 'BOOLEAN', 'nullable': False},
        'dependency_override_by': {'type': 'INTEGER', 'nullable': True},
        'planning_center_synced': {'type': 'BOOLEAN', 'nullable': False},
        'registration_status': {'type': 'VARCHAR(20)', 'nullable': True},
        'registration_notes': {'type': 'TEXT', 'nullable': True},
        'data_source': {'type': 'VARCHAR(20)', 'nullable': True},
        'csv_loaded_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'updated_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'created_by': {'type': 'INTEGER', 'nullable': True},
        'updated_by': {'type': 'INTEGER', 'nullable': True},
    },
    'campus': {
        'id': {'type': 'INTEGER', 'nullable': False},
        'name': {'type': 'VARCHAR(200)', 'nullable': False},
        'address': {'type': 'TEXT', 'nullable': True},
        'phone': {'type': 'VARCHAR(20)', 'nullable': True},
        'email': {'type': 'VARCHAR(255)', 'nullable': True},
        'planning_center_location_id': {'type': 'VARCHAR(50)', 'nullable': True},
        'is_active': {'type': 'BOOLEAN', 'nullable': False},
        'data_source': {'type': 'VARCHAR(20)', 'nullable': True},
        'csv_loaded_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'updated_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'created_by': {'type': 'INTEGER', 'nullable': True},
        'updated_by': {'type': 'INTEGER', 'nullable': True},
    },
    'role': {
        'id': {'type': 'INTEGER', 'nullable': False},
        'name': {'type': 'VARCHAR(50)', 'nullable': False},
        'description': {'type': 'TEXT', 'nullable': True},
        'permissions': {'type': 'JSON', 'nullable': True},
        'is_active': {'type': 'BOOLEAN', 'nullable': False},
        'data_source': {'type': 'VARCHAR(20)', 'nullable': True},
        'csv_loaded_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'updated_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'created_by': {'type': 'INTEGER', 'nullable': True},
        'updated_by': {'type': 'INTEGER', 'nullable': True},
    },
    'course_modules': {
        'id': {'type': 'INTEGER', 'nullable': False},
        'course_id': {'type': 'INTEGER', 'nullable': False},
        'title': {'type': 'VARCHAR(200)', 'nullable': False},
        'description': {'type': 'TEXT', 'nullable': True},
        'order_index': {'type': 'INTEGER', 'nullable': False},
        'is_active': {'type': 'BOOLEAN', 'nullable': False},
        'data_source': {'type': 'VARCHAR(20)', 'nullable': True},
        'csv_loaded_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': False},
        'updated_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': False},
        'created_by': {'type': 'INTEGER', 'nullable': True},
        'updated_by': {'type': 'INTEGER', 'nullable': True},
    },
    'course_content': {
        'id': {'type': 'INTEGER', 'nullable': False},
        'course_id': {'type': 'INTEGER', 'nullable': False},
        'module_id': {'type': 'INTEGER', 'nullable': True},
        'title': {'type': 'VARCHAR(200)', 'nullable': False},
        'description': {'type': 'TEXT', 'nullable': True},
        'content_type': {'type': 'VARCHAR', 'nullable': False},
        'storage_type': {'type': 'VARCHAR', 'nullable': False},
        'file_name': {'type': 'VARCHAR(255)', 'nullable': True},
        'file_size': {'type': 'INTEGER', 'nullable': True},
        'file_path': {'type': 'VARCHAR(500)', 'nullable': True},
        'mime_type': {'type': 'VARCHAR(100)', 'nullable': True},
        'external_url': {'type': 'VARCHAR(1000)', 'nullable': True},
        'embedded_content': {'type': 'TEXT', 'nullable': True},
        'duration': {'type': 'INTEGER', 'nullable': True},
        'download_count': {'type': 'INTEGER', 'nullable': False},
        'view_count': {'type': 'INTEGER', 'nullable': False},
        'order_index': {'type': 'INTEGER', 'nullable': False},
        'is_active': {'type': 'BOOLEAN', 'nullable': False},
        'data_source': {'type': 'VARCHAR(20)', 'nullable': True},
        'csv_loaded_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': True},
        'created_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': False},
        'updated_at': {'type': 'TIMESTAMP WITH TIME ZONE', 'nullable': False},
        'created_by': {'type': 'INTEGER', 'nullable': True},
        'updated_by': {'type': 'INTEGER', 'nullable': True},
    },
}


def get_database_columns(conn, table_name: str) -> Set[str]:
    """Get all columns for a table from the database"""
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
    """, (table_name,))
    columns = {row[0] for row in cur.fetchall()}
    cur.close()
    return columns


def verify_table_schema(conn, table_name: str, expected_columns: Dict) -> List[str]:
    """Verify table schema and return list of missing columns"""
    if table_name not in EXPECTED_COLUMNS:
        return []
    
    actual_columns = get_database_columns(conn, table_name)
    expected = set(EXPECTED_COLUMNS[table_name].keys())
    missing = expected - actual_columns
    extra = actual_columns - expected
    
    issues = []
    if missing:
        issues.append(f"  Missing columns: {', '.join(sorted(missing))}")
    if extra:
        issues.append(f"  Extra columns (not in model): {', '.join(sorted(extra))}")
    
    return issues


def main():
    """Main verification function"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable is not set")
        sys.exit(1)
    
    # Parse database URL
    parts = database_url.replace('postgresql://', '').split('/')
    userpass = parts[0].split('@')[0]
    user, password = userpass.split(':')
    hostport = parts[0].split('@')[1]
    host, port = hostport.split(':')
    dbname = parts[1]
    
    print("🔍 Comprehensive Database Schema Verification")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname
        )
        
        all_issues = {}
        
        for table_name in EXPECTED_COLUMNS.keys():
            print(f"\n📋 Checking table: {table_name}")
            issues = verify_table_schema(conn, table_name, EXPECTED_COLUMNS[table_name])
            if issues:
                all_issues[table_name] = issues
                for issue in issues:
                    print(f"  ❌ {issue}")
            else:
                print(f"  ✅ All columns present")
        
        conn.close()
        
        if all_issues:
            print("\n" + "=" * 60)
            print("❌ SCHEMA VERIFICATION FAILED")
            print("=" * 60)
            print("\nMissing columns found:")
            for table, issues in all_issues.items():
                print(f"\n{table}:")
                for issue in issues:
                    print(f"  {issue}")
            return False
        else:
            print("\n" + "=" * 60)
            print("✅ SCHEMA VERIFICATION PASSED")
            print("=" * 60)
            print("All expected columns are present in the database.")
            return True
            
    except Exception as e:
        print(f"❌ Error verifying schema: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

