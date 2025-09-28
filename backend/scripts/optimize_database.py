#!/usr/bin/env python3
"""
Database optimization script for Church Course Tracker
This script applies database optimizations and analyzes performance
"""

import os
import sys
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import engine, SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_database_performance():
    """Analyze database performance and suggest optimizations"""
    logger.info("🔍 Analyzing database performance...")
    
    with engine.connect() as conn:
        if "sqlite" in settings.DATABASE_URL:
            # SQLite analysis
            result = conn.execute(text("PRAGMA table_info(courses)"))
            logger.info("📊 Course table structure analyzed")
            
            # Check if indexes exist
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='index'"))
            indexes = [row[0] for row in result.fetchall()]
            logger.info(f"📈 Found {len(indexes)} indexes")
            
            # Analyze table sizes
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            for table in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                logger.info(f"📋 Table {table}: {count} rows")
        
        elif "postgresql" in settings.DATABASE_URL:
            # PostgreSQL analysis
            result = conn.execute(text("""
                SELECT schemaname, tablename, attname, n_distinct, correlation
                FROM pg_stats 
                WHERE schemaname = 'public'
                ORDER BY tablename, attname
            """))
            
            logger.info("📊 PostgreSQL table statistics:")
            for row in result.fetchall():
                logger.info(f"  {row[1]}.{row[2]}: {row[3]} distinct values, correlation: {row[4]}")
            
            # Check for missing indexes
            result = conn.execute(text("""
                SELECT schemaname, tablename, attname, n_distinct
                FROM pg_stats 
                WHERE schemaname = 'public' 
                AND n_distinct > 100
                AND attname NOT IN (
                    SELECT column_name 
                    FROM information_schema.key_column_usage 
                    WHERE table_schema = 'public'
                )
            """))
            
            missing_indexes = result.fetchall()
            if missing_indexes:
                logger.warning("⚠️  Potential missing indexes:")
                for row in missing_indexes:
                    logger.warning(f"  {row[1]}.{row[2]} ({row[3]} distinct values)")


def optimize_database():
    """Apply database optimizations"""
    logger.info("⚡ Applying database optimizations...")
    
    with engine.connect() as conn:
        if "sqlite" in settings.DATABASE_URL:
            # SQLite optimizations
            logger.info("🔧 Applying SQLite optimizations...")
            
            # Enable WAL mode
            conn.execute(text("PRAGMA journal_mode=WAL"))
            logger.info("✅ Enabled WAL mode")
            
            # Set synchronous mode
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            logger.info("✅ Set synchronous mode to NORMAL")
            
            # Increase cache size
            conn.execute(text("PRAGMA cache_size=10000"))
            logger.info("✅ Increased cache size to 10000")
            
            # Set temp store to memory
            conn.execute(text("PRAGMA temp_store=MEMORY"))
            logger.info("✅ Set temp store to memory")
            
            # Analyze tables for better query planning
            conn.execute(text("ANALYZE"))
            logger.info("✅ Analyzed tables for query optimization")
            
        elif "postgresql" in settings.DATABASE_URL:
            # PostgreSQL optimizations
            logger.info("🔧 Applying PostgreSQL optimizations...")
            
            # Update table statistics
            conn.execute(text("ANALYZE"))
            logger.info("✅ Updated table statistics")
            
            # Set work memory for this session
            conn.execute(text("SET work_mem = '256MB'"))
            logger.info("✅ Set work memory to 256MB")
            
            # Set effective cache size
            conn.execute(text("SET effective_cache_size = '1GB'"))
            logger.info("✅ Set effective cache size to 1GB")


def create_performance_views():
    """Create performance monitoring views"""
    logger.info("📊 Creating performance monitoring views...")
    
    with engine.connect() as conn:
        if "postgresql" in settings.DATABASE_URL:
            # Create view for slow queries
            conn.execute(text("""
                CREATE OR REPLACE VIEW slow_queries AS
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements 
                WHERE mean_time > 1000  -- Queries taking more than 1 second
                ORDER BY mean_time DESC
            """))
            logger.info("✅ Created slow queries view")
            
            # Create view for table sizes
            conn.execute(text("""
                CREATE OR REPLACE VIEW table_sizes AS
                SELECT 
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """))
            logger.info("✅ Created table sizes view")


def run_performance_tests():
    """Run performance tests on common queries"""
    logger.info("🧪 Running performance tests...")
    
    db = SessionLocal()
    try:
        # Test common queries
        test_queries = [
            "SELECT COUNT(*) FROM courses WHERE is_active = true",
            "SELECT COUNT(*) FROM course_enrollment WHERE status = 'enrolled'",
            "SELECT COUNT(*) FROM people WHERE is_active = true",
            "SELECT COUNT(*) FROM users WHERE is_active = true"
        ]
        
        for query in test_queries:
            start_time = time.time()
            result = db.execute(text(query))
            count = result.fetchone()[0]
            end_time = time.time()
            
            duration = (end_time - start_time) * 1000  # Convert to milliseconds
            logger.info(f"⚡ Query: {query[:50]}... - {count} rows in {duration:.2f}ms")
            
            if duration > 1000:  # More than 1 second
                logger.warning(f"⚠️  Slow query detected: {duration:.2f}ms")
    
    finally:
        db.close()


def main():
    """Main optimization function"""
    logger.info("🚀 Starting database optimization...")
    
    try:
        # Analyze current performance
        analyze_database_performance()
        
        # Apply optimizations
        optimize_database()
        
        # Create monitoring views (PostgreSQL only)
        if "postgresql" in settings.DATABASE_URL:
            create_performance_views()
        
        # Run performance tests
        run_performance_tests()
        
        logger.info("✅ Database optimization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database optimization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
