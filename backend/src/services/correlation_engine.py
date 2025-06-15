"""
Correlation Engine - Phase 2.1 Implementation
Intelligent cross-reference detection and work story generation

This is the main orchestration service that coordinates all correlation algorithms
to detect relationships between evidence items and generate work stories.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import time

from src.models.correlation_models import (
    EvidenceRelationship,
    WorkStory,
    CorrelationInsights,
    CorrelatedCollection,
    CorrelationRequest,
    CorrelationResponse,
    RelationshipType,
    DetectionMethod,
    WorkStoryStatus
)
from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType
from src.algorithms.jira_gitlab_linker import JiraGitLabLinker
from src.algorithms.confidence_scorer import ConfidenceScorer
from src.algorithms.work_story_grouper import WorkStoryGrouper
from src.algorithms.timeline_analyzer import TimelineAnalyzer
from src.algorithms.technology_detector import TechnologyDetector
from .llm_correlation_service import LLMCorrelationService, create_llm_correlation_service

logger = logging.getLogger(__name__)

class CorrelationEngine:
    """
    Intelligent cross-reference detection and work story generation
    
    This engine coordinates multiple algorithms to:
    1. Detect relationships between GitLab and JIRA evidence
    2. Score relationship confidence
    3. Group related evidence into work stories
    4. Analyze timelines and patterns
    5. Extract technology insights
    """
    
    def __init__(self, enable_llm: bool = True):
        """Initialize the correlation engine with all algorithm components"""
        self.jira_gitlab_linker = JiraGitLabLinker()
        self.confidence_scorer = ConfidenceScorer()
        self.work_story_grouper = WorkStoryGrouper()
        self.timeline_analyzer = TimelineAnalyzer()
        self.technology_detector = TechnologyDetector()
        
        # Configuration
        self.default_confidence_threshold = 0.3
        self.max_processing_time_seconds = 30
        
        # Initialize LLM service (Phase 2.1.2)
        self.enable_llm = enable_llm
        self.llm_service: Optional[LLMCorrelationService] = None
        
        if self.enable_llm:
            try:
                self.llm_service = create_llm_correlation_service()
                logger.info("LLM correlation service initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM service, falling back to rule-based: {e}")
                self.enable_llm = False
        
        logger.info("Correlation Engine initialized successfully")
    
    async def correlate_evidence(self, request: CorrelationRequest) -> CorrelationResponse:
        """
        Main correlation pipeline
        
        Args:
            request: Correlation request with evidence items and parameters
            
        Returns:
            CorrelationResponse with correlated collection and insights
        """
        start_time = time.time()
        logger.info(f"Starting evidence correlation with {len(request.evidence_items or [])} items (LLM enabled: {self.enable_llm})")
        
        try:
            # Validate input
            evidence_items = request.evidence_items or []
            if not evidence_items:
                return CorrelationResponse(
                    success=False,
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    items_processed=0,
                    relationships_detected=0,
                    work_stories_created=0,
                    errors=["No evidence items provided for correlation"]
                )
            
            # Step 1: Detect relationships between evidence items
            logger.info("Step 1: Detecting relationships between evidence items")
            relationships = await self._detect_relationships(evidence_items, request)
            
            # Step 2: Score relationship confidence
            logger.info("Step 2: Scoring relationship confidence")
            scored_relationships = await self._score_relationships(relationships, evidence_items)
            
            # Step 3: Filter by confidence threshold
            filtered_relationships = [
                rel for rel in scored_relationships 
                if rel.confidence_score >= request.confidence_threshold
            ]
            
            # Step 4: Group evidence into work stories
            logger.info("Step 3: Grouping evidence into work stories")
            work_stories = await self._create_work_stories(evidence_items, filtered_relationships, request)
            
            # Step 5: Analyze timelines and patterns
            logger.info("Step 4: Analyzing timelines and patterns")
            if request.analyze_work_patterns:
                work_stories = await self._analyze_work_patterns(work_stories)
            
            # Step 6: Detect technology stacks
            logger.info("Step 5: Detecting technology stacks")
            if request.detect_technology_stack:
                work_stories = await self._detect_technology_stacks(work_stories)
            
            # Step 7: Generate insights
            logger.info("Step 6: Generating correlation insights")
            insights = None
            if request.generate_insights:
                insights = await self._generate_insights(evidence_items, work_stories, filtered_relationships)
            
            # Step 8: LLM Enhancement (NEW - Phase 2.1.2)
            if self.enable_llm and self.llm_service:
                llm_relationships = await self._step_7_llm_enhancement(evidence_items)
                logger.info(f"Step 7 - LLM enhancement: {len(llm_relationships)} additional relationships found")
                
                # Merge LLM relationships with existing ones
                enhanced_relationships = self._merge_relationships(filtered_relationships, llm_relationships)
                logger.info(f"Step 7 - Total after merge: {len(enhanced_relationships)} relationships")
            else:
                logger.info("Step 7 - LLM enhancement skipped (disabled or unavailable)")
            
            # Create correlated collection
            correlated_collection = CorrelatedCollection(
                evidence_items=evidence_items,
                total_evidence_count=len(evidence_items),
                work_stories=work_stories,
                relationships=enhanced_relationships,
                insights=insights,
                processing_time_ms=int((time.time() - start_time) * 1000),
                correlation_metadata={
                    "confidence_threshold": request.confidence_threshold,
                    "total_relationships_detected": len(scored_relationships),
                    "filtered_relationships": len(filtered_relationships),
                    "algorithm_versions": {
                        "jira_gitlab_linker": "1.0.0",
                        "confidence_scorer": "1.0.0",
                        "work_story_grouper": "1.0.0",
                        "timeline_analyzer": "1.0.0",
                        "technology_detector": "1.0.0"
                    },
                    'llm_enabled': self.enable_llm,
                    'correlation_pipeline_version': '2.1.2'
                }
            )
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Correlation complete: {len(work_stories)} work stories, "
                       f"{len(enhanced_relationships)} relationships, "
                       f"{processing_time_ms}ms processing time")
            
            return CorrelationResponse(
                success=True,
                correlated_collection=correlated_collection,
                processing_time_ms=processing_time_ms,
                items_processed=len(evidence_items),
                relationships_detected=len(enhanced_relationships),
                work_stories_created=len(work_stories),
                avg_confidence_score=sum(r.confidence_score for r in enhanced_relationships) / len(enhanced_relationships) if enhanced_relationships else 0.0,
                correlation_coverage=correlated_collection.correlation_coverage
            )
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Correlation engine error: {str(e)}"
            logger.error(error_msg, exc_info=e)
            
            return CorrelationResponse(
                success=False,
                processing_time_ms=processing_time_ms,
                items_processed=len(request.evidence_items or []),
                relationships_detected=0,
                work_stories_created=0,
                errors=[error_msg]
            )
    
    async def _detect_relationships(self, evidence_items: List[UnifiedEvidenceItem], 
                                  request: CorrelationRequest) -> List[EvidenceRelationship]:
        """Detect relationships between evidence items"""
        relationships = []
        
        # Separate GitLab and JIRA items for cross-platform linking
        gitlab_items = [item for item in evidence_items if item.platform == PlatformType.GITLAB]
        jira_items = [item for item in evidence_items if item.platform == PlatformType.JIRA]
        
        logger.info(f"Detecting relationships: {len(gitlab_items)} GitLab items, {len(jira_items)} JIRA items")
        
        # Cross-platform relationship detection
        if gitlab_items and jira_items:
            cross_platform_relationships = await self.jira_gitlab_linker.detect_relationships(
                gitlab_items, jira_items
            )
            relationships.extend(cross_platform_relationships)
        
        # Same-platform relationship detection (future enhancement)
        # This could include duplicate detection within the same platform
        
        logger.info(f"Detected {len(relationships)} initial relationships")
        return relationships
    
    async def _score_relationships(self, relationships: List[EvidenceRelationship],
                                 evidence_items: List[UnifiedEvidenceItem]) -> List[EvidenceRelationship]:
        """Score relationship confidence"""
        evidence_map = {item.id: item for item in evidence_items}
        
        scored_relationships = []
        for relationship in relationships:
            primary_item = evidence_map.get(relationship.primary_evidence_id)
            related_item = evidence_map.get(relationship.related_evidence_id)
            
            if primary_item and related_item:
                confidence_score = await self.confidence_scorer.score_relationship(
                    relationship, primary_item, related_item
                )
                relationship.confidence_score = confidence_score
                scored_relationships.append(relationship)
        
        logger.info(f"Scored {len(scored_relationships)} relationships")
        return scored_relationships
    
    async def _create_work_stories(self, evidence_items: List[UnifiedEvidenceItem],
                                 relationships: List[EvidenceRelationship],
                                 request: CorrelationRequest) -> List[WorkStory]:
        """Group related evidence into work stories"""
        work_stories = await self.work_story_grouper.create_work_stories(
            evidence_items, relationships, request
        )
        
        logger.info(f"Created {len(work_stories)} work stories")
        return work_stories
    
    async def _analyze_work_patterns(self, work_stories: List[WorkStory]) -> List[WorkStory]:
        """Analyze timeline patterns in work stories"""
        for story in work_stories:
            timeline_data = await self.timeline_analyzer.analyze_work_story(story)
            story.timeline.update(timeline_data.get("timeline", {}))
            story.metadata.update(timeline_data.get("patterns", {}))
        
        logger.info(f"Analyzed patterns for {len(work_stories)} work stories")
        return work_stories
    
    async def _detect_technology_stacks(self, work_stories: List[WorkStory]) -> List[WorkStory]:
        """Detect technology stacks in work stories"""
        for story in work_stories:
            technologies = await self.technology_detector.detect_technologies(story)
            story.technology_stack = technologies
            
            # Calculate complexity score based on technology diversity and evidence
            complexity = await self.technology_detector.calculate_complexity(story)
            story.complexity_score = complexity
        
        logger.info(f"Detected technology stacks for {len(work_stories)} work stories")
        return work_stories
    
    async def _generate_insights(self, evidence_items: List[UnifiedEvidenceItem],
                               work_stories: List[WorkStory],
                               relationships: List[EvidenceRelationship]) -> CorrelationInsights:
        """Generate high-level insights from correlation analysis"""
        
        # Calculate basic statistics
        total_work_stories = len(work_stories)
        total_relationships = len(relationships)
        avg_confidence = sum(r.confidence_score for r in relationships) / len(relationships) if relationships else 0.0
        
        # Technology distribution
        technology_distribution = {}
        for story in work_stories:
            for tech in story.technology_stack:
                technology_distribution[tech] = technology_distribution.get(tech, 0) + 1
        
        # Work patterns analysis
        work_patterns = await self.timeline_analyzer.analyze_overall_patterns(work_stories)
        
        # Performance metrics
        sprint_metrics = await self._calculate_sprint_metrics(evidence_items, work_stories)
        
        # Collaboration analysis
        collaboration_score = await self._calculate_collaboration_score(evidence_items, work_stories)
        
        # Analysis period
        if evidence_items:
            dates = [item.evidence_date for item in evidence_items]
            analysis_period = {
                "start": min(dates),
                "end": max(dates)
            }
        else:
            analysis_period = {}
        
        insights = CorrelationInsights(
            total_work_stories=total_work_stories,
            total_relationships=total_relationships,
            avg_confidence_score=avg_confidence,
            technology_distribution=technology_distribution,
            work_patterns=work_patterns,
            sprint_performance_metrics=sprint_metrics,
            collaboration_score=collaboration_score,
            analysis_period=analysis_period
        )
        
        logger.info(f"Generated insights: {total_work_stories} stories, {total_relationships} relationships")
        return insights
    
    async def _calculate_sprint_metrics(self, evidence_items: List[UnifiedEvidenceItem],
                                      work_stories: List[WorkStory]) -> Dict[str, float]:
        """Calculate sprint performance metrics"""
        # This is a placeholder for sprint metrics calculation
        # In a real implementation, this would analyze sprint boundaries,
        # velocity, completion rates, etc.
        
        completed_stories = len([s for s in work_stories if s.status == WorkStoryStatus.COMPLETED])
        total_stories = len(work_stories)
        
        return {
            "completion_rate": completed_stories / total_stories if total_stories > 0 else 0.0,
            "avg_story_duration_days": sum(
                (s.duration.days if s.duration else 0) for s in work_stories
            ) / total_stories if total_stories > 0 else 0.0,
            "cross_platform_stories": len([
                s for s in work_stories if len(s.platforms_involved) > 1
            ]) / total_stories if total_stories > 0 else 0.0
        }
    
    async def _calculate_collaboration_score(self, evidence_items: List[UnifiedEvidenceItem],
                                           work_stories: List[WorkStory]) -> float:
        """Calculate collaboration score based on cross-platform activity"""
        if not work_stories:
            return 0.0
        
        # Count stories with multiple platforms
        cross_platform_stories = len([
            s for s in work_stories if len(s.platforms_involved) > 1
        ])
        
        # Count stories with multiple team members
        multi_member_stories = len([
            s for s in work_stories if len(s.team_members_involved) > 1
        ])
        
        # Calculate collaboration score (0.0 to 1.0)
        collaboration_score = (cross_platform_stories + multi_member_stories) / (len(work_stories) * 2)
        return min(collaboration_score, 1.0)
    
    async def _step_7_llm_enhancement(self, evidence_items: List[UnifiedEvidenceItem]) -> List[EvidenceRelationship]:
        """
        Step 7: LLM-enhanced semantic correlation (NEW - Phase 2.1.2)
        Uses cost-optimized 3-tier pipeline for semantic understanding
        """
        if not self.llm_service:
            logger.warning("LLM service not available for enhancement")
            return []
        
        try:
            logger.info("Starting LLM enhancement step...")
            llm_relationships = await self.llm_service.correlate_evidence_with_llm(evidence_items)
            
            # Add metadata to indicate LLM processing
            for relationship in llm_relationships:
                relationship.metadata = relationship.metadata or {}
                relationship.metadata['correlation_step'] = 'llm_enhancement'
                relationship.metadata['pipeline_version'] = '2.1.2'
            
            # Log usage report
            if hasattr(self.llm_service, 'get_usage_report'):
                usage_report = self.llm_service.get_usage_report()
                logger.info(f"LLM Usage: ${usage_report['current_usage']:.2f}/${usage_report['monthly_budget']:.2f} ({usage_report['budget_utilization']:.1f}%)")
            
            return llm_relationships
            
        except Exception as e:
            logger.error(f"LLM enhancement failed: {e}")
            return []
    
    def _merge_relationships(self, existing_relationships: List[EvidenceRelationship], 
                           llm_relationships: List[EvidenceRelationship]) -> List[EvidenceRelationship]:
        """
        Merge LLM relationships with existing ones, avoiding duplicates
        """
        # Create a set of existing relationship pairs
        existing_pairs = set()
        for rel in existing_relationships:
            pair_key = tuple(sorted([rel.evidence_id_1, rel.evidence_id_2]))
            existing_pairs.add(pair_key)
        
        # Add LLM relationships that don't duplicate existing ones
        merged_relationships = existing_relationships.copy()
        
        for llm_rel in llm_relationships:
            pair_key = tuple(sorted([llm_rel.evidence_id_1, llm_rel.evidence_id_2]))
            
            if pair_key not in existing_pairs:
                # New relationship from LLM
                merged_relationships.append(llm_rel)
                existing_pairs.add(pair_key)
            else:
                # Enhance existing relationship with LLM insights
                for existing_rel in merged_relationships:
                    existing_pair = tuple(sorted([existing_rel.evidence_id_1, existing_rel.evidence_id_2]))
                    if existing_pair == pair_key:
                        # Enhance with LLM metadata
                        existing_rel.metadata = existing_rel.metadata or {}
                        existing_rel.metadata['llm_validation'] = True
                        existing_rel.metadata['llm_confidence'] = llm_rel.confidence_score
                        existing_rel.metadata['llm_insights'] = llm_rel.metadata
                        
                        # Use higher confidence score
                        if llm_rel.confidence_score > existing_rel.confidence_score:
                            existing_rel.confidence_score = llm_rel.confidence_score
                        break
        
        logger.info(f"Merged relationships: {len(existing_relationships)} existing + {len(llm_relationships)} LLM = {len(merged_relationships)} total")
        return merged_relationships
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get correlation engine status and capabilities"""
        return {
            'pipeline_version': '2.1.2',
            'llm_enabled': self.enable_llm,
            'llm_available': self.llm_service is not None,
            'steps': [
                'platform_linking',
                'confidence_scoring',
                'work_story_grouping',
                'timeline_analysis', 
                'technology_detection',
                'pattern_analysis',
                'llm_enhancement'
            ],
            'algorithms': {
                'jira_gitlab_linker': 'active',
                'confidence_scorer': 'active',
                'work_story_grouper': 'active',
                'timeline_analyzer': 'active',
                'technology_detector': 'active',
                'llm_service': 'active' if self.llm_service else 'inactive'
            }
        }
    
    def get_llm_usage_report(self) -> Optional[Dict[str, Any]]:
        """Get LLM usage and cost information"""
        if self.llm_service and hasattr(self.llm_service, 'get_usage_report'):
            return self.llm_service.get_usage_report()
        return None

# Factory function for creating correlation engine
def create_correlation_engine(enable_llm: bool = True) -> CorrelationEngine:
    """Create and configure correlation engine with optional LLM enhancement"""
    return CorrelationEngine(enable_llm=enable_llm) 