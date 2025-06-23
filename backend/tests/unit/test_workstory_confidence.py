import pytest
from datetime import datetime

from src.models.correlation_models import (
    WorkStory,
    EvidenceRelationship,
    RelationshipType,
    DetectionMethod,
)
from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType, DataSourceType


def make_evidence(idx: int) -> UnifiedEvidenceItem:
    return UnifiedEvidenceItem(
        id=f"e{idx}",
        team_member_id="tm1",
        source="jira_ticket",
        title=f"TEST-{idx}: Demo",
        description="A demo evidence item",
        category="technical",
        evidence_date=datetime.utcnow(),
        platform=PlatformType.JIRA,
        data_source=DataSourceType.API,
    )


def test_workstory_confidence_score():
    item1 = make_evidence(1)
    item2 = make_evidence(2)

    rel1 = EvidenceRelationship(
        primary_evidence_id=item1.id,
        related_evidence_id=item2.id,
        relationship_type=RelationshipType.SEMANTIC_SIMILARITY,
        confidence_score=0.8,
        detection_method=DetectionMethod.LLM_SEMANTIC,
    )

    story = WorkStory(title="TEST workstory", evidence_items=[item1, item2], relationships=[rel1])

    assert story.confidence_score == pytest.approx(0.8)


def test_semantic_enums_existence():
    # Ensure new enum members exist and validate through Pydantic
    rel = EvidenceRelationship(
        primary_evidence_id="a",
        related_evidence_id="b",
        relationship_type=RelationshipType.SEMANTIC_SIMILARITY,
        confidence_score=0.5,
        detection_method=DetectionMethod.LLM_SEMANTIC,
    )
    assert rel.relationship_type == RelationshipType.SEMANTIC_SIMILARITY
    assert rel.detection_method == DetectionMethod.LLM_SEMANTIC 