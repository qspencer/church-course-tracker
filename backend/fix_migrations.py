#!/usr/bin/env python3
"""
Script to fix database migration issues
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def main():
    """Fix database migration issues"""
    backend_dir = Path(__file__).parent
    
    print("🔧 Fixing database migration issues...")
    
    # Set environment variables for local testing
    env = os.environ.copy()
    env['DATABASE_URL'] = env.get('DATABASE_URL', 'postgresql://user:pass@localhost/db')
    
    print("📊 Checking migration status...")
    
    # Try to run alembic heads to see current state
    cmd = "alembic heads"
    returncode, stdout, stderr = run_command(cmd, cwd=backend_dir)
    
    if returncode == 0:
        print("✅ Migration heads:")
        print(stdout)
    else:
        print("❌ Error checking heads:")
        print(stderr)
    
    print("🔄 Attempting to upgrade to head...")
    
    # Try to upgrade to head
    cmd = "alembic upgrade head"
    returncode, stdout, stderr = run_command(cmd, cwd=backend_dir)
    
    if returncode == 0:
        print("✅ Migration upgrade successful:")
        print(stdout)
        return True
    else:
        print("❌ Migration upgrade failed:")
        print(stderr)
        
        # Try to upgrade to specific revision
        print("🔄 Trying to upgrade to specific revision...")
        cmd = "alembic upgrade 002"
        returncode, stdout, stderr = run_command(cmd, cwd=backend_dir)
        
        if returncode == 0:
            print("✅ Partial upgrade successful:")
            print(stdout)
            return True
        else:
            print("❌ Partial upgrade also failed:")
            print(stderr)
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
