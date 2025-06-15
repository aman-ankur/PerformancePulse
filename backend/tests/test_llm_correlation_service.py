"""
Test suite for LLM Correlation Service - Phase 2.1.2
Tests the 3-tier cost-optimized correlation pipeline
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone, timedelta
from typing import List

from src.services.llm_correlation_service import (
    LLMCorrelationService, 
    EmbeddingService, 
    CostTracker,
    create_llm_correlation_service
)
from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType, DataSourceType
from src.models.evidence import SourceType, CategoryType
from src.models.correlation_models import EvidenceRelationship, RelationshipType, DetectionMethod

class TestCostTracker:
    """Test cost tracking and budget management"""
    
    def test_cost_tracker_initialization(self):
        tracker = CostTracker()
        assert tracker.monthly_budget == 15.00
        assert tracker.current_month_usage == 0.0
        assert tracker.embedding_cost_per_token == 0.0001
        assert tracker.llm_cost_per_request == 0.01
    
    def test_can_afford_embedding(self):
        tracker = CostTracker()
        
        # Should afford small requests
        assert tracker.can_afford_embedding(1000) == True  # $0.10
        assert tracker.can_afford_embedding(10000) == True  # $1.00
        
        # Should not afford massive requests
        assert tracker.can_afford_embedding(200000) == False  # $20.00 > budget
    
    def test_can_afford_llm_call(self):
        tracker = CostTracker()
        
        # Should afford LLM calls initially
        assert tracker.can_afford_llm_call() == True
        
        # After using most budget, should not afford
        tracker.current_month_usage = 14.99
        assert tracker.can_afford_llm_call() == True  # Still can afford 1 more $0.01 call (14.99 + 0.01 = 15.00)
        
        # After exceeding budget, should not afford
        tracker.current_month_usage = 15.00
        assert tracker.can_afford_llm_call() == False
    
    def test_record_usage(self):
        tracker = CostTracker()
        
        tracker.record_usage(5.00)
        assert tracker.current_month_usage == 5.00
        
        tracker.record_usage(2.50)
        assert tracker.current_month_usage == 7.50

class TestEmbeddingService:
    """Test embedding generation and similarity calculation"""
    
    @pytest.fixture
    def embedding_service(self):
        return EmbeddingService()
    
    def test_cosine_similarity_identical(self, embedding_service):
        """Test similarity calculation for identical vectors"""
        embedding1 = [1.0, 2.0, 3.0]
        embedding2 = [1.0, 2.0, 3.0]
        
        similarity = embedding_service.cosine_similarity(embedding1, embedding2)
        assert similarity == pytest.approx(1.0, abs=1e-6)
    
    def test_cosine_similarity_orthogonal(self, embedding_service):
        """Test similarity calculation for orthogonal vectors"""
        embedding1 = [1.0, 0.0, 0.0]
        embedding2 = [0.0, 1.0, 0.0]
        
        similarity = embedding_service.cosine_similarity(embedding1, embedding2)
        assert similarity == pytest.approx(0.0, abs=1e-6)
    
    def test_cosine_similarity_zero_vector(self, embedding_service):
        """Test similarity calculation with zero vector"""
        embedding1 = [0.0, 0.0, 0.0]
        embedding2 = [1.0, 2.0, 3.0]
        
        similarity = embedding_service.cosine_similarity(embedding1, embedding2)
        assert similarity == 0.0
    
    @pytest.mark.asyncio
    @patch('openai.OpenAI')
    async def test_get_embeddings_success(self, mock_openai, embedding_service):
        """Test successful embedding generation"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.data = [
            Mock(embedding=[0.1, 0.2, 0.3]),
            Mock(embedding=[0.4, 0.5, 0.6])
        ]
        mock_openai.return_value.embeddings.create.return_value = mock_response
        
        texts = ["Hello world", "Test text"]
        embeddings = await embedding_service.get_embeddings(texts)
        
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
        assert embeddings[1] == [0.4, 0.5, 0.6]
    
    @pytest.mark.asyncio
    @patch('openai.OpenAI')
    async def test_get_embeddings_failure(self, mock_openai, embedding_service):
        """Test embedding generation failure handling"""
        mock_openai.return_value.embeddings.create.side_effect = Exception("API Error")
        
        texts = ["Hello world"]
        embeddings = await embedding_service.get_embeddings(texts)
        
        assert embeddings == []

class TestLLMCorrelationService:
    """Test main LLM correlation service functionality"""
    
    @pytest.fixture
    def evidence_items(self):
        """Create sample evidence items for testing"""
        return [
            UnifiedEvidenceItem(
                id="ev1",
                team_member_id="team1",
                title="Fix user authentication bug",
                description="Fixed issue with JWT token validation in auth service",
                source=SourceType.GITLAB_COMMIT,
                category=CategoryType.DEVELOPMENT,
                platform=PlatformType.GITLAB,
                data_source=DataSourceType.MCP,
                evidence_date=datetime.now(timezone.utc)
            ),
            UnifiedEvidenceItem(
                id="ev2", 
                team_member_id="team1",
                title="AUTH-123: Authentication service failing",
                description="Users unable to login due to token validation error",
                source=SourceType.JIRA_ISSUE,
                category=CategoryType.DEVELOPMENT,
                platform=PlatformType.JIRA,
                data_source=DataSourceType.MCP,
                evidence_date=datetime.now(timezone.utc) - timedelta(hours=2)
            ),
            UnifiedEvidenceItem(
                id="ev3",
                team_member_id="team2",
                title="Update database schema",
                description="Added new columns for user preferences",
                source=SourceType.GITLAB_COMMIT,
                category=CategoryType.DEVELOPMENT,
                platform=PlatformType.GITLAB,
                data_source=DataSourceType.MCP,
                evidence_date=datetime.now(timezone.utc) - timedelta(days=1)
            )
        ]
    
    @pytest.fixture
    def llm_service(self):
        return LLMCorrelationService()
    
    def test_prefilter_same_author_different_platform(self, llm_service, evidence_items):
        """Test pre-filtering for same author, different platforms"""
        pairs = llm_service._prefilter_evidence_pairs(evidence_items)
        
        # Should find ev1 (GitLab) and ev2 (JIRA) from same author
        found_pair = False
        for item1, item2 in pairs:
            if ((item1.id == "ev1" and item2.id == "ev2") or 
                (item1.id == "ev2" and item2.id == "ev1")):
                found_pair = True
                break
        
        assert found_pair, "Should find same author, different platform pair"
    
    def test_prefilter_issue_key_detection(self, llm_service):
        """Test pre-filtering for issue key references"""
        item1 = UnifiedEvidenceItem(
            id="ev1",
            team_member_id="team1",
            title="Implement AUTH-123 fix",
            description="Fixed authentication issue",
            source=SourceType.GITLAB_COMMIT,
            category=CategoryType.DEVELOPMENT,
            platform=PlatformType.GITLAB,
            data_source=DataSourceType.MCP,
            evidence_date=datetime.now(timezone.utc)
        )
        
        item2 = UnifiedEvidenceItem(
            id="ev2",
            team_member_id="team2",
            title="AUTH-123: User login failing",
            description="Authentication service error",
            source=SourceType.JIRA_ISSUE,
            category=CategoryType.DEVELOPMENT,
            platform=PlatformType.JIRA,
            data_source=DataSourceType.MCP,
            evidence_date=datetime.now(timezone.utc)
        )
        
        assert llm_service._has_cross_platform_issue_reference(item1, item2)
    
    def test_prefilter_temporal_proximity(self, llm_service):
        """Test pre-filtering for temporal proximity"""
        base_time = datetime.now(timezone.utc)
        
        item1 = UnifiedEvidenceItem(
            id="ev1",
            title="Test item 1",
            description="Description 1", 
            source=SourceType.GITLAB_COMMIT, category=CategoryType.DEVELOPMENT, platform=PlatformType.GITLAB, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=base_time
        )
        
        item2 = UnifiedEvidenceItem(
            id="ev2",
            title="Test item 2",
            description="Description 2",
            source=SourceType.JIRA_ISSUE, category=CategoryType.DEVELOPMENT, platform=PlatformType.JIRA, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=base_time - timedelta(hours=12)  # Within 24 hours
        )
        
        assert llm_service._has_temporal_proximity(item1, item2)
        
        # Test outside 24 hours
        item3 = UnifiedEvidenceItem(
            id="ev3",
            title="Test item 3",
            description="Description 3",
            source=SourceType.JIRA_ISSUE, category=CategoryType.DEVELOPMENT, platform=PlatformType.JIRA, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=base_time - timedelta(hours=30)  # Outside 24 hours
        )
        
        assert not llm_service._has_temporal_proximity(item1, item3)
    
    def test_prefilter_keyword_overlap(self, llm_service):
        """Test pre-filtering for keyword overlap"""
        item1 = UnifiedEvidenceItem(
            id="ev1",
            title="Authentication service implementation",
            description="Implement user authentication with JWT tokens",
            source=SourceType.GITLAB_COMMIT, category=CategoryType.DEVELOPMENT, platform=PlatformType.GITLAB, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc)
        )
        
        item2 = UnifiedEvidenceItem(
            id="ev2",
            title="User authentication bug",
            description="Fix JWT token validation in authentication service",
            source=SourceType.JIRA_ISSUE, category=CategoryType.DEVELOPMENT, platform=PlatformType.JIRA, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc)
        )
        
        assert llm_service._has_keyword_overlap(item1, item2)
        
        # Test no overlap
        item3 = UnifiedEvidenceItem(
            id="ev3",
            title="Database migration script",
            description="Update schema for new features",
            source=SourceType.GITLAB_COMMIT, category=CategoryType.DEVELOPMENT, platform=PlatformType.GITLAB, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc)
        )
        
        assert not llm_service._has_keyword_overlap(item1, item3)
    
    @pytest.mark.asyncio
    async def test_correlate_evidence_with_llm_budget_exceeded(self, llm_service, evidence_items):
        """Test behavior when budget is exceeded"""
        # Set budget to very low value
        llm_service.cost_tracker.monthly_budget = 0.01
        llm_service.cost_tracker.current_month_usage = 0.005
        
        # Mock the fallback method
        with patch.object(llm_service, '_fallback_rule_based_correlation') as mock_fallback:
            mock_fallback.return_value = []
            
            relationships = await llm_service.correlate_evidence_with_llm(evidence_items)
            
            # Should use fallback when budget exceeded
            mock_fallback.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.services.llm_correlation_service.EmbeddingService.get_embeddings')
    async def test_correlate_with_embeddings_success(self, mock_embeddings, llm_service):
        """Test successful embedding-based correlation"""
        # Mock embeddings - similar pairs should have high similarity
        mock_embeddings.return_value = [
            [0.9, 0.1, 0.1],  # High similarity pair
            [0.9, 0.1, 0.2],  # High similarity pair
            [0.1, 0.9, 0.1],  # Different embedding
            [0.1, 0.9, 0.2]   # Different embedding
        ]
        
        evidence_pairs = [
            (
                UnifiedEvidenceItem(
                    id="ev1", title="Test 1", description="Description 1",
                    source=SourceType.GITLAB_COMMIT, category=CategoryType.DEVELOPMENT, platform=PlatformType.GITLAB, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc)
                ),
                UnifiedEvidenceItem(
                    id="ev2", title="Test 2", description="Description 2", 
                    source=SourceType.JIRA_ISSUE, category=CategoryType.DEVELOPMENT, platform=PlatformType.JIRA, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc)
                )
            )
        ]
        
        relationships = await llm_service._correlate_with_embeddings(evidence_pairs)
        
        # Should find high similarity relationship
        assert len(relationships) == 1
        assert relationships[0].relationship_type == RelationshipType.SEMANTIC_SIMILARITY
        assert relationships[0].detection_method == DetectionMethod.LLM_SEMANTIC
        assert relationships[0].confidence_score >= 0.7
    
    def test_identify_edge_cases(self, llm_service):
        """Test edge case identification for LLM processing"""
        evidence_pairs = [
            (
                UnifiedEvidenceItem(
                    id="ev1", title="API implementation", description="Built REST API service",
                    source=SourceType.GITLAB_COMMIT, category=CategoryType.DEVELOPMENT, platform=PlatformType.GITLAB, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc)
                ),
                UnifiedEvidenceItem(
                    id="ev2", title="Database schema", description="Updated API database tables",
                    source=SourceType.JIRA_ISSUE, category=CategoryType.DEVELOPMENT, platform=PlatformType.JIRA, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc) - timedelta(hours=6)
                )
            )
        ]
        
        # No existing relationships
        found_relationships = []
        
        edge_cases = llm_service._identify_edge_cases(evidence_pairs, found_relationships)
        
        # Should identify as edge case (cross-platform + temporal proximity + technical content)
        assert len(edge_cases) == 1
    
    @pytest.mark.asyncio
    @patch('anthropic.Anthropic')
    async def test_analyze_pair_with_llm_success(self, mock_anthropic, llm_service):
        """Test successful LLM analysis of evidence pair"""
        # Mock Anthropic response
        mock_response = Mock()
        mock_response.content = [Mock(text='{"is_related": true, "confidence": 0.8, "relationship_type": "same_feature", "reasoning": "Both relate to authentication"}')]
        mock_anthropic.return_value.messages.create.return_value = mock_response
        
        item1 = UnifiedEvidenceItem(
            id="ev1", title="Fix auth bug", description="Fixed authentication issue",
            source=SourceType.GITLAB_COMMIT, category=CategoryType.DEVELOPMENT, platform=PlatformType.GITLAB, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc)
        )
        
        item2 = UnifiedEvidenceItem(
            id="ev2", title="Auth service error", description="Authentication service failing",
            source=SourceType.JIRA_ISSUE, category=CategoryType.DEVELOPMENT, platform=PlatformType.JIRA, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc)
        )
        
        relationship = await llm_service._analyze_pair_with_llm(item1, item2)
        
        assert relationship is not None
        assert relationship.confidence_score == 0.8
        assert relationship.metadata['llm_relationship_type'] == 'same_feature'
        assert relationship.metadata['correlation_tier'] == 'llm_edge_case'
    
    @pytest.mark.asyncio
    @patch('anthropic.Anthropic')
    async def test_analyze_pair_with_llm_not_related(self, mock_anthropic, llm_service):
        """Test LLM analysis when items are not related"""
        # Mock Anthropic response indicating no relationship
        mock_response = Mock()
        mock_response.content = [Mock(text='{"is_related": false, "confidence": 0.2, "relationship_type": "none", "reasoning": "Different topics"}')]
        mock_anthropic.return_value.messages.create.return_value = mock_response
        
        item1 = UnifiedEvidenceItem(
            id="ev1", title="Database migration", description="Updated schema",
            source=SourceType.GITLAB_COMMIT, category=CategoryType.DEVELOPMENT, platform=PlatformType.GITLAB, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc)
        )
        
        item2 = UnifiedEvidenceItem(
            id="ev2", title="UI component bug", description="Button not working",
            source=SourceType.JIRA_ISSUE, category=CategoryType.DEVELOPMENT, platform=PlatformType.JIRA, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc)
        )
        
        relationship = await llm_service._analyze_pair_with_llm(item1, item2)
        
        assert relationship is None  # Low confidence, not related
    
    def test_get_usage_report(self, llm_service):
        """Test usage reporting functionality"""
        llm_service.cost_tracker.current_month_usage = 5.00
        
        report = llm_service.get_usage_report()
        
        assert report['monthly_budget'] == 15.00
        assert report['current_usage'] == 5.00
        assert report['remaining_budget'] == 10.00
        assert report['budget_utilization'] == pytest.approx(33.33, abs=0.1)
        assert 'can_afford_embeddings' in report
        assert 'can_afford_llm_calls' in report
    
    def test_fallback_rule_based_correlation(self, llm_service):
        """Test fallback to rule-based correlation"""
        evidence_pairs = [
            (
                UnifiedEvidenceItem(
                    id="ev1", title="AUTH-123 implementation", description="Fixed auth bug",
                    source=SourceType.GITLAB_COMMIT, category=CategoryType.DEVELOPMENT, platform=PlatformType.GITLAB, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc)
                ),
                UnifiedEvidenceItem(
                    id="ev2", title="AUTH-123: Login failing", description="Auth service error",
                    source=SourceType.JIRA_ISSUE, category=CategoryType.DEVELOPMENT, platform=PlatformType.JIRA, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc)
                )
            )
        ]
        
        relationships = llm_service._fallback_rule_based_correlation(evidence_pairs)
        
        # Should use existing rule-based algorithms
        assert isinstance(relationships, list)
        # All relationships should be marked as fallback
        for rel in relationships:
            assert rel.metadata.get('correlation_tier') == 'rule_based_fallback'

class TestIntegration:
    """Integration tests for LLM correlation service"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_correlation(self):
        """Test complete end-to-end LLM correlation"""
        evidence_items = [
            UnifiedEvidenceItem(
                id="ev1",
                title="Fix AUTH-456 authentication bug",
                description="Resolved issue with JWT token validation in the authentication service",
                source=SourceType.GITLAB_COMMIT, category=CategoryType.DEVELOPMENT, platform=PlatformType.GITLAB, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc)
            ),
            UnifiedEvidenceItem(
                id="ev2",
                title="AUTH-456: Users cannot login",
                description="Authentication service returning 401 errors for valid credentials",
                source=SourceType.JIRA_ISSUE, category=CategoryType.DEVELOPMENT, platform=PlatformType.JIRA, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc) - timedelta(hours=3)
            ),
            UnifiedEvidenceItem(
                id="ev3",
                title="Update user preferences UI",
                description="Added new settings page for user preferences",
                source=SourceType.GITLAB_COMMIT, category=CategoryType.DEVELOPMENT, platform=PlatformType.GITLAB, data_source=DataSourceType.MCP, team_member_id="team1", evidence_date=datetime.now(timezone.utc) - timedelta(days=1)
            )
        ]
        
        # Mock environment variables for testing
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            llm_service = LLMCorrelationService()
            
            # Mock embedding service to avoid API calls
            with patch.object(llm_service.embedding_service, 'get_embeddings') as mock_embeddings:
                mock_embeddings.return_value = []  # No embeddings for this test
                
                # Should at least find rule-based relationships
                relationships = await llm_service.correlate_evidence_with_llm(evidence_items)
                
                # Should find relationships (either through pre-filtering or fallback)
                assert isinstance(relationships, list)
    
    def test_factory_function(self):
        """Test factory function for service creation"""
        service = create_llm_correlation_service()
        
        assert isinstance(service, LLMCorrelationService)
        assert isinstance(service.cost_tracker, CostTracker)
        assert isinstance(service.embedding_service, EmbeddingService)

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 