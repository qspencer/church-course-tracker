#!/usr/bin/env python3
"""
Query the database directly to confirm all columns exist.
This script can be run in the ECS container or locally with DATABASE_URL set.
"""
import os
import sys
import psycopg2
from urllib.parse import urlparse

def check_columns():
    """Check if all required columns exist in the database"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is not set")
        return 1
    
    # Parse database URL
    # postgresql://user:pass@host:port/dbname
    try:
        parts = database_url.replace('postgresql://', '').split('/')
        userpass = parts[0].split('@')[0]
        user, password = userpass.split(':')
        hostport = parts[0].split('@')[1]
        host, port = hostport.split(':')
        dbname = parts[1]
    except Exception as e:
        print(f"❌ ERROR: Could not parse DATABASE_URL: {e}")
        return 1
    
    print(f"🔍 Connecting to database: {host}:{port}/{dbname}")
    print("")
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname
        )
        cur = conn.cursor()
        
        # Columns to check
        columns_to_check = [
            ('people', 'campus_id'),
            ('people', 'campus_assigned_date'),
            ('courses', 'planning_center_event_template_id'),
            ('course_enrollment', 'course_instance_id'),
            ('course_enrollment', 'assigned_teacher_id'),
        ]
        
        print("=" * 70)
        print("COLUMN EXISTENCE CHECK")
        print("=" * 70)
        print()
        
        all_exist = True
        for table_name, column_name in columns_to_check:
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name = %s
            """, (table_name, column_name))
            
            result = cur.fetchone()
            if result:
                col_name, data_type, is_nullable = result
                status = "✅ EXISTS"
                print(f"{status:12} {table_name:25}.{column_name:35} ({data_type}, nullable: {is_nullable})")
            else:
                status = "❌ MISSING"
                print(f"{status:12} {table_name:25}.{column_name:35}")
                all_exist = False
        
        print()
        print("=" * 70)
        
        # Also check for indexes on these columns
        print()
        print("INDEX CHECK")
        print("=" * 70)
        print()
        
        indexes_to_check = [
            ('people', 'campus_id'),
            ('courses', 'planning_center_event_template_id'),
            ('course_enrollment', 'course_instance_id'),
            ('course_enrollment', 'assigned_teacher_id'),
        ]
        
        for table_name, column_name in indexes_to_check:
            cur.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes 
                WHERE tablename = %s AND indexdef LIKE %s
                LIMIT 1
            """, (table_name, f'%{column_name}%'))
            
            result = cur.fetchone()
            if result:
                index_name, index_def = result
                print(f"✅ INDEX     {table_name:25}.{column_name:35} ({index_name})")
            else:
                print(f"⚠️  NO INDEX  {table_name:25}.{column_name:35}")
        
        # Check foreign keys
        print()
        print("=" * 70)
        print("FOREIGN KEY CHECK")
        print("=" * 70)
        print()
        
        fks_to_check = [
            ('people', 'campus_id', 'campus', 'id'),
            ('course_enrollment', 'course_instance_id', 'course_instances', 'id'),
            ('course_enrollment', 'assigned_teacher_id', 'course_instance_teachers', 'id'),
        ]
        
        for table_name, column_name, ref_table, ref_column in fks_to_check:
            cur.execute("""
                SELECT 
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = %s
                    AND kcu.column_name = %s
            """, (table_name, column_name))
            
            result = cur.fetchone()
            if result:
                constraint_name, _, _, ref_tbl, ref_col = result
                print(f"✅ FK        {table_name:25}.{column_name:35} -> {ref_tbl}.{ref_col}")
            else:
                print(f"⚠️  NO FK     {table_name:25}.{column_name:35} -> {ref_table}.{ref_column}")
        
        print()
        print("=" * 70)
        if all_exist:
            print("✅ ALL COLUMNS EXIST!")
        else:
            print("❌ SOME COLUMNS ARE MISSING!")
        print("=" * 70)
        
        cur.close()
        conn.close()
        
        return 0 if all_exist else 1
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(check_columns())
