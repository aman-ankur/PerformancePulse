"""
Work Story Grouper Algorithm
Phase 2.1 Implementation - Group related evidence into coherent work stories

This algorithm creates work stories by:
1. Finding primary JIRA tickets with high-confidence relationships
2. Collecting all related GitLab items
3. Creating timeline from evidence dates
4. Generating meaningful work story titles
"""

import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict

from src.models.correlation_models import (
    EvidenceRelationship,
    WorkStory,
    WorkStoryStatus,
    CorrelationRequest,
    RelationshipType
)
from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType

logger = logging.getLogger(__name__)

class WorkStoryGrouper:
    """
    Group related evidence into coherent work stories
    
    Strategy:
    1. Use relationship graph to find connected components
    2. Identify primary JIRA tickets as story anchors
    3. Group all related evidence around these anchors
    4. Generate meaningful titles and timelines
    """
    
    def __init__(self):
        """Initialize the work story grouper"""
        self.min_confidence_for_grouping = 0.5
        self.max_story_size = 20  # Maximum evidence items per story
        
        logger.info("Work Story Grouper initialized")
    
    async def create_work_stories(self, evidence_items: List[UnifiedEvidenceItem],
                                relationships: List[EvidenceRelationship],
                                request: CorrelationRequest) -> List[WorkStory]:
        """
        Group evidence using relationship graph
        
        Args:
            evidence_items: All evidence items to group
            relationships: Detected relationships between items
            request: Correlation request with parameters
            
        Returns:
            List of work stories
        """
        logger.info(f"Creating work stories from {len(evidence_items)} items and {len(relationships)} relationships")
        
        # Filter relationships by confidence
        high_confidence_relationships = [
            rel for rel in relationships 
            if rel.confidence_score >= self.min_confidence_for_grouping
        ]
        
        # Build relationship graph
        relationship_graph = self._build_relationship_graph(evidence_items, high_confidence_relationships)
        
        # Find connected components (groups of related evidence)
        connected_components = self._find_connected_components(relationship_graph)
        
        # Create work stories from components
        work_stories = []
        for component in connected_components:
            if len(component) >= request.min_evidence_per_story:
                story = await self._create_work_story_from_component(
                    component, evidence_items, high_confidence_relationships, request
                )
                if story:
                    work_stories.append(story)
        
        # Handle orphaned evidence (items not in any relationship)
        orphaned_items = self._find_orphaned_evidence(evidence_items, connected_components)
        orphaned_stories = await self._create_orphaned_stories(orphaned_items, request)
        work_stories.extend(orphaned_stories)
        
        # Sort stories by importance/size
        work_stories.sort(key=lambda s: (len(s.evidence_items), s.complexity_score), reverse=True)
        
        # Limit number of stories if requested
        if len(work_stories) > request.max_work_stories:
            work_stories = work_stories[:request.max_work_stories]
        
        logger.info(f"Created {len(work_stories)} work stories")
        return work_stories
    
    def _build_relationship_graph(self, evidence_items: List[UnifiedEvidenceItem],
                                relationships: List[EvidenceRelationship]) -> Dict[str, Set[str]]:
        """Build an undirected graph of evidence relationships"""
        graph = defaultdict(set)
        
        # Add all evidence items as nodes
        for item in evidence_items:
            graph[item.id] = set()
        
        # Add edges from relationships
        for rel in relationships:
            graph[rel.primary_evidence_id].add(rel.related_evidence_id)
            graph[rel.related_evidence_id].add(rel.primary_evidence_id)
        
        return dict(graph)
    
    def _find_connected_components(self, graph: Dict[str, Set[str]]) -> List[Set[str]]:
        """Find connected components in the relationship graph using DFS"""
        visited = set()
        components = []
        
        def dfs(node: str, component: Set[str]):
            if node in visited:
                return
            visited.add(node)
            component.add(node)
            
            for neighbor in graph.get(node, set()):
                dfs(neighbor, component)
        
        for node in graph:
            if node not in visited:
                component = set()
                dfs(node, component)
                if component:
                    components.append(component)
        
        return components
    
    async def _create_work_story_from_component(self, component: Set[str],
                                              evidence_items: List[UnifiedEvidenceItem],
                                              relationships: List[EvidenceRelationship],
                                              request: CorrelationRequest) -> Optional[WorkStory]:
        """Create a work story from a connected component"""
        # Get evidence items for this component
        evidence_map = {item.id: item for item in evidence_items}
        component_items = [evidence_map[item_id] for item_id in component if item_id in evidence_map]
        
        if not component_items:
            return None
        
        # Get relationships within this component
        component_relationships = [
            rel for rel in relationships
            if rel.primary_evidence_id in component and rel.related_evidence_id in component
        ]
        
        # Find primary JIRA ticket (if any)
        primary_jira_ticket = self._find_primary_jira_ticket(component_items, component_relationships)
        
        # Generate story title and description
        title = self._generate_story_title(component_items, primary_jira_ticket)
        description = self._generate_story_description(component_items, component_relationships)
        
        # Analyze timeline
        timeline = self._analyze_story_timeline(component_items)
        
        # Determine status
        status = self._determine_story_status(component_items)
        
        # Get team members involved
        team_members = self._extract_team_members(component_items)
        
        # Calculate basic complexity score
        complexity_score = self._calculate_basic_complexity(component_items)
        
        # Determine primary platform
        primary_platform = self._determine_primary_platform(component_items)
        
        work_story = WorkStory(
            title=title,
            description=description,
            evidence_items=component_items,
            relationships=component_relationships,
            primary_jira_ticket=primary_jira_ticket,
            primary_platform=primary_platform,
            timeline=timeline,
            duration=timeline.get('end') - timeline.get('start') if timeline.get('start') and timeline.get('end') else None,
            team_members_involved=team_members,
            status=status,
            complexity_score=complexity_score
        )
        
        return work_story
    
    def _find_primary_jira_ticket(self, items: List[UnifiedEvidenceItem],
                                relationships: List[EvidenceRelationship]) -> Optional[str]:
        """Find the primary JIRA ticket for this work story"""
        # Look for JIRA items that are targets of "SOLVES" relationships
        solved_tickets = set()
        for rel in relationships:
            if rel.relationship_type == RelationshipType.SOLVES:
                # Find the JIRA item being solved
                for item in items:
                    if item.id == rel.related_evidence_id and item.platform == PlatformType.JIRA:
                        ticket_key = item.metadata.get('key') or self._extract_jira_key_from_title(item.title)
                        if ticket_key:
                            solved_tickets.add(ticket_key)
        
        if solved_tickets:
            return list(solved_tickets)[0]  # Return first one
        
        # Fallback: look for any JIRA ticket in the story
        for item in items:
            if item.platform == PlatformType.JIRA:
                ticket_key = item.metadata.get('key') or self._extract_jira_key_from_title(item.title)
                if ticket_key:
                    return ticket_key
        
        return None
    
    def _extract_jira_key_from_title(self, title: str) -> Optional[str]:
        """Extract JIRA key from title"""
        import re
        match = re.search(r'\b([A-Z]{2,10}-\d+)\b', title)
        return match.group(1) if match else None
    
    def _generate_story_title(self, items: List[UnifiedEvidenceItem], 
                            primary_jira_ticket: Optional[str]) -> str:
        """Generate a meaningful title for the work story"""
        if primary_jira_ticket:
            # Find the JIRA item with this ticket
            for item in items:
                if item.platform == PlatformType.JIRA and primary_jira_ticket in item.title:
                    return item.title
        
        # Fallback: use the most descriptive title
        titles_by_length = sorted(items, key=lambda x: len(x.title), reverse=True)
        if titles_by_length:
            return titles_by_length[0].title
        
        return "Work Story"
    
    def _generate_story_description(self, items: List[UnifiedEvidenceItem],
                                  relationships: List[EvidenceRelationship]) -> str:
        """Generate a description for the work story"""
        platforms = set(item.platform for item in items)
        relationship_types = set(rel.relationship_type for rel in relationships)
        
        description_parts = [
            f"Work story involving {len(items)} evidence items across {', '.join(platforms)} platforms."
        ]
        
        if relationship_types:
            description_parts.append(f"Relationship types: {', '.join(relationship_types)}.")
        
        return " ".join(description_parts)
    
    def _analyze_story_timeline(self, items: List[UnifiedEvidenceItem]) -> Dict[str, datetime]:
        """Analyze the timeline of evidence in the story"""
        if not items:
            return {}
        
        dates = [item.evidence_date for item in items]
        timeline = {
            "start": min(dates),
            "end": max(dates)
        }
        
        # Add milestones (first GitLab activity, first JIRA activity, etc.)
        gitlab_dates = [item.evidence_date for item in items if item.platform == PlatformType.GITLAB]
        jira_dates = [item.evidence_date for item in items if item.platform == PlatformType.JIRA]
        
        if gitlab_dates:
            timeline["first_gitlab_activity"] = min(gitlab_dates)
            timeline["last_gitlab_activity"] = max(gitlab_dates)
        
        if jira_dates:
            timeline["first_jira_activity"] = min(jira_dates)
            timeline["last_jira_activity"] = max(jira_dates)
        
        return timeline
    
    def _determine_story_status(self, items: List[UnifiedEvidenceItem]) -> WorkStoryStatus:
        """Determine the status of the work story"""
        # Simple heuristic based on JIRA status if available
        for item in items:
            if item.platform == PlatformType.JIRA:
                status = item.metadata.get('status', '').lower()
                if status in ['done', 'closed', 'resolved', 'completed']:
                    return WorkStoryStatus.COMPLETED
                elif status in ['blocked', 'on hold']:
                    return WorkStoryStatus.BLOCKED
                elif status in ['in progress', 'in review', 'in development']:
                    return WorkStoryStatus.IN_PROGRESS
        
        # Fallback: check if there's recent activity
        recent_activity = any(
            (datetime.utcnow() - item.evidence_date).days <= 7 
            for item in items
        )
        
        return WorkStoryStatus.IN_PROGRESS if recent_activity else WorkStoryStatus.UNKNOWN
    
    def _extract_team_members(self, items: List[UnifiedEvidenceItem]) -> List[str]:
        """Extract team members involved in the work story"""
        members = set()
        
        for item in items:
            # Extract from various metadata fields
            for field in ['author', 'assignee', 'reporter', 'created_by']:
                if field in item.metadata and item.metadata[field]:
                    members.add(str(item.metadata[field]))
        
        return list(members)
    
    def _calculate_basic_complexity(self, items: List[UnifiedEvidenceItem]) -> float:
        """Calculate a basic complexity score for the work story"""
        # Simple complexity based on number of items and platforms
        num_items = len(items)
        num_platforms = len(set(item.platform for item in items))
        
        # Base complexity from item count (normalized to 0-1)
        item_complexity = min(num_items / 10.0, 1.0)
        
        # Platform diversity bonus
        platform_bonus = (num_platforms - 1) * 0.2
        
        return min(item_complexity + platform_bonus, 1.0)
    
    def _determine_primary_platform(self, items: List[UnifiedEvidenceItem]) -> Optional[PlatformType]:
        """Determine the primary platform for the work story"""
        platform_counts = {}
        for item in items:
            platform_counts[item.platform] = platform_counts.get(item.platform, 0) + 1
        
        if platform_counts:
            return max(platform_counts.keys(), key=lambda p: platform_counts[p])
        
        return None
    
    def _find_orphaned_evidence(self, evidence_items: List[UnifiedEvidenceItem],
                              connected_components: List[Set[str]]) -> List[UnifiedEvidenceItem]:
        """Find evidence items that are not part of any connected component"""
        all_connected_ids = set()
        for component in connected_components:
            all_connected_ids.update(component)
        
        orphaned = [item for item in evidence_items if item.id not in all_connected_ids]
        return orphaned
    
    async def _create_orphaned_stories(self, orphaned_items: List[UnifiedEvidenceItem],
                                     request: CorrelationRequest) -> List[WorkStory]:
        """Create individual work stories for orphaned evidence items"""
        stories = []
        
        # Group orphaned items by platform and date proximity
        grouped_orphans = self._group_orphaned_items(orphaned_items)
        
        for group in grouped_orphans:
            if len(group) >= request.min_evidence_per_story:
                story = WorkStory(
                    title=f"Individual Work: {group[0].title[:50]}...",
                    description=f"Standalone work with {len(group)} evidence items",
                    evidence_items=group,
                    relationships=[],
                    timeline=self._analyze_story_timeline(group),
                    team_members_involved=self._extract_team_members(group),
                    status=self._determine_story_status(group),
                    complexity_score=self._calculate_basic_complexity(group),
                    primary_platform=self._determine_primary_platform(group)
                )
                stories.append(story)
        
        return stories
    
    def _group_orphaned_items(self, orphaned_items: List[UnifiedEvidenceItem]) -> List[List[UnifiedEvidenceItem]]:
        """Group orphaned items by similarity"""
        # Simple grouping by platform and temporal proximity
        groups = []
        remaining_items = orphaned_items.copy()
        
        while remaining_items:
            current_item = remaining_items.pop(0)
            current_group = [current_item]
            
            # Find items from same platform within 7 days
            items_to_remove = []
            for item in remaining_items:
                if (item.platform == current_item.platform and 
                    abs((item.evidence_date - current_item.evidence_date).days) <= 7):
                    current_group.append(item)
                    items_to_remove.append(item)
            
            # Remove grouped items from remaining
            for item in items_to_remove:
                remaining_items.remove(item)
            
            groups.append(current_group)
        
        return groups 