#!/usr/bin/env python3
"""
Comprehensive test runner for Church Course Tracker
Runs all backend and frontend tests for the new content management and audit features
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None, description=""):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Command timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    """Main test runner function"""
    print("🧪 Church Course Tracker - Comprehensive Test Suite")
    print("=" * 60)
    
    # Get project root directory
    project_root = Path(__file__).parent.absolute()
    backend_dir = project_root / "backend"
    frontend_dir = project_root / "frontend" / "church-course-tracker"
    
    # Check if directories exist
    if not backend_dir.exists():
        print(f"❌ Backend directory not found: {backend_dir}")
        return 1
    
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return 1
    
    print(f"📁 Project root: {project_root}")
    print(f"📁 Backend directory: {backend_dir}")
    print(f"📁 Frontend directory: {frontend_dir}")
    
    # Track test results
    test_results = []
    
    # Backend Tests
    print("\n🔧 Running Backend Tests")
    print("=" * 60)
    
    # Test new content management models
    success = run_command(
        "python -m pytest tests/test_course_content_models.py -v",
        cwd=backend_dir,
        description="Course Content Models Tests"
    )
    test_results.append(("Backend - Course Content Models", success))
    
    # Test audit models
    success = run_command(
        "python -m pytest tests/test_audit_models.py -v",
        cwd=backend_dir,
        description="Audit Models Tests"
    )
    test_results.append(("Backend - Audit Models", success))
    
    # Test content service
    success = run_command(
        "python -m pytest tests/test_content_service.py -v",
        cwd=backend_dir,
        description="Content Service Tests"
    )
    test_results.append(("Backend - Content Service", success))
    
    # Test audit service
    success = run_command(
        "python -m pytest tests/test_audit_service.py -v",
        cwd=backend_dir,
        description="Audit Service Tests"
    )
    test_results.append(("Backend - Audit Service", success))
    
    # Test course content endpoints
    success = run_command(
        "python -m pytest tests/test_course_content_endpoints.py -v",
        cwd=backend_dir,
        description="Course Content Endpoints Tests"
    )
    test_results.append(("Backend - Course Content Endpoints", success))
    
    # Test audit endpoints
    success = run_command(
        "python -m pytest tests/test_audit_endpoints.py -v",
        cwd=backend_dir,
        description="Audit Endpoints Tests"
    )
    test_results.append(("Backend - Audit Endpoints", success))
    
    # Test integration tests
    success = run_command(
        "python -m pytest tests/test_integration_course_content.py -v",
        cwd=backend_dir,
        description="Integration Tests"
    )
    test_results.append(("Backend - Integration Tests", success))
    
    # Frontend Tests
    print("\n🎨 Running Frontend Tests")
    print("=" * 60)
    
    # Check if npm is available
    npm_check = run_command("npm --version", description="Check npm availability")
    if not npm_check:
        print("❌ npm not available, skipping frontend tests")
    else:
        # Install dependencies if needed
        if not (frontend_dir / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            run_command("npm install", cwd=frontend_dir, description="Install Frontend Dependencies")
        
        # Test course content service
        success = run_command(
            "npm test -- --include='**/course-content.service.spec.ts' --watch=false",
            cwd=frontend_dir,
            description="Course Content Service Tests"
        )
        test_results.append(("Frontend - Course Content Service", success))
        
        # Test audit service
        success = run_command(
            "npm test -- --include='**/audit.service.spec.ts' --watch=false",
            cwd=frontend_dir,
            description="Audit Service Tests"
        )
        test_results.append(("Frontend - Audit Service", success))
        
        # Test course content component
        success = run_command(
            "npm test -- --include='**/course-content.component.spec.ts' --watch=false",
            cwd=frontend_dir,
            description="Course Content Component Tests"
        )
        test_results.append(("Frontend - Course Content Component", success))
        
        # Test audit component
        success = run_command(
            "npm test -- --include='**/audit.component.spec.ts' --watch=false",
            cwd=frontend_dir,
            description="Audit Component Tests"
        )
        test_results.append(("Frontend - Audit Component", success))
        
        # Test course content models
        success = run_command(
            "npm test -- --include='**/course-content.model.spec.ts' --watch=false",
            cwd=frontend_dir,
            description="Course Content Models Tests"
        )
        test_results.append(("Frontend - Course Content Models", success))
        
        # Test audit models
        success = run_command(
            "npm test -- --include='**/audit.model.spec.ts' --watch=false",
            cwd=frontend_dir,
            description="Audit Models Tests"
        )
        test_results.append(("Frontend - Audit Models", success))
        
        # Test integration tests
        success = run_command(
            "npm test -- --include='**/integration/*.spec.ts' --watch=false",
            cwd=frontend_dir,
            description="Frontend Integration Tests"
        )
        test_results.append(("Frontend - Integration Tests", success))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 Total: {len(test_results)} tests")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The new content management and audit features are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())


