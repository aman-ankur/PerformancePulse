"""Unit tests for correlation models"""

import pytest
from datetime import datetime, timedelta
from typing import List
import uuid

from src.models.correlation_models import (
    RelationshipType,
    DetectionMethod,
    WorkStoryStatus,
    EvidenceRelationship,
    WorkStory,
    TechnologyInsight,
    WorkPattern,
    CorrelationInsights,
    CorrelatedCollection,
    CorrelationRequest,
    CorrelationResponse
)
from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType, DataSourceType


class TestRelationshipType:
    """Test RelationshipType enum"""
    
    def test_relationship_types(self):
        """Test all relationship type values"""
        assert RelationshipType.SOLVES == "solves"
        assert RelationshipType.REFERENCES == "references"
        assert RelationshipType.RELATED_TO == "related_to"
        assert RelationshipType.DUPLICATE == "duplicate"
        assert RelationshipType.SEQUENTIAL == "sequential"
        assert RelationshipType.CAUSAL == "causal"


class TestDetectionMethod:
    """Test DetectionMethod enum"""
    
    def test_detection_methods(self):
        """Test all detection method values"""
        assert DetectionMethod.ISSUE_KEY == "issue_key"
        assert DetectionMethod.BRANCH_NAME == "branch_name"
        assert DetectionMethod.CONTENT_ANALYSIS == "content_analysis"
        assert DetectionMethod.TEMPORAL_PROXIMITY == "temporal_proximity"
        assert DetectionMethod.AUTHOR_CORRELATION == "author_correlation"
        assert DetectionMethod.MANUAL == "manual"


class TestEvidenceRelationship:
    """Test EvidenceRelationship model"""
    
    def test_create_relationship(self):
        """Test creating a basic relationship"""
        rel = EvidenceRelationship(
            primary_evidence_id="item1",
            related_evidence_id="item2",
            relationship_type=RelationshipType.SOLVES,
            confidence_score=0.9,
            detection_method=DetectionMethod.ISSUE_KEY
        )
        
        assert rel.primary_evidence_id == "item1"
        assert rel.related_evidence_id == "item2"
        assert rel.relationship_type == RelationshipType.SOLVES
        assert rel.confidence_score == 0.9
        assert rel.detection_method == DetectionMethod.ISSUE_KEY
        assert rel.id is not None
        assert rel.detected_at is not None
        assert "solves relationship detected via issue_key" in rel.evidence_summary
    
    def test_relationship_validation(self):
        """Test relationship validation"""
        # Test confidence score bounds
        with pytest.raises(ValueError):
            EvidenceRelationship(
                primary_evidence_id="item1",
                related_evidence_id="item2",
                relationship_type=RelationshipType.SOLVES,
                confidence_score=1.5,  # Invalid: > 1.0
                detection_method=DetectionMethod.ISSUE_KEY
            )
        
        with pytest.raises(ValueError):
            EvidenceRelationship(
                primary_evidence_id="item1",
                related_evidence_id="item2",
                relationship_type=RelationshipType.SOLVES,
                confidence_score=-0.1,  # Invalid: < 0.0
                detection_method=DetectionMethod.ISSUE_KEY
            )
    
    def test_custom_evidence_summary(self):
        """Test custom evidence summary"""
        rel = EvidenceRelationship(
            primary_evidence_id="item1",
            related_evidence_id="item2",
            relationship_type=RelationshipType.SOLVES,
            confidence_score=0.9,
            detection_method=DetectionMethod.ISSUE_KEY,
            evidence_summary="Custom summary"
        )
        
        assert rel.evidence_summary == "Custom summary"


class TestWorkStory:
    """Test WorkStory model"""
    
    def create_test_evidence(self) -> List[UnifiedEvidenceItem]:
        """Create test evidence items"""
        return [
            UnifiedEvidenceItem(
                team_member_id="user1",
                source="jira_ticket",
                title="TEST-123: Bug fix",
                description="Fix authentication bug",
                category="technical",
                evidence_date=datetime.now() - timedelta(days=2),
                platform=PlatformType.JIRA,
                data_source=DataSourceType.API,
                metadata={"key": "TEST-123"}
            ),
            UnifiedEvidenceItem(
                team_member_id="user1",
                source="gitlab_commit",
                title="Fix auth bug",
                description="Fixed authentication issue",
                category="technical",
                evidence_date=datetime.now() - timedelta(days=1),
                platform=PlatformType.GITLAB,
                data_source=DataSourceType.API,
                metadata={"branch": "feature/TEST-123"}
            )
        ]
    
    def test_create_work_story(self):
        """Test creating a work story"""
        evidence_items = self.create_test_evidence()
        
        story = WorkStory(
            title="TEST-123: Authentication Bug Fix",
            description="Fix authentication bug in login system",
            evidence_items=evidence_items,
            primary_jira_ticket="TEST-123",
            technology_stack=["Python", "FastAPI"]
        )
        
        assert story.title == "TEST-123: Authentication Bug Fix"
        assert len(story.evidence_items) == 2
        assert story.primary_jira_ticket == "TEST-123"
        assert "Python" in story.technology_stack
        assert story.status == WorkStoryStatus.UNKNOWN
        assert story.id is not None
    
    def test_work_story_properties(self):
        """Test work story computed properties"""
        evidence_items = self.create_test_evidence()
        
        story = WorkStory(
            title="Test Story",
            evidence_items=evidence_items
        )
        
        assert story.evidence_count == 2
        assert PlatformType.JIRA in story.platforms_involved
        assert PlatformType.GITLAB in story.platforms_involved
        
        date_range = story.date_range
        assert "start" in date_range
        assert "end" in date_range
    
    def test_add_evidence(self):
        """Test adding evidence to work story"""
        story = WorkStory(title="Test Story")
        evidence = self.create_test_evidence()[0]
        
        initial_count = story.evidence_count
        story.add_evidence(evidence)
        
        assert story.evidence_count == initial_count + 1
        assert evidence in story.evidence_items
    
    def test_add_relationship(self):
        """Test adding relationship to work story"""
        story = WorkStory(title="Test Story")
        
        rel = EvidenceRelationship(
            primary_evidence_id="item1",
            related_evidence_id="item2",
            relationship_type=RelationshipType.SOLVES,
            confidence_score=0.9,
            detection_method=DetectionMethod.ISSUE_KEY
        )
        
        initial_count = len(story.relationships)
        story.add_relationship(rel)
        
        assert len(story.relationships) == initial_count + 1
        assert rel in story.relationships
    
    def test_title_validation(self):
        """Test work story title validation"""
        with pytest.raises(ValueError):
            WorkStory(title="")  # Empty title
        
        with pytest.raises(ValueError):
            WorkStory(title="   ")  # Whitespace only


class TestTechnologyInsight:
    """Test TechnologyInsight model"""
    
    def test_create_technology_insight(self):
        """Test creating technology insight"""
        insight = TechnologyInsight(
            technology="Python",
            usage_count=5,
            confidence_score=0.8,
            evidence_sources=["item1", "item2"],
            first_seen=datetime.now() - timedelta(days=10),
            last_seen=datetime.now()
        )
        
        assert insight.technology == "Python"
        assert insight.usage_count == 5
        assert insight.confidence_score == 0.8
        assert len(insight.evidence_sources) == 2


class TestWorkPattern:
    """Test WorkPattern model"""
    
    def test_create_work_pattern(self):
        """Test creating work pattern"""
        pattern = WorkPattern(
            pattern_type="commit_frequency",
            description="High commit frequency detected",
            frequency=3.5,
            confidence_score=0.9,
            evidence_count=10,
            time_period={
                "start": datetime.now() - timedelta(days=7),
                "end": datetime.now()
            }
        )
        
        assert pattern.pattern_type == "commit_frequency"
        assert pattern.frequency == 3.5
        assert pattern.evidence_count == 10


class TestCorrelationRequest:
    """Test CorrelationRequest model"""
    
    def test_create_request_with_evidence_items(self):
        """Test creating request with evidence items"""
        evidence_items = [
            UnifiedEvidenceItem(
                team_member_id="user1",
                source="jira_ticket",
                title="Test",
                description="Test description",
                category="technical",
                evidence_date=datetime.now(),
                platform=PlatformType.JIRA,
                data_source=DataSourceType.API
            )
        ]
        
        request = CorrelationRequest(evidence_items=evidence_items)
        
        assert request.evidence_items == evidence_items
        assert request.evidence_collection_id is None
        assert request.confidence_threshold == 0.3
        assert request.detect_technology_stack is True
    
    def test_create_request_with_collection_id(self):
        """Test creating request with collection ID"""
        request = CorrelationRequest(evidence_collection_id="collection123")
        
        assert request.evidence_collection_id == "collection123"
        assert request.evidence_items is None
    
    def test_request_validation_error(self):
        """Test request validation fails when neither source is provided"""
        with pytest.raises(ValueError, match="Either evidence_collection_id or evidence_items must be provided"):
            CorrelationRequest()
    
    def test_request_parameters(self):
        """Test request parameters"""
        request = CorrelationRequest(
            evidence_collection_id="test",
            confidence_threshold=0.5,
            max_work_stories=25,
            include_low_confidence=True,
            detect_technology_stack=False,
            analyze_work_patterns=False,
            generate_insights=False,
            min_evidence_per_story=3,
            max_story_duration_days=30
        )
        
        assert request.confidence_threshold == 0.5
        assert request.max_work_stories == 25
        assert request.include_low_confidence is True
        assert request.detect_technology_stack is False
        assert request.min_evidence_per_story == 3
        assert request.max_story_duration_days == 30


class TestCorrelationResponse:
    """Test CorrelationResponse model"""
    
    def test_create_successful_response(self):
        """Test creating successful response"""
        response = CorrelationResponse(
            success=True,
            processing_time_ms=100,
            items_processed=5,
            relationships_detected=3,
            work_stories_created=2,
            avg_confidence_score=0.8,
            correlation_coverage=80.0
        )
        
        assert response.success is True
        assert response.processing_time_ms == 100
        assert response.items_processed == 5
        assert response.relationships_detected == 3
        assert response.work_stories_created == 2
        assert response.avg_confidence_score == 0.8
        assert response.correlation_coverage == 80.0
        assert response.has_errors is False
        assert response.has_warnings is False
    
    def test_response_with_errors(self):
        """Test response with errors"""
        response = CorrelationResponse(
            success=False,
            processing_time_ms=50,
            items_processed=0,
            relationships_detected=0,
            work_stories_created=0,
            errors=["Test error", "Another error"],
            warnings=["Test warning"]
        )
        
        assert response.success is False
        assert response.has_errors is True
        assert response.has_warnings is True
        assert len(response.errors) == 2
        assert len(response.warnings) == 1


class TestCorrelatedCollection:
    """Test CorrelatedCollection model"""
    
    def test_create_correlated_collection(self):
        """Test creating correlated collection"""
        evidence_items = [
            UnifiedEvidenceItem(
                team_member_id="user1",
                source="jira_ticket",
                title="Test",
                description="Test description",
                category="technical",
                evidence_date=datetime.now(),
                platform=PlatformType.JIRA,
                data_source=DataSourceType.API
            )
        ]
        
        collection = CorrelatedCollection(
            evidence_items=evidence_items,
            total_evidence_count=1
        )
        
        assert len(collection.evidence_items) == 1
        assert collection.total_evidence_count == 1
        assert collection.work_story_count == 0
        assert collection.relationship_count == 0
        assert collection.correlation_coverage == 0.0
    
    def test_correlation_coverage_calculation(self):
        """Test correlation coverage calculation"""
        evidence_items = [
            UnifiedEvidenceItem(
                id="item1",
                team_member_id="user1",
                source="jira_ticket",
                title="Test 1",
                description="Test description",
                category="technical",
                evidence_date=datetime.now(),
                platform=PlatformType.JIRA,
                data_source=DataSourceType.API
            ),
            UnifiedEvidenceItem(
                id="item2",
                team_member_id="user1",
                source="gitlab_commit",
                title="Test 2",
                description="Test description",
                category="technical",
                evidence_date=datetime.now(),
                platform=PlatformType.GITLAB,
                data_source=DataSourceType.API
            )
        ]
        
        work_story = WorkStory(
            title="Test Story",
            evidence_items=[evidence_items[0]]  # Only first item is correlated
        )
        
        collection = CorrelatedCollection(
            evidence_items=evidence_items,
            total_evidence_count=2,
            work_stories=[work_story]
        )
        
        # 1 out of 2 items correlated = 50%
        assert collection.correlation_coverage == 50.0 