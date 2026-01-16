"""
Direct script to create system_settings table
Used when migrations are blocked by other issues
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base
from app.models.system_settings import SystemSettings

def create_table():
    """Create system_settings table directly"""
    engine = create_engine(settings.DATABASE_URL)
    
    # Check if table exists
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='system_settings'
        """))
        if result.fetchone():
            print("Table 'system_settings' already exists")
            return
    
    # Create table
    Base.metadata.create_all(bind=engine, tables=[SystemSettings.__table__])
    print("Table 'system_settings' created successfully")
    
    # Create indexes
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_system_settings_id 
            ON system_settings(id)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_system_settings_key 
            ON system_settings(key)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_system_settings_category 
            ON system_settings(category)
        """))
        conn.commit()
    print("Indexes created successfully")

if __name__ == "__main__":
    create_table()
