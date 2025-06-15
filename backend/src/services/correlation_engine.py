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
    
    def __init__(self):
        """Initialize the correlation engine with all algorithm components"""
        self.jira_gitlab_linker = JiraGitLabLinker()
        self.confidence_scorer = ConfidenceScorer()
        self.work_story_grouper = WorkStoryGrouper()
        self.timeline_analyzer = TimelineAnalyzer()
        self.technology_detector = TechnologyDetector()
        
        # Configuration
        self.default_confidence_threshold = 0.3
        self.max_processing_time_seconds = 30
        
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
        logger.info(f"Starting evidence correlation with {len(request.evidence_items or [])} items")
        
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
            
            # Create correlated collection
            correlated_collection = CorrelatedCollection(
                evidence_items=evidence_items,
                total_evidence_count=len(evidence_items),
                work_stories=work_stories,
                relationships=filtered_relationships,
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
                    }
                }
            )
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Correlation complete: {len(work_stories)} work stories, "
                       f"{len(filtered_relationships)} relationships, "
                       f"{processing_time_ms}ms processing time")
            
            return CorrelationResponse(
                success=True,
                correlated_collection=correlated_collection,
                processing_time_ms=processing_time_ms,
                items_processed=len(evidence_items),
                relationships_detected=len(filtered_relationships),
                work_stories_created=len(work_stories),
                avg_confidence_score=sum(r.confidence_score for r in filtered_relationships) / len(filtered_relationships) if filtered_relationships else 0.0,
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

# Factory function for easy instantiation
def create_correlation_engine() -> CorrelationEngine:
    """Create a new correlation engine instance"""
    return CorrelationEngine() 