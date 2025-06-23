from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging
from uuid import UUID
from ..services.correlation_engine import create_correlation_engine
from ..services.database_service import DatabaseService
from ..models.correlation_models import CorrelationRequest, CorrelationResponse
from ..models.unified_evidence import UnifiedEvidenceItem, PlatformType, DataSourceType

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/correlate", response_model=CorrelationResponse)
async def correlate_evidence(request: CorrelationRequest, db: DatabaseService = Depends(DatabaseService)):
    """
    Correlate evidence using the full 7-step pipeline including LLM enhancement.
    If no evidence items are provided, fetches them from the database.
    """
    try:
        logger.info(f"Received correlation request for team member: {request.team_member_id}")
        logger.info(f"Request parameters: confidence_threshold={request.confidence_threshold}, "
                   f"max_work_stories={request.max_work_stories}, "
                   f"include_low_confidence={request.include_low_confidence}")

        # If no evidence items provided but team_member_id is, fetch evidence
        if not request.evidence_items and request.team_member_id:
            logger.info(f"No evidence items provided, fetching from database for team member {request.team_member_id}")
            raw_items = await db.get_evidence_items(UUID(request.team_member_id))

            def map_platform(src: str) -> PlatformType:
                if src.startswith("gitlab_"):
                    return PlatformType.GITLAB
                if src.startswith("jira_"):
                    return PlatformType.JIRA
                return PlatformType.DOCUMENT

            unified_items = []
            for db_item in raw_items:
                try:
                    unified_items.append(UnifiedEvidenceItem(
                        id=str(db_item.id),
                        team_member_id=str(db_item.team_member_id),
                        source=db_item.source,
                        title=db_item.title,
                        description=db_item.description,
                        category=db_item.category,
                        evidence_date=db_item.evidence_date,
                        source_url=db_item.source_url,
                        platform=map_platform(db_item.source),
                        data_source=DataSourceType.API,
                        author_name=getattr(db_item, "author_name", None),
                        author_email=getattr(db_item, "author_email", None),
                        metadata=db_item.metadata or {},
                    ))
                except Exception as map_err:
                    logger.warning(f"Failed to map DB evidence {db_item.id}: {map_err}")

            request.evidence_items = unified_items
            logger.info(f"Fetched {len(unified_items)} evidence items from database")
            for item in unified_items:
                logger.debug(
                    "Evidence item: id=%s, source=%s, platform=%s, date=%s",
                    item.id,
                    item.source,
                    item.platform,
                    item.evidence_date,
                )

        correlation_engine = create_correlation_engine(enable_llm=True)
        logger.info("Created correlation engine with LLM enabled")
        
        response = await correlation_engine.correlate_evidence(request)
        
        # Log response details
        logger.info(f"Correlation completed: success={response.success}, "
                   f"processing_time={response.processing_time_ms}ms")
        
        if response.correlated_collection:
            logger.info(
                "Generated %s work stories and %s relationships",
                len(response.correlated_collection.work_stories),
                len(response.correlated_collection.relationships),
            )

            # Detailed work story logs only in debug mode
            for story in response.correlated_collection.work_stories:
                logger.debug(
                    "Work story: id=%s, title=%s, confidence=%s",
                    story.id,
                    story.title,
                    story.confidence_score,
                )
        else:
            logger.warning("No correlated collection in response")
            
        if response.errors:
            logger.error(f"Correlation errors: {response.errors}")
        if response.warnings:
            logger.warning(f"Correlation warnings: {response.warnings}")
            
        return response
    except Exception as e:
        logger.error(f"Evidence correlation failed: {str(e)}", exc_info=True)
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
        # Get correlation engine instance
        from ..services.correlation_engine import CorrelationEngine
        engine = CorrelationEngine()
        
        # Get LLM status
        llm_status = engine.get_llm_status()
        
        if not llm_status['enabled']:
            return {
                "success": False,
                "error": "LLM service not available",
                "reason": llm_status.get('reason', 'Unknown'),
                "fallback_mode": llm_status['fallback_mode']
            }
            
        if llm_status['status'] == 'budget_exceeded':
            return {
                "success": False,
                "error": "Monthly budget exceeded",
                "usage_report": llm_status['usage_report'],
                "fallback_mode": llm_status['fallback_mode']
            }
            
        return {
            "success": True,
            "status": llm_status['status'],
            "usage_report": {
                "total_cost": llm_status['usage_report']['total_cost'],
                "embedding_requests": llm_status['usage_report']['embedding_requests'],
                "llm_requests": llm_status['usage_report']['llm_requests'],
                "budget_limit": llm_status['usage_report']['budget_limit'],
                "budget_remaining": llm_status['usage_report']['budget_remaining'],
                "cost_breakdown": {
                    "embeddings_cost": llm_status['usage_report']['cost_breakdown']['embeddings_cost'],
                    "llm_cost": llm_status['usage_report']['cost_breakdown']['llm_cost']
                },
                "usage_period": {
                    "start_date": llm_status['usage_report']['usage_period']['start_date'],
                    "end_date": llm_status['usage_report']['usage_period']['end_date']
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get LLM usage: {e}")
        return {
            "success": False,
            "error": "Failed to get LLM usage",
            "reason": str(e),
            "fallback_mode": "rule-based"
        } 