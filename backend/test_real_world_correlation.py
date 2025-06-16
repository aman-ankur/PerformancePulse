#!/usr/bin/env python3
"""
Real-World LLM Correlation Test
Collects actual JIRA tickets and GitLab MRs from the last week and tests LLM-enhanced correlation
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from services.llm_correlation_service import LLMCorrelationService
from services.gitlab_service import GitLabService
from services.jira_service import JiraService
from models.evidence import EvidenceItem, SourceType, CategoryType
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config.dev.env")

class RealWorldTester:
    def __init__(self):
        self.gitlab_service = GitLabService()
        self.jira_service = JiraService()
        self.llm_service = LLMCorrelationService()
        
        # Check API key configuration
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        print("🔧 Configuration Check:")
        print(f"   Anthropic API Key: {'✅ Set' if self.anthropic_key and self.anthropic_key != 'your_anthropic_api_key_here' else '❌ Missing'}")
        print(f"   OpenAI API Key: {'✅ Set' if self.openai_key and self.openai_key != 'your_openai_api_key_here' else '❌ Missing'}")
        print(f"   GitLab Token: {'✅ Set' if os.getenv('GITLAB_PERSONAL_ACCESS_TOKEN') else '❌ Missing'}")
        print(f"   JIRA Token: {'✅ Set' if os.getenv('JIRA_API_TOKEN') else '❌ Missing'}")
        print()

    async def collect_last_week_data(self) -> Dict[str, List[EvidenceItem]]:
        """Collect JIRA tickets and GitLab MRs from the last week"""
        
        # Calculate date range (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        print(f"📅 Collecting data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print()
        
        evidence_items = []
        
        # Collect GitLab MRs and commits
        print("🦊 Collecting GitLab data...")
        try:
            gitlab_data = await self.gitlab_service.collect_evidence(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            evidence_items.extend(gitlab_data)
            print(f"   ✅ Found {len(gitlab_data)} GitLab items")
        except Exception as e:
            print(f"   ❌ GitLab collection failed: {e}")
        
        # Collect JIRA tickets
        print("🎫 Collecting JIRA data...")
        try:
            jira_data = await self.jira_service.collect_evidence(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            evidence_items.extend(jira_data)
            print(f"   ✅ Found {len(jira_data)} JIRA items")
        except Exception as e:
            print(f"   ❌ JIRA collection failed: {e}")
        
        print(f"\n📊 Total evidence items collected: {len(evidence_items)}")
        
        # Group by team member (based on author/assignee)
        team_data = {}
        for item in evidence_items:
            author = item.metadata.get('author', 'Unknown')
            if author not in team_data:
                team_data[author] = []
            team_data[author].append(item)
        
        print(f"👥 Team members found: {list(team_data.keys())}")
        print()
        
        return team_data

    async def test_correlation_methods(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Test different correlation methods and compare results"""
        
        print("🧠 Testing correlation methods...")
        
        results = {
            'evidence_count': len(evidence_items),
            'rule_based': None,
            'llm_enhanced': None,
            'comparison': None
        }
        
        # Test 1: Rule-based correlation only
        print("   🔧 Testing rule-based correlation...")
        try:
            rule_based_result = await self.llm_service.correlate_evidence_rule_based_only(evidence_items)
            results['rule_based'] = {
                'relationships_found': len(rule_based_result.relationships),
                'avg_confidence': sum(r.confidence_score for r in rule_based_result.relationships) / len(rule_based_result.relationships) if rule_based_result.relationships else 0,
                'processing_time': rule_based_result.processing_time_ms,
                'cost': 0.0
            }
            print(f"      ✅ Found {len(rule_based_result.relationships)} relationships")
        except Exception as e:
            print(f"      ❌ Rule-based correlation failed: {e}")
            results['rule_based'] = {'error': str(e)}
        
        # Test 2: LLM-enhanced correlation (if API keys available)
        if self.anthropic_key and self.openai_key and \
           self.anthropic_key != 'your_anthropic_api_key_here' and \
           self.openai_key != 'your_openai_api_key_here':
            
            print("   🧠 Testing LLM-enhanced correlation...")
            try:
                llm_result = await self.llm_service.correlate_evidence_with_llm(evidence_items)
                results['llm_enhanced'] = {
                    'relationships_found': len(llm_result.relationships),
                    'avg_confidence': sum(r.confidence_score for r in llm_result.relationships) / len(llm_result.relationships) if llm_result.relationships else 0,
                    'processing_time': llm_result.processing_time_ms,
                    'cost': llm_result.total_cost,
                    'method_breakdown': llm_result.method_breakdown,
                    'llm_enhanced_count': sum(1 for r in llm_result.relationships if r.detection_method in ['embedding', 'llm'])
                }
                print(f"      ✅ Found {len(llm_result.relationships)} relationships")
                print(f"      💰 Cost: ${llm_result.total_cost:.4f}")
                print(f"      🧠 LLM-enhanced: {results['llm_enhanced']['llm_enhanced_count']} relationships")
            except Exception as e:
                print(f"      ❌ LLM-enhanced correlation failed: {e}")
                results['llm_enhanced'] = {'error': str(e)}
        else:
            print("   ⚠️  Skipping LLM-enhanced correlation (API keys not configured)")
            results['llm_enhanced'] = {'skipped': 'API keys not configured'}
        
        return results

    def print_detailed_results(self, team_data: Dict[str, List[EvidenceItem]], correlation_results: Dict[str, Any]):
        """Print detailed analysis of the correlation results"""
        
        print("\n" + "="*80)
        print("📊 DETAILED CORRELATION ANALYSIS")
        print("="*80)
        
        # Team member breakdown
        print("\n👥 TEAM MEMBER BREAKDOWN:")
        for member, items in team_data.items():
            gitlab_items = [i for i in items if i.source == 'gitlab']
            jira_items = [i for i in items if i.source == 'jira']
            print(f"   {member}:")
            print(f"      GitLab: {len(gitlab_items)} items")
            print(f"      JIRA: {len(jira_items)} items")
        
        # Correlation method comparison
        print("\n🔍 CORRELATION METHOD COMPARISON:")
        
        if correlation_results['rule_based'] and 'error' not in correlation_results['rule_based']:
            rb = correlation_results['rule_based']
            print(f"   Rule-based:")
            print(f"      Relationships: {rb['relationships_found']}")
            print(f"      Avg Confidence: {rb['avg_confidence']:.2%}")
            print(f"      Processing Time: {rb['processing_time']}ms")
            print(f"      Cost: $0.00")
        
        if correlation_results['llm_enhanced'] and 'error' not in correlation_results['llm_enhanced'] and 'skipped' not in correlation_results['llm_enhanced']:
            llm = correlation_results['llm_enhanced']
            print(f"   LLM-enhanced:")
            print(f"      Relationships: {llm['relationships_found']}")
            print(f"      Avg Confidence: {llm['avg_confidence']:.2%}")
            print(f"      Processing Time: {llm['processing_time']}ms")
            print(f"      Cost: ${llm['cost']:.4f}")
            print(f"      LLM-enhanced: {llm['llm_enhanced_count']} relationships")
            if 'method_breakdown' in llm:
                print(f"      Method breakdown: {llm['method_breakdown']}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if correlation_results['llm_enhanced'] and 'error' not in correlation_results['llm_enhanced'] and 'skipped' not in correlation_results['llm_enhanced']:
            llm = correlation_results['llm_enhanced']
            rb = correlation_results['rule_based']
            
            if llm['relationships_found'] > rb['relationships_found']:
                improvement = llm['relationships_found'] - rb['relationships_found']
                print(f"   ✅ LLM found {improvement} additional relationships ({improvement/rb['relationships_found']*100:.1f}% improvement)")
            
            if llm['avg_confidence'] > rb['avg_confidence']:
                confidence_improvement = llm['avg_confidence'] - rb['avg_confidence']
                print(f"   ✅ LLM improved confidence by {confidence_improvement:.1%}")
            
            monthly_cost = llm['cost'] * 30  # Rough monthly estimate
            print(f"   💰 Estimated monthly cost: ${monthly_cost:.2f}")
            
            if monthly_cost < 15:
                print(f"   ✅ Well within $15/month budget")
            else:
                print(f"   ⚠️  May exceed $15/month budget")
        else:
            print("   ⚠️  Configure API keys to test LLM-enhanced correlation")
            print("   📝 Add your Anthropic and OpenAI API keys to config.dev.env")

    async def run_test(self):
        """Run the complete real-world test"""
        
        print("🚀 PERFORMANCEPULSE REAL-WORLD LLM CORRELATION TEST")
        print("="*60)
        print()
        
        # Step 1: Collect data
        team_data = await self.collect_last_week_data()
        
        if not team_data:
            print("❌ No data collected. Please check your GitLab and JIRA configuration.")
            return
        
        # Step 2: Test correlation for each team member
        all_evidence = []
        for member, items in team_data.items():
            all_evidence.extend(items)
        
        if len(all_evidence) < 2:
            print("⚠️  Need at least 2 evidence items to test correlation.")
            return
        
        # Step 3: Run correlation tests
        correlation_results = await self.test_correlation_methods(all_evidence)
        
        # Step 4: Print detailed analysis
        self.print_detailed_results(team_data, correlation_results)
        
        # Step 5: Save results to file
        results_file = f"correlation_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'team_data_summary': {member: len(items) for member, items in team_data.items()},
                'correlation_results': correlation_results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
        print("\n🎉 Test completed!")

async def main():
    """Main test function"""
    tester = RealWorldTester()
    await tester.run_test()

if __name__ == "__main__":
    asyncio.run(main()) 