"""
JIRA-GitLab Linker Algorithm
Phase 2.1 Implementation - Detect relationships between GitLab and JIRA evidence

This algorithm implements multiple strategies to detect relationships:
1. Issue key detection in GitLab content
2. Branch name pattern matching
3. Content similarity analysis
4. Temporal proximity correlation
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from src.models.correlation_models import (
    EvidenceRelationship,
    RelationshipType,
    DetectionMethod
)
from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType

logger = logging.getLogger(__name__)

class JiraGitLabLinker:
    """
    Detect relationships between GitLab and JIRA evidence items
    
    Uses multiple detection strategies:
    - Issue key references (highest confidence)
    - Branch name patterns (high confidence)
    - Content similarity (medium confidence)
    - Temporal proximity (low confidence)
    """
    
    def __init__(self):
        """Initialize the JIRA-GitLab linker"""
        # Common JIRA key patterns (PROJECT-123, PROJ-456, etc.)
        self.jira_key_pattern = re.compile(r'\b([A-Z]{2,10}-\d+)\b')
        
        # Branch name patterns that might contain JIRA keys
        self.branch_patterns = [
            re.compile(r'feature/([A-Z]{2,10}-\d+)'),
            re.compile(r'bugfix/([A-Z]{2,10}-\d+)'),
            re.compile(r'hotfix/([A-Z]{2,10}-\d+)'),
            re.compile(r'([A-Z]{2,10}-\d+)[-_]'),
            re.compile(r'([A-Z]{2,10}-\d+)$')
        ]
        
        # Keywords that indicate relationship types
        self.solve_keywords = ['fix', 'fixes', 'fixed', 'resolve', 'resolves', 'resolved', 'close', 'closes', 'closed']
        self.reference_keywords = ['ref', 'refs', 'reference', 'references', 'related', 'see', 'regarding']
        
        logger.info("JIRA-GitLab Linker initialized")
    
    async def detect_relationships(self, gitlab_items: List[UnifiedEvidenceItem],
                                 jira_items: List[UnifiedEvidenceItem]) -> List[EvidenceRelationship]:
        """
        Main method to detect relationships between GitLab and JIRA items
        
        Args:
            gitlab_items: List of GitLab evidence items
            jira_items: List of JIRA evidence items
            
        Returns:
            List of detected relationships
        """
        relationships = []
        
        logger.info(f"Detecting relationships between {len(gitlab_items)} GitLab and {len(jira_items)} JIRA items")
        
        # Create JIRA key lookup for efficient matching
        jira_key_map = self._create_jira_key_map(jira_items)
        
        for gitlab_item in gitlab_items:
            # Strategy 1: Issue key detection
            issue_key_relationships = await self._detect_issue_key_references(
                gitlab_item, jira_items, jira_key_map
            )
            relationships.extend(issue_key_relationships)
            
            # Strategy 2: Branch name pattern matching
            branch_relationships = await self._detect_branch_name_patterns(
                gitlab_item, jira_items, jira_key_map
            )
            relationships.extend(branch_relationships)
            
            # Strategy 3: Content similarity (if no direct references found)
            if not issue_key_relationships and not branch_relationships:
                content_relationships = await self._detect_content_similarity(
                    gitlab_item, jira_items
                )
                relationships.extend(content_relationships)
        
        # Remove duplicates
        unique_relationships = self._deduplicate_relationships(relationships)
        
        logger.info(f"Detected {len(unique_relationships)} unique relationships")
        return unique_relationships
    
    def _create_jira_key_map(self, jira_items: List[UnifiedEvidenceItem]) -> Dict[str, UnifiedEvidenceItem]:
        """Create a map of JIRA keys to items for efficient lookup"""
        jira_map = {}
        
        for item in jira_items:
            # Extract JIRA key from title or metadata
            jira_key = self._extract_jira_key_from_item(item)
            if jira_key:
                jira_map[jira_key] = item
        
        return jira_map
    
    def _extract_jira_key_from_item(self, jira_item: UnifiedEvidenceItem) -> Optional[str]:
        """Extract JIRA key from a JIRA item"""
        # Try to find JIRA key in title first
        title_match = self.jira_key_pattern.search(jira_item.title)
        if title_match:
            return title_match.group(1)
        
        # Try metadata if available
        if 'key' in jira_item.metadata:
            return jira_item.metadata['key']
        
        # Try description as last resort
        desc_match = self.jira_key_pattern.search(jira_item.description)
        if desc_match:
            return desc_match.group(1)
        
        return None
    
    async def _detect_issue_key_references(self, gitlab_item: UnifiedEvidenceItem,
                                         jira_items: List[UnifiedEvidenceItem],
                                         jira_key_map: Dict[str, UnifiedEvidenceItem]) -> List[EvidenceRelationship]:
        """
        Find JIRA issue keys in GitLab commits/MRs
        
        Examples:
        - Commit: "TEST-1234: Fix authentication bug"
        - Branch: "feature/TEST-1234-auth-fix"
        - MR Description: "Resolves TEST-1234"
        """
        relationships = []
        
        # Search in title
        title_keys = self.jira_key_pattern.findall(gitlab_item.title)
        
        # Search in description
        description_keys = self.jira_key_pattern.findall(gitlab_item.description)
        
        # Search in metadata (branch names, etc.)
        metadata_keys = []
        if 'branch_name' in gitlab_item.metadata:
            metadata_keys.extend(self.jira_key_pattern.findall(gitlab_item.metadata['branch_name']))
        
        # Combine all found keys
        all_keys = set(title_keys + description_keys + metadata_keys)
        
        for jira_key in all_keys:
            if jira_key in jira_key_map:
                jira_item = jira_key_map[jira_key]
                
                # Determine relationship type based on context
                relationship_type = self._determine_relationship_type(gitlab_item, jira_key)
                
                relationship = EvidenceRelationship(
                    primary_evidence_id=gitlab_item.id,
                    related_evidence_id=jira_item.id,
                    relationship_type=relationship_type,
                    confidence_score=0.9,  # High confidence for direct key references
                    detection_method=DetectionMethod.ISSUE_KEY,
                    evidence_summary=f"GitLab item references JIRA key {jira_key}",
                    metadata={
                        "jira_key": jira_key,
                        "found_in": self._get_reference_location(gitlab_item, jira_key)
                    }
                )
                relationships.append(relationship)
        
        return relationships
    
    def _determine_relationship_type(self, gitlab_item: UnifiedEvidenceItem, jira_key: str) -> RelationshipType:
        """Determine the type of relationship based on context"""
        content = f"{gitlab_item.title} {gitlab_item.description}".lower()
        
        # Check for solve keywords
        for keyword in self.solve_keywords:
            if keyword in content and jira_key.lower() in content:
                return RelationshipType.SOLVES
        
        # Check for reference keywords
        for keyword in self.reference_keywords:
            if keyword in content and jira_key.lower() in content:
                return RelationshipType.REFERENCES
        
        # Default to related
        return RelationshipType.RELATED_TO
    
    def _get_reference_location(self, gitlab_item: UnifiedEvidenceItem, jira_key: str) -> List[str]:
        """Get locations where JIRA key was found"""
        locations = []
        
        if jira_key in gitlab_item.title:
            locations.append("title")
        if jira_key in gitlab_item.description:
            locations.append("description")
        if 'branch_name' in gitlab_item.metadata and jira_key in gitlab_item.metadata['branch_name']:
            locations.append("branch_name")
        
        return locations
    
    async def _detect_branch_name_patterns(self, gitlab_item: UnifiedEvidenceItem,
                                         jira_items: List[UnifiedEvidenceItem],
                                         jira_key_map: Dict[str, UnifiedEvidenceItem]) -> List[EvidenceRelationship]:
        """
        Match GitLab branch names to JIRA tickets
        Patterns: feature/PROJ-123, bugfix/PROJ-456, PROJ-789-description
        """
        relationships = []
        
        # Get branch name from metadata
        branch_name = gitlab_item.metadata.get('branch_name', '')
        if not branch_name:
            return relationships
        
        # Try each branch pattern
        for pattern in self.branch_patterns:
            matches = pattern.findall(branch_name)
            for jira_key in matches:
                if jira_key in jira_key_map:
                    jira_item = jira_key_map[jira_key]
                    
                    relationship = EvidenceRelationship(
                        primary_evidence_id=gitlab_item.id,
                        related_evidence_id=jira_item.id,
                        relationship_type=RelationshipType.RELATED_TO,
                        confidence_score=0.7,  # High confidence for branch patterns
                        detection_method=DetectionMethod.BRANCH_NAME,
                        evidence_summary=f"Branch name '{branch_name}' contains JIRA key {jira_key}",
                        metadata={
                            "jira_key": jira_key,
                            "branch_name": branch_name,
                            "pattern_matched": pattern.pattern
                        }
                    )
                    relationships.append(relationship)
        
        return relationships
    
    async def _detect_content_similarity(self, gitlab_item: UnifiedEvidenceItem,
                                       jira_items: List[UnifiedEvidenceItem]) -> List[EvidenceRelationship]:
        """
        Semantic similarity between GitLab descriptions and JIRA content
        Using simple keyword matching and basic similarity scoring
        """
        relationships = []
        
        # Simple keyword-based similarity for now
        # In a more advanced implementation, this could use NLP/embeddings
        
        gitlab_keywords = self._extract_keywords(gitlab_item.title + " " + gitlab_item.description)
        
        for jira_item in jira_items:
            jira_keywords = self._extract_keywords(jira_item.title + " " + jira_item.description)
            
            # Calculate simple similarity score
            similarity_score = self._calculate_keyword_similarity(gitlab_keywords, jira_keywords)
            
            # Only create relationship if similarity is above threshold
            if similarity_score > 0.3:
                relationship = EvidenceRelationship(
                    primary_evidence_id=gitlab_item.id,
                    related_evidence_id=jira_item.id,
                    relationship_type=RelationshipType.RELATED_TO,
                    confidence_score=similarity_score * 0.6,  # Scale down for content similarity
                    detection_method=DetectionMethod.CONTENT_ANALYSIS,
                    evidence_summary=f"Content similarity score: {similarity_score:.2f}",
                    metadata={
                        "similarity_score": similarity_score,
                        "common_keywords": list(gitlab_keywords.intersection(jira_keywords))
                    }
                )
                relationships.append(relationship)
        
        return relationships
    
    def _extract_keywords(self, text: str) -> set:
        """Extract meaningful keywords from text"""
        # Simple keyword extraction - remove common words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = {word for word in words if len(word) > 3 and word not in stop_words}
        
        return keywords
    
    def _calculate_keyword_similarity(self, keywords1: set, keywords2: set) -> float:
        """Calculate similarity between two keyword sets"""
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        # Jaccard similarity
        return len(intersection) / len(union) if union else 0.0
    
    def _deduplicate_relationships(self, relationships: List[EvidenceRelationship]) -> List[EvidenceRelationship]:
        """Remove duplicate relationships, keeping the highest confidence one"""
        seen = {}
        
        for rel in relationships:
            key = (rel.primary_evidence_id, rel.related_evidence_id)
            
            if key not in seen or rel.confidence_score > seen[key].confidence_score:
                seen[key] = rel
        
        return list(seen.values()) 