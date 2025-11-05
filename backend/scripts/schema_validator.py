#!/usr/bin/env python3
"""
Dynamic Database Schema Validator
Reads SQLAlchemy models and compares them to the actual database schema.
This prevents schema mismatches before they cause runtime errors.
"""

import os
import sys
import psycopg2
from typing import Dict, List, Set, Optional, Tuple
from sqlalchemy import inspect, MetaData, Table
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import CreateTable

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all models to register them with Base.metadata
from app.core.database import Base
from app.models import *  # This imports all models

def get_model_tables() -> Dict[str, Table]:
    """Get all tables from SQLAlchemy models"""
    return {table.name: table for table in Base.metadata.tables.values()}

def get_database_tables(conn) -> Set[str]:
    """Get all tables from the database"""
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    return {row[0] for row in cur.fetchall()}

def get_database_columns(conn, table_name: str) -> Dict[str, Dict]:
    """Get all columns for a table from the database"""
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = %s AND table_schema = 'public'
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns = {}
    for row in cur.fetchall():
        col_name, data_type, max_length, is_nullable, default = row
        columns[col_name] = {
            'type': data_type,
            'max_length': max_length,
            'nullable': is_nullable == 'YES',
            'default': default
        }
    return columns

def compare_table_schema(model_table: Table, db_columns: Dict, table_name: str) -> List[Tuple[str, str]]:
    """Compare model table to database columns and return issues"""
    issues = []
    model_columns = {col.name: col for col in model_table.columns}
    
    # Check for missing columns in database
    for col_name, col in model_columns.items():
        if col_name not in db_columns:
            issues.append(('missing_column', f"{table_name}.{col_name}"))
    
    # Check for nullable mismatches
    for col_name, col in model_columns.items():
        if col_name in db_columns:
            db_nullable = db_columns[col_name]['nullable']
            model_nullable = col.nullable
            if db_nullable != model_nullable:
                issues.append(('nullable_mismatch', 
                    f"{table_name}.{col_name}: model={model_nullable}, db={db_nullable}"))
    
    return issues

def validate_schema(database_url: str) -> Tuple[bool, List[str]]:
    """Validate database schema against SQLAlchemy models"""
    errors = []
    warnings = []
    
    try:
        # Parse database URL
        if database_url.startswith('postgresql://'):
            parts = database_url.replace('postgresql://', '').split('/')
            userpass = parts[0].split('@')[0]
            user, password = userpass.split(':')
            hostport = parts[0].split('@')[1]
            host, port = hostport.split(':')
            dbname = parts[1]
        else:
            raise ValueError(f"Unsupported database URL format: {database_url}")
        
        # Connect to database
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=dbname,
            user=user,
            password=password
        )
        
        # Get tables from models and database
        model_tables = get_model_tables()
        db_tables = get_database_tables(conn)
        
        print(f"\n📊 Schema Validation Report")
        print("=" * 60)
        print(f"Model tables: {len(model_tables)}")
        print(f"Database tables: {len(db_tables)}")
        
        # Check for missing tables
        missing_tables = set(model_tables.keys()) - db_tables
        if missing_tables:
            errors.append(f"Missing tables: {', '.join(missing_tables)}")
        
        # Check each table
        for table_name, model_table in model_tables.items():
            if table_name not in db_tables:
                continue  # Already reported as missing
            
            db_columns = get_database_columns(conn, table_name)
            issues = compare_table_schema(model_table, db_columns, table_name)
            
            for issue_type, issue_msg in issues:
                if issue_type == 'missing_column':
                    errors.append(f"Missing column: {issue_msg}")
                elif issue_type == 'nullable_mismatch':
                    warnings.append(f"Nullable mismatch: {issue_msg}")
        
        conn.close()
        
        # Print summary
        print(f"\n✅ Errors: {len(errors)}")
        print(f"⚠️  Warnings: {len(warnings)}")
        
        if errors:
            print("\n❌ Schema Errors:")
            for error in errors:
                print(f"   - {error}")
        
        if warnings:
            print("\n⚠️  Schema Warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        return len(errors) == 0, errors + warnings
        
    except Exception as e:
        error_msg = f"Schema validation failed: {str(e)}"
        print(f"❌ {error_msg}")
        return False, [error_msg]

if __name__ == "__main__":
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    is_valid, issues = validate_schema(database_url)
    
    if is_valid:
        print("\n✅ Schema validation passed!")
        sys.exit(0)
    else:
        print(f"\n❌ Schema validation failed with {len(issues)} issues")
        sys.exit(1)

