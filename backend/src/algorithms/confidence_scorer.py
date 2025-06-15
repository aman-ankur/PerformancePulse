"""
Confidence Scorer Algorithm
Phase 2.1 Implementation - Calculate confidence scores for evidence relationships

This algorithm evaluates the strength of relationships based on:
1. Detection method strength
2. Temporal proximity
3. Author correlation
4. Content similarity strength
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from src.models.correlation_models import (
    EvidenceRelationship,
    DetectionMethod,
    RelationshipType
)
from src.models.unified_evidence import UnifiedEvidenceItem

logger = logging.getLogger(__name__)

class ConfidenceScorer:
    """
    Calculate confidence scores for evidence relationships
    
    Scoring factors:
    - Detection method (issue_key=0.9, branch_name=0.7, content=0.4)
    - Temporal proximity (closer dates = higher confidence)
    - Author correlation (same person = +0.1 bonus)
    - Content similarity strength
    """
    
    def __init__(self):
        """Initialize the confidence scorer"""
        # Base confidence scores by detection method
        self.method_confidence = {
            DetectionMethod.ISSUE_KEY: 0.9,
            DetectionMethod.BRANCH_NAME: 0.7,
            DetectionMethod.CONTENT_ANALYSIS: 0.4,
            DetectionMethod.TEMPORAL_PROXIMITY: 0.3,
            DetectionMethod.AUTHOR_CORRELATION: 0.5,
            DetectionMethod.MANUAL: 1.0
        }
        
        # Maximum time difference for temporal bonus (7 days)
        self.max_temporal_bonus_days = 7
        
        logger.info("Confidence Scorer initialized")
    
    async def score_relationship(self, relationship: EvidenceRelationship,
                               primary_item: UnifiedEvidenceItem,
                               related_item: UnifiedEvidenceItem) -> float:
        """
        Calculate 0.0-1.0 confidence score for a relationship
        
        Args:
            relationship: The relationship to score
            primary_item: Primary evidence item
            related_item: Related evidence item
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        # Start with base confidence from detection method
        base_confidence = self.method_confidence.get(relationship.detection_method, 0.3)
        
        # Calculate temporal proximity bonus
        temporal_bonus = self._calculate_temporal_bonus(primary_item, related_item)
        
        # Calculate author correlation bonus
        author_bonus = self._calculate_author_bonus(primary_item, related_item)
        
        # Calculate content similarity bonus (if available)
        content_bonus = self._calculate_content_bonus(relationship, primary_item, related_item)
        
        # Calculate relationship type bonus
        relationship_bonus = self._calculate_relationship_bonus(relationship.relationship_type)
        
        # Combine all factors
        total_confidence = base_confidence + temporal_bonus + author_bonus + content_bonus + relationship_bonus
        
        # Ensure score is between 0.0 and 1.0
        final_confidence = max(0.0, min(1.0, total_confidence))
        
        logger.debug(f"Confidence scoring: base={base_confidence:.2f}, "
                    f"temporal={temporal_bonus:.2f}, author={author_bonus:.2f}, "
                    f"content={content_bonus:.2f}, relationship={relationship_bonus:.2f}, "
                    f"final={final_confidence:.2f}")
        
        return final_confidence
    
    def _calculate_temporal_bonus(self, primary_item: UnifiedEvidenceItem,
                                related_item: UnifiedEvidenceItem) -> float:
        """Calculate bonus based on temporal proximity"""
        time_diff = abs((primary_item.evidence_date - related_item.evidence_date).days)
        
        if time_diff == 0:
            return 0.1  # Same day bonus
        elif time_diff <= self.max_temporal_bonus_days:
            # Linear decay over max_temporal_bonus_days
            return 0.1 * (1 - time_diff / self.max_temporal_bonus_days)
        else:
            return 0.0  # No bonus for distant dates
    
    def _calculate_author_bonus(self, primary_item: UnifiedEvidenceItem,
                              related_item: UnifiedEvidenceItem) -> float:
        """Calculate bonus for same author"""
        # Extract author information from metadata
        primary_author = self._extract_author(primary_item)
        related_author = self._extract_author(related_item)
        
        if primary_author and related_author and primary_author == related_author:
            return 0.1  # Same author bonus
        
        return 0.0
    
    def _extract_author(self, item: UnifiedEvidenceItem) -> Optional[str]:
        """Extract author information from evidence item"""
        # Try various metadata fields for author information
        author_fields = ['author', 'assignee', 'reporter', 'created_by', 'username']
        
        for field in author_fields:
            if field in item.metadata and item.metadata[field]:
                return str(item.metadata[field]).lower()
        
        return None
    
    def _calculate_content_bonus(self, relationship: EvidenceRelationship,
                               primary_item: UnifiedEvidenceItem,
                               related_item: UnifiedEvidenceItem) -> float:
        """Calculate bonus based on content similarity"""
        # If relationship was detected via content analysis, use the similarity score
        if relationship.detection_method == DetectionMethod.CONTENT_ANALYSIS:
            similarity_score = relationship.metadata.get('similarity_score', 0.0)
            return similarity_score * 0.2  # Scale to max 0.2 bonus
        
        # For other methods, calculate basic content overlap
        primary_words = set(primary_item.title.lower().split() + primary_item.description.lower().split())
        related_words = set(related_item.title.lower().split() + related_item.description.lower().split())
        
        if primary_words and related_words:
            overlap = len(primary_words.intersection(related_words))
            total = len(primary_words.union(related_words))
            overlap_ratio = overlap / total if total > 0 else 0.0
            return overlap_ratio * 0.1  # Scale to max 0.1 bonus
        
        return 0.0
    
    def _calculate_relationship_bonus(self, relationship_type: RelationshipType) -> float:
        """Calculate bonus based on relationship type strength"""
        # Some relationship types are stronger indicators than others
        type_bonuses = {
            RelationshipType.SOLVES: 0.1,      # Strong relationship
            RelationshipType.REFERENCES: 0.05,  # Medium relationship
            RelationshipType.RELATED_TO: 0.0,   # Neutral
            RelationshipType.DUPLICATE: 0.1,    # Strong relationship
            RelationshipType.SEQUENTIAL: 0.05,  # Medium relationship
            RelationshipType.CAUSAL: 0.1        # Strong relationship
        }
        
        return type_bonuses.get(relationship_type, 0.0)
    
    async def validate_relationship_logic(self, relationship: EvidenceRelationship,
                                        primary_item: UnifiedEvidenceItem,
                                        related_item: UnifiedEvidenceItem) -> bool:
        """
        Validate that relationship makes logical sense
        
        Args:
            relationship: The relationship to validate
            primary_item: Primary evidence item
            related_item: Related evidence item
            
        Returns:
            True if relationship is logically valid
        """
        # Check for obvious logical inconsistencies
        
        # 1. Items shouldn't relate to themselves
        if primary_item.id == related_item.id:
            return False
        
        # 2. Check temporal logic for certain relationship types
        if relationship.relationship_type == RelationshipType.SOLVES:
            # GitLab work should generally come after JIRA ticket creation
            # (though this isn't always true, so we're lenient)
            pass
        
        # 3. Check platform logic
        # Cross-platform relationships are expected, same-platform might be duplicates
        if primary_item.platform == related_item.platform:
            # Same platform relationships should have high confidence or be duplicates
            if relationship.confidence_score < 0.7 and relationship.relationship_type != RelationshipType.DUPLICATE:
                return False
        
        # 4. Check confidence threshold
        if relationship.confidence_score < 0.1:  # Very low confidence
            return False
        
        return True 