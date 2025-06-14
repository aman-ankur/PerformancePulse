#!/usr/bin/env python3
"""
Evidence Collection API Endpoints
FastAPI endpoints for collecting evidence from GitLab using MCP-first hybrid approach
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import logging
import os

from ...services.gitlab_hybrid_client import GitLabHybridClient, create_gitlab_client, EvidenceItem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/evidence", tags=["evidence"])

# Configuration - these should be set via environment variables
GITLAB_TOKEN = os.getenv("GITLAB_PERSONAL_ACCESS_TOKEN")
GITLAB_PROJECT_ID = os.getenv("GITLAB_PROJECT_ID")  # Set this to your GitLab project ID
GITLAB_URL = os.getenv("GITLAB_API_URL", "https://gitlab.com/api/v4")

if not GITLAB_TOKEN:
    logger.warning("GITLAB_PERSONAL_ACCESS_TOKEN not configured")

if not GITLAB_PROJECT_ID:
    logger.warning("GITLAB_PROJECT_ID not configured")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "evidence_collection"}

@router.get("/gitlab/health")
async def gitlab_health_check():
    """Check GitLab MCP and API health"""
    if not GITLAB_TOKEN:
        raise HTTPException(status_code=500, detail="GitLab token not configured")
    
    if not GITLAB_PROJECT_ID:
        raise HTTPException(status_code=500, detail="GitLab project ID not configured")
    
    client = create_gitlab_client(GITLAB_TOKEN, GITLAB_PROJECT_ID, gitlab_url=GITLAB_URL)
    
    try:
        # Check MCP health
        mcp_healthy = await client.check_mcp_health()
        
        # Check API health by getting project details
        api_healthy = False
        try:
            project_details = await client.api_client.get_project_details(GITLAB_PROJECT_ID)
            api_healthy = bool(project_details.get("id"))
        except Exception as e:
            logger.error(f"API health check failed: {e}")
        
        return {
            "mcp_healthy": mcp_healthy,
            "api_healthy": api_healthy,
            "project_id": GITLAB_PROJECT_ID,
            "gitlab_url": GITLAB_URL
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/gitlab/collect/{username}")
async def collect_gitlab_evidence(
    username: str,
    days_back: int = Query(7, ge=1, le=90, description="Number of days to look back")
):
    """
    Collect GitLab evidence for a specific user
    
    Uses MCP-first hybrid approach:
    1. Try GitLab MCP server first
    2. Fallback to direct API if MCP fails
    """
    if not GITLAB_TOKEN:
        raise HTTPException(status_code=500, detail="GitLab token not configured")
    
    if not GITLAB_PROJECT_ID:
        raise HTTPException(status_code=500, detail="GitLab project ID not configured")
    
    logger.info(f"Collecting GitLab evidence for {username}, {days_back} days back")
    
    try:
        # Create hybrid client
        client = create_gitlab_client(GITLAB_TOKEN, GITLAB_PROJECT_ID, gitlab_url=GITLAB_URL)
        
        # Collect comprehensive evidence
        evidence_items = await client.get_comprehensive_evidence(username, days_back)
        
        # Transform to API response format
        evidence_response = []
        for item in evidence_items:
            evidence_response.append({
                "id": item.id,
                "team_member_id": item.team_member_id,
                "source": item.source,
                "title": item.title,
                "description": item.description,
                "source_url": item.source_url,
                "category": item.category,
                "evidence_date": item.evidence_date.isoformat(),
                "created_at": item.created_at.isoformat(),
                "metadata": {
                    **item.metadata,
                    "data_source": item.data_source.value,
                    "fallback_used": item.fallback_used
                }
            })
        
        return {
            "username": username,
            "days_back": days_back,
            "evidence_count": len(evidence_response),
            "evidence": evidence_response,
            "collection_summary": {
                "total_items": len(evidence_response),
                "merge_requests": len([e for e in evidence_response if e["source"] == "gitlab_mr"]),
                "issues": len([e for e in evidence_response if e["source"] == "gitlab_issue"]),
                "mcp_items": len([e for e in evidence_response if e["metadata"]["data_source"] == "mcp"]),
                "api_items": len([e for e in evidence_response if e["metadata"]["data_source"] == "api"]),
                "fallback_used": any(e["metadata"]["fallback_used"] for e in evidence_response)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to collect evidence for {username}: {e}")
        raise HTTPException(status_code=500, detail=f"Evidence collection failed: {str(e)}")

@router.get("/gitlab/merge-requests/{username}")
async def get_gitlab_merge_requests(
    username: str,
    days_back: int = Query(7, ge=1, le=90)
):
    """Get GitLab merge requests for a specific user"""
    if not GITLAB_TOKEN:
        raise HTTPException(status_code=500, detail="GitLab token not configured")
    
    if not GITLAB_PROJECT_ID:
        raise HTTPException(status_code=500, detail="GitLab project ID not configured")
    
    try:
        client = create_gitlab_client(GITLAB_TOKEN, GITLAB_PROJECT_ID, gitlab_url=GITLAB_URL)
        since_date = datetime.now() - timedelta(days=days_back)
        
        evidence_items = await client.get_merge_requests(username, since_date)
        
        return {
            "username": username,
            "merge_requests": [
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "source_url": item.source_url,
                    "category": item.category,
                    "evidence_date": item.evidence_date.isoformat(),
                    "metadata": {
                        **item.metadata,
                        "data_source": item.data_source.value,
                        "fallback_used": item.fallback_used
                    }
                }
                for item in evidence_items
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get merge requests for {username}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get merge requests: {str(e)}")

@router.get("/gitlab/issues/{username}")
async def get_gitlab_issues(
    username: str,
    days_back: int = Query(7, ge=1, le=90)
):
    """Get GitLab issues for a specific user"""
    if not GITLAB_TOKEN:
        raise HTTPException(status_code=500, detail="GitLab token not configured")
    
    if not GITLAB_PROJECT_ID:
        raise HTTPException(status_code=500, detail="GitLab project ID not configured")
    
    try:
        client = create_gitlab_client(GITLAB_TOKEN, GITLAB_PROJECT_ID, gitlab_url=GITLAB_URL)
        since_date = datetime.now() - timedelta(days=days_back)
        
        evidence_items = await client.get_issues(username, since_date)
        
        return {
            "username": username,
            "issues": [
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "source_url": item.source_url,
                    "category": item.category,
                    "evidence_date": item.evidence_date.isoformat(),
                    "metadata": {
                        **item.metadata,
                        "data_source": item.data_source.value,
                        "fallback_used": item.fallback_used
                    }
                }
                for item in evidence_items
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get issues for {username}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get issues: {str(e)}")

@router.get("/stats")
async def get_evidence_stats():
    """Get evidence collection statistics"""
    # This would typically query the database for stored evidence
    # For now, return basic stats
    return {
        "total_evidence_items": 0,
        "sources": {
            "gitlab_mr": 0,
            "gitlab_issue": 0,
            "jira_ticket": 0
        },
        "categories": {
            "technical": 0,
            "collaboration": 0,
            "delivery": 0
        },
        "collection_methods": {
            "mcp": 0,
            "api": 0
        }
    }

@router.post("/test-collection")
async def test_evidence_collection(
    username: str = Query(..., description="GitLab username to test")
):
    """
    Test evidence collection for development/debugging
    """
    if not GITLAB_TOKEN:
        raise HTTPException(status_code=500, detail="GitLab token not configured")
    
    if not GITLAB_PROJECT_ID:
        raise HTTPException(status_code=500, detail="GitLab project ID not configured")
    
    logger.info(f"Testing evidence collection for {username}")
    
    try:
        client = create_gitlab_client(GITLAB_TOKEN, GITLAB_PROJECT_ID, gitlab_url=GITLAB_URL)
        
        # Test MCP health
        mcp_healthy = await client.check_mcp_health()
        
        # Test basic collection (last 1 day)
        evidence_items = await client.get_comprehensive_evidence(username, days_back=1)
        
        return {
            "test_results": {
                "mcp_healthy": mcp_healthy,
                "evidence_collected": len(evidence_items),
                "collection_successful": True
            },
            "evidence_summary": [
                {
                    "source": item.source,
                    "title": item.title[:50] + "..." if len(item.title) > 50 else item.title,
                    "category": item.category,
                    "data_source": item.data_source.value,
                    "fallback_used": item.fallback_used
                }
                for item in evidence_items[:5]  # Show first 5 items
            ]
        }
        
    except Exception as e:
        logger.error(f"Test collection failed: {e}")
        return {
            "test_results": {
                "mcp_healthy": False,
                "evidence_collected": 0,
                "collection_successful": False,
                "error": str(e)
            },
            "evidence_summary": []
        } 