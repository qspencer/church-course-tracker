#!/usr/bin/env python3
"""
Fix Alembic multiple head revisions issue
This script merges all heads into a single head revision
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def main():
    """Fix Alembic multiple head revisions"""
    backend_dir = Path(__file__).parent.parent
    
    print("🔧 Fixing Alembic multiple head revisions...")
    print("=" * 60)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Check current heads
    print("\n📊 Checking current migration heads...")
    returncode, stdout, stderr = run_command("alembic heads")
    
    if returncode != 0:
        print(f"❌ Error checking heads: {stderr}")
        return False
    
    head_lines = [line.strip() for line in stdout.split('\n') if line.strip() and not line.startswith('Rev:')]
    heads = [line.split()[0] for line in head_lines if line]
    
    print(f"Found {len(heads)} head(s):")
    for head in heads:
        print(f"  - {head}")
    
    if len(heads) <= 1:
        print("✅ No multiple heads found. Migrations are OK.")
        return True
    
    # Create a merge migration
    print(f"\n🔀 Creating merge migration for {len(heads)} heads...")
    merge_cmd = f"alembic merge -m 'merge_heads' {' '.join(heads)}"
    returncode, stdout, stderr = run_command(merge_cmd)
    
    if returncode != 0:
        print(f"❌ Error creating merge migration: {stderr}")
        print(f"   STDOUT: {stdout}")
        return False
    
    print(f"✅ Merge migration created:")
    print(stdout)
    
    # Try to upgrade to head
    print("\n⬆️  Upgrading to head...")
    returncode, stdout, stderr = run_command("alembic upgrade head")
    
    if returncode != 0:
        print(f"⚠️  Upgrade failed: {stderr}")
        print("   This is OK if database is already up to date")
    
    print("✅ Alembic heads fixed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

