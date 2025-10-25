#!/usr/bin/env python3
"""
Test runner script for the Church Course Tracker backend
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run all tests with coverage reporting"""
    
    # Change to the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Test commands
    test_commands = [
        # Run all tests with coverage
        ["python", "-m", "pytest", "tests/", "-v", "--cov=app", "--cov-report=html", "--cov-report=term"],
        
        # Run specific test categories
        ["python", "-m", "pytest", "tests/test_models.py", "-v", "-m", "unit"],
        ["python", "-m", "pytest", "tests/test_schemas.py", "-v", "-m", "unit"],
        ["python", "-m", "pytest", "tests/test_services.py", "-v", "-m", "unit"],
        ["python", "-m", "pytest", "tests/test_endpoints.py", "-v", "-m", "integration"],
    ]
    
    print("🧪 Running Church Course Tracker Backend Tests")
    print("=" * 50)
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n📋 Test Run {i}: {' '.join(cmd[2:])}")
        print("-" * 30)
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=False)
            print(f"✅ Test run {i} completed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Test run {i} failed with exit code {e.returncode}")
            return False
        except FileNotFoundError:
            print(f"❌ pytest not found. Please install test dependencies:")
            print("   pip install -r requirements.txt")
            return False
    
    print("\n🎉 All tests completed successfully!")
    print("\n📊 Coverage report generated in htmlcov/index.html")
    return True

def run_specific_test(test_file: str):
    """Run a specific test file"""
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    cmd = ["python", "-m", "pytest", f"tests/{test_file}", "-v"]
    
    print(f"🧪 Running specific test: {test_file}")
    print("=" * 50)
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Test {test_file} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Test {test_file} failed with exit code {e.returncode}")
        return False

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        if not test_file.endswith('.py'):
            test_file += '.py'
        success = run_specific_test(test_file)
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
