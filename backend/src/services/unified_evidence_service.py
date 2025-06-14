"""
Unified Evidence Service - Week 1 Implementation
Orchestrates evidence collection from multiple platforms with validation and error handling

Architecture:
- Wraps existing GitLab and JIRA hybrid clients
- Provides unified interface for evidence collection
- Adds validation and normalization layer
- Maintains backward compatibility
- Implements circuit breaker pattern for resilience
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import time

from ..models.unified_evidence import (
    UnifiedEvidenceItem,
    EvidenceCollection,
    CollectionRequest,
    CollectionResponse,
    PlatformType,
    DataSourceType,
    EvidenceValidator,
    ValidationStatus
)
from ..models.search_criteria import (
    JQLSearchCriteria, create_sprint_search, create_user_search, SearchScope
)
from .gitlab_hybrid_client import GitLabHybridClient, create_gitlab_client
from .jira_hybrid_client import JiraHybridClient, create_jira_client

logger = logging.getLogger(__name__)

@dataclass
class PlatformHealth:
    """Health status of a platform client"""
    platform: PlatformType
    healthy: bool
    last_check: datetime
    error_message: Optional[str] = None
    response_time_ms: Optional[int] = None

@dataclass
class CollectionMetrics:
    """Metrics for evidence collection performance"""
    start_time: datetime
    end_time: Optional[datetime] = None
    total_items_collected: int = 0
    items_by_platform: Dict[PlatformType, int] = None
    items_by_source: Dict[DataSourceType, int] = None
    validation_summary: Dict[str, Any] = None
    platform_response_times: Dict[PlatformType, int] = None
    errors_encountered: List[str] = None
    
    def __post_init__(self):
        if self.items_by_platform is None:
            self.items_by_platform = {}
        if self.items_by_source is None:
            self.items_by_source = {}
        if self.platform_response_times is None:
            self.platform_response_times = {}
        if self.errors_encountered is None:
            self.errors_encountered = []
    
    @property
    def total_duration_ms(self) -> int:
        """Total collection duration in milliseconds"""
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds() * 1000)
        return 0

class UnifiedEvidenceService:
    """
    Unified Evidence Service - Week 1 Implementation
    
    Provides a single interface for collecting evidence from multiple platforms
    while maintaining backward compatibility with existing clients.
    """
    
    def __init__(self, 
                 gitlab_token: str,
                 gitlab_project_id: str,
                 jira_mcp_server_url: str,
                 jira_cloud_id: str,
                 jira_base_url: str,
                 jira_api_token: str,
                 jira_user_email: str,
                 jira_project_key: Optional[str] = None,
                 gitlab_url: str = "https://gitlab.com/api/v4"):
        """
        Initialize the unified evidence service
        
        Args:
            gitlab_token: GitLab personal access token
            gitlab_project_id: GitLab project ID
            jira_mcp_server_url: JIRA MCP server URL
            jira_cloud_id: JIRA cloud ID
            jira_base_url: JIRA base URL
            jira_api_token: JIRA API token
            jira_user_email: JIRA user email
            jira_project_key: JIRA project key (optional)
            gitlab_url: GitLab API URL
        """
        
        # Initialize platform clients
        self.gitlab_client = create_gitlab_client(
            gitlab_token=gitlab_token,
            project_id=gitlab_project_id,
            gitlab_url=gitlab_url
        )
        
        self.jira_client = create_jira_client(
            mcp_server_url=jira_mcp_server_url,
            cloud_id=jira_cloud_id,
            jira_base_url=jira_base_url,
            api_token=jira_api_token,
            user_email=jira_user_email,
            project_key=jira_project_key
        )
        
        # Health tracking
        self.platform_health: Dict[PlatformType, PlatformHealth] = {}
        self.last_health_check = datetime.utcnow() - timedelta(hours=1)  # Force initial check
        
        # Configuration
        self.health_check_interval = timedelta(minutes=5)
        self.circuit_breaker_threshold = 3  # Failures before circuit opens
        self.circuit_breaker_timeout = timedelta(minutes=2)
        
        logger.info("Unified Evidence Service initialized successfully")
    
    async def collect_evidence(self, request: CollectionRequest) -> CollectionResponse:
        """
        Main method to collect evidence from multiple platforms
        
        Args:
            request: Evidence collection request
            
        Returns:
            CollectionResponse with collected evidence and metrics
        """
        metrics = CollectionMetrics(start_time=datetime.utcnow())
        logger.info(f"Starting evidence collection for user {request.username}")
        
        try:
            # Health check if needed
            await self._ensure_platform_health()
            
            # Collect from each platform concurrently
            collection_tasks = []
            
            if PlatformType.GITLAB in request.platforms:
                collection_tasks.append(
                    self._collect_gitlab_evidence(request, metrics)
                )
            
            if PlatformType.JIRA in request.platforms:
                collection_tasks.append(
                    self._collect_jira_evidence(request, metrics)
                )
            
            # Execute collection tasks concurrently
            results = await asyncio.gather(*collection_tasks, return_exceptions=True)
            
            # Process results
            all_evidence = []
            collection_errors = []
            collection_warnings = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_msg = f"Platform collection failed: {str(result)}"
                    collection_errors.append(error_msg)
                    metrics.errors_encountered.append(error_msg)
                    logger.error(error_msg, exc_info=result)
                else:
                    evidence_items, warnings = result
                    all_evidence.extend(evidence_items)
                    collection_warnings.extend(warnings)
            
            # Create unified collection
            collection = EvidenceCollection(
                items=all_evidence,
                total_count=len(all_evidence)
            )
            
            # Validate if requested
            if request.validate_items:
                validation_summary = EvidenceValidator.validate_collection(collection)
                metrics.validation_summary = validation_summary
                logger.info(f"Validation complete: {validation_summary['valid_items']}/{validation_summary['total_items']} items valid")
            
            # Update metrics
            metrics.end_time = datetime.utcnow()
            metrics.total_items_collected = len(all_evidence)
            
            for item in all_evidence:
                metrics.items_by_platform[item.platform] = metrics.items_by_platform.get(item.platform, 0) + 1
                metrics.items_by_source[item.data_source] = metrics.items_by_source.get(item.data_source, 0) + 1
            
            # Create response
            response = CollectionResponse(
                success=len(collection_errors) == 0,  # Success if no critical errors
                collection=collection,
                errors=collection_errors,
                warnings=collection_warnings,
                performance_metrics=self._create_performance_metrics(metrics)
            )
            
            logger.info(f"Evidence collection completed: {len(all_evidence)} items collected in {metrics.total_duration_ms}ms")
            return response
            
        except Exception as e:
            metrics.end_time = datetime.utcnow()
            error_msg = f"Unified evidence collection failed: {str(e)}"
            logger.error(error_msg, exc_info=e)
            
            return CollectionResponse(
                success=False,
                errors=[error_msg],
                performance_metrics=self._create_performance_metrics(metrics)
            )
    
    async def _collect_gitlab_evidence(self, request: CollectionRequest, metrics: CollectionMetrics) -> Tuple[List[UnifiedEvidenceItem], List[str]]:
        """Collect evidence from GitLab"""
        start_time = time.time()
        warnings = []
        
        try:
            # Check if GitLab is healthy
            if not self.platform_health.get(PlatformType.GITLAB, PlatformHealth(PlatformType.GITLAB, True, datetime.utcnow())).healthy:
                raise Exception("GitLab platform is currently unhealthy")
            
            # Collect GitLab evidence using existing client
            gitlab_evidence = await self.gitlab_client.get_comprehensive_evidence(
                username=request.username,
                days_back=(datetime.utcnow() - request.since_date).days
            )
            
            # Transform to unified format
            unified_evidence = []
            for item in gitlab_evidence:
                try:
                    unified_item = self._transform_gitlab_item(item, request.team_member_id)
                    unified_evidence.append(unified_item)
                except Exception as e:
                    warnings.append(f"Failed to transform GitLab item {item.id}: {str(e)}")
                    logger.warning(f"GitLab item transformation failed: {e}")
            
            # Record response time
            response_time = int((time.time() - start_time) * 1000)
            metrics.platform_response_times[PlatformType.GITLAB] = response_time
            
            logger.info(f"GitLab collection completed: {len(unified_evidence)} items in {response_time}ms")
            return unified_evidence, warnings
            
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            metrics.platform_response_times[PlatformType.GITLAB] = response_time
            self._update_platform_health(PlatformType.GITLAB, False, str(e))
            raise e
    
    async def _collect_jira_evidence(self, request: CollectionRequest, metrics: CollectionMetrics) -> Tuple[List[UnifiedEvidenceItem], List[str]]:
        """Collect evidence from JIRA with configurable search criteria"""
        start_time = time.time()
        warnings = []
        
        try:
            # Check if JIRA is healthy
            if not self.platform_health.get(PlatformType.JIRA, PlatformHealth(PlatformType.JIRA, True, datetime.utcnow())).healthy:
                raise Exception("JIRA platform is currently unhealthy")
            
            # Create configurable search criteria from request
            search_criteria = self._build_jira_search_criteria(request)
            
            # Collect JIRA evidence using configurable search
            jira_evidence = await self.jira_client.get_issues(
                username=request.username,
                since_date=request.since_date,
                search_criteria=search_criteria
            )
            
            # Transform to unified format
            unified_evidence = []
            for item in jira_evidence:
                try:
                    unified_item = self._transform_jira_item(item, request.team_member_id)
                    unified_evidence.append(unified_item)
                except Exception as e:
                    warnings.append(f"Failed to transform JIRA item {item.id}: {str(e)}")
                    logger.warning(f"JIRA item transformation failed: {e}")
            
            # Record response time
            response_time = int((time.time() - start_time) * 1000)
            metrics.platform_response_times[PlatformType.JIRA] = response_time
            
            logger.info(f"JIRA collection completed: {len(unified_evidence)} items in {response_time}ms")
            logger.info(f"Search criteria used - Project: {search_criteria.project_key}, Sprint: {search_criteria.sprint_name}")
            return unified_evidence, warnings
            
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            metrics.platform_response_times[PlatformType.JIRA] = response_time
            self._update_platform_health(PlatformType.JIRA, False, str(e))
            raise e
    
    def _build_jira_search_criteria(self, request: CollectionRequest) -> JQLSearchCriteria:
        """Build configurable JIRA search criteria from collection request"""
        
        # Determine search scopes based on available parameters
        search_scopes = []
        
        if request.sprint_name:
            search_scopes.append(SearchScope.SPRINT_SPECIFIC)
            logger.info(f"Configured for sprint-specific search: {request.sprint_name}")
        
        search_scopes.extend([SearchScope.USER_ASSIGNED, SearchScope.RECENT_ACTIVITY])
        
        # Create flexible search criteria (NO hardcoded values!)
        return JQLSearchCriteria(
            username=request.username,
            project_key=request.project_key,
            sprint_name=request.sprint_name,
            since_date=request.since_date,
            days_back=(datetime.utcnow() - request.since_date).days,
            search_scopes=search_scopes,
            max_results=request.max_items_per_platform,
            issue_types=request.issue_types,
            statuses=request.statuses,
            priorities=request.priorities,
            labels=request.labels,
            components=request.components,
            custom_jql_filters=request.custom_jql_filters,
            include_open_sprints=True,
            include_unassigned=False
        )
    
    def _transform_gitlab_item(self, gitlab_item, team_member_id: str) -> UnifiedEvidenceItem:
        """Transform GitLab evidence item to unified format"""
        
        # Map GitLab source to unified source
        source_mapping = {
            "gitlab_commit": "gitlab_commit",
            "gitlab_mr": "gitlab_mr"
        }
        
        return UnifiedEvidenceItem(
            id=gitlab_item.id,
            team_member_id=team_member_id,
            source=source_mapping.get(gitlab_item.source, gitlab_item.source),
            title=gitlab_item.title,
            description=gitlab_item.description,
            category=gitlab_item.category,
            evidence_date=gitlab_item.evidence_date,
            source_url=gitlab_item.source_url,
            platform=PlatformType.GITLAB,
            data_source=DataSourceType.MCP if gitlab_item.data_source.value == "mcp" else DataSourceType.API,
            fallback_used=gitlab_item.fallback_used,
            created_at=gitlab_item.created_at,
            metadata={
                **gitlab_item.metadata,
                "original_source": gitlab_item.source,
                "platform_specific": {
                    "gitlab": {
                        "data_source": gitlab_item.data_source.value,
                        "fallback_used": gitlab_item.fallback_used
                    }
                }
            }
        )
    
    def _transform_jira_item(self, jira_item, team_member_id: str) -> UnifiedEvidenceItem:
        """Transform JIRA evidence item to unified format"""
        
        return UnifiedEvidenceItem(
            id=jira_item.id,
            team_member_id=team_member_id,
            source="jira_ticket",
            title=jira_item.title,
            description=jira_item.description,
            category=jira_item.category,
            evidence_date=jira_item.evidence_date,
            source_url=jira_item.source_url,
            platform=PlatformType.JIRA,
            data_source=DataSourceType.MCP if jira_item.data_source.value == "mcp" else DataSourceType.API,
            fallback_used=jira_item.fallback_used,
            created_at=jira_item.created_at,
            metadata={
                **jira_item.metadata,
                "original_source": jira_item.source,
                "platform_specific": {
                    "jira": {
                        "data_source": jira_item.data_source.value,
                        "fallback_used": jira_item.fallback_used
                    }
                }
            }
        )
    
    async def _ensure_platform_health(self):
        """Ensure platform health checks are up to date"""
        now = datetime.utcnow()
        
        if now - self.last_health_check > self.health_check_interval:
            await self._check_all_platform_health()
            self.last_health_check = now
    
    async def _check_all_platform_health(self):
        """Check health of all platforms"""
        logger.info("Performing platform health checks")
        
        # Check GitLab health
        try:
            gitlab_healthy = await self.gitlab_client.check_mcp_health()
            self._update_platform_health(PlatformType.GITLAB, gitlab_healthy)
        except Exception as e:
            self._update_platform_health(PlatformType.GITLAB, False, str(e))
        
        # Check JIRA health
        try:
            jira_healthy = await self.jira_client.health_check()
            self._update_platform_health(PlatformType.JIRA, jira_healthy)
        except Exception as e:
            self._update_platform_health(PlatformType.JIRA, False, str(e))
    
    def _update_platform_health(self, platform: PlatformType, healthy: bool, error_message: Optional[str] = None):
        """Update platform health status"""
        self.platform_health[platform] = PlatformHealth(
            platform=platform,
            healthy=healthy,
            last_check=datetime.utcnow(),
            error_message=error_message
        )
        
        status = "healthy" if healthy else "unhealthy"
        logger.info(f"Platform {platform.value} is {status}")
        if error_message:
            logger.warning(f"Platform {platform.value} error: {error_message}")
    
    def _create_performance_metrics(self, metrics: CollectionMetrics) -> Dict[str, Any]:
        """Create performance metrics dictionary"""
        return {
            "total_duration_ms": metrics.total_duration_ms,
            "total_items_collected": metrics.total_items_collected,
            "items_by_platform": dict(metrics.items_by_platform),
            "items_by_source": dict(metrics.items_by_source),
            "platform_response_times": dict(metrics.platform_response_times),
            "validation_summary": metrics.validation_summary,
            "errors_count": len(metrics.errors_encountered),
            "collection_timestamp": metrics.start_time.isoformat()
        }
    
    async def get_platform_health(self) -> Dict[PlatformType, PlatformHealth]:
        """Get current platform health status"""
        await self._ensure_platform_health()
        return self.platform_health.copy()
    
    async def close(self):
        """Close all platform clients"""
        try:
            await self.jira_client.close()
        except Exception as e:
            logger.warning(f"Error closing JIRA client: {e}")
        
        logger.info("Unified Evidence Service closed")


def create_unified_evidence_service(
    gitlab_token: str,
    gitlab_project_id: str,
    jira_mcp_server_url: str,
    jira_cloud_id: str,
    jira_base_url: str,
    jira_api_token: str,
    jira_user_email: str,
    jira_project_key: Optional[str] = None,
    **kwargs
) -> UnifiedEvidenceService:
    """
    Factory function to create a unified evidence service
    
    This function provides a clean interface for creating the service
    with proper dependency injection and configuration.
    """
    return UnifiedEvidenceService(
        gitlab_token=gitlab_token,
        gitlab_project_id=gitlab_project_id,
        jira_mcp_server_url=jira_mcp_server_url,
        jira_cloud_id=jira_cloud_id,
        jira_base_url=jira_base_url,
        jira_api_token=jira_api_token,
        jira_user_email=jira_user_email,
        jira_project_key=jira_project_key,
        **kwargs
    ) 