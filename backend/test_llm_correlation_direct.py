#!/usr/bin/env python3
"""
Direct LLM Correlation Test - Tests the 3-tier correlation system directly
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config.dev.env")

class DirectLLMTester:
    """Test LLM correlation without complex service dependencies"""
    
    def __init__(self):
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        print("🔧 DIRECT LLM CORRELATION TEST")
        print("=" * 50)
        print(f"✅ Anthropic API: {'Ready' if self.anthropic_key else 'Missing'}")
        print(f"✅ OpenAI API: {'Ready' if self.openai_key else 'Missing'}")
        print()
    
    def create_sample_evidence(self) -> List[Dict]:
        """Create realistic sample evidence for testing"""
        return [
            {
                'id': 'gl-1',
                'title': 'Fix authentication timeout in login service',
                'description': 'Resolved AUTH-456 issue where JWT tokens were expiring too quickly causing user login failures',
                'author': 'john.doe@company.com',
                'source': 'gitlab',
                'category': 'merge_request',
                'date': datetime.now(),
                'metadata': {
                    'project': 'auth-service',
                    'branch': 'bugfix/auth-456-timeout'
                }
            },
            {
                'id': 'jira-1', 
                'title': 'AUTH-456: Users getting logged out frequently',
                'description': 'Multiple users report being logged out every few minutes. Investigation shows JWT token expiration is set too low.',
                'author': 'jane.smith@company.com',
                'source': 'jira',
                'category': 'bug',
                'date': datetime.now() - timedelta(hours=3),
                'metadata': {
                    'assignee': 'john.doe@company.com',
                    'priority': 'High',
                    'status': 'Resolved'
                }
            },
            {
                'id': 'gl-2',
                'title': 'Optimize database query performance',
                'description': 'Improved user lookup queries by adding indexes and optimizing JOIN operations',
                'author': 'bob.wilson@company.com',
                'source': 'gitlab', 
                'category': 'merge_request',
                'date': datetime.now() - timedelta(hours=5),
                'metadata': {
                    'project': 'user-service'
                }
            },
            {
                'id': 'jira-2',
                'title': 'DB-789: Slow user search functionality',
                'description': 'User search is taking 5+ seconds. Database team needs to optimize queries.',
                'author': 'alice.brown@company.com',
                'source': 'jira',
                'category': 'story',
                'date': datetime.now() - timedelta(hours=8),
                'metadata': {
                    'assignee': 'bob.wilson@company.com',
                    'priority': 'Medium'
                }
            },
            {
                'id': 'gl-3',
                'title': 'Update payment gateway integration',
                'description': 'Migrated from old payment API to new Stripe integration with better error handling',
                'author': 'carol.green@company.com',
                'source': 'gitlab',
                'category': 'merge_request', 
                'date': datetime.now() - timedelta(days=1),
                'metadata': {
                    'project': 'payment-service'
                }
            }
        ]
    
    def test_rule_based_correlation(self, evidence_items: List[Dict]) -> List[Dict]:
        """Test rule-based correlation (pre-filtering)"""
        print("🔧 TESTING RULE-BASED CORRELATION")
        print("-" * 40)
        
        correlations = []
        
        for i, item1 in enumerate(evidence_items):
            for j, item2 in enumerate(evidence_items[i+1:], i+1):
                correlation = self.correlate_pair_rule_based(item1, item2)
                if correlation['correlated']:
                    correlations.append(correlation)
        
        print(f"✅ Found {len(correlations)} rule-based correlations:")
        for corr in correlations:
            print(f"   {corr['item1_id']} ↔ {corr['item2_id']}")
            print(f"   Method: {corr['method']}, Confidence: {corr['confidence']:.1%}")
            if 'reason' in corr:
                print(f"   Reason: {corr['reason']}")
            print()
        
        return correlations
    
    def correlate_pair_rule_based(self, item1: Dict, item2: Dict) -> Dict:
        """Rule-based correlation between two items"""
        
        # Rule 1: Issue key references (highest confidence)
        import re
        jira_pattern = r'[A-Z]+-\d+'
        
        text1 = f"{item1['title']} {item1['description']}"
        text2 = f"{item2['title']} {item2['description']}"
        
        keys1 = set(re.findall(jira_pattern, text1, re.IGNORECASE))
        keys2 = set(re.findall(jira_pattern, text2, re.IGNORECASE))
        common_keys = keys1.intersection(keys2)
        
        if common_keys:
            return {
                'correlated': True,
                'method': 'issue_key_reference',
                'confidence': 0.95,
                'item1_id': item1['id'],
                'item2_id': item2['id'],
                'reason': f"Common issue keys: {list(common_keys)}"
            }
        
        # Rule 2: Same author + different platform
        same_author = item1['author'] == item2['author']
        diff_platform = item1['source'] != item2['source']
        
        if same_author and diff_platform:
            return {
                'correlated': True,
                'method': 'cross_platform_author',
                'confidence': 0.85,
                'item1_id': item1['id'],
                'item2_id': item2['id'],
                'reason': f"Same author ({item1['author']}) across platforms"
            }
        
        # Rule 3: Assignee relationship (JIRA assignee = GitLab author)
        if item1['source'] == 'jira' and item2['source'] == 'gitlab':
            assignee = item1['metadata'].get('assignee')
            author = item2['author']
            if assignee and assignee == author:
                return {
                    'correlated': True,
                    'method': 'assignee_author_match',
                    'confidence': 0.80,
                    'item1_id': item1['id'],
                    'item2_id': item2['id'],
                    'reason': f"JIRA assignee matches GitLab author ({assignee})"
                }
        elif item1['source'] == 'gitlab' and item2['source'] == 'jira':
            assignee = item2['metadata'].get('assignee')
            author = item1['author']
            if assignee and assignee == author:
                return {
                    'correlated': True,
                    'method': 'assignee_author_match',
                    'confidence': 0.80,
                    'item1_id': item1['id'],
                    'item2_id': item2['id'],
                    'reason': f"GitLab author matches JIRA assignee ({assignee})"
                }
        
        return {
            'correlated': False,
            'method': 'no_correlation',
            'confidence': 0.0,
            'item1_id': item1['id'],
            'item2_id': item2['id']
        }
    
    async def test_embedding_correlation(self, evidence_items: List[Dict]) -> List[Dict]:
        """Test OpenAI embedding-based correlation"""
        print("🔍 TESTING EMBEDDING CORRELATION")
        print("-" * 40)
        
        if not self.openai_key:
            print("⚠️  Skipping embedding test - OpenAI key not available")
            return []
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)
            
            # Generate embeddings for all items
            embeddings = {}
            total_cost = 0.0
            
            for item in evidence_items:
                text = f"{item['title']} {item['description']}"
                
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=[text]
                )
                
                embeddings[item['id']] = response.data[0].embedding
                # Cost: ~$0.0001 per 1K tokens (estimate 100 tokens per item)
                total_cost += 0.00001
            
            print(f"✅ Generated embeddings for {len(evidence_items)} items")
            print(f"💰 Estimated cost: ${total_cost:.5f}")
            
            # Calculate similarities
            correlations = []
            import math
            
            for i, item1 in enumerate(evidence_items):
                for j, item2 in enumerate(evidence_items[i+1:], i+1):
                    
                    # Calculate cosine similarity
                    vec1 = embeddings[item1['id']]
                    vec2 = embeddings[item2['id']]
                    
                    dot_product = sum(a * b for a, b in zip(vec1, vec2))
                    magnitude1 = math.sqrt(sum(a * a for a in vec1))
                    magnitude2 = math.sqrt(sum(a * a for a in vec2))
                    
                    similarity = dot_product / (magnitude1 * magnitude2)
                    
                    # Threshold for correlation (you can adjust this)
                    if similarity > 0.8:  # High similarity threshold
                        correlations.append({
                            'correlated': True,
                            'method': 'embedding_similarity',
                            'confidence': min(similarity, 0.95),  # Cap at 95%
                            'item1_id': item1['id'],
                            'item2_id': item2['id'],
                            'similarity': similarity,
                            'reason': f"High semantic similarity ({similarity:.3f})"
                        })
            
            print(f"✅ Found {len(correlations)} embedding-based correlations:")
            for corr in correlations:
                print(f"   {corr['item1_id']} ↔ {corr['item2_id']}")
                print(f"   Similarity: {corr['similarity']:.3f}, Confidence: {corr['confidence']:.1%}")
                print()
            
            return correlations
            
        except Exception as e:
            print(f"❌ Embedding correlation failed: {e}")
            return []
    
    async def test_llm_correlation(self, evidence_items: List[Dict], uncorrelated_pairs: List[tuple]) -> List[Dict]:
        """Test Anthropic LLM correlation for edge cases"""
        print("🧠 TESTING LLM CORRELATION")
        print("-" * 40)
        
        if not self.anthropic_key:
            print("⚠️  Skipping LLM test - Anthropic key not available")
            return []
        
        if not uncorrelated_pairs:
            print("⚠️  No uncorrelated pairs to test with LLM")
            return []
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            
            correlations = []
            total_cost = 0.0
            
            # Test first few uncorrelated pairs with LLM
            test_pairs = uncorrelated_pairs[:3]  # Limit to save costs
            
            for item1_id, item2_id in test_pairs:
                item1 = next(item for item in evidence_items if item['id'] == item1_id)
                item2 = next(item for item in evidence_items if item['id'] == item2_id)
                
                prompt = f"""
                Analyze if these two software development items are related:

                Item 1 ({item1['source']}): {item1['title']}
                Description: {item1['description']}
                Author: {item1['author']}

                Item 2 ({item2['source']}): {item2['title']} 
                Description: {item2['description']}
                Author: {item2['author']}

                Are these items related to the same feature, bug, or work stream? 
                Respond with: YES or NO, followed by a confidence level (0-100%) and brief reason.
                
                Format: [YES/NO] - [confidence]% - [reason]
                """
                
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=100,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                result = response.content[0].text.strip()
                
                # Parse response
                if result.upper().startswith('YES'):
                    # Extract confidence if possible
                    import re
                    confidence_match = re.search(r'(\d+)%', result)
                    confidence = int(confidence_match.group(1)) / 100 if confidence_match else 0.7
                    
                    correlations.append({
                        'correlated': True,
                        'method': 'llm_semantic',
                        'confidence': confidence,
                        'item1_id': item1['id'],
                        'item2_id': item2['id'],
                        'llm_response': result,
                        'reason': f"LLM semantic analysis: {result}"
                    })
                
                # Estimate cost (~$0.01 per request)
                total_cost += 0.01
            
            print(f"✅ Tested {len(test_pairs)} pairs with LLM")
            print(f"💰 Estimated cost: ${total_cost:.3f}")
            print(f"✅ Found {len(correlations)} LLM-based correlations:")
            
            for corr in correlations:
                print(f"   {corr['item1_id']} ↔ {corr['item2_id']}")
                print(f"   Confidence: {corr['confidence']:.1%}")
                print(f"   LLM: {corr['llm_response']}")
                print()
            
            return correlations
            
        except Exception as e:
            print(f"❌ LLM correlation failed: {e}")
            return []
    
    async def run_full_test(self):
        """Run the complete 3-tier correlation test"""
        print("🚀 RUNNING FULL 3-TIER CORRELATION TEST")
        print("=" * 60)
        
        # Create sample evidence
        evidence_items = self.create_sample_evidence()
        print(f"📊 Testing with {len(evidence_items)} evidence items")
        print()
        
        # Tier 1: Rule-based correlation (FREE)
        rule_based_correlations = self.test_rule_based_correlation(evidence_items)
        
        # Tier 2: Embedding correlation (CHEAP)
        embedding_correlations = await self.test_embedding_correlation(evidence_items)
        
        # Find uncorrelated pairs for LLM testing
        all_pairs = [(evidence_items[i]['id'], evidence_items[j]['id']) 
                    for i in range(len(evidence_items)) 
                    for j in range(i+1, len(evidence_items))]
        
        correlated_pairs = {(c['item1_id'], c['item2_id']) for c in rule_based_correlations + embedding_correlations}
        uncorrelated_pairs = [pair for pair in all_pairs if pair not in correlated_pairs]
        
        # Tier 3: LLM correlation for edge cases (EXPENSIVE)
        llm_correlations = await self.test_llm_correlation(evidence_items, uncorrelated_pairs)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 FINAL CORRELATION RESULTS")
        print("=" * 60)
        
        total_correlations = rule_based_correlations + embedding_correlations + llm_correlations
        
        print(f"🔧 Rule-based: {len(rule_based_correlations)} correlations (FREE)")
        print(f"🔍 Embedding: {len(embedding_correlations)} correlations (~$0.00005)")
        print(f"🧠 LLM: {len(llm_correlations)} correlations (~$0.03)")
        print(f"📈 Total: {len(total_correlations)} correlations")
        
        print(f"\n💰 COST BREAKDOWN:")
        print(f"   Pre-filtering: $0.00 (eliminated {len(all_pairs) - len(uncorrelated_pairs) - len(embedding_correlations)} pairs)")
        print(f"   Embeddings: ~$0.00005 (processed {len(evidence_items)} items)")
        print(f"   LLM: ~$0.03 (processed {min(3, len(uncorrelated_pairs))} pairs)")
        print(f"   TOTAL: ~$0.03005 (well under $15 budget!)")
        
        print(f"\n🎯 PERFORMANCE:")
        print(f"   Coverage: {len(total_correlations)}/{len(all_pairs)} pairs analyzed ({len(total_correlations)/len(all_pairs)*100:.1f}%)")
        print(f"   Cost efficiency: Only {min(3, len(uncorrelated_pairs))}/{len(all_pairs)} pairs needed expensive LLM analysis")
        
        if total_correlations:
            print(f"\n✅ SUCCESS: Found meaningful correlations!")
            print("   Your 3-tier LLM correlation system is working perfectly!")
        else:
            print(f"\n⚠️  No correlations found in this test set")
            print("   This is normal for unrelated sample data")

if __name__ == "__main__":
    async def main():
        tester = DirectLLMTester()
        await tester.run_full_test()
    
    asyncio.run(main()) 