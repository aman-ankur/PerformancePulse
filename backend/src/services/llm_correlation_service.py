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
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import logging

from anthropic import Anthropic
import openai
from openai import OpenAI

from ..models.correlation_models import (
    UnifiedEvidenceItem,
    EvidenceRelationship,
    RelationshipType,
    DetectionMethod
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CostTracker:
    """Track LLM usage costs with monthly budget limits"""
    monthly_budget: float = 15.00  # $15/month limit
    current_month_usage: float = 0.0
    embedding_cost_per_token: float = 0.0001  # Approximate cost
    llm_cost_per_request: float = 0.01  # Approximate cost for edge cases
    _usage_file = "llm_usage.json"
    
    def __post_init__(self):
        """Load persisted usage data"""
        logger.debug("Initializing CostTracker")
        self.load_usage()
    
    def can_afford_embedding(self, estimated_tokens: int) -> bool:
        estimated_cost = estimated_tokens * self.embedding_cost_per_token
        can_afford = (self.current_month_usage + estimated_cost) <= self.monthly_budget
        logger.debug(f"Can afford embedding? {can_afford} (estimated cost: ${estimated_cost:.4f})")
        return can_afford
    
    def can_afford_llm_call(self) -> bool:
        can_afford = (self.current_month_usage + self.llm_cost_per_request) <= self.monthly_budget
        logger.debug(f"Can afford LLM call? {can_afford} (cost: ${self.llm_cost_per_request:.4f})")
        return can_afford
    
    def record_usage(self, cost: float):
        self.current_month_usage += cost
        logger.info(f"LLM usage: ${cost:.4f}, Total this month: ${self.current_month_usage:.4f}/${self.monthly_budget}")
        self.save_usage()
    
    def load_usage(self):
        """Load usage data from file"""
        try:
            if os.path.exists(self._usage_file):
                with open(self._usage_file, 'r') as f:
                    data = json.load(f)
                    # Reset usage if it's a new month
                    last_update = datetime.fromisoformat(data.get('last_update', '2000-01-01'))
                    if last_update.month != datetime.now().month:
                        logger.info("New month detected, resetting usage")
                        self.current_month_usage = 0.0
                    else:
                        self.current_month_usage = data.get('current_month_usage', 0.0)
                        logger.info(f"Loaded current month usage: ${self.current_month_usage:.4f}")
            else:
                logger.info("No usage file found, starting fresh")
                self.current_month_usage = 0.0
        except Exception as e:
            logger.error(f"Failed to load usage data: {e}")
            self.current_month_usage = 0.0
    
    def save_usage(self):
        """Save usage data to file"""
        try:
            data = {
                'current_month_usage': self.current_month_usage,
                'last_update': datetime.now().isoformat()
            }
            with open(self._usage_file, 'w') as f:
                json.dump(data, f)
            logger.debug(f"Saved usage data: ${self.current_month_usage:.4f}")
        except Exception as e:
            logger.error(f"Failed to save usage data: {e}")

class EmbeddingService:
    """Handle embedding generation for semantic similarity"""
    
    def __init__(self):
        logger.debug("Initializing EmbeddingService")
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            logger.error("OpenAI API key not found in environment")
            raise ValueError("OpenAI API key not configured")
            
        # Log key details (safely)
        logger.debug(f"OpenAI API key found (starts with: {openai_key[:4]}...)")
        
        try:
            self.client = OpenAI(api_key=openai_key)
            # Test the client
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=["Test embedding"]
            )
            if response and response.data:
                logger.info("EmbeddingService initialized and tested successfully")
            else:
                logger.error("EmbeddingService test failed - no response data")
                raise ValueError("EmbeddingService test failed")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
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

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two embedding vectors"""
        try:
            if len(vec1) != len(vec2) or not vec1:
                return 0.0

            # Manual cosine similarity (no numpy dependency)
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5

            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0

            return dot_product / (magnitude1 * magnitude2)
        except Exception as e:
            logger.error(f"Failed cosine similarity calculation: {e}")
            return 0.0

class LLMCorrelationService:
    """
    LLM-based correlation service for evidence analysis
    Uses a 3-tier approach for cost optimization:
    1. Pre-filtering (FREE)
    2. Embedding similarity (cheap)
    3. LLM resolution (expensive, edge cases only)
    """
    
    def __init__(self):
        """Initialize LLM correlation service with cost tracking and API clients"""
        logger.debug("Initializing LLMCorrelationService")
        
        # Load and validate environment variables
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Log environment details
        env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
        logger.debug(f"Looking for .env file at: {env_path}")
        logger.debug(f"Current environment variables:")
        logger.debug(f"- OPENAI_API_KEY present: {bool(openai_key)} (starts with: {openai_key[:4] if openai_key else 'None'})")
        logger.debug(f"- ANTHROPIC_API_KEY present: {bool(anthropic_key)} (starts with: {anthropic_key[:4] if anthropic_key else 'None'})")
        
        self.cost_tracker = CostTracker()
        
        # Initialize embedding service first
        try:
            logger.debug("Initializing EmbeddingService")
            self.embedding_service = EmbeddingService()
        except Exception as e:
            logger.error(f"Failed to initialize EmbeddingService: {e}")
            raise
        
        # Initialize LLM clients with validation
        try:
            if anthropic_key:
                try:
                    self.anthropic_client = Anthropic(api_key=anthropic_key)
                    # Test the client
                    response = self.anthropic_client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=10,
                        messages=[{"role": "user", "content": "Test"}]
                    )
                    if response:
                        logger.info("Anthropic client initialized and tested successfully")
                    else:
                        logger.error("Anthropic client test failed - no response")
                        self.anthropic_client = None
                except Exception as e:
                    logger.error(f"Failed to initialize/test Anthropic client: {e}")
                    self.anthropic_client = None
            else:
                self.anthropic_client = None
                logger.warning("Anthropic API key not found")
            
            if openai_key:
                try:
                    self.openai_client = OpenAI(api_key=openai_key)
                    # Test the client
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Test"}],
                        max_tokens=10
                    )
                    if response:
                        logger.info("OpenAI client initialized and tested successfully")
                    else:
                        logger.error("OpenAI client test failed - no response")
                        self.openai_client = None
                except Exception as e:
                    logger.error(f"Failed to initialize/test OpenAI client: {e}")
                    self.openai_client = None
            else:
                self.openai_client = None
                logger.warning("OpenAI API key not found")
            
            if not (self.anthropic_client or self.openai_client):
                logger.error("No LLM clients available - both API keys are missing or invalid")
                raise ValueError("No LLM clients available - both API keys are missing or invalid")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM clients: {e}")
            self.anthropic_client = None
            self.openai_client = None
            raise
        
        # Configuration
        self.embedding_similarity_threshold = 0.7  # Threshold for embedding similarity
        self.prefilter_rules = [
            'same_author_different_platform',
            'issue_key_in_title_or_description', 
            'temporal_proximity',
            'keyword_overlap'
        ]
        logger.info("LLMCorrelationService initialized successfully")
        
        # Log final service state
        logger.info("LLM Service Status:")
        logger.info(f"- Embedding Service: {'✅ Ready' if self.embedding_service else '❌ Not Available'}")
        logger.info(f"- Anthropic Client: {'✅ Ready' if self.anthropic_client else '❌ Not Available'}")
        logger.info(f"- OpenAI Client: {'✅ Ready' if self.openai_client else '❌ Not Available'}")
        logger.info(f"- Cost Tracker: Current Usage ${self.cost_tracker.current_month_usage:.4f}/${self.cost_tracker.monthly_budget:.2f}")
    
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
                        primary_evidence_id=item1.id,
                        related_evidence_id=item2.id,
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
            pair_key = tuple(sorted([rel.primary_evidence_id, rel.related_evidence_id]))
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
You are an expert software-engineering analyst. Decide whether the two evidence items below are related.

INSTRUCTIONS (VERY IMPORTANT):
• Return a SINGLE-LINE valid JSON object.
• Do NOT wrap it in markdown or code fences.
• Do NOT add any extra keys or text.
• Strings must use double quotes and be escaped per JSON rules.

EXPECTED SHAPE:
{{"is_related":true,"confidence":0.82,"relationship_type":"workflow_progression","reasoning":"<15 words>"}}

EVIDENCE 1
Source: {item1.source}
Title: {item1.title}
Description: {item1.description}
Author: {item1.author_email}
Date: {item1.evidence_date}

EVIDENCE 2
Source: {item2.source}
Title: {item2.title}
Description: {item2.description}
Author: {item2.author_email}
Date: {item2.evidence_date}
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
            
            # Sanitize / extract JSON (strip code fences or preambles)
            import re
            match = re.search(r"\{.*\}", content, re.S)
            if not match:
                raise ValueError("No JSON object found in LLM response")
            json_text = match.group(0)

            result = json.loads(json_text)
            
            if result.get('is_related', False) and result.get('confidence', 0) >= 0.6:
                return EvidenceRelationship(
                    primary_evidence_id=item1.id,
                    related_evidence_id=item2.id,
                    relationship_type=RelationshipType.SEMANTIC_SIMILARITY,
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
        """Get current usage and cost report"""
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        return {
            "total_cost": self.cost_tracker.current_month_usage,
            "embedding_requests": 0,  # TODO: Track these
            "llm_requests": 0,  # TODO: Track these
            "budget_limit": self.cost_tracker.monthly_budget,
            "budget_remaining": self.cost_tracker.monthly_budget - self.cost_tracker.current_month_usage,
            "can_afford_llm_calls": self.cost_tracker.can_afford_llm_call(),
            "cost_breakdown": {
                "embeddings_cost": 0.0,  # TODO: Track separately
                "llm_cost": self.cost_tracker.current_month_usage  # For now, all cost is LLM
            },
            "usage_period": {
                "start_date": month_start.isoformat(),
                "end_date": month_end.isoformat()
            },
            "current_usage": self.cost_tracker.current_month_usage,
            "monthly_budget": self.cost_tracker.monthly_budget,
            "budget_utilization": (self.cost_tracker.current_month_usage / self.cost_tracker.monthly_budget * 100) if self.cost_tracker.monthly_budget else 0.0
        }

def create_llm_correlation_service() -> Optional[LLMCorrelationService]:
    """Create and configure LLM correlation service"""
    try:
        # Check if LLM is enabled in config
        llm_enabled = os.getenv('LLM_ENABLED', 'false').lower() == 'true'
        if not llm_enabled:
            logger.warning("LLM service is disabled in configuration")
            return None

        # Get API keys
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if not anthropic_key and not openai_key:
            logger.error("No LLM API keys configured. Set ANTHROPIC_API_KEY and/or OPENAI_API_KEY in .env")
            return None
            
        # Get budget configuration
        try:
            monthly_budget = float(os.getenv('LLM_MONTHLY_BUDGET', '15.00'))
        except ValueError:
            logger.warning("Invalid LLM_MONTHLY_BUDGET value, using default $15.00")
            monthly_budget = 15.00
            
        # Create and configure service
        service = LLMCorrelationService()
        service.cost_tracker.monthly_budget = monthly_budget
        
        # Verify service initialization
        if not (service.anthropic_client or service.openai_client):
            logger.error("LLM service failed to initialize API clients")
            return None
        
        # Log configuration status
        logger.info("LLM service configured successfully:")
        logger.info(f"- Anthropic API: {'Ready' if service.anthropic_client else 'Not configured'}")
        logger.info(f"- OpenAI API: {'Ready' if service.openai_client else 'Not configured'}")
        logger.info(f"- Monthly budget: ${monthly_budget:.2f}")
        logger.info(f"- Current usage: ${service.cost_tracker.current_month_usage:.2f}")
        
        return service
        
    except Exception as e:
        logger.error(f"Failed to create LLM service: {e}")
        return None 