"""
JIRA Search Criteria Models
Flexible configuration for JIRA searches without hardcoded values
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

class SearchScope(Enum):
    """Search scope for JIRA queries"""
    USER_ASSIGNED = "user_assigned"
    PROJECT_ALL = "project_all"
    SPRINT_SPECIFIC = "sprint_specific"
    RECENT_ACTIVITY = "recent_activity"
    CUSTOM_JQL = "custom_jql"

class Priority(Enum):
    """Search priority levels"""
    HIGH = 1
    MEDIUM = 2
    LOW = 3

@dataclass
class JQLSearchCriteria:
    """
    Flexible JQL search criteria configuration
    Replaces hardcoded values with configurable parameters
    """
    # Core search parameters
    username: str
    project_key: Optional[str] = None
    sprint_name: Optional[str] = None
    
    # Date filters
    since_date: Optional[datetime] = None
    until_date: Optional[datetime] = None
    days_back: int = 30
    
    # Search scope and behavior
    search_scopes: List[SearchScope] = field(default_factory=lambda: [
        SearchScope.SPRINT_SPECIFIC,
        SearchScope.USER_ASSIGNED,
        SearchScope.RECENT_ACTIVITY
    ])
    
    # Query parameters
    max_results: int = 50
    include_unassigned: bool = False
    include_open_sprints: bool = True
    include_closed_items: bool = False
    
    # Issue type filters
    issue_types: Optional[List[str]] = None  # ['Story', 'Bug', 'Task']
    statuses: Optional[List[str]] = None     # ['In Progress', 'Done']
    priorities: Optional[List[str]] = None   # ['High', 'Medium']
    
    # Custom filters
    labels: Optional[List[str]] = None
    components: Optional[List[str]] = None
    fix_versions: Optional[List[str]] = None
    
    # Advanced options
    custom_jql_filters: Optional[List[str]] = None
    order_by: str = "updated DESC"
    
    def __post_init__(self):
        """Initialize computed fields"""
        if self.since_date is None and self.days_back:
            self.since_date = datetime.utcnow() - timedelta(days=self.days_back)

@dataclass 
class JQLQuery:
    """Generated JQL query with metadata"""
    jql: str
    scope: SearchScope
    priority: Priority
    description: str
    max_results: int = 50

class JQLBuilder:
    """
    Builder for flexible JQL queries
    Eliminates hardcoded search criteria
    """
    
    def __init__(self, criteria: JQLSearchCriteria):
        self.criteria = criteria
        
    def build_queries(self) -> List[JQLQuery]:
        """Build prioritized list of JQL queries based on criteria"""
        queries = []
        
        for scope in self.criteria.search_scopes:
            query = self._build_query_for_scope(scope)
            if query:
                queries.append(query)
        
        return queries
    
    def _build_query_for_scope(self, scope: SearchScope) -> Optional[JQLQuery]:
        """Build JQL query for specific search scope"""
        
        base_filters = self._build_base_filters()
        
        if scope == SearchScope.SPRINT_SPECIFIC and self.criteria.sprint_name:
            jql = f"sprint = '{self.criteria.sprint_name}'"
            if self.criteria.project_key:
                jql += f" AND project = '{self.criteria.project_key}'"
            if not self.criteria.include_unassigned:
                jql += f" AND assignee = '{self.criteria.username}'"
            jql += base_filters
            
            return JQLQuery(
                jql=jql,
                scope=scope,
                priority=Priority.HIGH,
                description=f"Sprint-specific search: {self.criteria.sprint_name}",
                max_results=self.criteria.max_results
            )
            
        elif scope == SearchScope.USER_ASSIGNED:
            jql = f"assignee = '{self.criteria.username}'"
            if self.criteria.project_key:
                jql += f" AND project = '{self.criteria.project_key}'"
            jql += base_filters
            jql += f" ORDER BY {self.criteria.order_by}"
            
            return JQLQuery(
                jql=jql,
                scope=scope,
                priority=Priority.MEDIUM,
                description=f"User assigned tickets for {self.criteria.username}",
                max_results=self.criteria.max_results
            )
            
        elif scope == SearchScope.PROJECT_ALL and self.criteria.project_key:
            jql = f"project = '{self.criteria.project_key}'"
            jql += base_filters
            jql += f" ORDER BY {self.criteria.order_by}"
            
            return JQLQuery(
                jql=jql,
                scope=scope,
                priority=Priority.LOW,
                description=f"All project activity: {self.criteria.project_key}",
                max_results=self.criteria.max_results
            )
            
        elif scope == SearchScope.RECENT_ACTIVITY:
            jql = ""
            if self.criteria.project_key:
                jql = f"project = '{self.criteria.project_key}'"
            else:
                jql = f"assignee = '{self.criteria.username}'"
                
            jql += base_filters
            jql += f" ORDER BY {self.criteria.order_by}"
            
            return JQLQuery(
                jql=jql,
                scope=scope,
                priority=Priority.MEDIUM,
                description="Recent activity search",
                max_results=self.criteria.max_results
            )
        
        return None
    
    def _build_base_filters(self) -> str:
        """Build common base filters for all queries"""
        filters = []
        
        # Date filters
        if self.criteria.since_date:
            since_str = self.criteria.since_date.strftime('%Y-%m-%d')
            filters.append(f"updated >= '{since_str}'")
            
        if self.criteria.until_date:
            until_str = self.criteria.until_date.strftime('%Y-%m-%d')
            filters.append(f"updated <= '{until_str}'")
        
        # Issue type filters
        if self.criteria.issue_types:
            types_str = "', '".join(self.criteria.issue_types)
            filters.append(f"issuetype in ('{types_str}')")
            
        # Status filters
        if self.criteria.statuses:
            statuses_str = "', '".join(self.criteria.statuses)
            filters.append(f"status in ('{statuses_str}')")
            
        # Priority filters
        if self.criteria.priorities:
            priorities_str = "', '".join(self.criteria.priorities)
            filters.append(f"priority in ('{priorities_str}')")
            
        # Label filters
        if self.criteria.labels:
            for label in self.criteria.labels:
                filters.append(f"labels = '{label}'")
                
        # Component filters
        if self.criteria.components:
            components_str = "', '".join(self.criteria.components)
            filters.append(f"component in ('{components_str}')")
            
        # Fix version filters
        if self.criteria.fix_versions:
            versions_str = "', '".join(self.criteria.fix_versions)
            filters.append(f"fixVersion in ('{versions_str}')")
            
        # Custom JQL filters
        if self.criteria.custom_jql_filters:
            filters.extend(self.criteria.custom_jql_filters)
        
        return " AND " + " AND ".join(filters) if filters else ""

# Convenience functions for common search patterns
def create_sprint_search(username: str, sprint_name: str, project_key: str, 
                        days_back: int = 30) -> JQLSearchCriteria:
    """Create criteria for sprint-specific search"""
    return JQLSearchCriteria(
        username=username,
        project_key=project_key,
        sprint_name=sprint_name,
        days_back=days_back,
        search_scopes=[SearchScope.SPRINT_SPECIFIC, SearchScope.USER_ASSIGNED]
    )

def create_user_search(username: str, project_key: str = None, 
                      days_back: int = 30, since_date: datetime = None) -> JQLSearchCriteria:
    """Create criteria for user-focused search"""
    return JQLSearchCriteria(
        username=username,
        project_key=project_key,
        days_back=days_back,
        since_date=since_date,
        search_scopes=[SearchScope.USER_ASSIGNED, SearchScope.RECENT_ACTIVITY]
    )

def create_project_search(project_key: str, username: str = None,
                         days_back: int = 14) -> JQLSearchCriteria:
    """Create criteria for project-wide search"""
    scopes = [SearchScope.PROJECT_ALL]
    if username:
        scopes.insert(0, SearchScope.USER_ASSIGNED)
        
    return JQLSearchCriteria(
        username=username or "currentUser()",
        project_key=project_key,
        days_back=days_back,
        search_scopes=scopes
    ) 