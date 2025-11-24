#!/usr/bin/env python3
"""
Teardown test data for E2E tests

This script removes CSV-loaded test data from the database after E2E tests complete.
It uses the EnhancedCSVDataLoader's clear_csv_data_only method which only removes
data that was loaded from CSV, preserving any user-entered data.

Note: This requires database access. If running against production without
database access, set E2E_SKIP_DATA_CLEANUP=true to skip cleanup.
"""

import os
import sys
import logging
from pathlib import Path

# Check if we should skip data cleanup
if os.getenv('E2E_SKIP_DATA_CLEANUP', 'false').lower() == 'true':
    print('⏭️  Skipping test data cleanup (E2E_SKIP_DATA_CLEANUP=true)')
    sys.exit(0)

# Add the backend directory to the Python path
project_root = Path(__file__).parent.parent.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

# Change to backend directory to ensure relative imports work
original_cwd = os.getcwd()
try:
    os.chdir(backend_dir)
    
    try:
        from app.core.enhanced_csv_loader import EnhancedCSVDataLoader
        from app.core.database import SessionLocal
    except ImportError as e:
        print(f'⚠️  Could not import backend modules: {e}')
        print('   This may be expected if testing against production without database access.')
        print('   Set E2E_SKIP_DATA_CLEANUP=true to skip cleanup.')
        sys.exit(0)
finally:
    os.chdir(original_cwd)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clear_test_data() -> dict:
    """
    Clear CSV-loaded test data from the database
    
    Returns:
        Dictionary with counts of deleted records by type
    """
    logger.info("Starting CSV test data cleanup...")
    
    # Change to backend directory for database operations
    project_root = Path(__file__).parent.parent.parent
    backend_dir = project_root / "backend"
    os.chdir(backend_dir)
    
    try:
        loader = EnhancedCSVDataLoader()
        db = SessionLocal()
        
        try:
            # Get summary before clearing
            summary_before = loader.get_csv_data_summary(db)
            logger.info(f"CSV data before cleanup: {summary_before}")
            
            # Clear only CSV-loaded data
            results = loader.clear_csv_data_only(db)
            logger.info(f"✅ Successfully cleared CSV test data: {results}")
            return results
        except Exception as e:
            logger.error(f"❌ Error clearing CSV data: {e}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to clear test data: {e}")
        raise


if __name__ == "__main__":
    try:
        results = clear_test_data()
        print("✅ Test data cleared successfully!")
        print("\nDeleted records:")
        for data_type, count in results.items():
            print(f"  - {data_type}: {count} records")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error clearing test data: {e}")
        sys.exit(1)

