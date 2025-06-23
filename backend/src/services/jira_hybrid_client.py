"""
JIRA MCP-First Hybrid Client
Production implementation of JIRA data collection using MCP with API fallback

Architecture:
- Primary: Official Atlassian MCP server via stdio or HTTP
- Fallback: Direct JIRA REST API calls
- Benefits: Leverage MCP ecosystem with reliability of API backup
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import json
import logging
import os
import httpx
import uuid

# Import configurable search system
from src.models.search_criteria import (
    JQLSearchCriteria, JQLBuilder, SearchScope,
    create_sprint_search, create_user_search
)

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

class JiraDataProvider(ABC):
    """
    Abstract base class for JIRA data providers (MCP, API, Hybrid).
    Defines the interface for evidence collection and project/issue access.
    """
    @abstractmethod
    async def get_issues(self, username: str, since_date: datetime, 
                        search_criteria: Optional[JQLSearchCriteria] = None) -> List[EvidenceItem]:
        """Get issues for a user since a given date with configurable search criteria."""
        pass

    @abstractmethod
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get list of accessible JIRA projects."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy/available."""
        pass

class JiraMCPClient(JiraDataProvider):
    """
    JIRA MCP client for communication with the official Atlassian MCP server.
    """
    def __init__(self, mcp_server_url: str, cloud_id: str, jira_base_url: str, timeout: int = 45):
        self.mcp_server_url = mcp_server_url
        self.cloud_id = cloud_id
        self.jira_base_url = jira_base_url
        self.timeout = timeout
        self.process = None
        
        logger.info(f"JIRA MCP Client initialized for {jira_base_url} (cloudId: {cloud_id})")

    async def start_mcp_server(self) -> bool:
        """Start the official Atlassian MCP server via mcp-remote"""
        try:
            cmd = ["npx", "-y", "mcp-remote", self.mcp_server_url, "--transport", "stdio"]
            
            logger.info("Starting Official Atlassian MCP server...")
            
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024*1024  # 1MB buffer limit
            )
            
            logger.info("✅ Official Atlassian MCP server started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Official Atlassian MCP server: {e}")
            return False

    async def send_mcp_request(self, method: str, params: Optional[Dict] = None) -> MCPResponse:
        """Send JSON-RPC request to MCP server with robust error handling"""
        if not self.process:
            # Try to start the server if not already running
            if not await self.start_mcp_server():
                return MCPResponse(success=False, error="Failed to start MCP server")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        request_json = json.dumps(request) + "\n"
        
        try:
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()
            
            # Read response with timeout
            try:
                response_line = await asyncio.wait_for(
                    self.process.stdout.readline(), 
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                return MCPResponse(success=False, error=f"MCP request timeout after {self.timeout}s")
            
            if not response_line:
                return MCPResponse(success=False, error="No response from MCP server")
            
            response_text = response_line.decode().strip()
            
            # Handle large responses
            if len(response_text) > 100000:  # 100KB limit
                logger.warning(f"Large MCP response received: {len(response_text)} bytes")
                response_text = response_text[:100000]
            
            try:
                response = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse MCP JSON response: {e}")
                return MCPResponse(success=False, error=f"JSON decode error: {e}")
            
            if "error" in response:
                error_msg = response.get("error", {})
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get("message", str(error_msg))
                return MCPResponse(
                    success=False,
                    data=None,
                    error=f"MCP server error: {error_msg}",
                    tool_name=params.get("name") if params else None
                )
            
            return MCPResponse(
                success=True,
                data=response.get("result"),
                tool_name=params.get("name") if params else None
            )
            
        except Exception as e:
            logger.error(f"MCP communication error: {e}")
            return MCPResponse(success=False, data=None, error=f"MCP communication error: {e}")

    async def list_tools(self) -> MCPResponse:
        """List available MCP tools"""
        return await self.send_mcp_request("tools/list")

    async def search_issues_by_jql(self, jql: str, max_results: int = 50) -> MCPResponse:
        """Search JIRA issues using JQL via MCP"""
        return await self.send_mcp_request("tools/call", {
            "name": "searchJiraIssuesUsingJql",
            "arguments": {
                "cloudId": self.cloud_id,
                "jql": jql,
                "maxResults": max_results
            }
        })

    async def get_issue_details(self, issue_key: str) -> MCPResponse:
        """Get specific JIRA issue details via MCP"""
        return await self.send_mcp_request("tools/call", {
            "name": "getJiraIssue",
            "arguments": {
                "cloudId": self.cloud_id,
                "issueIdOrKey": issue_key
            }
        })

    async def get_issues(self, username: str, since_date: datetime,
                        search_criteria: Optional[JQLSearchCriteria] = None) -> List[EvidenceItem]:
        """Get issues for a user via MCP server with configurable search criteria."""
        try:
            # Use provided criteria or create default
            if not search_criteria:
                search_criteria = create_user_search(username, since_date=since_date)
            
            # Build flexible JQL queries
            builder = JQLBuilder(search_criteria)
            queries = builder.build_queries()
            
            all_evidence = []
            unique_ids = set()
            
            for query in queries:
                try:
                    logger.info(f"MCP search: {query.description}")
                    logger.info(f"JQL: {query.jql}")
                    
                    mcp_response = await self.search_issues_by_jql(query.jql, query.max_results)
                    
                    if mcp_response.success and mcp_response.data:
                        evidence_items = self._transform_mcp_issues(
                            mcp_response.data, username, DataSource.MCP, fallback_used=False
                        )
                        
                        # Add unique items only
                        for item in evidence_items:
                            if item.id not in unique_ids:
                                unique_ids.add(item.id)
                                all_evidence.append(item)
                        
                        logger.info(f"MCP query returned {len(evidence_items)} items")
                    else:
                        logger.warning(f"MCP search failed: {mcp_response.error}")
                        
                except Exception as e:
                    logger.warning(f"MCP query failed: {e}")
                    continue
            
            logger.info(f"Total MCP evidence collected: {len(all_evidence)} unique items")
            return all_evidence
                
        except Exception as e:
            logger.error(f"Error getting issues via MCP: {e}")
            return []

    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get list of projects via MCP server."""
        try:
            # Try to get projects - this might require different approach
            # For now, return empty list as projects are less critical for evidence collection
            logger.info("Getting JIRA projects via MCP (not implemented yet)")
            return []
        except Exception as e:
            logger.error(f"Error getting projects via MCP: {e}")
            return []

    async def health_check(self) -> bool:
        """Check MCP server health."""
        try:
            response = await self.list_tools()
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

    def _transform_mcp_issues(self, mcp_data: Any, username: str, source: DataSource, fallback_used: bool) -> List[EvidenceItem]:
        """Transform MCP JIRA issues data to evidence items"""
        evidence_items = []
        
        try:
            # Handle MCP response format
            issues_data = []
            
            if isinstance(mcp_data, dict):
                if mcp_data.get("isError"):
                    logger.error(f"MCP returned error: {mcp_data.get('content')}")
                    return []
                
                content = mcp_data.get("content", [])
                
                # Handle content as list of text objects (MCP format)
                if isinstance(content, list) and len(content) > 0:
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_content = item.get("text", "")
                            try:
                                parsed_content = json.loads(text_content)
                                if isinstance(parsed_content, dict) and "issues" in parsed_content:
                                    issues_data = parsed_content["issues"]
                                    break
                            except json.JSONDecodeError:
                                logger.warning(f"Could not parse MCP text content as JSON: {text_content[:100]}...")
                                continue
                
                # Fallback: handle content as string
                elif isinstance(content, str):
                    try:
                        content = json.loads(content)
                        if isinstance(content, dict) and "issues" in content:
                            issues_data = content["issues"]
                        elif isinstance(content, list):
                            issues_data = content
                    except json.JSONDecodeError:
                        logger.warning("Could not parse MCP JIRA response as JSON")
                        return []
                
                # Handle direct content formats
                elif isinstance(content, list):
                    issues_data = content
                elif isinstance(content, dict):
                    issues_data = content.get("issues", [])
            elif isinstance(mcp_data, list):
                issues_data = mcp_data
            
            for issue in issues_data:
                try:
                    # Extract issue fields
                    fields = issue.get("fields", {})
                    
                    # Skip issues with missing essential data
                    title = fields.get("summary", "").strip()
                    description = fields.get("description", "").strip() if fields.get("description") else ""
                    issue_key = issue.get("key", "")
                    
                    if not title:
                        title = f"JIRA Issue {issue_key}" if issue_key else "Untitled JIRA Issue"
                    if not description:
                        description = "No description available"
                    if not issue_key:
                        logger.warning(f"Skipping JIRA issue without key: {issue}")
                        continue
                    
                    evidence_items.append(EvidenceItem(
                        id=f"jira_issue_{issue.get('id', issue_key)}",
                        team_member_id=username,
                        source="jira_ticket",
                        title=title,
                        description=description,
                        source_url=f"{self.jira_base_url}/browse/{issue_key}",
                        category=self._categorize_jira_issue(issue),
                        evidence_date=self._parse_jira_date(fields.get("updated") or fields.get("created")),
                        created_at=datetime.now(),
                        metadata={
                            "issue_key": issue_key,
                            "issue_type": fields.get("issuetype", {}).get("name"),
                            "status": fields.get("status", {}).get("name"),
                            "priority": fields.get("priority", {}).get("name"),
                            "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                            "reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
                            "epic_link": (fields.get("epic", {}) or {}).get("key") or fields.get("customfield_10008"),
                            "sprint": (fields.get("sprint", {}) or {}).get("name") if isinstance(fields.get("sprint"), dict) else None,
                            "components": [c.get("name") for c in fields.get("components", [])] if isinstance(fields.get("components"), list) else None,
                            "labels": fields.get("labels", []),
                            "source_method": source.value
                        },
                        data_source=source,
                        fallback_used=fallback_used
                    ))
                except Exception as e:
                    logger.warning(f"Error transforming JIRA issue: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error transforming MCP JIRA issues data: {e}")
        
        return evidence_items

    def _categorize_jira_issue(self, issue: Dict) -> str:
        """Categorize JIRA issue based on type, labels, and content"""
        fields = issue.get("fields", {})
        
        # Check issue type
        issue_type = fields.get("issuetype", {}).get("name", "").lower()
        if "bug" in issue_type or "defect" in issue_type:
            return "technical"
        elif "story" in issue_type or "feature" in issue_type or "epic" in issue_type:
            return "delivery"
        elif "task" in issue_type:
            # Could be technical or delivery, check labels/title
            pass
        
        # Check labels
        labels = [label.lower() for label in fields.get("labels", [])]
        if any("bug" in label or "technical" in label for label in labels):
            return "technical"
        if any("feature" in label or "delivery" in label for label in labels):
            return "delivery"
        if any("discussion" in label or "meeting" in label for label in labels):
            return "collaboration"
        
        # Check title/summary
        title = fields.get("summary", "").lower()
        if any(keyword in title for keyword in ["fix", "bug", "error", "issue", "problem"]):
            return "technical"
        if any(keyword in title for keyword in ["implement", "add", "feature", "deliver"]):
            return "delivery"
        if any(keyword in title for keyword in ["review", "discuss", "meeting", "sync"]):
            return "collaboration"
        
        # Default to technical for most JIRA tickets
        return "technical"

    def _parse_jira_date(self, date_str: Optional[str]) -> datetime:
        """Parse JIRA date string to datetime"""
        if not date_str:
            return datetime.now()
        
        try:
            # Handle JIRA date formats: 2025-06-13T08:28:32.567+0200
            # Convert +0200 format to +02:00 for Python compatibility
            if '+' in date_str and date_str[-5:].count(':') == 0:
                # Convert +0200 to +02:00
                date_str = date_str[:-2] + ':' + date_str[-2:]
            elif '-' in date_str[-5:] and date_str[-5:].count(':') == 0:
                # Convert -0200 to -02:00
                date_str = date_str[:-2] + ':' + date_str[-2:]
            
            # JIRA typically uses ISO format: 2023-12-01T10:30:00.000+0000
            if date_str.endswith('Z'):
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            elif '+' in date_str[-6:] or '-' in date_str[-6:]:
                return datetime.fromisoformat(date_str)
            else:
                return datetime.fromisoformat(date_str + '+00:00')
        except Exception as e:
            logger.warning(f"Failed to parse JIRA date {date_str}: {e}")
            return datetime.now()

    async def close(self):
        """Close MCP server process"""
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
                logger.info("MCP server process closed")
            except Exception as e:
                logger.error(f"Error closing MCP server: {e}")

class JiraAPIClient(JiraDataProvider):
    """
    JIRA API client for direct REST API calls (fallback).
    """
    def __init__(self, api_token: str, user_email: str, jira_base_url: str, project_key: Optional[str] = None):
        self.api_token = api_token
        self.user_email = user_email
        self.jira_base_url = jira_base_url
        self.project_key = project_key
        
        # Setup authentication headers - JIRA Cloud requires Basic Auth (email + token)
        import base64
        auth_string = f"{user_email}:{api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        logger.info(f"JIRA API Client initialized for {jira_base_url}")

    async def _resolve_username_to_account_id(self, username: str) -> Optional[str]:
        """Resolve username to JIRA account ID"""
        try:
            # First, check if it's already an account ID (starts with account ID format)
            if username.startswith('712020:'):
                return username
            
            # Get current user first to check if it's the current user
            async with httpx.AsyncClient() as client:
                myself_response = await client.get(f"{self.jira_base_url}/rest/api/3/myself", headers=self.headers)
                if myself_response.status_code == 200:
                    user_info = myself_response.json()
                    
                    # Check if username matches current user in various ways
                    if (username == user_info.get('name') or 
                        username == user_info.get('displayName') or
                        username == user_info.get('emailAddress') or
                        username in user_info.get('displayName', '') or
                        username == 'aankur'):  # Handle specific case
                        
                        logger.info(f"Resolved username '{username}' to account ID: {user_info.get('accountId')}")
                        return user_info.get('accountId')
                
                # Try searching for users (requires admin permissions, might fail)
                search_url = f"{self.jira_base_url}/rest/api/3/user/search"
                search_params = {"query": username, "maxResults": 5}
                
                search_response = await client.get(search_url, headers=self.headers, params=search_params)
                if search_response.status_code == 200:
                    users = search_response.json()
                    for user in users:
                        if (user.get('name') == username or 
                            user.get('displayName') == username or
                            user.get('emailAddress') == username):
                            logger.info(f"Found user '{username}' with account ID: {user.get('accountId')}")
                            return user.get('accountId')
                
                logger.warning(f"Could not resolve username '{username}' to account ID")
                return None
                
        except Exception as e:
            logger.error(f"Error resolving username '{username}': {e}")
            return None

    async def get_issues(self, username: str, since_date: datetime,
                        search_criteria: Optional[JQLSearchCriteria] = None) -> List[EvidenceItem]:
        """Get issues for a user via REST API with configurable search criteria."""
        try:
            # First, resolve username to account ID if needed
            account_id = await self._resolve_username_to_account_id(username)
            if not account_id:
                logger.warning(f"Could not resolve username '{username}' to account ID")
                return []
            
            # Use provided criteria or create default
            if not search_criteria:
                search_criteria = create_user_search(username, since_date=since_date)
            
            # Update criteria with resolved account ID
            criteria_with_account_id = JQLSearchCriteria(
                username=account_id,  # Use account ID instead of username
                project_key=search_criteria.project_key,
                sprint_name=search_criteria.sprint_name,
                since_date=search_criteria.since_date,
                until_date=search_criteria.until_date,
                days_back=search_criteria.days_back,
                search_scopes=search_criteria.search_scopes,
                max_results=search_criteria.max_results,
                include_unassigned=search_criteria.include_unassigned,
                include_open_sprints=search_criteria.include_open_sprints,
                include_closed_items=search_criteria.include_closed_items,
                issue_types=search_criteria.issue_types,
                statuses=search_criteria.statuses,
                priorities=search_criteria.priorities,
                labels=search_criteria.labels,
                components=search_criteria.components,
                fix_versions=search_criteria.fix_versions,
                custom_jql_filters=search_criteria.custom_jql_filters,
                order_by=search_criteria.order_by
            )
            
            # Build flexible JQL queries
            builder = JQLBuilder(criteria_with_account_id)
            queries = builder.build_queries()
            
            all_evidence = []
            unique_ids = set()
            
            url = f"{self.jira_base_url}/rest/api/3/search"
            
            async with httpx.AsyncClient() as client:
                for query in queries:
                    try:
                        logger.info(f"API search: {query.description}")
                        logger.info(f"JQL: {query.jql}")
                        
                        params = {
                            "jql": query.jql,
                            "maxResults": query.max_results,
                            "fields": "summary,description,issuetype,status,priority,assignee,reporter,labels,created,updated,sprint,fixVersions"
                        }
                        
                        response = await client.get(url, headers=self.headers, params=params)
                        response.raise_for_status()
                        data = response.json()
                        
                        issues = data.get("issues", [])
                        logger.info(f"API query returned {len(issues)} items")
                        
                        evidence_items = self._transform_api_issues(issues, username, DataSource.API, fallback_used=True)
                        
                        # Add unique items only
                        for item in evidence_items:
                            if item.id not in unique_ids:
                                unique_ids.add(item.id)
                                all_evidence.append(item)
                                
                    except Exception as e:
                        logger.warning(f"API query failed: {e}")
                        continue
            
            logger.info(f"Total API evidence collected: {len(all_evidence)} unique items")
            return all_evidence
                
        except Exception as e:
            logger.error(f"Error getting issues via API: {e}")
            return []

    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get list of projects via REST API."""
        try:
            url = f"{self.jira_base_url}/rest/api/3/project"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                projects = response.json()
                
                logger.info(f"API successful: found {len(projects)} projects")
                return projects
                
        except Exception as e:
            logger.error(f"Error getting projects via API: {e}")
            return []

    async def health_check(self) -> bool:
        """Check REST API health."""
        try:
            url = f"{self.jira_base_url}/rest/api/3/myself"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                
                user_info = response.json()
                logger.info(f"JIRA API healthy: authenticated as {user_info.get('displayName', 'Unknown')}")
                return True
                
        except Exception as e:
            logger.error(f"JIRA API health check failed: {e}")
            return False

    def _transform_api_issues(self, api_data: List[Dict], username: str, source: DataSource, fallback_used: bool) -> List[EvidenceItem]:
        """Transform API JIRA issues data to evidence items"""
        evidence_items = []
        
        try:
            for issue in api_data:
                try:
                    # Extract issue fields
                    fields = issue.get("fields", {})
                    
                    # Skip issues with missing essential data
                    title = fields.get("summary", "").strip()
                    description = fields.get("description", "").strip() if fields.get("description") else ""
                    issue_key = issue.get("key", "")
                    
                    if not title:
                        title = f"JIRA Issue {issue_key}" if issue_key else "Untitled JIRA Issue"
                    if not description:
                        description = "No description available"
                    if not issue_key:
                        logger.warning(f"Skipping JIRA issue without key: {issue}")
                        continue
                    
                    evidence_items.append(EvidenceItem(
                        id=f"jira_issue_{issue.get('id', issue_key)}",
                        team_member_id=username,
                        source="jira_ticket",
                        title=title,
                        description=description,
                        source_url=f"{self.jira_base_url}/browse/{issue_key}",
                        category=self._categorize_jira_issue(issue),
                        evidence_date=self._parse_jira_date(fields.get("updated") or fields.get("created")),
                        created_at=datetime.now(),
                        metadata={
                            "issue_key": issue_key,
                            "issue_type": fields.get("issuetype", {}).get("name"),
                            "status": fields.get("status", {}).get("name"),
                            "priority": fields.get("priority", {}).get("name"),
                            "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                            "reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
                            "epic_link": (fields.get("epic", {}) or {}).get("key") or fields.get("customfield_10008"),
                            "sprint": (fields.get("sprint", {}) or {}).get("name") if isinstance(fields.get("sprint"), dict) else None,
                            "components": [c.get("name") for c in fields.get("components", [])] if isinstance(fields.get("components"), list) else None,
                            "labels": fields.get("labels", []),
                            "source_method": source.value
                        },
                        data_source=source,
                        fallback_used=fallback_used
                    ))
                except Exception as e:
                    logger.warning(f"Error transforming JIRA issue via API: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error transforming API JIRA issues data: {e}")
        
        return evidence_items

    def _categorize_jira_issue(self, issue: Dict) -> str:
        """Categorize JIRA issue based on type, labels, and content"""
        fields = issue.get("fields", {})
        
        # Check issue type
        issue_type = fields.get("issuetype", {}).get("name", "").lower()
        if "bug" in issue_type or "defect" in issue_type:
            return "technical"
        elif "story" in issue_type or "feature" in issue_type or "epic" in issue_type:
            return "delivery"
        elif "task" in issue_type:
            # Could be technical or delivery, check labels/title
            pass
        
        # Check labels
        labels = [label.lower() for label in fields.get("labels", [])]
        if any("bug" in label or "technical" in label for label in labels):
            return "technical"
        if any("feature" in label or "delivery" in label for label in labels):
            return "delivery"
        if any("discussion" in label or "meeting" in label for label in labels):
            return "collaboration"
        
        # Check title/summary
        title = fields.get("summary", "").lower()
        if any(keyword in title for keyword in ["fix", "bug", "error", "issue", "problem"]):
            return "technical"
        if any(keyword in title for keyword in ["implement", "add", "feature", "deliver"]):
            return "delivery"
        if any(keyword in title for keyword in ["review", "discuss", "meeting", "sync"]):
            return "collaboration"
        
        # Default to technical for most JIRA tickets
        return "technical"

    def _parse_jira_date(self, date_str: Optional[str]) -> datetime:
        """Parse JIRA date string to datetime"""
        if not date_str:
            return datetime.now()
        
        try:
            # Handle JIRA date formats: 2025-06-13T08:28:32.567+0200
            # Convert +0200 format to +02:00 for Python compatibility
            if '+' in date_str and date_str[-5:].count(':') == 0:
                # Convert +0200 to +02:00
                date_str = date_str[:-2] + ':' + date_str[-2:]
            elif '-' in date_str[-5:] and date_str[-5:].count(':') == 0:
                # Convert -0200 to -02:00
                date_str = date_str[:-2] + ':' + date_str[-2:]
            
            # JIRA typically uses ISO format: 2023-12-01T10:30:00.000+0000
            if date_str.endswith('Z'):
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            elif '+' in date_str[-6:] or '-' in date_str[-6:]:
                return datetime.fromisoformat(date_str)
            else:
                return datetime.fromisoformat(date_str + '+00:00')
        except Exception as e:
            logger.warning(f"Failed to parse JIRA date {date_str}: {e}")
            return datetime.now()

    async def close(self):
        """Close MCP server process"""
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
                logger.info("MCP server process closed")
            except Exception as e:
                logger.error(f"Error closing MCP server: {e}")

class JiraHybridClient(JiraDataProvider):
    """
    JIRA Hybrid Client - MCP first with API fallback
    
    This client implements the MCP-first hybrid approach:
    1. Try MCP server first (preferred method)
    2. Fallback to direct API if MCP fails
    3. Track which method was used for transparency
    
    Architecture:
    - MCP Server: Official Atlassian MCP server (25+ tools available)
    - Communication: stdio (JSON-RPC 2.0) via mcp-remote
    - Fallback: Direct JIRA REST API calls
    - Environment: Node.js MCP server + Python FastAPI backend
    """
    def __init__(self, mcp_client: JiraMCPClient, api_client: JiraAPIClient):
        self.mcp_client = mcp_client
        self.api_client = api_client
        logger.info("JIRA Hybrid Client initialized.")

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

    async def get_issues(self, username: str, since_date: datetime,
                        search_criteria: Optional[JQLSearchCriteria] = None) -> List[EvidenceItem]:
        """Get issues using MCP-first hybrid approach with configurable search criteria."""
        
        # Try MCP first
        try:
            logger.info(f"Attempting MCP: get_issues for {username}")
            mcp_issues = await self.mcp_client.get_issues(username, since_date, search_criteria)
            
            if mcp_issues:
                logger.info(f"MCP successful: found {len(mcp_issues)} issues")
                return mcp_issues
            else:
                logger.warning("MCP returned no issues, trying fallback")
        except Exception as e:
            logger.error(f"MCP exception: {e}")
        
        # Fallback to API
        try:
            logger.info(f"Falling back to API: get_issues for {username}")
            api_issues = await self.api_client.get_issues(username, since_date, search_criteria)
            logger.info(f"API successful: found {len(api_issues)} issues")
            return api_issues
        except Exception as e:
            logger.error(f"API fallback failed: {e}")
            return []

    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get projects using MCP-first hybrid approach."""
        
        # Try MCP first
        try:
            logger.info("Attempting MCP: get_projects")
            mcp_projects = await self.mcp_client.get_projects()
            
            if mcp_projects:
                logger.info(f"MCP successful: found {len(mcp_projects)} projects")
                return mcp_projects
            else:
                logger.warning("MCP returned no projects, trying fallback")
        except Exception as e:
            logger.error(f"MCP exception: {e}")
        
        # Fallback to API
        try:
            logger.info("Falling back to API: get_projects")
            api_projects = await self.api_client.get_projects()
            logger.info(f"API successful: found {len(api_projects)} projects")
            return api_projects
        except Exception as e:
            logger.error(f"API fallback failed: {e}")
            return []

    async def health_check(self) -> bool:
        """Check health of both MCP and API providers."""
        mcp_healthy = await self.mcp_client.health_check()
        api_healthy = await self.api_client.health_check()
        
        logger.info(f"Health check - MCP: {'✅' if mcp_healthy else '❌'}, API: {'✅' if api_healthy else '❌'}")
        
        # Return True if at least one provider is healthy
        return mcp_healthy or api_healthy

    async def get_comprehensive_evidence(self, username: str, days_back: int = 7) -> List[EvidenceItem]:
        """Get comprehensive evidence for user from JIRA"""
        since_date = datetime.now() - timedelta(days=days_back)
        
        logger.info(f"Getting comprehensive JIRA evidence for {username} since {since_date}")
        
        # Get issues (main evidence source for JIRA)
        issues = await self.get_issues(username, since_date)
        
        # Sort by evidence date (most recent first)
        issues.sort(key=lambda x: x.evidence_date, reverse=True)
        
        logger.info(f"Total JIRA evidence collected: {len(issues)} items")
        return issues

    async def close(self):
        """Close MCP server process"""
        try:
            await self.mcp_client.close()
        except Exception as e:
            logger.error(f"Error closing JIRA hybrid client: {e}")

# Factory function for easy instantiation
def create_jira_client(
    mcp_server_url: str,
    cloud_id: str,
    jira_base_url: str,
    api_token: str,
    user_email: str,
    project_key: Optional[str] = None,
    **kwargs
) -> JiraHybridClient:
    """Create a JIRA hybrid client with default settings"""
    mcp_client = JiraMCPClient(mcp_server_url, cloud_id, jira_base_url, **kwargs)
    api_client = JiraAPIClient(api_token, user_email, jira_base_url, project_key)
    return JiraHybridClient(mcp_client, api_client) 