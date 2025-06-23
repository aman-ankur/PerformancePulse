"""
Correlation Models for Intelligent Cross-Reference Detection
Phase 2.1 Implementation - Core data models for evidence correlation
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator, model_validator
from enum import Enum
import uuid

from .unified_evidence import UnifiedEvidenceItem, PlatformType

class RelationshipType(str, Enum):
    """Types of relationships between evidence items"""
    SOLVES = "solves"  # GitLab MR solves JIRA ticket
    REFERENCES = "references"  # Evidence references another item
    RELATED_TO = "related_to"  # General relationship
    DUPLICATE = "duplicate"  # Same work across platforms
    SEQUENTIAL = "sequential"  # Work done in sequence
    CAUSAL = "causal"  # One item caused another
    SEMANTIC_SIMILARITY = "semantic_similarity"  # Relationship inferred via LLM/NLP

class DetectionMethod(str, Enum):
    """Methods used to detect relationships"""
    ISSUE_KEY = "issue_key"  # JIRA key found in GitLab content
    BRANCH_NAME = "branch_name"  # Branch name contains ticket reference
    CONTENT_ANALYSIS = "content_analysis"  # Semantic similarity
    TEMPORAL_PROXIMITY = "temporal_proximity"  # Time-based correlation
    AUTHOR_CORRELATION = "author_correlation"  # Same author
    MANUAL = "manual"  # Manually specified
    LLM_SEMANTIC = "llm_semantic"  # Semantic relationship detected by LLM

class WorkStoryStatus(str, Enum):
    """Status of work stories"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"

class EvidenceRelationship(BaseModel):
    """Relationship between two evidence items"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    primary_evidence_id: str
    related_evidence_id: str
    relationship_type: RelationshipType
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    detection_method: DetectionMethod
    evidence_summary: str = ""  # Human-readable relationship description
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.evidence_summary:
            self.evidence_summary = f"{self.relationship_type} relationship detected via {self.detection_method}"

class WorkStory(BaseModel):
    """Grouped related evidence forming a coherent work narrative"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str  # e.g., "TEST-1234: Authentication Bug Fix"
    description: str = ""
    evidence_items: List[UnifiedEvidenceItem] = Field(default_factory=list)
    relationships: List[EvidenceRelationship] = Field(default_factory=list)
    
    # Primary context
    primary_jira_ticket: Optional[str] = None
    primary_platform: Optional[PlatformType] = None
    
    # Timeline information
    timeline: Dict[str, datetime] = Field(default_factory=dict)  # start, end, key_milestones
    duration: Optional[timedelta] = None
    
    # Work characteristics
    technology_stack: List[str] = Field(default_factory=list)
    complexity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    team_members_involved: List[str] = Field(default_factory=list)
    
    # Status and metrics
    status: WorkStoryStatus = WorkStoryStatus.UNKNOWN
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Work story title cannot be empty")
        return v.strip()
    
    @property
    def evidence_count(self) -> int:
        """Number of evidence items in this work story"""
        return len(self.evidence_items)
    
    @property
    def platforms_involved(self) -> List[PlatformType]:
        """List of platforms involved in this work story"""
        return list(set(item.platform for item in self.evidence_items))
    
    @property
    def date_range(self) -> Dict[str, datetime]:
        """Date range of evidence in this work story"""
        if not self.evidence_items:
            return {}
        
        dates = [item.evidence_date for item in self.evidence_items]
        return {
            "start": min(dates),
            "end": max(dates)
        }
    
    def add_evidence(self, evidence: UnifiedEvidenceItem):
        """Add evidence item to this work story"""
        if evidence not in self.evidence_items:
            self.evidence_items.append(evidence)
            self.updated_at = datetime.utcnow()
    
    def add_relationship(self, relationship: EvidenceRelationship):
        """Add relationship to this work story"""
        if relationship not in self.relationships:
            self.relationships.append(relationship)
            self.updated_at = datetime.utcnow()

    # ------------------------------------------------------------------
    # Derived metrics / convenience helpers
    # ------------------------------------------------------------------

    @property
    def confidence_score(self) -> float:
        """Average confidence of relationships in this work-story.

        This is provided mainly for logging / API convenience so that
        callers don't crash if they try to access *story.confidence_score*.
        If the story currently has no relationships it returns **0.0**.
        """
        if not self.relationships:
            return 0.0
        return sum(r.confidence_score for r in self.relationships) / len(self.relationships)

class TechnologyInsight(BaseModel):
    """Technology usage insights from work evidence"""
    technology: str
    usage_count: int
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    evidence_sources: List[str] = Field(default_factory=list)  # Evidence IDs
    first_seen: datetime
    last_seen: datetime

class WorkPattern(BaseModel):
    """Detected work patterns"""
    pattern_type: str  # e.g., "commit_frequency", "review_cycle", "ticket_resolution"
    description: str
    frequency: float  # Pattern frequency (e.g., commits per day)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    evidence_count: int
    time_period: Dict[str, datetime]  # start, end
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CorrelationInsights(BaseModel):
    """High-level insights from correlation analysis"""
    # Summary statistics
    total_work_stories: int
    total_relationships: int
    avg_confidence_score: float = Field(..., ge=0.0, le=1.0)
    
    # Technology insights
    technology_distribution: Dict[str, int] = Field(default_factory=dict)
    technology_insights: List[TechnologyInsight] = Field(default_factory=list)
    
    # Work patterns
    work_patterns: List[WorkPattern] = Field(default_factory=list)
    work_pattern_summary: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance metrics
    sprint_performance_metrics: Dict[str, float] = Field(default_factory=dict)
    productivity_indicators: Dict[str, Any] = Field(default_factory=dict)
    
    # Collaboration insights
    collaboration_score: float = Field(default=0.0, ge=0.0, le=1.0)
    cross_platform_activity: Dict[str, int] = Field(default_factory=dict)
    
    # Quality indicators
    code_review_participation: float = Field(default=0.0, ge=0.0, le=1.0)
    documentation_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Timeline insights
    analysis_period: Dict[str, datetime] = Field(default_factory=dict)
    peak_activity_periods: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    analysis_version: str = "2.1.0"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CorrelatedCollection(BaseModel):
    """Enhanced evidence collection with correlation data"""
    # Base collection data
    evidence_items: List[UnifiedEvidenceItem]
    total_evidence_count: int
    
    # Correlation data
    work_stories: List[WorkStory] = Field(default_factory=list)
    relationships: List[EvidenceRelationship] = Field(default_factory=list)
    insights: Optional[CorrelationInsights] = None
    
    # Processing metadata
    correlation_metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time_ms: Optional[int] = None
    correlation_version: str = "2.1.0"
    
    @property
    def work_story_count(self) -> int:
        """Number of work stories generated"""
        return len(self.work_stories)
    
    @property
    def relationship_count(self) -> int:
        """Number of relationships detected"""
        return len(self.relationships)
    
    @property
    def correlation_coverage(self) -> float:
        """Percentage of evidence items that are part of work stories"""
        if not self.evidence_items:
            return 0.0
        
        correlated_items = set()
        for story in self.work_stories:
            for item in story.evidence_items:
                correlated_items.add(item.id)
        
        return len(correlated_items) / len(self.evidence_items) * 100.0

class CorrelationRequest(BaseModel):
    """Request for evidence correlation analysis"""
    evidence_collection_id: Optional[str] = None  # If correlating existing collection
    team_member_id: Optional[str] = None  # Team member ID to fetch evidence for
    evidence_items: Optional[List[UnifiedEvidenceItem]] = None  # Direct evidence input
    
    # Correlation parameters
    confidence_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    max_work_stories: int = Field(default=50, ge=1, le=200)
    include_low_confidence: bool = False
    
    # Analysis options
    detect_technology_stack: bool = True
    analyze_work_patterns: bool = True
    generate_insights: bool = True
    
    # Filtering options
    min_evidence_per_story: int = Field(default=2, ge=1)
    max_story_duration_days: int = Field(default=90, ge=1)
    
    @model_validator(mode='after')
    def validate_input_source(self):
        """Validate that at least one input source is provided"""
        if not any([self.evidence_collection_id, self.team_member_id, self.evidence_items]):
            raise ValueError("Must provide either evidence_collection_id, team_member_id, or evidence_items")
        return self

class CorrelationResponse(BaseModel):
    """Response from correlation analysis"""
    success: bool
    correlated_collection: Optional[CorrelatedCollection] = None
    
    # Processing information
    processing_time_ms: int
    items_processed: int
    relationships_detected: int
    work_stories_created: int
    
    # Quality metrics
    avg_confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    correlation_coverage: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Error handling
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    # Metadata
    correlation_version: str = "2.1.0"
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def has_errors(self) -> bool:
        """Check if response has errors"""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if response has warnings"""
        return len(self.warnings) > 0 