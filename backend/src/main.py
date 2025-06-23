"""
PerformancePulse Backend - FastAPI Application

Main entry point for the FastAPI backend that handles:
- Team management and authentication
- Evidence collection from GitLab/Jira
- AI processing with Claude
- Background job management
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# Module-level logger
logger = logging.getLogger(__name__)

# Reduce noise from uvicorn access logs
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
logger.debug(f"Looking for .env file at: {env_path}")

if not env_path.exists():
    logger.error(f"Required .env file not found at {env_path}")
    raise FileNotFoundError(f"Required .env file not found at {env_path}")

load_dotenv(env_path)

# Import routers - using the names as exported in their respective modules
from src.api.auth import router as auth_router
from src.api.team import router as team_router
from src.api.evidence_api import router as evidence_api_router

# Create FastAPI app
app = FastAPI(
    title="PerformancePulse API",
    description="Backend API for PerformancePulse - Performance Analytics Platform",
    version="2.1.2"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # TODO: Configure for production
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(team_router, prefix="/api/team", tags=["Team Management"])
app.include_router(evidence_api_router, prefix="/api", tags=["Evidence API"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.1.2"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 