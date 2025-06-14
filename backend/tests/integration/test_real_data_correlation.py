"""
Integration Test for Unified Evidence Service with Real Data
Tests the complete evidence collection pipeline with actual GitLab and JIRA data

Usage:
    python test_real_data_correlation.py --gitlab-project=12345678 --jira-project=TEST --username=testuser
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.models.unified_evidence import (
    CollectionRequest,
    PlatformType,
    DataSourceType,
    ValidationStatus
)
from src.services.unified_evidence_service import create_unified_evidence_service

class RealDataIntegrationTester:
    """Integration tester for real data validation"""
    
    def __init__(self):
        # Load configuration from environment or config file
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """Load configuration from environment variables"""
        config = {}
        
        # Try to load from backend config file if environment variables not set
        config_file = Path(__file__).parent.parent.parent / "config.dev.env"
        if config_file.exists():
            print(f"Loading configuration from {config_file}")
            with open(config_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value
        
        # Override with environment variables if present
        env_vars = [
            'GITLAB_PERSONAL_ACCESS_TOKEN',
            'GITLAB_PROJECT_ID',
            'GITLAB_API_URL',
            'JIRA_BASE_URL',
            'JIRA_CLOUD_ID',
            'JIRA_MCP_SERVER_URL',
            'JIRA_API_TOKEN',
            'JIRA_USER_EMAIL',
            'JIRA_PROJECT_KEY'
        ]
        
        for var in env_vars:
            if os.getenv(var):
                config[var] = os.getenv(var)
        
        return config
    
    async def test_unified_evidence_collection(self, 
                                             gitlab_project_id: str,
                                             jira_project_key: str,
                                             username: str,
                                             days_back: int = 7) -> dict:
        """Test unified evidence collection with real data"""
        
        print("=" * 60)
        print("🧪 UNIFIED EVIDENCE SERVICE - REAL DATA INTEGRATION TEST")
        print("=" * 60)
        
        # Validate configuration
        required_config = [
            'GITLAB_PERSONAL_ACCESS_TOKEN',
            'JIRA_BASE_URL',
            'JIRA_CLOUD_ID',
            'JIRA_API_TOKEN',
            'JIRA_USER_EMAIL'
        ]
        
        missing_config = [key for key in required_config if not self.config.get(key)]
        if missing_config:
            print(f"❌ Missing configuration: {missing_config}")
            return {"success": False, "error": f"Missing configuration: {missing_config}"}
        
        print(f"📋 Test Configuration:")
        print(f"   GitLab Project: {gitlab_project_id}")
        print(f"   JIRA Project: {jira_project_key}")
        print(f"   Username: {username}")
        print(f"   Days Back: {days_back}")
        print(f"   GitLab URL: {self.config.get('GITLAB_API_URL', 'https://gitlab.com/api/v4')}")
        print(f"   JIRA URL: {self.config.get('JIRA_BASE_URL')}")
        print()
        
        # Create unified evidence service
        try:
            service = create_unified_evidence_service(
                gitlab_token=self.config['GITLAB_PERSONAL_ACCESS_TOKEN'],
                gitlab_project_id=gitlab_project_id,
                jira_mcp_server_url=self.config.get('JIRA_MCP_SERVER_URL', 'https://mcp.atlassian.com/v1/sse'),
                jira_cloud_id=self.config['JIRA_CLOUD_ID'],
                jira_base_url=self.config['JIRA_BASE_URL'],
                jira_api_token=self.config['JIRA_API_TOKEN'],
                jira_user_email=self.config['JIRA_USER_EMAIL'],
                jira_project_key=jira_project_key,
                gitlab_url=self.config.get('GITLAB_API_URL', 'https://gitlab.com/api/v4')
            )
            print("✅ Unified Evidence Service created successfully")
        except Exception as e:
            print(f"❌ Failed to create service: {e}")
            return {"success": False, "error": str(e)}
        
        test_results = {}
        
        try:
            # Test 1: Platform Health Check
            print("\n🔍 Testing Platform Health...")
            health_status = await service.get_platform_health()
            
            for platform, health in health_status.items():
                status = "✅ Healthy" if health.healthy else f"❌ Unhealthy: {health.error_message}"
                print(f"   {platform.value}: {status}")
            
            test_results["platform_health"] = {
                platform.value: {"healthy": health.healthy, "error": health.error_message}
                for platform, health in health_status.items()
            }
            
            # Test 2: Individual Platform Collections
            print("\n📊 Testing Individual Platform Collections...")
            
            # Test GitLab only
            print("   Testing GitLab collection...")
            gitlab_request = CollectionRequest(
                team_member_id="test-integration-user",
                username=username,
                since_date=datetime.utcnow() - timedelta(days=days_back),
                platforms=[PlatformType.GITLAB],
                max_items_per_platform=50
            )
            
            gitlab_response = await service.collect_evidence(gitlab_request)
            print(f"      GitLab: {gitlab_response.collection.total_count if gitlab_response.collection else 0} items")
            if gitlab_response.errors:
                print(f"      GitLab Errors: {gitlab_response.errors}")
            
            # Test JIRA only
            print("   Testing JIRA collection...")
            jira_request = CollectionRequest(
                team_member_id="test-integration-user",
                username=username,
                since_date=datetime.utcnow() - timedelta(days=days_back),
                platforms=[PlatformType.JIRA],
                max_items_per_platform=50
            )
            
            jira_response = await service.collect_evidence(jira_request)
            print(f"      JIRA: {jira_response.collection.total_count if jira_response.collection else 0} items")
            if jira_response.errors:
                print(f"      JIRA Errors: {jira_response.errors}")
            
            # Test 3: Unified Collection
            print("\n🔄 Testing Unified Evidence Collection...")
            unified_request = CollectionRequest(
                team_member_id="test-integration-user",
                username=username,
                since_date=datetime.utcnow() - timedelta(days=days_back),
                platforms=[PlatformType.GITLAB, PlatformType.JIRA],
                max_items_per_platform=50,
                validate_items=True
            )
            
            unified_response = await service.collect_evidence(unified_request)
            
            if unified_response.collection:
                collection = unified_response.collection
                print(f"   ✅ Total Items Collected: {collection.total_count}")
                print(f"   📊 Platform Distribution:")
                for platform, count in collection.platform_counts.items():
                    print(f"      {platform.value}: {count} items")
                
                print(f"   🔌 Source Distribution:")
                for source, count in collection.source_counts.items():
                    print(f"      {source.value}: {count} items")
                
                print(f"   📂 Category Distribution:")
                for category, count in collection.category_counts.items():
                    print(f"      {category}: {count} items")
                
                # Validation results
                if unified_response.performance_metrics and unified_response.performance_metrics.get('validation_summary'):
                    validation = unified_response.performance_metrics['validation_summary']
                    print(f"   ✅ Validation Results:")
                    print(f"      Valid: {validation.get('valid_items', 0)}")
                    print(f"      Invalid: {validation.get('invalid_items', 0)}")
                    print(f"      Warnings: {validation.get('warning_items', 0)}")
                
                # Performance metrics
                if unified_response.performance_metrics:
                    metrics = unified_response.performance_metrics
                    print(f"   ⚡ Performance:")
                    print(f"      Duration: {metrics.get('total_duration_ms', 0)}ms")
                    if 'platform_response_times' in metrics:
                        for platform, time_ms in metrics['platform_response_times'].items():
                            print(f"      {platform}: {time_ms}ms")
            
            if unified_response.errors:
                print(f"   ❌ Errors: {unified_response.errors}")
            
            if unified_response.warnings:
                print(f"   ⚠️  Warnings: {unified_response.warnings}")
            
            # Test 4: Data Quality Analysis
            print("\n🔍 Data Quality Analysis...")
            if unified_response.collection and unified_response.collection.items:
                items = unified_response.collection.items
                
                # Sample some items for detailed inspection
                sample_size = min(3, len(items))
                print(f"   Inspecting {sample_size} sample items:")
                
                for i, item in enumerate(items[:sample_size]):
                    print(f"\n   📄 Item {i+1}:")
                    print(f"      ID: {item.id}")
                    print(f"      Platform: {item.platform.value}")
                    print(f"      Source: {item.source}")
                    print(f"      Title: {item.title[:50]}...")
                    print(f"      Category: {item.category}")
                    print(f"      Date: {item.evidence_date}")
                    print(f"      Data Source: {item.data_source.value}")
                    print(f"      Fallback Used: {item.fallback_used}")
                    if item.validation_result:
                        print(f"      Validation: {item.validation_result.status.value}")
                        if item.validation_result.errors:
                            print(f"      Errors: {item.validation_result.errors}")
                        if item.validation_result.warnings:
                            print(f"      Warnings: {item.validation_result.warnings}")
            
            # Compile results
            test_results.update({
                "gitlab_collection": {
                    "success": gitlab_response.success,
                    "items_count": gitlab_response.collection.total_count if gitlab_response.collection else 0,
                    "errors": gitlab_response.errors,
                    "warnings": gitlab_response.warnings
                },
                "jira_collection": {
                    "success": jira_response.success,
                    "items_count": jira_response.collection.total_count if jira_response.collection else 0,
                    "errors": jira_response.errors,
                    "warnings": jira_response.warnings
                },
                "unified_collection": {
                    "success": unified_response.success,
                    "items_count": unified_response.collection.total_count if unified_response.collection else 0,
                    "platform_counts": dict(unified_response.collection.platform_counts) if unified_response.collection else {},
                    "source_counts": dict(unified_response.collection.source_counts) if unified_response.collection else {},
                    "category_counts": dict(unified_response.collection.category_counts) if unified_response.collection else {},
                    "errors": unified_response.errors,
                    "warnings": unified_response.warnings,
                    "performance_metrics": unified_response.performance_metrics
                }
            })
            
            print("\n" + "=" * 60)
            print("🎉 INTEGRATION TEST COMPLETED SUCCESSFULLY")
            print("=" * 60)
            
            return {"success": True, "results": test_results}
            
        except Exception as e:
            print(f"\n❌ Integration test failed: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e), "partial_results": test_results}
        
        finally:
            await service.close()
            print("\n🔒 Service closed")

async def main():
    """Main entry point for integration testing"""
    parser = argparse.ArgumentParser(description='Test unified evidence service with real data')
    parser.add_argument('--gitlab-project', default='12345678', help='GitLab project ID')
    parser.add_argument('--jira-project', default='TEST', help='JIRA project key')
    parser.add_argument('--username', default='testuser', help='Username to test with')
    parser.add_argument('--days-back', type=int, default=7, help='Days back to collect evidence')
    parser.add_argument('--save-results', help='File to save test results (JSON)')
    
    args = parser.parse_args()
    
    tester = RealDataIntegrationTester()
    results = await tester.test_unified_evidence_collection(
        gitlab_project_id=args.gitlab_project,
        jira_project_key=args.jira_project,
        username=args.username,
        days_back=args.days_back
    )
    
    if args.save_results:
        with open(args.save_results, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"📁 Results saved to {args.save_results}")
    
    # Exit with appropriate code
    sys.exit(0 if results.get("success") else 1)

if __name__ == "__main__":
    asyncio.run(main()) 