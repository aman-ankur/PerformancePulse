"""
Database connection configuration for PerformancePulse
Handles Supabase client initialization and connection management
"""

import os
import logging
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Load environment variables from specific .env file
env_path = Path('/Users/aankur/workspace/PerformancePulse/backend/.env')
if not env_path.exists():
    raise FileNotFoundError(f"Required .env file not found at: {env_path}")

load_result = load_dotenv(dotenv_path=env_path, verbose=True)
if not load_result:
    raise RuntimeError(f"Failed to load environment variables from: {env_path}")

class DatabaseConnection:
    """Manages Supabase database connections with proper error handling"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize Supabase client with environment variables"""
        try:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                logger.error("Missing Supabase configuration in environment variables")
                return False
            
            # Initialize client
            logger.info(f"Initializing Supabase client with URL: {supabase_url}")
            self.client = create_client(supabase_url, supabase_key)
            
            # Test the connection with a simple query
            logger.info("Testing connection with a simple query...")
            self.client.table('profiles').select("*").limit(1).execute()
            
            self._initialized = True
            logger.info("✅ Supabase client initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Response details: {e.response.text if hasattr(e.response, 'text') else str(e.response)}")
            return False
    
    def get_client(self) -> Client:
        """Get the Supabase client, initializing if necessary"""
        if not self._initialized or not self.client:
            if not self.initialize():
                raise ConnectionError("Unable to initialize Supabase client")
        return self.client
    
    def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            client = self.get_client()
            # Simple query to test connection
            client.table('profiles').select("*").limit(1).execute()
            logger.info("Database health check successful")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

# Global database connection instance
db_connection = DatabaseConnection()

def get_supabase_client() -> Client:
    """Get the global Supabase client instance"""
    return db_connection.get_client()

def test_database_connection() -> bool:
    """Test database connection for development/testing"""
    return db_connection.health_check() 