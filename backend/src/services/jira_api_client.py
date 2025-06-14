from typing import List, Dict
from datetime import datetime, timedelta
import httpx
from src.utils.log import logger

class JiraAPIClient:
    def __init__(self, base_url: str, project_key: str, headers: dict):
        self.base_url = base_url
        self.project_key = project_key
        self.headers = headers
        self.client = httpx.AsyncClient()

    async def get_user_issues(self, username: str, days_back: int = 30, 
                            sprint_name: str = None, include_all_sprints: bool = True,
                            include_recent: bool = True, max_results: int = 50) -> List[Dict]:
        """
        Get issues assigned to user with flexible search criteria
        
        Args:
            username: Username to search for
            days_back: Days to look back for recent activity
            sprint_name: Specific sprint name to search (None for no sprint filter)
            include_all_sprints: Whether to include open sprints search
            include_recent: Whether to include recent activity search
            max_results: Maximum results per query
        """
        try:
            # Resolve username to account ID
            account_id = await self._resolve_username_to_account_id(username)
            
            # Calculate date range
            since_date = datetime.utcnow() - timedelta(days=days_back)
            since_str = since_date.strftime('%Y-%m-%d')
            
            # Build flexible JQL queries based on parameters
            jql_queries = []
            
            # Sprint-specific queries (if sprint_name provided)
            if sprint_name:
                jql_queries.extend([
                    f"sprint = '{sprint_name}' AND project = '{self.project_key}' AND assignee = '{account_id}'",
                    f"sprint = '{sprint_name}' AND project = '{self.project_key}'"
                ])
            
            # Open sprints queries (if enabled)
            if include_all_sprints:
                jql_queries.extend([
                    f"project = '{self.project_key}' AND assignee = '{account_id}' AND sprint in openSprints()",
                    f"project = '{self.project_key}' AND sprint in openSprints()"
                ])
            
            # Recent activity queries (if enabled)  
            if include_recent:
                jql_queries.extend([
                    f"project = '{self.project_key}' AND assignee = '{account_id}' AND updated >= '{since_str}'",
                    f"project = '{self.project_key}' AND updated >= '{since_str}' ORDER BY updated DESC"
                ])
            
            # Fallback: all user assignments in project
            if not jql_queries:
                jql_queries.append(f"project = '{self.project_key}' AND assignee = '{account_id}'")
            
            all_issues = []
            unique_keys = set()
            
            for jql in jql_queries:
                try:
                    params = {
                        "jql": jql,
                        "maxResults": max_results,
                        "fields": "summary,status,assignee,reporter,updated,created,description,priority,issuetype,sprint,fixVersions"
                    }
                    
                    response = await self.client.get(f"{self.base_url}/rest/api/3/search", 
                                                   headers=self.headers, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        issues = data.get("issues", [])
                        
                        # Add unique issues only
                        for issue in issues:
                            if issue['key'] not in unique_keys:
                                unique_keys.add(issue['key'])
                                all_issues.append(issue)
                        
                        logger.info(f"JQL '{jql}' returned {len(issues)} issues")
                        
                        # If we found issues with the priority queries, prefer those
                        if issues and jql in jql_queries[:2]:  # Sprint-specific queries
                            logger.info(f"Found current sprint data, prioritizing these results")
                            break
                            
                    else:
                        logger.warning(f"JQL query failed: {jql}, status: {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"JQL query error: {jql}, error: {e}")
                    continue
            
            logger.info(f"Total unique issues found: {len(all_issues)}")
            return all_issues
            
        except Exception as e:
            logger.error(f"Error getting user issues: {e}")
            return []
    
    async def search_issues(self, jql: str, max_results: int = 50, 
                          fields: List[str] = None) -> List[Dict]:
        """
        Generic JIRA search with custom JQL
        
        Args:
            jql: Custom JQL query string
            max_results: Maximum number of results
            fields: List of fields to retrieve (None for default set)
        """
        try:
            default_fields = [
                "summary", "status", "assignee", "reporter", "updated", 
                "created", "description", "priority", "issuetype", "sprint", "fixVersions"
            ]
            
            params = {
                "jql": jql,
                "maxResults": max_results,
                "fields": ",".join(fields or default_fields)
            }
            
            response = await self.client.get(f"{self.base_url}/rest/api/3/search", 
                                           headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get("issues", [])
                logger.info(f"Custom JQL '{jql}' returned {len(issues)} issues")
                return issues
            else:
                logger.warning(f"JQL search failed: {jql}, status: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error executing JQL search '{jql}': {e}")
            return []
    
    async def _resolve_username_to_account_id(self, username: str) -> str:
        """Resolve username to account ID for JQL queries"""
        try:
            # First try to get current user info to see if it matches
            response = await self.client.get(f"{self.base_url}/rest/api/3/myself", headers=self.headers)
            if response.status_code == 200:
                user_info = response.json()
                account_id = user_info.get('accountId')
                logger.info(f"Using current user account ID: {account_id}")
                return account_id
            
            # Fallback: Search for user by displayName or email
            search_response = await self.client.get(f"{self.base_url}/rest/api/3/user/search",
                                                  headers=self.headers,
                                                  params={"query": username})
            if search_response.status_code == 200:
                users = search_response.json()
                if users:
                    return users[0].get('accountId', username)
            
            logger.warning(f"Could not resolve username {username} to account ID, using as-is")
            return username
            
        except Exception as e:
            logger.warning(f"Error resolving username {username}: {e}")
            return username
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose() 