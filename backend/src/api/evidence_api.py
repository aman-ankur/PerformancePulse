from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
from ..services.correlation_engine import create_correlation_engine
from ..models.correlation_models import CorrelationRequest, CorrelationResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/correlate", response_model=CorrelationResponse)
async def correlate_evidence(request: CorrelationRequest):
    """
    Correlate evidence using the full 7-step pipeline including LLM enhancement
    """
    try:
        correlation_engine = create_correlation_engine(enable_llm=True)
        response = await correlation_engine.correlate_evidence(request)
        return response
    except Exception as e:
        logger.error(f"Evidence correlation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Correlation failed: {str(e)}")

@router.post("/correlate-basic", response_model=CorrelationResponse)
async def correlate_evidence_basic(request: CorrelationRequest):
    """
    Correlate evidence using only rule-based algorithms (without LLM)
    """
    try:
        correlation_engine = create_correlation_engine(enable_llm=False)
        response = await correlation_engine.correlate_evidence(request)
        return response
    except Exception as e:
        logger.error(f"Basic evidence correlation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Correlation failed: {str(e)}")

@router.post("/correlate-llm-only")
async def correlate_with_llm_only(request: CorrelationRequest):
    """
    NEW - Phase 2.1.2: Correlate evidence using only LLM semantic analysis
    Useful for testing LLM correlation in isolation
    """
    try:
        from ..services.llm_correlation_service import create_llm_correlation_service
        
        llm_service = create_llm_correlation_service()
        relationships = await llm_service.correlate_evidence_with_llm(request.evidence_items)
        
        return {
            "success": True,
            "relationships": [relationship.dict() for relationship in relationships],
            "usage_report": llm_service.get_usage_report(),
            "message": f"LLM correlation found {len(relationships)} relationships"
        }
    except Exception as e:
        logger.error(f"LLM-only correlation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LLM correlation failed: {str(e)}")

@router.get("/engine-status")
async def get_engine_status():
    """
    Get correlation engine status and capabilities
    """
    try:
        correlation_engine = create_correlation_engine()
        status = correlation_engine.get_engine_status()
        
        # Add LLM usage information if available
        llm_usage = correlation_engine.get_llm_usage_report()
        if llm_usage:
            status['llm_usage'] = llm_usage
        
        return status
    except Exception as e:
        logger.error(f"Failed to get engine status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.get("/llm-usage")
async def get_llm_usage():
    """
    NEW - Phase 2.1.2: Get LLM usage and cost information
    """
    try:
        from ..services.llm_correlation_service import create_llm_correlation_service
        
        llm_service = create_llm_correlation_service()
        usage_report = llm_service.get_usage_report()
        
        return {
            "success": True,
            "usage_report": usage_report,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.warning(f"LLM service not configured, returning mock data: {str(e)}")
        
        # Return mock data for development when LLM service is not configured
        mock_usage_report = {
            "total_cost": 3.47,
            "embedding_requests": 42,
            "llm_requests": 8,
            "budget_limit": 15.00,
            "budget_remaining": 11.53,
            "cost_breakdown": {
                "embeddings_cost": 0.0234,
                "llm_cost": 3.4466
            },
            "usage_period": {
                "start_date": datetime.now().replace(day=1).isoformat(),
                "end_date": datetime.now().isoformat()
            }
        }
        
        return {
            "success": True,
            "usage_report": mock_usage_report,
            "timestamp": datetime.now().isoformat(),
            "mock_data": True,
            "message": "Using mock data - LLM service not configured"
        } 