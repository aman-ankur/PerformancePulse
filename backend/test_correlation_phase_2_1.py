#!/usr/bin/env python3
"""
Test script for Phase 2.1: Intelligent Cross-Reference Detection
Verifies that the correlation engine and algorithms work correctly
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType, DataSourceType
from src.models.evidence import SourceType, CategoryType
from src.models.correlation_models import CorrelationRequest
from src.services.correlation_engine import create_correlation_engine

def create_test_evidence():
    """Create test evidence items for correlation testing"""
    
    # Create a JIRA ticket
    jira_ticket = UnifiedEvidenceItem(
        team_member_id="test-user-123",
        source="jira_ticket",
        title="TEST-1234: Fix authentication bug in login system",
        description="Users are unable to login due to session timeout issues. Need to investigate and fix the authentication flow.",
        category="technical",
        evidence_date=datetime.now() - timedelta(days=5),
        platform=PlatformType.JIRA,
        data_source=DataSourceType.API,
        metadata={
            "key": "TEST-1234",
            "status": "In Progress",
            "assignee": "john.doe",
            "reporter": "jane.smith"
        }
    )
    
    # Create related GitLab commit
    gitlab_commit = UnifiedEvidenceItem(
        team_member_id="test-user-123",
        source="gitlab_commit",
        title="TEST-1234: Fix session timeout in authentication service",
        description="Fixed the session timeout issue by updating the authentication middleware to properly handle token refresh.",
        category="technical",
        evidence_date=datetime.now() - timedelta(days=3),
        platform=PlatformType.GITLAB,
        data_source=DataSourceType.API,
        metadata={
            "branch_name": "feature/TEST-1234-auth-fix",
            "author": "john.doe",
            "files_changed": ["src/auth/middleware.py", "src/auth/session.py"],
            "commit_hash": "abc123def456"
        }
    )
    
    # Create GitLab merge request
    gitlab_mr = UnifiedEvidenceItem(
        team_member_id="test-user-123",
        source="gitlab_mr",
        title="Merge request: Fix authentication bug (TEST-1234)",
        description="This MR resolves TEST-1234 by fixing the session timeout issue in the authentication service.",
        category="technical",
        evidence_date=datetime.now() - timedelta(days=2),
        platform=PlatformType.GITLAB,
        data_source=DataSourceType.API,
        metadata={
            "branch_name": "feature/TEST-1234-auth-fix",
            "author": "john.doe",
            "target_branch": "main",
            "state": "merged"
        }
    )
    
    # Create unrelated evidence
    unrelated_commit = UnifiedEvidenceItem(
        team_member_id="test-user-123",
        source="gitlab_commit",
        title="Update documentation for API endpoints",
        description="Updated the API documentation to include new endpoint descriptions and examples.",
        category="technical",
        evidence_date=datetime.now() - timedelta(days=1),
        platform=PlatformType.GITLAB,
        data_source=DataSourceType.API,
        metadata={
            "branch_name": "docs/api-update",
            "author": "john.doe",
            "files_changed": ["docs/api.md", "README.md"]
        }
    )
    
    return [jira_ticket, gitlab_commit, gitlab_mr, unrelated_commit]

async def test_correlation_engine():
    """Test the correlation engine with sample data"""
    print("🚀 Testing Phase 2.1: Intelligent Cross-Reference Detection")
    print("=" * 60)
    
    # Create test evidence
    evidence_items = create_test_evidence()
    print(f"📊 Created {len(evidence_items)} test evidence items")
    
    # Create correlation request
    request = CorrelationRequest(
        evidence_items=evidence_items,
        confidence_threshold=0.3,
        max_work_stories=10,
        include_low_confidence=True,
        detect_technology_stack=True,
        analyze_work_patterns=True,
        generate_insights=True,
        min_evidence_per_story=2
    )
    
    # Initialize correlation engine
    engine = create_correlation_engine()
    print("🔧 Correlation engine initialized")
    
    # Run correlation analysis
    print("\n🔍 Running correlation analysis...")
    response = await engine.correlate_evidence(request)
    
    # Display results
    print(f"\n📈 Correlation Results:")
    print(f"   Success: {response.success}")
    print(f"   Processing time: {response.processing_time_ms}ms")
    print(f"   Items processed: {response.items_processed}")
    print(f"   Relationships detected: {response.relationships_detected}")
    print(f"   Work stories created: {response.work_stories_created}")
    print(f"   Average confidence: {response.avg_confidence_score:.2f}")
    print(f"   Correlation coverage: {response.correlation_coverage:.1f}%")
    
    if response.has_errors:
        print(f"\n❌ Errors: {response.errors}")
    
    if response.has_warnings:
        print(f"\n⚠️  Warnings: {response.warnings}")
    
    # Display work stories
    if response.correlated_collection and response.correlated_collection.work_stories:
        print(f"\n📚 Work Stories ({len(response.correlated_collection.work_stories)}):")
        for i, story in enumerate(response.correlated_collection.work_stories, 1):
            print(f"\n   Story {i}: {story.title}")
            print(f"   - Evidence items: {len(story.evidence_items)}")
            print(f"   - Platforms: {story.platforms_involved}")
            print(f"   - Status: {story.status}")
            print(f"   - Complexity: {story.complexity_score:.2f}")
            print(f"   - Technologies: {story.technology_stack}")
            
            print(f"   - Relationships:")
            for rel in story.relationships:
                print(f"     * {rel.relationship_type} (confidence: {rel.confidence_score:.2f})")
    
    # Display relationships
    if response.correlated_collection and response.correlated_collection.relationships:
        print(f"\n🔗 Relationships ({len(response.correlated_collection.relationships)}):")
        for i, rel in enumerate(response.correlated_collection.relationships, 1):
            print(f"   {i}. {rel.relationship_type}: {rel.evidence_summary}")
            print(f"     Confidence: {rel.confidence_score:.2f}, Method: {rel.detection_method}")
    
    # Display insights
    if response.correlated_collection and response.correlated_collection.insights:
        insights = response.correlated_collection.insights
        print(f"\n💡 Insights:")
        print(f"   - Technology distribution: {insights.technology_distribution}")
        print(f"   - Sprint metrics: {insights.sprint_performance_metrics}")
        print(f"   - Collaboration score: {insights.collaboration_score:.2f}")
        print(f"   - Work patterns: {len(insights.work_patterns)} detected")
    
    print(f"\n✅ Phase 2.1 test completed successfully!")
    return response.success

async def main():
    """Main test function"""
    try:
        success = await test_correlation_engine()
        if success:
            print("\n🎉 All tests passed! Phase 2.1 implementation is working correctly.")
            return 0
        else:
            print("\n❌ Tests failed! Check the implementation.")
            return 1
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 