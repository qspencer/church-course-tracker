#!/usr/bin/env python3
"""
Setup test data for E2E tests using CSV loader

This script loads CSV test data into the database before E2E tests run.
It uses the EnhancedCSVDataLoader which tracks data source, allowing
selective cleanup after tests complete.

Note: This requires database access. If running against production without
database access, set E2E_SKIP_DATA_LOAD=true to skip data loading.
"""

import os
import sys
import logging
from pathlib import Path

# Check if we should skip data loading
if os.getenv('E2E_SKIP_DATA_LOAD', 'false').lower() == 'true':
    print('⏭️  Skipping test data load (E2E_SKIP_DATA_LOAD=true)')
    print('   Tests will use existing data in the database')
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
        from app.core.config import settings
    except ImportError as e:
        print(f'⚠️  Could not import backend modules: {e}')
        print('   This may be expected if testing against production without database access.')
        print('   Set E2E_SKIP_DATA_LOAD=true to skip data loading.')
        sys.exit(0)
finally:
    os.chdir(original_cwd)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_test_data(force_reload: bool = False) -> dict:
    """
    Load CSV test data into the database
    
    Args:
        force_reload: If True, reload data even if it already exists
        
    Returns:
        Dictionary with counts of loaded records by type
    """
    logger.info("Starting CSV test data load...")
    
    # Change to backend directory for database operations
    os.chdir(backend_dir)
    
    # Use the data directory from settings or default
    data_dir = getattr(settings, 'CSV_DATA_DIR', 'data/csv')
    
    # If data_dir is relative, make it relative to backend directory
    if not os.path.isabs(data_dir):
        data_dir = backend_dir / data_dir
    
    logger.info(f"Using CSV data directory: {data_dir}")
    
    if not os.path.exists(data_dir):
        logger.warning(f"CSV data directory not found: {data_dir}")
        logger.info("Creating directory and sample data...")
        os.makedirs(data_dir, exist_ok=True)
        # Try to create sample data if directory is empty
        from app.core.csv_loader import create_sample_csv_files
        try:
            create_sample_csv_files(str(data_dir))
            logger.info("Sample CSV files created")
        except Exception as e:
            logger.warning(f"Could not create sample CSV files: {e}")
            return {}
    
    try:
        loader = EnhancedCSVDataLoader(str(data_dir))
        db = SessionLocal()
        
        try:
            results = loader.load_all_data(db, force_reload=force_reload)
            logger.info(f"✅ Successfully loaded CSV test data: {results}")
            return results
        except Exception as e:
            logger.error(f"❌ Error loading CSV data: {e}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to load test data: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Load CSV test data for E2E tests")
    parser.add_argument('--force', action='store_true', 
                       help='Force reload data even if it already exists')
    
    args = parser.parse_args()
    
    try:
        results = load_test_data(force_reload=args.force)
        print("✅ Test data loaded successfully!")
        print("\nLoaded records:")
        for data_type, count in results.items():
            print(f"  - {data_type}: {count} records")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error loading test data: {e}")
        sys.exit(1)

