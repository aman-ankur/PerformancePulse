"""
Timeline Analyzer Algorithm
Phase 2.1 Implementation - Analyze temporal patterns in work evidence

This algorithm analyzes:
1. Work patterns (commit frequency, review cycles, ticket resolution)
2. Sprint boundary detection
3. Work distribution across team members
4. Temporal correlations between platforms
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from src.models.correlation_models import WorkStory, WorkPattern
from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType

logger = logging.getLogger(__name__)

class TimelineAnalyzer:
    """
    Analyze temporal patterns in work evidence
    
    Capabilities:
    - Detect work patterns and rhythms
    - Identify sprint boundaries
    - Analyze work distribution
    - Calculate velocity metrics
    """
    
    def __init__(self):
        """Initialize the timeline analyzer"""
        self.sprint_duration_days = 14  # Typical sprint length
        self.work_day_hours = 8
        
        logger.info("Timeline Analyzer initialized")
    
    async def analyze_work_story(self, work_story: WorkStory) -> Dict[str, Any]:
        """
        Analyze timeline patterns for a single work story
        
        Args:
            work_story: Work story to analyze
            
        Returns:
            Dictionary with timeline analysis results
        """
        if not work_story.evidence_items:
            return {"timeline": {}, "patterns": {}}
        
        # Analyze work sequence
        work_sequence = self._analyze_work_sequence(work_story.evidence_items)
        
        # Detect development patterns
        dev_patterns = self._detect_development_patterns(work_story.evidence_items)
        
        # Calculate work velocity
        velocity_metrics = self._calculate_work_velocity(work_story.evidence_items)
        
        # Analyze cross-platform timing
        cross_platform_timing = self._analyze_cross_platform_timing(work_story.evidence_items)
        
        return {
            "timeline": {
                "work_sequence": work_sequence,
                "cross_platform_timing": cross_platform_timing
            },
            "patterns": {
                "development_patterns": dev_patterns,
                "velocity_metrics": velocity_metrics
            }
        }
    
    def _analyze_work_sequence(self, items: List[UnifiedEvidenceItem]) -> Dict[str, Any]:
        """Analyze the sequence of work activities"""
        # Sort items by date
        sorted_items = sorted(items, key=lambda x: x.evidence_date)
        
        sequence = []
        for item in sorted_items:
            sequence.append({
                "date": item.evidence_date,
                "platform": item.platform,
                "type": item.source,
                "title": item.title[:50] + "..." if len(item.title) > 50 else item.title
            })
        
        # Detect typical patterns
        patterns = self._detect_sequence_patterns(sorted_items)
        
        return {
            "sequence": sequence,
            "patterns": patterns,
            "duration_days": (sorted_items[-1].evidence_date - sorted_items[0].evidence_date).days if len(sorted_items) > 1 else 0
        }
    
    def _detect_sequence_patterns(self, sorted_items: List[UnifiedEvidenceItem]) -> List[str]:
        """Detect common work sequence patterns"""
        patterns = []
        
        if len(sorted_items) < 2:
            return patterns
        
        # Check for JIRA -> GitLab pattern (ticket first, then development)
        jira_first = any(item.platform == PlatformType.JIRA for item in sorted_items[:2])
        gitlab_later = any(item.platform == PlatformType.GITLAB for item in sorted_items[1:])
        
        if jira_first and gitlab_later:
            patterns.append("ticket_driven_development")
        
        # Check for rapid iteration (multiple activities in short time)
        rapid_activities = 0
        for i in range(1, len(sorted_items)):
            time_diff = (sorted_items[i].evidence_date - sorted_items[i-1].evidence_date).days
            if time_diff <= 1:
                rapid_activities += 1
        
        if rapid_activities >= len(sorted_items) * 0.5:
            patterns.append("rapid_iteration")
        
        # Check for long development cycle
        total_duration = (sorted_items[-1].evidence_date - sorted_items[0].evidence_date).days
        if total_duration > 30:
            patterns.append("long_development_cycle")
        elif total_duration <= 3:
            patterns.append("quick_turnaround")
        
        return patterns
    
    def _detect_development_patterns(self, items: List[UnifiedEvidenceItem]) -> Dict[str, Any]:
        """Detect development patterns from evidence"""
        patterns = {}
        
        # Analyze activity by day of week
        day_distribution = defaultdict(int)
        for item in items:
            day_of_week = item.evidence_date.strftime('%A')
            day_distribution[day_of_week] += 1
        
        patterns["day_distribution"] = dict(day_distribution)
        
        # Analyze activity by platform
        platform_distribution = defaultdict(int)
        for item in items:
            platform_distribution[item.platform] += 1
        
        patterns["platform_distribution"] = dict(platform_distribution)
        
        # Detect work intensity (activities per day)
        if items:
            date_range = (max(item.evidence_date for item in items) - 
                         min(item.evidence_date for item in items)).days + 1
            patterns["activities_per_day"] = len(items) / max(date_range, 1)
        
        return patterns
    
    def _calculate_work_velocity(self, items: List[UnifiedEvidenceItem]) -> Dict[str, float]:
        """Calculate work velocity metrics"""
        if not items:
            return {}
        
        # Group items by week
        weekly_activity = defaultdict(int)
        for item in items:
            week_start = item.evidence_date - timedelta(days=item.evidence_date.weekday())
            week_key = week_start.strftime('%Y-W%U')
            weekly_activity[week_key] += 1
        
        # Calculate velocity metrics
        weekly_counts = list(weekly_activity.values())
        
        return {
            "avg_weekly_activity": sum(weekly_counts) / len(weekly_counts) if weekly_counts else 0,
            "max_weekly_activity": max(weekly_counts) if weekly_counts else 0,
            "min_weekly_activity": min(weekly_counts) if weekly_counts else 0,
            "velocity_consistency": 1.0 - (max(weekly_counts) - min(weekly_counts)) / max(max(weekly_counts), 1) if weekly_counts else 0
        }
    
    def _analyze_cross_platform_timing(self, items: List[UnifiedEvidenceItem]) -> Dict[str, Any]:
        """Analyze timing relationships between platforms"""
        gitlab_items = [item for item in items if item.platform == PlatformType.GITLAB]
        jira_items = [item for item in items if item.platform == PlatformType.JIRA]
        
        if not gitlab_items or not jira_items:
            return {}
        
        # Calculate time differences
        first_jira = min(item.evidence_date for item in jira_items)
        first_gitlab = min(item.evidence_date for item in gitlab_items)
        last_jira = max(item.evidence_date for item in jira_items)
        last_gitlab = max(item.evidence_date for item in gitlab_items)
        
        return {
            "jira_to_gitlab_delay_days": (first_gitlab - first_jira).days,
            "development_duration_days": (last_gitlab - first_gitlab).days,
            "total_cycle_time_days": (max(last_jira, last_gitlab) - first_jira).days
        }
    
    async def analyze_overall_patterns(self, work_stories: List[WorkStory]) -> List[WorkPattern]:
        """Analyze patterns across all work stories"""
        patterns = []
        
        if not work_stories:
            return patterns
        
        # Analyze commit frequency pattern
        commit_pattern = await self._analyze_commit_frequency(work_stories)
        if commit_pattern:
            patterns.append(commit_pattern)
        
        # Analyze review cycle pattern
        review_pattern = await self._analyze_review_cycles(work_stories)
        if review_pattern:
            patterns.append(review_pattern)
        
        # Analyze ticket resolution pattern
        resolution_pattern = await self._analyze_ticket_resolution(work_stories)
        if resolution_pattern:
            patterns.append(resolution_pattern)
        
        return patterns
    
    async def _analyze_commit_frequency(self, work_stories: List[WorkStory]) -> Optional[WorkPattern]:
        """Analyze commit frequency patterns"""
        all_gitlab_items = []
        for story in work_stories:
            gitlab_items = [item for item in story.evidence_items if item.platform == PlatformType.GITLAB]
            all_gitlab_items.extend(gitlab_items)
        
        if not all_gitlab_items:
            return None
        
        # Calculate commits per day
        date_counts = defaultdict(int)
        for item in all_gitlab_items:
            date_key = item.evidence_date.date()
            date_counts[date_key] += 1
        
        daily_commits = list(date_counts.values())
        avg_commits_per_day = sum(daily_commits) / len(daily_commits) if daily_commits else 0
        
        return WorkPattern(
            pattern_type="commit_frequency",
            description=f"Average {avg_commits_per_day:.1f} commits per active day",
            frequency=avg_commits_per_day,
            confidence_score=0.8,
            evidence_count=len(all_gitlab_items),
            time_period={
                "start": min(item.evidence_date for item in all_gitlab_items),
                "end": max(item.evidence_date for item in all_gitlab_items)
            }
        )
    
    async def _analyze_review_cycles(self, work_stories: List[WorkStory]) -> Optional[WorkPattern]:
        """Analyze code review cycle patterns"""
        review_cycles = []
        
        for story in work_stories:
            # Look for MR creation to merge patterns
            mrs = [item for item in story.evidence_items 
                  if item.platform == PlatformType.GITLAB and 'merge_request' in item.source.lower()]
            
            if len(mrs) >= 2:
                # Calculate time between MR creation and merge
                mr_dates = [item.evidence_date for item in mrs]
                cycle_time = (max(mr_dates) - min(mr_dates)).days
                review_cycles.append(cycle_time)
        
        if not review_cycles:
            return None
        
        avg_cycle_time = sum(review_cycles) / len(review_cycles)
        
        return WorkPattern(
            pattern_type="review_cycle",
            description=f"Average {avg_cycle_time:.1f} days from MR creation to merge",
            frequency=1.0 / avg_cycle_time if avg_cycle_time > 0 else 0,
            confidence_score=0.7,
            evidence_count=len(review_cycles),
            time_period={
                "start": datetime.utcnow() - timedelta(days=30),
                "end": datetime.utcnow()
            }
        )
    
    async def _analyze_ticket_resolution(self, work_stories: List[WorkStory]) -> Optional[WorkPattern]:
        """Analyze ticket resolution patterns"""
        resolution_times = []
        
        for story in work_stories:
            jira_items = [item for item in story.evidence_items if item.platform == PlatformType.JIRA]
            
            if jira_items:
                # Calculate time from first to last JIRA activity
                jira_dates = [item.evidence_date for item in jira_items]
                resolution_time = (max(jira_dates) - min(jira_dates)).days
                resolution_times.append(resolution_time)
        
        if not resolution_times:
            return None
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times)
        
        return WorkPattern(
            pattern_type="ticket_resolution",
            description=f"Average {avg_resolution_time:.1f} days to resolve tickets",
            frequency=1.0 / avg_resolution_time if avg_resolution_time > 0 else 0,
            confidence_score=0.6,
            evidence_count=len(resolution_times),
            time_period={
                "start": datetime.utcnow() - timedelta(days=30),
                "end": datetime.utcnow()
            }
        )
    
    async def detect_sprint_boundaries(self, evidence_items: List[UnifiedEvidenceItem]) -> List[Dict[str, Any]]:
        """Auto-detect sprint/milestone boundaries from evidence clustering"""
        if not evidence_items:
            return []
        
        # Sort items by date
        sorted_items = sorted(evidence_items, key=lambda x: x.evidence_date)
        
        # Group items into potential sprints based on activity gaps
        sprints = []
        current_sprint_items = []
        
        for i, item in enumerate(sorted_items):
            if not current_sprint_items:
                current_sprint_items.append(item)
                continue
            
            # Check if there's a significant gap (more than 3 days with no activity)
            last_date = current_sprint_items[-1].evidence_date
            gap_days = (item.evidence_date - last_date).days
            
            if gap_days > 3 and len(current_sprint_items) >= 3:
                # End current sprint
                sprints.append({
                    "start_date": current_sprint_items[0].evidence_date,
                    "end_date": current_sprint_items[-1].evidence_date,
                    "item_count": len(current_sprint_items),
                    "duration_days": (current_sprint_items[-1].evidence_date - current_sprint_items[0].evidence_date).days
                })
                current_sprint_items = [item]
            else:
                current_sprint_items.append(item)
        
        # Add final sprint if it has enough items
        if len(current_sprint_items) >= 3:
            sprints.append({
                "start_date": current_sprint_items[0].evidence_date,
                "end_date": current_sprint_items[-1].evidence_date,
                "item_count": len(current_sprint_items),
                "duration_days": (current_sprint_items[-1].evidence_date - current_sprint_items[0].evidence_date).days
            })
        
        return sprints 