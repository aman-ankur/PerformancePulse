#!/usr/bin/env python3
"""
GitLab MCP-First Hybrid Client
Production implementation of GitLab data collection using MCP with API fallback

Architecture:
- Primary: GitLab MCP server (@zereight/mcp-gitlab) via stdio communication
- Fallback: Direct GitLab API calls via HTTP
- Benefits: Leverage proven MCP ecosystem with reliability of API backup
- Tools available: 65 GitLab tools from MCP server
"""

import subprocess
import json
import logging
import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import httpx

# Configure logging
logger = logging.getLogger(__name__)

class DataSource(Enum):
    MCP = "mcp"
    API = "api"

@dataclass
class EvidenceItem:
    """Standardized evidence item from any source"""
    id: str
    team_member_id: str
    source: str  # 'gitlab_commit', 'gitlab_mr', 'jira_ticket'
    title: str
    description: str
    source_url: Optional[str]
    category: str  # 'technical', 'collaboration', 'delivery'
    evidence_date: datetime
    created_at: datetime
    metadata: Dict[str, Any]
    data_source: DataSource
    fallback_used: bool = False

@dataclass
class MCPResponse:
    """Response from MCP server"""
    success: bool
    data: Any
    error: Optional[str] = None
    tool_name: Optional[str] = None

class GitLabMCPClient:
    """GitLab MCP client for stdio communication"""
    
    def __init__(self, 
                 gitlab_token: str,
                 gitlab_url: str = "https://gitlab.com/api/v4"):
        self.gitlab_token = gitlab_token
        self.gitlab_url = gitlab_url
        
        # MCP server environment
        self.mcp_env = {
            **os.environ,
            "GITLAB_PERSONAL_ACCESS_TOKEN": gitlab_token,
            "GITLAB_API_URL": gitlab_url,
            "GITLAB_READ_ONLY_MODE": "false",
            "USE_GITLAB_WIKI": "true",
            "USE_MILESTONE": "true",
            "USE_PIPELINE": "true"
        }
    
    async def send_mcp_request(self, method: str, params: Optional[Dict] = None) -> MCPResponse:
        """Send request to GitLab MCP server via stdio"""
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        request_json = json.dumps(request) + "\n"
        
        try:
            # Start MCP server process using npx
            process = await asyncio.create_subprocess_exec(
                "npx", "-y", "@zereight/mcp-gitlab",
                env=self.mcp_env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send request and get response
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=request_json.encode()),
                timeout=30.0
            )
            
            stdout = stdout.decode() if stdout else ""
            stderr = stderr.decode() if stderr else ""
            
            if stderr:
                logger.warning(f"MCP server stderr: {stderr}")
            
            if stdout:
                try:
                    response = json.loads(stdout.strip())
                    if "error" in response:
                        return MCPResponse(
                            success=False,
                            data=None,
                            error=response.get("error", {}).get("message", "Unknown MCP error"),
                            tool_name=params.get("name") if params else None
                        )
                    
                    return MCPResponse(
                        success=True,
                        data=response.get("result"),
                        tool_name=params.get("name") if params else None
                    )
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse MCP response: {e}")
                    return MCPResponse(success=False, data=None, error=f"JSON decode error: {e}")
            else:
                return MCPResponse(success=False, data=None, error="No response from MCP server")
                
        except asyncio.TimeoutError:
            if 'process' in locals():
                process.kill()
            return MCPResponse(success=False, data=None, error="MCP server timeout")
        except Exception as e:
            logger.error(f"MCP communication error: {e}")
            return MCPResponse(success=False, data=None, error=f"MCP communication error: {e}")
    
    async def list_tools(self) -> MCPResponse:
        """List available MCP tools"""
        return await self.send_mcp_request("tools/list")
    
    async def get_merge_requests(self, project_id: str, username: str, since_date: datetime) -> MCPResponse:
        """Get merge requests for user via MCP"""
        return await self.send_mcp_request("tools/call", {
            "name": "list_merge_requests",
            "arguments": {
                "project_id": project_id,
                "author_username": username,
                "created_after": since_date.isoformat(),
                "per_page": 50,
                "state": "all"
            }
        })
    
    async def get_project_details(self, project_id: str) -> MCPResponse:
        """Get project details via MCP"""
        return await self.send_mcp_request("tools/call", {
            "name": "get_project",
            "arguments": {
                "project_id": project_id
            }
        })
    
    async def get_issues(self, project_id: str, username: str, since_date: datetime) -> MCPResponse:
        """Get issues for user via MCP"""
        return await self.send_mcp_request("tools/call", {
            "name": "list_issues",
            "arguments": {
                "project_id": project_id,
                "author_username": username,
                "created_after": since_date.isoformat(),
                "per_page": 50
            }
        })

class GitLabAPIClient:
    """GitLab API client for fallback"""
    
    def __init__(self, gitlab_token: str, gitlab_url: str = "https://gitlab.com/api/v4"):
        self.gitlab_token = gitlab_token
        self.gitlab_url = gitlab_url
        self.headers = {
            "Authorization": f"Bearer {gitlab_token}",
            "Content-Type": "application/json"
        }
    
    async def get_merge_requests(self, project_id: str, username: str, since_date: datetime) -> List[Dict]:
        """Get merge requests via direct API"""
        url = f"{self.gitlab_url}/projects/{project_id}/merge_requests"
        params = {
            "author_username": username,
            "created_after": since_date.isoformat(),
            "per_page": 50,
            "state": "all"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_project_details(self, project_id: str) -> Dict:
        """Get project details via direct API"""
        url = f"{self.gitlab_url}/projects/{project_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    async def get_issues(self, project_id: str, username: str, since_date: datetime) -> List[Dict]:
        """Get issues via direct API"""
        url = f"{self.gitlab_url}/projects/{project_id}/issues"
        params = {
            "author_username": username,
            "created_after": since_date.isoformat(),
            "per_page": 50
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()

class GitLabHybridClient:
    """
    GitLab Hybrid Client - MCP first with API fallback
    
    This client implements the MCP-first hybrid approach:
    1. Try MCP server first (preferred method)
    2. Fallback to direct API if MCP fails
    3. Track which method was used for transparency
    
    Architecture:
    - MCP Server: @zereight/mcp-gitlab (65 tools available)
    - Communication: stdio (JSON-RPC 2.0)
    - Fallback: Direct HTTP API calls
    - Environment: Node.js MCP server + Python FastAPI backend
    """
    
    def __init__(self, 
                 gitlab_token: str,
                 project_id: str,
                 gitlab_url: str = "https://gitlab.com/api/v4"):
        self.gitlab_token = gitlab_token
        self.project_id = project_id
        self.gitlab_url = gitlab_url
        
        # Initialize both clients
        self.mcp_client = GitLabMCPClient(gitlab_token, gitlab_url)
        self.api_client = GitLabAPIClient(gitlab_token, gitlab_url)
        
        logger.info(f"GitLab Hybrid Client initialized for project {project_id}")
    
    async def check_mcp_health(self) -> bool:
        """Check if MCP server is available and working"""
        try:
            response = await self.mcp_client.list_tools()
            if response.success and response.data:
                tools = response.data.get("tools", [])
                logger.info(f"MCP server healthy: {len(tools)} tools available")
                return True
            else:
                logger.warning(f"MCP server unhealthy: {response.error}")
                return False
        except Exception as e:
            logger.error(f"MCP health check failed: {e}")
            return False
    
    async def get_merge_requests(self, username: str, since_date: datetime) -> List[EvidenceItem]:
        """Get merge requests using MCP-first hybrid approach"""
        
        # Try MCP first
        try:
            logger.info(f"Attempting MCP: get_merge_requests for {username}")
            mcp_response = await self.mcp_client.get_merge_requests(self.project_id, username, since_date)
            
            if mcp_response.success and mcp_response.data:
                logger.info("MCP successful: transforming merge requests data")
                return self._transform_mcp_merge_requests(mcp_response.data, username, DataSource.MCP, fallback_used=False)
            else:
                logger.warning(f"MCP failed: {mcp_response.error}")
        except Exception as e:
            logger.error(f"MCP exception: {e}")
        
        # Fallback to API
        try:
            logger.info(f"Falling back to API: get_merge_requests for {username}")
            api_data = await self.api_client.get_merge_requests(self.project_id, username, since_date)
            logger.info("API successful: transforming merge requests data")
            return self._transform_api_merge_requests(api_data, username, DataSource.API, fallback_used=True)
        except Exception as e:
            logger.error(f"API fallback failed: {e}")
            return []
    
    async def get_issues(self, username: str, since_date: datetime) -> List[EvidenceItem]:
        """Get issues using MCP-first hybrid approach"""
        
        # Try MCP first
        try:
            logger.info(f"Attempting MCP: get_issues for {username}")
            mcp_response = await self.mcp_client.get_issues(self.project_id, username, since_date)
            
            if mcp_response.success and mcp_response.data:
                logger.info("MCP successful: transforming issues data")
                return self._transform_mcp_issues(mcp_response.data, username, DataSource.MCP, fallback_used=False)
            else:
                logger.warning(f"MCP failed: {mcp_response.error}")
        except Exception as e:
            logger.error(f"MCP exception: {e}")
        
        # Fallback to API
        try:
            logger.info(f"Falling back to API: get_issues for {username}")
            api_data = await self.api_client.get_issues(self.project_id, username, since_date)
            logger.info("API successful: transforming issues data")
            return self._transform_api_issues(api_data, username, DataSource.API, fallback_used=True)
        except Exception as e:
            logger.error(f"API fallback failed: {e}")
            return []
    
    async def get_comprehensive_evidence(self, username: str, days_back: int = 7) -> List[EvidenceItem]:
        """Get comprehensive evidence for user from multiple sources"""
        since_date = datetime.now() - timedelta(days=days_back)
        
        logger.info(f"Getting comprehensive evidence for {username} since {since_date}")
        
        # Collect all evidence types
        evidence_items = []
        
        # Get merge requests
        mrs = await self.get_merge_requests(username, since_date)
        evidence_items.extend(mrs)
        logger.info(f"Collected {len(mrs)} merge requests")
        
        # Get issues
        issues = await self.get_issues(username, since_date)
        evidence_items.extend(issues)
        logger.info(f"Collected {len(issues)} issues")
        
        # Sort by evidence date (most recent first)
        evidence_items.sort(key=lambda x: x.evidence_date, reverse=True)
        
        logger.info(f"Total evidence collected: {len(evidence_items)} items")
        return evidence_items
    
    def _transform_mcp_merge_requests(self, mcp_data: Any, username: str, source: DataSource, fallback_used: bool) -> List[EvidenceItem]:
        """Transform MCP merge request data to evidence items"""
        evidence_items = []
        
        try:
            # MCP data comes in content format
            if isinstance(mcp_data, dict) and "content" in mcp_data:
                content = mcp_data["content"]
                if isinstance(content, list) and len(content) > 0:
                    # Parse the JSON content
                    text_content = content[0].get("text", "")
                    if text_content:
                        mrs_data = json.loads(text_content)
                        
                        for mr in mrs_data:
                            evidence_items.append(EvidenceItem(
                                id=f"gitlab_mr_{mr['id']}",
                                team_member_id=username,
                                source="gitlab_mr",
                                title=mr.get("title", ""),
                                description=mr.get("description", ""),
                                source_url=mr.get("web_url", ""),
                                category=self._categorize_merge_request(mr),
                                evidence_date=self._parse_date(mr.get("updated_at") or mr.get("created_at")),
                                created_at=datetime.now(),
                                metadata={
                                    "mr_iid": mr.get("iid"),
                                    "state": mr.get("state"),
                                    "draft": mr.get("draft") or mr.get("work_in_progress"),
                                    "changes_count": self._safe_int(mr.get("changes_count")),
                                    "approvals_before_merge": self._safe_int(mr.get("approvals_before_merge")),
                                    "discussions_count": self._safe_int(mr.get("user_notes_count") or mr.get("discussions_count")),
                                    "author": mr.get("author", {}).get("username"),
                                    "source_method": source.value
                                },
                                data_source=source,
                                fallback_used=fallback_used
                            ))
            elif isinstance(mcp_data, list):
                # Handle direct list format
                for mr in mcp_data:
                    evidence_items.append(EvidenceItem(
                        id=f"gitlab_mr_{mr['id']}",
                        team_member_id=username,
                        source="gitlab_mr",
                        title=mr.get("title", ""),
                        description=mr.get("description", ""),
                        source_url=mr.get("web_url", ""),
                        category=self._categorize_merge_request(mr),
                        evidence_date=self._parse_date(mr.get("updated_at") or mr.get("created_at")),
                        created_at=datetime.now(),
                        metadata={
                            "mr_iid": mr.get("iid"),
                            "state": mr.get("state"),
                            "draft": mr.get("draft") or mr.get("work_in_progress"),
                            "changes_count": self._safe_int(mr.get("changes_count")),
                            "approvals_before_merge": self._safe_int(mr.get("approvals_before_merge")),
                            "discussions_count": self._safe_int(mr.get("user_notes_count") or mr.get("discussions_count")),
                            "author": mr.get("author", {}).get("username"),
                            "source_method": source.value
                        },
                        data_source=source,
                        fallback_used=fallback_used
                    ))
        except Exception as e:
            logger.error(f"Error transforming MCP merge request data: {e}")
        
        return evidence_items
    
    def _transform_api_merge_requests(self, api_data: List[Dict], username: str, source: DataSource, fallback_used: bool) -> List[EvidenceItem]:
        """Transform API merge request data to evidence items"""
        evidence_items = []
        
        try:
            for mr in api_data:
                evidence_items.append(EvidenceItem(
                    id=f"gitlab_mr_{mr['id']}",
                    team_member_id=username,
                    source="gitlab_mr",
                    title=mr.get("title", ""),
                    description=mr.get("description", ""),
                    source_url=mr.get("web_url", ""),
                    category=self._categorize_merge_request(mr),
                    evidence_date=self._parse_date(mr.get("updated_at") or mr.get("created_at")),
                    created_at=datetime.now(),
                    metadata={
                        "mr_iid": mr.get("iid"),
                        "state": mr.get("state"),
                        "draft": mr.get("draft") or mr.get("work_in_progress"),
                        "changes_count": self._safe_int(mr.get("changes_count")),
                        "approvals_before_merge": self._safe_int(mr.get("approvals_before_merge")),
                        "discussions_count": self._safe_int(mr.get("user_notes_count") or mr.get("discussions_count")),
                        "author": mr.get("author", {}).get("username"),
                        "source_method": source.value
                    },
                    data_source=source,
                    fallback_used=fallback_used
                ))
        except Exception as e:
            logger.error(f"Error transforming API merge request data: {e}")
        
        return evidence_items
    
    def _transform_mcp_issues(self, mcp_data: Any, username: str, source: DataSource, fallback_used: bool) -> List[EvidenceItem]:
        """Transform MCP issues data to evidence items"""
        evidence_items = []
        
        try:
            # Similar to MCP merge requests transformation
            if isinstance(mcp_data, dict) and "content" in mcp_data:
                content = mcp_data["content"]
                if isinstance(content, list) and len(content) > 0:
                    text_content = content[0].get("text", "")
                    if text_content:
                        issues_data = json.loads(text_content)
                        
                        for issue in issues_data:
                            evidence_items.append(EvidenceItem(
                                id=f"gitlab_issue_{issue['id']}",
                                team_member_id=username,
                                source="gitlab_issue",
                                title=issue.get("title", ""),
                                description=issue.get("description", ""),
                                source_url=issue.get("web_url", ""),
                                category=self._categorize_issue(issue),
                                evidence_date=self._parse_date(issue.get("created_at")),
                                created_at=datetime.now(),
                                metadata={
                                    "issue_iid": issue.get("iid"),
                                    "state": issue.get("state"),
                                    "author": issue.get("author", {}).get("username"),
                                    "labels": issue.get("labels", []),
                                    "source_method": source.value
                                },
                                data_source=source,
                                fallback_used=fallback_used
                            ))
            elif isinstance(mcp_data, list):
                # Handle direct list format
                for issue in mcp_data:
                    evidence_items.append(EvidenceItem(
                        id=f"gitlab_issue_{issue['id']}",
                        team_member_id=username,
                        source="gitlab_issue",
                        title=issue.get("title", ""),
                        description=issue.get("description", ""),
                        source_url=issue.get("web_url", ""),
                        category=self._categorize_issue(issue),
                        evidence_date=self._parse_date(issue.get("created_at")),
                        created_at=datetime.now(),
                        metadata={
                            "issue_iid": issue.get("iid"),
                            "state": issue.get("state"),
                            "author": issue.get("author", {}).get("username"),
                            "labels": issue.get("labels", []),
                            "source_method": source.value
                        },
                        data_source=source,
                        fallback_used=fallback_used
                    ))
        except Exception as e:
            logger.error(f"Error transforming MCP issues data: {e}")
        
        return evidence_items
    
    def _transform_api_issues(self, api_data: List[Dict], username: str, source: DataSource, fallback_used: bool) -> List[EvidenceItem]:
        """Transform API issues data to evidence items"""
        evidence_items = []
        
        try:
            for issue in api_data:
                evidence_items.append(EvidenceItem(
                    id=f"gitlab_issue_{issue['id']}",
                    team_member_id=username,
                    source="gitlab_issue",
                    title=issue.get("title", ""),
                    description=issue.get("description", ""),
                    source_url=issue.get("web_url", ""),
                    category=self._categorize_issue(issue),
                    evidence_date=self._parse_date(issue.get("created_at")),
                    created_at=datetime.now(),
                    metadata={
                        "issue_iid": issue.get("iid"),
                        "state": issue.get("state"),
                        "author": issue.get("author", {}).get("username"),
                        "labels": issue.get("labels", []),
                        "source_method": source.value
                    },
                    data_source=source,
                    fallback_used=fallback_used
                ))
        except Exception as e:
            logger.error(f"Error transforming API issues data: {e}")
        
        return evidence_items
    
    def _categorize_merge_request(self, mr: Dict) -> str:
        """Categorize merge request based on title and description"""
        title = mr.get("title", "").lower()
        description = mr.get("description", "").lower()
        labels = [label.get("name", "").lower() for label in mr.get("labels", [])]
        
        # Check for technical keywords
        technical_keywords = ["fix", "bug", "refactor", "optimize", "performance", "security", "test"]
        if any(keyword in title or keyword in description for keyword in technical_keywords):
            return "technical"
        
        # Check for collaboration keywords
        collaboration_keywords = ["review", "discussion", "feedback", "meeting", "sync"]
        if any(keyword in title or keyword in description for keyword in collaboration_keywords):
            return "collaboration"
        
        # Check for delivery keywords
        delivery_keywords = ["feature", "implement", "add", "deploy", "release", "deliver"]
        if any(keyword in title or keyword in description for keyword in delivery_keywords):
            return "delivery"
        
        # Default
        return "technical"
    
    def _categorize_issue(self, issue: Dict) -> str:
        """Categorize issue based on title, description, and labels"""
        title = issue.get("title", "").lower()
        description = issue.get("description", "").lower()
        labels = [label.get("name", "").lower() if isinstance(label, dict) else str(label).lower() for label in issue.get("labels", [])]
        
        # Check labels first
        if any("bug" in label for label in labels):
            return "technical"
        if any("feature" in label for label in labels):
            return "delivery"
        if any("discussion" in label or "question" in label for label in labels):
            return "collaboration"
        
        # Fallback to title/description analysis
        return self._categorize_merge_request(issue)  # Reuse MR logic
    
    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse ISO date string to datetime"""
        if not date_str:
            return datetime.now()
        
        try:
            # Handle both with and without timezone
            if date_str.endswith('Z'):
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            elif '+' in date_str[-6:] or '-' in date_str[-6:]:
                return datetime.fromisoformat(date_str)
            else:
                return datetime.fromisoformat(date_str + '+00:00')
        except Exception as e:
            logger.warning(f"Failed to parse date {date_str}: {e}")
            return datetime.now()

    def _safe_int(self, value: Optional[Union[int, str]]) -> Optional[int]:
        """Safely convert value to int or return None if not a valid integer"""
        if isinstance(value, (int, str)):
            try:
                return int(value)
            except ValueError:
                pass
        return None

# Factory function for easy instantiation
def create_gitlab_client(gitlab_token: str, project_id: str, **kwargs) -> GitLabHybridClient:
    """Create a GitLab hybrid client with default settings"""
    return GitLabHybridClient(
        gitlab_token=gitlab_token,
        project_id=project_id,
        **kwargs
    ) 