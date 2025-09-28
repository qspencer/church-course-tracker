#!/usr/bin/env python3
"""
Run database migrations inside ECS container
"""

import subprocess
import sys
import os

def run_migrations():
    """Run Alembic migrations"""
    print("🏗️  Church Course Tracker - Database Migrations")
    print("=" * 50)
    print("Running database migrations...")
    print()
    
    try:
        # Set environment variables
        os.environ['DATABASE_URL'] = 'postgresql://postgres:qicBHo2ypeSkuyrU@church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com:5432/church_course_tracker'
        
        # Run alembic upgrade
        result = subprocess.run(
            ['alembic', 'upgrade', 'head'],
            capture_output=True,
            text=True,
            cwd='/app'
        )
        
        if result.returncode == 0:
            print("✅ Database migrations completed successfully!")
            print(result.stdout)
            return True
        else:
            print("❌ Database migrations failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    if success:
        print("🎉 Database setup completed!")
        sys.exit(0)
    else:
        print("❌ Database setup failed!")
        sys.exit(1)

