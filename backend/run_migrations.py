#!/usr/bin/env python3
"""
Run database migrations on the production database.
This script can be executed in the Docker container or locally.
"""
import os
import sys
import subprocess

def main():
    """Run Alembic migrations"""
    # Ensure we're in the backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is not set")
        sys.exit(1)
    
    print(f"🔄 Running migrations on database: {database_url[:50]}...")
    print("")
    
    try:
        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=backend_dir,
            check=True,
            capture_output=True,
            text=True
        )
        
        print("✅ Migrations completed successfully!")
        print(result.stdout)
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return 1
    except FileNotFoundError:
        print("❌ ERROR: alembic command not found. Make sure alembic is installed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
