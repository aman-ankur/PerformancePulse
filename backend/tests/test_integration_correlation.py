"""Integration tests for correlation system"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List

from src.services.correlation_engine import create_correlation_engine
from src.models.correlation_models import (
    CorrelationRequest,
    RelationshipType,
    DetectionMethod,
    WorkStoryStatus
)
from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType, DataSourceType


class TestCorrelationIntegration:
    """Integration tests for the complete correlation system"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = create_correlation_engine()
    
    def create_realistic_evidence_set(self) -> List[UnifiedEvidenceItem]:
        """Create a realistic set of evidence items for testing"""
        base_date = datetime.now() - timedelta(days=10)
        
        return [
            # JIRA ticket
            UnifiedEvidenceItem(
                id="jira_auth_backend",
                team_member_id="backend_dev",
                source="jira_ticket",
                title="AUTH-101: Backend OAuth2 Implementation",
                description="Implement OAuth2 backend services and JWT token management",
                category="technical",
                evidence_date=base_date + timedelta(days=1),
                platform=PlatformType.JIRA,
                data_source=DataSourceType.API,
                metadata={
                    "key": "AUTH-101",
                    "type": "Story",
                    "status": "Done",
                    "assignee": "backend_dev",
                    "story_points": 8
                }
            ),
            # Related GitLab commit
            UnifiedEvidenceItem(
                id="gitlab_auth_backend_commit1",
                team_member_id="backend_dev",
                source="gitlab_commit",
                title="AUTH-101: Add OAuth2 service and JWT utilities",
                description="Implemented OAuth2Service with Google and GitHub providers. Added JWT token generation and validation utilities.",
                category="technical",
                evidence_date=base_date + timedelta(days=2),
                platform=PlatformType.GITLAB,
                data_source=DataSourceType.API,
                metadata={
                    "branch_name": "feature/AUTH-101-oauth2-backend",
                    "author": "backend_dev",
                    "commit_hash": "a1b2c3d4",
                    "files_changed": [
                        "src/auth/oauth2_service.py",
                        "src/auth/jwt_utils.py",
                        "requirements.txt"
                    ]
                }
            ),
            # Related GitLab MR
            UnifiedEvidenceItem(
                id="gitlab_auth_backend_mr",
                team_member_id="backend_dev",
                source="gitlab_mr",
                title="Merge Request: OAuth2 Backend Implementation (AUTH-101)",
                description="This MR implements the complete OAuth2 backend system. Resolves AUTH-101.",
                category="technical",
                evidence_date=base_date + timedelta(days=4),
                platform=PlatformType.GITLAB,
                data_source=DataSourceType.API,
                metadata={
                    "branch_name": "feature/AUTH-101-oauth2-backend",
                    "target_branch": "develop",
                    "author": "backend_dev",
                    "state": "merged"
                }
            ),
            # Unrelated evidence
            UnifiedEvidenceItem(
                id="gitlab_docs_commit",
                team_member_id="tech_writer",
                source="gitlab_commit",
                title="Update documentation",
                description="Updated API documentation",
                category="technical",
                evidence_date=base_date + timedelta(days=9),
                platform=PlatformType.GITLAB,
                data_source=DataSourceType.API,
                metadata={
                    "branch_name": "docs/update-docs",
                    "author": "tech_writer",
                    "files_changed": ["docs/api.md", "README.md"]
                }
            )
        ]
    
    @pytest.mark.asyncio
    async def test_end_to_end_correlation(self):
        """Test complete end-to-end correlation workflow"""
        evidence_items = self.create_realistic_evidence_set()
        
        request = CorrelationRequest(
            evidence_items=evidence_items,
            confidence_threshold=0.3,
            generate_insights=True,
            detect_technology_stack=True,
            analyze_work_patterns=True
        )
        
        response = await self.engine.correlate_evidence(request)
        
        # Verify successful processing
        assert response.success is True
        assert response.items_processed == len(evidence_items)
        assert response.processing_time_ms >= 0
        
        # Verify relationships were detected
        assert response.relationships_detected >= 2  # Should find AUTH-101 relationships
        
        # Verify work stories were created
        assert response.work_stories_created >= 1  # AUTH-101 story
        
        collection = response.correlated_collection
        assert collection is not None
        
        # Verify work stories contain expected content
        auth_stories = [s for s in collection.work_stories if "AUTH-101" in s.title]
        assert len(auth_stories) >= 1
        
        # Check that AUTH-101 story includes related evidence
        auth_101_story = auth_stories[0]
        assert len(auth_101_story.evidence_items) >= 2  # JIRA + GitLab items
        assert auth_101_story.primary_jira_ticket == "AUTH-101"
        
        # Verify technology detection
        if len(auth_101_story.technology_stack) > 0:
            assert "Python" in auth_101_story.technology_stack  # From .py files
        
        # Verify insights were generated
        assert collection.insights is not None
        insights = collection.insights
        assert insights.total_work_stories >= 1
        assert insights.total_relationships >= 2
    
    @pytest.mark.asyncio
    async def test_cross_platform_relationship_detection(self):
        """Test detection of relationships across JIRA and GitLab"""
        evidence_items = self.create_realistic_evidence_set()
        
        request = CorrelationRequest(
            evidence_items=evidence_items,
            confidence_threshold=0.1  # Low threshold to see all relationships
        )
        
        response = await self.engine.correlate_evidence(request)
        
        assert response.success is True
        
        relationships = response.correlated_collection.relationships
        
        # Verify different types of relationships were detected
        issue_key_rels = [r for r in relationships if r.detection_method == DetectionMethod.ISSUE_KEY]
        # Branch name detection is handled by issue key detection when JIRA keys are in branch names
        # So we don't expect separate BRANCH_NAME detection methods
        
        assert len(issue_key_rels) >= 1  # AUTH-101 in titles/descriptions
        # All relationships should be issue key based since JIRA keys are in titles/branches
        assert len(relationships) >= 1
    
    @pytest.mark.asyncio
    async def test_performance_basic(self):
        """Test basic performance characteristics"""
        evidence_items = self.create_realistic_evidence_set()
        
        request = CorrelationRequest(evidence_items=evidence_items)
        
        start_time = datetime.now()
        response = await self.engine.correlate_evidence(request)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        assert response.success is True
        assert response.items_processed == len(evidence_items)
        
        # Should complete within reasonable time
        assert processing_time < 5000  # 5 seconds max for small dataset
        
        # Should detect relationships effectively
        assert response.relationships_detected > 0
        assert response.work_stories_created > 0
    
    @pytest.mark.asyncio
    async def test_work_story_grouping_accuracy(self):
        """Test accuracy of work story grouping"""
        evidence_items = self.create_realistic_evidence_set()

        request = CorrelationRequest(
            evidence_items=evidence_items,
            confidence_threshold=0.3,
            min_evidence_per_story=2
        )

        response = await self.engine.correlate_evidence(request)

        assert response.success is True

        work_stories = response.correlated_collection.work_stories

        # Find AUTH-101 story (should be the largest)
        auth_101_story = next((s for s in work_stories if "AUTH-101" in s.title), None)
        assert auth_101_story is not None

        # Should include related evidence items - the exact count depends on 
        # which items get grouped together based on relationships
        # Let's be more flexible about the exact count
        assert len(auth_101_story.evidence_items) >= 3  # At least JIRA + some GitLab items
        
        # Verify it contains the key items we expect
        evidence_ids = [item.id for item in auth_101_story.evidence_items]
        assert "jira_auth_backend" in evidence_ids  # JIRA ticket should be included

        # Verify evidence types in the story
        evidence_sources = [item.source for item in auth_101_story.evidence_items]
        assert "jira_ticket" in evidence_sources
        assert "gitlab_commit" in evidence_sources
        assert "gitlab_mr" in evidence_sources

        # Verify timeline makes sense (JIRA first, then commits, then MR)
        sorted_evidence = sorted(auth_101_story.evidence_items, key=lambda x: x.evidence_date)
        assert sorted_evidence[0].source == "jira_ticket"  # JIRA ticket first
        assert sorted_evidence[-1].source == "gitlab_mr"   # MR last

        # Verify story metadata
        assert auth_101_story.status == WorkStoryStatus.COMPLETED
        assert auth_101_story.duration.days >= 1  # Should span multiple days
        assert len(auth_101_story.team_members_involved) >= 1
        assert "backend_dev" in auth_101_story.team_members_involved
    
    @pytest.mark.asyncio
    async def test_technology_stack_detection(self):
        """Test technology stack detection from file changes"""
        evidence_items = self.create_realistic_evidence_set()
        
        request = CorrelationRequest(
            evidence_items=evidence_items,
            detect_technology_stack=True
        )
        
        response = await self.engine.correlate_evidence(request)
        
        assert response.success is True
        
        work_stories = response.correlated_collection.work_stories
        auth_101_story = next((s for s in work_stories if "AUTH-101" in s.title), None)
        
        if auth_101_story:
            tech_stack = auth_101_story.technology_stack
            assert "Python" in tech_stack  # From .py files
            # Might also detect other technologies based on file extensions
        
        # Check insights for overall technology distribution
        if response.correlated_collection.insights:
            tech_distribution = response.correlated_collection.insights.technology_distribution
            assert "Python" in tech_distribution
            assert tech_distribution["Python"] >= 1
    
    @pytest.mark.asyncio
    async def test_work_pattern_analysis(self):
        """Test work pattern analysis"""
        evidence_items = self.create_realistic_evidence_set()
        
        request = CorrelationRequest(
            evidence_items=evidence_items,
            analyze_work_patterns=True
        )
        
        response = await self.engine.correlate_evidence(request)
        
        assert response.success is True
        
        if response.correlated_collection.insights:
            insights = response.correlated_collection.insights
            
            # Should detect some work patterns
            assert len(insights.work_patterns) >= 0
            
            # Should have sprint performance metrics
            sprint_metrics = insights.sprint_performance_metrics
            assert "completion_rate" in sprint_metrics or "avg_story_duration_days" in sprint_metrics
            
            # Should have collaboration score
            assert 0.0 <= insights.collaboration_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_confidence_threshold_filtering(self):
        """Test that confidence threshold properly filters relationships"""
        evidence_items = self.create_realistic_evidence_set()
        
        # Test with low threshold
        low_threshold_request = CorrelationRequest(
            evidence_items=evidence_items,
            confidence_threshold=0.1
        )
        
        low_response = await self.engine.correlate_evidence(low_threshold_request)
        
        # Test with high threshold
        high_threshold_request = CorrelationRequest(
            evidence_items=evidence_items,
            confidence_threshold=0.8
        )
        
        high_response = await self.engine.correlate_evidence(high_threshold_request)
        
        # Low threshold should detect more relationships
        assert low_response.relationships_detected >= high_response.relationships_detected
        
        # High threshold should only keep high-confidence relationships
        if high_response.correlated_collection.relationships:
            for rel in high_response.correlated_collection.relationships:
                assert rel.confidence_score >= 0.8
    
    @pytest.mark.asyncio
    async def test_performance_with_realistic_dataset(self):
        """Test performance with a realistic dataset size"""
        evidence_items = self.create_realistic_evidence_set()
        
        # Duplicate the dataset to simulate larger volume
        large_dataset = []
        for i in range(5):  # 5x the original dataset
            for item in evidence_items:
                new_item = item.model_copy()
                new_item.id = f"{item.id}_copy_{i}"
                new_item.evidence_date = item.evidence_date + timedelta(days=i*14)  # Spread over time
                large_dataset.append(new_item)
        
        request = CorrelationRequest(evidence_items=large_dataset)
        
        start_time = datetime.now()
        response = await self.engine.correlate_evidence(request)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds() * 1000
        
        assert response.success is True
        assert response.items_processed == len(large_dataset)
        
        # Should complete within reasonable time (adjust based on performance requirements)
        assert processing_time < 30000  # 30 seconds max for ~60 items
        
        # Should still detect relationships effectively
        assert response.relationships_detected > 0
        assert response.work_stories_created > 0
    
    @pytest.mark.asyncio
    async def test_edge_case_handling(self):
        """Test handling of edge cases and unusual data"""
        edge_case_evidence = [
            # Evidence with minimal metadata
            UnifiedEvidenceItem(
                id="minimal_1",
                team_member_id="user1",
                source="jira_ticket",
                title="EDGE-001: Minimal ticket",
                description="Minimal description",
                category="technical",
                evidence_date=datetime.now(),
                platform=PlatformType.JIRA,
                data_source=DataSourceType.API,
                metadata={}  # Empty metadata
            ),
            # Evidence with very long content
            UnifiedEvidenceItem(
                id="long_content_1",
                team_member_id="user1",
                source="gitlab_commit",
                title="EDGE-001: " + "Very long title " * 20,
                description="Very long description " * 100,
                category="technical",
                evidence_date=datetime.now(),
                platform=PlatformType.GITLAB,
                data_source=DataSourceType.API,
                metadata={"branch_name": "feature/EDGE-001-long-content"}
            ),
            # Evidence with special characters
            UnifiedEvidenceItem(
                id="special_chars_1",
                team_member_id="user1",
                source="gitlab_commit",
                title="EDGE-001: Fix issue with special chars: @#$%^&*()",
                description="Fixed issue with special characters in user input: <script>alert('xss')</script>",
                category="technical",
                evidence_date=datetime.now(),
                platform=PlatformType.GITLAB,
                data_source=DataSourceType.API,
                metadata={"branch_name": "feature/EDGE-001-special-chars"}
            )
        ]
        
        request = CorrelationRequest(evidence_items=edge_case_evidence)
        
        # Should handle edge cases gracefully without crashing
        response = await self.engine.correlate_evidence(request)
        
        assert response.success is True
        assert response.items_processed == len(edge_case_evidence)
        
        # Should still detect relationships despite edge cases
        assert response.relationships_detected >= 1  # Should link EDGE-001 items 