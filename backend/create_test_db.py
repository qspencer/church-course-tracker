#!/usr/bin/env python3
"""
Create a fresh test database with the correct schema
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set up environment
os.environ["DATABASE_URL"] = "sqlite:///./data/church_course_tracker.db"

# Import after setting environment variables
from app.core.database import Base
from app.models import *

def create_test_database():
    """Create a fresh test database with all tables"""
    
    # Create database engine
    engine = create_engine(
        "sqlite:///./data/church_course_tracker.db",
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create a session to verify tables were created
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Check if courses table has the correct schema
        result = session.execute(text("PRAGMA table_info(courses)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'title' in columns:
            print("✅ Courses table has 'title' column")
        else:
            print("❌ Courses table missing 'title' column")
            print(f"Available columns: {columns}")
            
        # Check course_modules table
        result = session.execute(text("PRAGMA table_info(course_modules)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'order_index' in columns:
            print("✅ Course modules table has 'order_index' column")
        else:
            print("❌ Course modules table missing 'order_index' column")
            print(f"Available columns: {columns}")
            
        # Check course_content table
        result = session.execute(text("PRAGMA table_info(course_content)"))
        columns = [row[1] for row in result.fetchall()]
        
        if 'order_index' in columns:
            print("✅ Course content table has 'order_index' column")
        else:
            print("❌ Course content table missing 'order_index' column")
            print(f"Available columns: {columns}")
            
        print("✅ Test database created successfully!")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_test_database()
