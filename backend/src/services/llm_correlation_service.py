"""
LLM Correlation Service - Phase 2.1.2
Cost-optimized semantic correlation with 3-tier pipeline:
1. Pre-filtering (FREE) - eliminate 70-90% of unrelated pairs
2. Embedding similarity ($0.0001 each) - handle 85-90% of correlations  
3. LLM edge cases ($0.01 each) - resolve final 5-10%
Budget: <$15/month for 3 team members
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from dataclasses import dataclass
import logging

from anthropic import Anthropic
import openai
from openai import OpenAI

from ..models.unified_evidence import UnifiedEvidenceItem 
from ..models.correlation_models import EvidenceRelationship, RelationshipType, DetectionMethod

logger = logging.getLogger(__name__)

@dataclass
class CostTracker:
    """Track LLM usage costs with monthly budget limits"""
    monthly_budget: float = 15.00  # $15/month limit
    current_month_usage: float = 0.0
    embedding_cost_per_token: float = 0.0001  # Approximate cost
    llm_cost_per_request: float = 0.01  # Approximate cost for edge cases
    
    def can_afford_embedding(self, estimated_tokens: int) -> bool:
        estimated_cost = estimated_tokens * self.embedding_cost_per_token
        return (self.current_month_usage + estimated_cost) <= self.monthly_budget
    
    def can_afford_llm_call(self) -> bool:
        return (self.current_month_usage + self.llm_cost_per_request) <= self.monthly_budget
    
    def record_usage(self, cost: float):
        self.current_month_usage += cost
        logger.info(f"LLM usage: ${cost:.4f}, Total this month: ${self.current_month_usage:.4f}/${self.monthly_budget}")

class EmbeddingService:
    """Handle embedding generation for semantic similarity"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for text content"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",  # Cost-effective model
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        import math
        
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        magnitude1 = math.sqrt(sum(a * a for a in embedding1))
        magnitude2 = math.sqrt(sum(a * a for a in embedding2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

class LLMCorrelationService:
    """Main LLM correlation service with cost optimization"""
    
    def __init__(self):
        self.cost_tracker = CostTracker()
        self.embedding_service = EmbeddingService()
        
        # Initialize LLM clients
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        self.anthropic_client = Anthropic(api_key=anthropic_key) if anthropic_key else None
        self.openai_client = OpenAI(api_key=openai_key) if openai_key else None
        
        # Configuration
        self.embedding_similarity_threshold = 0.7  # Threshold for embedding similarity
        self.prefilter_rules = [
            'same_author_different_platform',
            'issue_key_in_title_or_description', 
            'temporal_proximity',
            'keyword_overlap'
        ]
    
    async def correlate_evidence_with_llm(self, evidence_items: List[UnifiedEvidenceItem]) -> List[EvidenceRelationship]:
        """
        Main correlation method with 3-tier cost optimization:
        Tier 1: Pre-filtering (FREE) 
        Tier 2: Embedding similarity (cheap)
        Tier 3: LLM resolution (expensive, edge cases only)
        """
        logger.info(f"Starting LLM correlation for {len(evidence_items)} evidence items")
        
        # Tier 1: Pre-filtering (FREE) - eliminate obviously unrelated pairs
        filtered_pairs = self._prefilter_evidence_pairs(evidence_items)
        logger.info(f"Pre-filtering: {len(filtered_pairs)} pairs after filtering from {len(evidence_items)*(len(evidence_items)-1)//2} total pairs")
        
        if not filtered_pairs:
            return []
        
        # Tier 2: Embedding similarity (cheap) - semantic correlation
        semantic_relationships = await self._correlate_with_embeddings(filtered_pairs)
        logger.info(f"Embedding correlation: {len(semantic_relationships)} relationships found")
        
        # Tier 3: LLM edge cases (expensive) - only unclear relationships
        edge_case_pairs = self._identify_edge_cases(filtered_pairs, semantic_relationships)
        llm_relationships = await self._correlate_edge_cases_with_llm(edge_case_pairs)
        logger.info(f"LLM edge cases: {len(llm_relationships)} additional relationships found")
        
        # Combine all relationships
        all_relationships = semantic_relationships + llm_relationships
        
        logger.info(f"Total LLM correlation results: {len(all_relationships)} relationships")
        return all_relationships
    
    def _prefilter_evidence_pairs(self, evidence_items: List[UnifiedEvidenceItem]) -> List[Tuple[UnifiedEvidenceItem, UnifiedEvidenceItem]]:
        """
        Tier 1: Pre-filtering using rule-based logic (FREE)
        Eliminate 70-90% of obviously unrelated pairs
        """
        filtered_pairs = []
        
        for i, item1 in enumerate(evidence_items):
            for j, item2 in enumerate(evidence_items[i+1:], i+1):
                if self._passes_prefilter(item1, item2):
                    filtered_pairs.append((item1, item2))
        
        return filtered_pairs
    
    def _passes_prefilter(self, item1: UnifiedEvidenceItem, item2: UnifiedEvidenceItem) -> bool:
        """Check if a pair passes pre-filtering rules"""
        
        # Rule 1: Same author, different platforms (high correlation likelihood)
        if (item1.author_email == item2.author_email and 
            item1.source != item2.source):
            return True
        
        # Rule 2: Issue key detection (JIRA-123 in GitLab MR)
        if self._has_cross_platform_issue_reference(item1, item2):
            return True
        
        # Rule 3: Temporal proximity (within 24 hours)
        if self._has_temporal_proximity(item1, item2):
            return True
        
        # Rule 4: Significant keyword overlap
        if self._has_keyword_overlap(item1, item2):
            return True
        
        return False
    
    def _has_cross_platform_issue_reference(self, item1: UnifiedEvidenceItem, item2: UnifiedEvidenceItem) -> bool:
        """Check for cross-platform issue references"""
        import re
        
        # Common JIRA key patterns
        jira_pattern = r'[A-Z]+-\d+'
        
        # Extract potential issue keys from both items
        text1 = f"{item1.title} {item1.description}".lower()
        text2 = f"{item2.title} {item2.description}".lower()
        
        keys1 = set(re.findall(jira_pattern, text1, re.IGNORECASE))
        keys2 = set(re.findall(jira_pattern, text2, re.IGNORECASE))
        
        # Check for common issue keys
        return bool(keys1.intersection(keys2))
    
    def _has_temporal_proximity(self, item1: UnifiedEvidenceItem, item2: UnifiedEvidenceItem) -> bool:
        """Check if items are temporally close (within 24 hours)"""
        if not (item1.evidence_date and item2.evidence_date):
            return False
        
        time_diff = abs((item1.evidence_date - item2.evidence_date).total_seconds())
        return time_diff <= 24 * 3600  # 24 hours
    
    def _has_keyword_overlap(self, item1: UnifiedEvidenceItem, item2: UnifiedEvidenceItem) -> bool:
        """Check for significant keyword overlap"""
        import re
        
        # Extract meaningful keywords (3+ characters, not common words)
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'way', 'when', 'with'}
        
        text1 = f"{item1.title} {item1.description}".lower()
        text2 = f"{item2.title} {item2.description}".lower()
        
        words1 = set(re.findall(r'\b\w{3,}\b', text1)) - stop_words
        words2 = set(re.findall(r'\b\w{3,}\b', text2)) - stop_words
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1.intersection(words2))
        min_words = min(len(words1), len(words2))
        
        # Require at least 20% keyword overlap
        return (overlap / min_words) >= 0.2
    
    async def _correlate_with_embeddings(self, evidence_pairs: List[Tuple[UnifiedEvidenceItem, UnifiedEvidenceItem]]) -> List[EvidenceRelationship]:
        """
        Tier 2: Embedding-based semantic correlation (cheap)
        Handle 85-90% of remaining correlations
        """
        if not evidence_pairs:
            return []
        
        # Estimate cost and check budget
        estimated_tokens = sum(len(f"{item1.title} {item1.description} {item2.title} {item2.description}".split()) 
                              for item1, item2 in evidence_pairs)
        
        if not self.cost_tracker.can_afford_embedding(estimated_tokens):
            logger.warning("Embedding budget exceeded, using rule-based fallback")
            return self._fallback_rule_based_correlation(evidence_pairs)
        
        try:
            relationships = []
            
            # Process in batches to avoid API limits
            batch_size = 20
            for i in range(0, len(evidence_pairs), batch_size):
                batch = evidence_pairs[i:i+batch_size]
                batch_relationships = await self._process_embedding_batch(batch)
                relationships.extend(batch_relationships)
            
            # Record cost
            actual_cost = estimated_tokens * self.cost_tracker.embedding_cost_per_token
            self.cost_tracker.record_usage(actual_cost)
            
            return relationships
            
        except Exception as e:
            logger.error(f"Embedding correlation failed: {e}")
            return self._fallback_rule_based_correlation(evidence_pairs)
    
    async def _process_embedding_batch(self, evidence_pairs: List[Tuple[UnifiedEvidenceItem, UnifiedEvidenceItem]]) -> List[EvidenceRelationship]:
        """Process a batch of evidence pairs for embedding similarity"""
        relationships = []
        
        # Prepare texts for embedding
        texts = []
        for item1, item2 in evidence_pairs:
            text1 = f"{item1.title} {item1.description}"
            text2 = f"{item2.title} {item2.description}"
            texts.extend([text1, text2])
        
        # Get embeddings
        embeddings = await self.embedding_service.get_embeddings(texts)
        
        if len(embeddings) != len(texts):
            logger.error("Embedding count mismatch")
            return []
        
        # Calculate similarities
        for i, (item1, item2) in enumerate(evidence_pairs):
            embedding1_idx = i * 2
            embedding2_idx = i * 2 + 1
            
            if embedding1_idx < len(embeddings) and embedding2_idx < len(embeddings):
                similarity = self.embedding_service.cosine_similarity(
                    embeddings[embedding1_idx], 
                    embeddings[embedding2_idx]
                )
                
                if similarity >= self.embedding_similarity_threshold:
                    relationship = EvidenceRelationship(
                        evidence_id_1=item1.id,
                        evidence_id_2=item2.id,
                        relationship_type=RelationshipType.SEMANTIC_SIMILARITY,
                        confidence_score=min(similarity, 1.0),
                        detection_method=DetectionMethod.LLM_SEMANTIC,
                        metadata={
                            'embedding_similarity': similarity,
                            'correlation_tier': 'embedding'
                        }
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _identify_edge_cases(self, all_pairs: List[Tuple[UnifiedEvidenceItem, UnifiedEvidenceItem]], 
                           found_relationships: List[EvidenceRelationship]) -> List[Tuple[UnifiedEvidenceItem, UnifiedEvidenceItem]]:
        """Identify pairs that need LLM resolution (edge cases)"""
        
        # Get evidence IDs that already have relationships
        related_pairs = set()
        for rel in found_relationships:
            pair_key = tuple(sorted([rel.evidence_id_1, rel.evidence_id_2]))
            related_pairs.add(pair_key)
        
        # Find unresolved pairs that passed pre-filtering but weren't caught by embeddings
        edge_cases = []
        for item1, item2 in all_pairs:
            pair_key = tuple(sorted([item1.id, item2.id]))
            if pair_key not in related_pairs:
                # Additional heuristics for identifying true edge cases
                if self._is_potential_edge_case(item1, item2):
                    edge_cases.append((item1, item2))
        
        # Limit edge cases to control costs (max 10 per correlation run)
        return edge_cases[:10]
    
    def _is_potential_edge_case(self, item1: UnifiedEvidenceItem, item2: UnifiedEvidenceItem) -> bool:
        """Identify potential edge cases that might benefit from LLM analysis"""
        
        # Same author but low embedding similarity might be related
        if item1.author_email == item2.author_email:
            return True
        
        # Cross-platform with temporal proximity but no clear keyword match
        if (item1.source != item2.source and 
            self._has_temporal_proximity(item1, item2)):
            return True
        
        # Technical content that might have implicit relationships
        technical_keywords = ['api', 'database', 'service', 'component', 'module', 'function']
        text1 = f"{item1.title} {item1.description}".lower()
        text2 = f"{item2.title} {item2.description}".lower()
        
        has_technical1 = any(keyword in text1 for keyword in technical_keywords)
        has_technical2 = any(keyword in text2 for keyword in technical_keywords)
        
        return has_technical1 and has_technical2
    
    async def _correlate_edge_cases_with_llm(self, edge_cases: List[Tuple[UnifiedEvidenceItem, UnifiedEvidenceItem]]) -> List[EvidenceRelationship]:
        """
        Tier 3: LLM resolution for edge cases (expensive)
        Only for final 5-10% that need human-like reasoning
        """
        if not edge_cases:
            return []
        
        relationships = []
        
        for item1, item2 in edge_cases:
            if not self.cost_tracker.can_afford_llm_call():
                logger.warning("LLM budget exceeded, stopping edge case processing")
                break
            
            try:
                relationship = await self._analyze_pair_with_llm(item1, item2)
                if relationship:
                    relationships.append(relationship)
                
                # Record cost
                self.cost_tracker.record_usage(self.cost_tracker.llm_cost_per_request)
                
            except Exception as e:
                logger.error(f"LLM analysis failed for pair {item1.id}-{item2.id}: {e}")
                continue
        
        return relationships
    
    async def _analyze_pair_with_llm(self, item1: UnifiedEvidenceItem, item2: UnifiedEvidenceItem) -> Optional[EvidenceRelationship]:
        """Analyze a single evidence pair with LLM for relationship detection"""
        
        prompt = f"""
Analyze these two software development evidence items and determine if they are related:

Evidence 1:
- Source: {item1.source}
- Title: {item1.title}
- Description: {item1.description}
- Author: {item1.author_email}
- Date: {item1.evidence_date}

Evidence 2:
- Source: {item2.source}
- Title: {item2.title}
- Description: {item2.description}
- Author: {item2.author_email}
- Date: {item2.evidence_date}

Are these evidence items related? Consider:
1. Do they refer to the same feature, bug, or project component?
2. Are they part of the same development workflow?
3. Do they show progression of the same work?
4. Are they complementary activities (e.g., code + review, issue + implementation)?

Respond with JSON only:
{{
    "is_related": true/false,
    "confidence": 0.0-1.0,
    "relationship_type": "same_feature|workflow_progression|complementary_activities|technical_dependency|none",
    "reasoning": "brief explanation"
}}
"""
        
        try:
            if self.anthropic_client:
                response = self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",  # Cost-effective model
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text
            elif self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Cost-effective model
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.choices[0].message.content
            else:
                logger.error("No LLM client available")
                return None
            
            # Parse JSON response
            result = json.loads(content)
            
            if result.get('is_related', False) and result.get('confidence', 0) >= 0.6:
                return EvidenceRelationship(
                    evidence_id_1=item1.id,
                    evidence_id_2=item2.id,
                    relationship_type=RelationshipType.SEMANTIC_SIMILARITY,  # Map to existing enum
                    confidence_score=result['confidence'],
                    detection_method=DetectionMethod.LLM_SEMANTIC,
                    metadata={
                        'llm_relationship_type': result.get('relationship_type'),
                        'llm_reasoning': result.get('reasoning'),
                        'correlation_tier': 'llm_edge_case'
                    }
                )
            
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return None
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return None
    
    def _fallback_rule_based_correlation(self, evidence_pairs: List[Tuple[UnifiedEvidenceItem, UnifiedEvidenceItem]]) -> List[EvidenceRelationship]:
        """Fallback to rule-based correlation when budget is exceeded"""
        logger.info("Using rule-based fallback correlation")
        
        # Import existing rule-based algorithms
        from ..algorithms.jira_gitlab_linker import JiraGitLabLinker
        from ..algorithms.confidence_scorer import ConfidenceScorer
        
        linker = JiraGitLabLinker()
        scorer = ConfidenceScorer()
        
        relationships = []
        
        for item1, item2 in evidence_pairs:
            # Use existing rule-based detection
            detected_relationships = linker.detect_relationships([item1, item2])
            for rel in detected_relationships:
                # Update detection method to indicate fallback
                rel.metadata = rel.metadata or {}
                rel.metadata['correlation_tier'] = 'rule_based_fallback'
                relationships.append(rel)
        
        return relationships
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Get current usage and budget status"""
        return {
            'monthly_budget': self.cost_tracker.monthly_budget,
            'current_usage': self.cost_tracker.current_month_usage,
            'remaining_budget': self.cost_tracker.monthly_budget - self.cost_tracker.current_month_usage,
            'budget_utilization': (self.cost_tracker.current_month_usage / self.cost_tracker.monthly_budget) * 100,
            'can_afford_embeddings': self.cost_tracker.can_afford_embedding(1000),  # Sample check
            'can_afford_llm_calls': self.cost_tracker.can_afford_llm_call()
        }

# Factory function for easy integration
def create_llm_correlation_service() -> LLMCorrelationService:
    """Create and configure LLM correlation service"""
    return LLMCorrelationService() 