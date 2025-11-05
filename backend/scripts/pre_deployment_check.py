#!/usr/bin/env python3
"""
Pre-deployment database schema check
This script should be run before deploying to catch schema issues early.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.schema_validator import validate_schema

def main():
    """Run pre-deployment checks"""
    print("🔍 Pre-Deployment Database Schema Check")
    print("=" * 60)
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("   Set it before running this script")
        sys.exit(1)
    
    # Validate schema
    is_valid, issues = validate_schema(database_url)
    
    if is_valid:
        print("\n✅ Pre-deployment check PASSED!")
        print("   Database schema matches SQLAlchemy models")
        sys.exit(0)
    else:
        print(f"\n❌ Pre-deployment check FAILED!")
        print(f"   Found {len(issues)} schema issues")
        print("\n   Please fix these issues before deploying:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n   You can fix these by:")
        print("   1. Running migrations: alembic upgrade head")
        print("   2. Running the schema fix script in start.sh")
        print("   3. Creating a new migration for missing tables/columns")
        sys.exit(1)

if __name__ == "__main__":
    main()

