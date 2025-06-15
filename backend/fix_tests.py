#!/usr/bin/env python3
"""
Quick script to fix test file imports and model usage
"""

import re

def fix_test_file():
    file_path = 'tests/test_llm_correlation_service.py'
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace EvidenceSource.GITLAB
    content = re.sub(
        r'source=EvidenceSource\.GITLAB,?\s*author_email="[^"]*",?\s*',
        'source=SourceType.GITLAB_COMMIT, category=CategoryType.DEVELOPMENT, platform=PlatformType.GITLAB, data_source="mcp", team_member_id="team1", ',
        content
    )
    
    # Replace EvidenceSource.JIRA
    content = re.sub(
        r'source=EvidenceSource\.JIRA,?\s*author_email="[^"]*",?\s*',
        'source=SourceType.JIRA_ISSUE, category=CategoryType.DEVELOPMENT, platform=PlatformType.JIRA, data_source="mcp", team_member_id="team1", ',
        content
    )
    
    # Replace remaining EvidenceSource.GITLAB without author_email
    content = re.sub(
        r'source=EvidenceSource\.GITLAB',
        'source=SourceType.GITLAB_COMMIT, category=CategoryType.DEVELOPMENT, platform=PlatformType.GITLAB, data_source="mcp", team_member_id="team1"',
        content
    )
    
    # Replace remaining EvidenceSource.JIRA without author_email
    content = re.sub(
        r'source=EvidenceSource\.JIRA',
        'source=SourceType.JIRA_ISSUE, category=CategoryType.DEVELOPMENT, platform=PlatformType.JIRA, data_source="mcp", team_member_id="team1"',
        content
    )
    
    # Fix data_source enum usage
    content = re.sub(r'data_source="mcp"', 'data_source=DataSourceType.MCP', content)
    
    # Add DataSourceType import
    content = re.sub(
        r'from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType',
        'from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType, DataSourceType',
        content
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed test file successfully")

if __name__ == "__main__":
    fix_test_file() 