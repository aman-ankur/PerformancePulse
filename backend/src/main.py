"""
PerformancePulse Backend - FastAPI Application

Main entry point for the FastAPI backend that handles:
- Team management and authentication
- Evidence collection from GitLab/Jira
- AI processing with Claude
- Background job management
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from .api.auth import router as auth_router
from .api.team import router as team_router
from .api.evidence import router as evidence_router
from .api.endpoints.evidence import router as evidence_endpoints_router
from .api.evidence_api import router as evidence_api_router

# Initialize FastAPI app
app = FastAPI(
    title="PerformancePulse API",
    description="Backend API for performance data aggregation and AI analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development
        "https://performancepulse.vercel.app",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app", "*.render.com"]
)

# Include API routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(team_router, prefix="/api/team", tags=["Team Management"])
app.include_router(evidence_router, prefix="/api/evidence", tags=["Evidence Collection"])
app.include_router(evidence_endpoints_router, tags=["Evidence Endpoints"])
app.include_router(evidence_api_router, prefix="/api", tags=["Evidence API"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "PerformancePulse API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check for monitoring"""
    return {
        "status": "healthy",
        "service": "performancepulse-backend",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 