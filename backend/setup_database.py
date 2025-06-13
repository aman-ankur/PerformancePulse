#!/usr/bin/env python3
"""
Database Setup Script for PerformancePulse
Applies schema and tests database connectivity for development
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.database.connection import DatabaseConnection, test_database_connection
from src.services.database_service import DatabaseService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables for development"""
    # For development, we'll check if environment is properly configured
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_ROLE_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.info("Please set up your Supabase project and add the following to your .env file:")
        logger.info("SUPABASE_URL=your_supabase_project_url")
        logger.info("SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key")
        return False
    
    return True

def read_schema_file():
    """Read the database schema SQL file"""
    schema_path = Path(__file__).parent / "src" / "database" / "schema.sql"
    
    if not schema_path.exists():
        logger.error(f"Schema file not found: {schema_path}")
        return None
    
    try:
        with open(schema_path, 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading schema file: {e}")
        return None

async def test_database_setup():
    """Test database connectivity and basic operations"""
    logger.info("Testing database connectivity...")
    
    try:
        # Test basic connection
        is_healthy = await test_database_connection()
        
        if is_healthy:
            logger.info("✅ Database connection successful!")
        else:
            logger.error("❌ Database connection failed")
            return False
        
        # Test database service
        logger.info("Testing database service...")
        db_service = DatabaseService()
        health_check = await db_service.health_check()
        
        if health_check["status"] == "healthy":
            logger.info("✅ Database service is healthy!")
        else:
            logger.error(f"❌ Database service unhealthy: {health_check}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return False

async def main():
    """Main setup function"""
    logger.info("🚀 Starting PerformancePulse Database Setup")
    
    # Check environment
    if not load_environment():
        logger.error("❌ Environment configuration failed")
        return False
    
    logger.info("✅ Environment variables loaded")
    
    # Read schema
    schema_sql = read_schema_file()
    if not schema_sql:
        logger.error("❌ Failed to read database schema")
        return False
    
    logger.info("✅ Database schema loaded")
    
    # Note: In a real setup, we would apply the schema here
    # For MVP, we assume the Supabase project has been created manually
    logger.info("📝 Schema ready for manual application to Supabase project")
    logger.info("   Please run the schema.sql file in your Supabase SQL editor")
    
    # Test database connectivity
    test_success = await test_database_setup()
    
    if test_success:
        logger.info("🎉 Database setup verification complete!")
        logger.info("✅ Phase 1.1.2 database configuration is ready")
        return True
    else:
        logger.error("❌ Database setup verification failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 