"""
Unified Evidence Models for Cross-Platform Correlation
Extends existing EvidenceItem with correlation and validation capabilities
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field, validator
from enum import Enum
from dataclasses import dataclass
import uuid

# Import existing models for compatibility
from ..models.evidence import EvidenceItem as DBEvidenceItem, SourceType, CategoryType

class PlatformType(str, Enum):
    """Supported platforms for evidence collection"""
    GITLAB = "gitlab"
    JIRA = "jira"
    DOCUMENT = "document"

class DataSourceType(str, Enum):
    """Data source type for tracking collection method"""
    MCP = "mcp"
    API = "api"
    MANUAL = "manual"

class ValidationStatus(str, Enum):
    """Evidence validation status"""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    WARNING = "warning"

@dataclass
class ValidationResult:
    """Result of evidence validation"""
    status: ValidationStatus
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]

class UnifiedEvidenceItem(BaseModel):
    """
    Enhanced evidence item with cross-platform correlation capabilities
    Compatible with existing EvidenceItem but adds correlation metadata
    """
    # Core fields (compatible with existing EvidenceItem)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_member_id: str
    source: SourceType
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1, max_length=5000)
    category: CategoryType
    evidence_date: datetime
    source_url: Optional[str] = None
    
    # Enhanced fields for correlation
    platform: PlatformType
    data_source: DataSourceType
    fallback_used: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Correlation metadata
    correlation_id: Optional[str] = None  # Links related evidence across platforms
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Rich metadata for correlation
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Validation
    validation_result: Optional[ValidationResult] = None
    
    @validator('evidence_date', pre=True)
    def parse_evidence_date(cls, v):
        """Parse various date formats"""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                try:
                    return datetime.strptime(v, '%Y-%m-%d')
                except ValueError:
                    return datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        """Ensure title is meaningful"""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """Ensure description is meaningful"""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()
    
    def to_db_evidence_item(self) -> DBEvidenceItem:
        """Convert to database-compatible EvidenceItem"""
        return DBEvidenceItem(
            id=uuid.UUID(self.id),
            team_member_id=uuid.UUID(self.team_member_id),
            title=self.title,
            description=self.description,
            source=self.source,
            category=self.category,
            evidence_date=self.evidence_date.date(),
            source_url=self.source_url,
            metadata=self.metadata,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

class EvidenceCollection(BaseModel):
    """Collection of evidence items with metadata"""
    items: List[UnifiedEvidenceItem]
    total_count: int
    platform_counts: Dict[PlatformType, int] = Field(default_factory=dict)
    source_counts: Dict[DataSourceType, int] = Field(default_factory=dict)
    category_counts: Dict[CategoryType, int] = Field(default_factory=dict)
    date_range: Dict[str, datetime] = Field(default_factory=dict)
    collection_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        self._calculate_metadata()
    
    def _calculate_metadata(self):
        """Calculate collection metadata"""
        if not self.items:
            return
        
        # Platform counts
        for item in self.items:
            self.platform_counts[item.platform] = self.platform_counts.get(item.platform, 0) + 1
            self.source_counts[item.data_source] = self.source_counts.get(item.data_source, 0) + 1
            self.category_counts[item.category] = self.category_counts.get(item.category, 0) + 1
        
        # Date range
        dates = [item.evidence_date for item in self.items]
        self.date_range = {
            "earliest": min(dates),
            "latest": max(dates)
        }
        
        # Collection metadata
        self.collection_metadata = {
            "fallback_usage": sum(1 for item in self.items if item.fallback_used),
            "validation_pending": sum(1 for item in self.items if item.validation_result and item.validation_result.status == ValidationStatus.PENDING),
            "avg_confidence": sum(item.confidence_score for item in self.items if item.confidence_score) / len([item for item in self.items if item.confidence_score]) if any(item.confidence_score for item in self.items) else None
        }

class CollectionRequest(BaseModel):
    """Request for evidence collection with configurable search criteria"""
    team_member_id: str
    username: str  # Platform username
    since_date: datetime
    platforms: List[PlatformType] = Field(default=[PlatformType.GITLAB, PlatformType.JIRA])
    max_items_per_platform: int = Field(default=100, ge=1, le=500)
    include_metadata: bool = True
    validate_items: bool = True
    
    # Configurable search parameters (replaces hardcoded values)
    project_key: Optional[str] = None  # JIRA project key (e.g., "TEST")
    sprint_name: Optional[str] = None  # Sprint name (e.g., "Flights ASI Sprint 10")
    issue_types: Optional[List[str]] = None  # Issue types to filter
    statuses: Optional[List[str]] = None  # Issue statuses to filter
    priorities: Optional[List[str]] = None  # Issue priorities to filter
    labels: Optional[List[str]] = None  # Labels to filter
    components: Optional[List[str]] = None  # Components to filter
    custom_jql_filters: Optional[List[str]] = None  # Custom JQL filters
    
    @validator('since_date')
    def validate_since_date(cls, v):
        """Ensure since_date is not in the future"""
        if v > datetime.utcnow():
            raise ValueError("since_date cannot be in the future")
        return v
    
    @validator('platforms')
    def validate_platforms(cls, v):
        """Ensure at least one platform is selected"""
        if not v:
            raise ValueError("At least one platform must be selected")
        return v

class CollectionResponse(BaseModel):
    """Response from evidence collection"""
    success: bool
    collection: Optional[EvidenceCollection] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def has_errors(self) -> bool:
        return bool(self.errors)
    
    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)

class EvidenceValidator:
    """Validates evidence items for quality and completeness"""
    
    @staticmethod
    def validate_item(item: UnifiedEvidenceItem) -> ValidationResult:
        """Validate a single evidence item"""
        errors = []
        warnings = []
        metadata = {}
        
        # Required field validation
        if not item.title or len(item.title.strip()) < 3:
            errors.append("Title must be at least 3 characters long")
        
        if not item.description or len(item.description.strip()) < 10:
            errors.append("Description must be at least 10 characters long")
        
        if not item.team_member_id:
            errors.append("team_member_id is required")
        
        # Quality checks
        if item.title == item.description[:len(item.title)]:
            warnings.append("Title and description appear to be identical")
        
        if not item.source_url:
            warnings.append("No source URL provided - reduces traceability")
        
                # Date validation (handle timezone-aware dates)
        current_time = datetime.utcnow()
        evidence_date = item.evidence_date
        
        # Make both timezone-naive for comparison if needed
        if evidence_date.tzinfo is not None:
            evidence_date = evidence_date.replace(tzinfo=None)
        if current_time.tzinfo is not None:
            current_time = current_time.replace(tzinfo=None)
            
        if evidence_date > current_time:
            errors.append("Evidence date cannot be in the future")
        
        if item.evidence_date < datetime.utcnow() - timedelta(days=365):
            warnings.append("Evidence is more than 1 year old")
        
        # Metadata validation
        metadata['validation_timestamp'] = datetime.utcnow().isoformat()
        metadata['character_counts'] = {
            'title': len(item.title),
            'description': len(item.description)
        }
        
        # Determine status
        if errors:
            status = ValidationStatus.INVALID
        elif warnings:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.VALID
        
        return ValidationResult(
            status=status,
            errors=errors,
            warnings=warnings,
            metadata=metadata
        )
    
    @staticmethod
    def validate_collection(collection: EvidenceCollection) -> Dict[str, Any]:
        """Validate an entire evidence collection"""
        validation_summary = {
            'total_items': len(collection.items),
            'valid_items': 0,
            'invalid_items': 0,
            'warning_items': 0,
            'common_errors': {},
            'common_warnings': {}
        }
        
        for item in collection.items:
            if not item.validation_result:
                item.validation_result = EvidenceValidator.validate_item(item)
            
            if item.validation_result.status == ValidationStatus.VALID:
                validation_summary['valid_items'] += 1
            elif item.validation_result.status == ValidationStatus.INVALID:
                validation_summary['invalid_items'] += 1
            elif item.validation_result.status == ValidationStatus.WARNING:
                validation_summary['warning_items'] += 1
            
            # Track common issues
            for error in item.validation_result.errors:
                validation_summary['common_errors'][error] = validation_summary['common_errors'].get(error, 0) + 1
            
            for warning in item.validation_result.warnings:
                validation_summary['common_warnings'][warning] = validation_summary['common_warnings'].get(warning, 0) + 1
        
        return validation_summary 