"""
Technology Detector Algorithm
Phase 2.1 Implementation - Identify technologies and skills from work evidence

This algorithm detects:
1. Technologies from file extensions and content
2. Frameworks and tools mentioned
3. Programming languages used
4. Work complexity estimation
"""

import re
import logging
from typing import List, Dict, Any, Set
from collections import Counter

from src.models.correlation_models import WorkStory, TechnologyInsight
from src.models.unified_evidence import UnifiedEvidenceItem, PlatformType

logger = logging.getLogger(__name__)

class TechnologyDetector:
    """
    Identify technologies and skills from work evidence
    
    Detection methods:
    - File extensions from commit/MR data
    - Framework mentions in titles/descriptions
    - Tool references in content
    - Technology keywords in JIRA tickets
    """
    
    def __init__(self):
        """Initialize the technology detector"""
        # File extension to technology mapping
        self.file_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cs': 'C#',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.less': 'LESS',
            '.vue': 'Vue.js',
            '.jsx': 'React',
            '.tsx': 'React',
            '.json': 'JSON',
            '.xml': 'XML',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.dockerfile': 'Docker',
            '.tf': 'Terraform',
            '.sh': 'Shell',
            '.ps1': 'PowerShell',
            '.r': 'R',
            '.m': 'MATLAB',
            '.dart': 'Dart'
        }
        
        # Framework and tool patterns
        self.technology_patterns = {
            # Web Frameworks
            'React': [r'\breact\b', r'react-', r'jsx', r'tsx'],
            'Vue.js': [r'\bvue\b', r'vue-', r'\.vue'],
            'Angular': [r'\bangular\b', r'@angular'],
            'Next.js': [r'\bnext\.?js\b', r'next-'],
            'Nuxt.js': [r'\bnuxt\.?js\b', r'nuxt-'],
            'Svelte': [r'\bsvelte\b'],
            
            # Backend Frameworks
            'FastAPI': [r'\bfastapi\b', r'fast-api'],
            'Django': [r'\bdjango\b'],
            'Flask': [r'\bflask\b'],
            'Express.js': [r'\bexpress\.?js\b', r'\bexpress\b'],
            'Spring': [r'\bspring\b', r'spring-'],
            'Laravel': [r'\blaravel\b'],
            'Rails': [r'\brails\b', r'ruby on rails'],
            'ASP.NET': [r'\basp\.?net\b'],
            
            # Databases
            'PostgreSQL': [r'\bpostgres\b', r'\bpostgresql\b', r'psql'],
            'MySQL': [r'\bmysql\b'],
            'MongoDB': [r'\bmongo\b', r'\bmongodb\b'],
            'Redis': [r'\bredis\b'],
            'SQLite': [r'\bsqlite\b'],
            'Elasticsearch': [r'\belastic\b', r'\belasticsearch\b'],
            
            # Cloud & DevOps
            'Docker': [r'\bdocker\b', r'dockerfile'],
            'Kubernetes': [r'\bk8s\b', r'\bkubernetes\b', r'kubectl'],
            'AWS': [r'\baws\b', r'amazon web services'],
            'Azure': [r'\bazure\b'],
            'GCP': [r'\bgcp\b', r'google cloud'],
            'Terraform': [r'\bterraform\b', r'\.tf'],
            'Jenkins': [r'\bjenkins\b'],
            'GitLab CI': [r'gitlab.?ci', r'\.gitlab-ci'],
            'GitHub Actions': [r'github.?actions', r'\.github/workflows'],
            
            # Testing
            'Jest': [r'\bjest\b'],
            'Pytest': [r'\bpytest\b'],
            'JUnit': [r'\bjunit\b'],
            'Cypress': [r'\bcypress\b'],
            'Selenium': [r'\bselenium\b'],
            
            # Tools
            'Git': [r'\bgit\b'],
            'npm': [r'\bnpm\b'],
            'yarn': [r'\byarn\b'],
            'pip': [r'\bpip\b'],
            'Maven': [r'\bmaven\b'],
            'Gradle': [r'\bgradle\b'],
            'Webpack': [r'\bwebpack\b'],
            'Vite': [r'\bvite\b'],
            
            # Mobile
            'React Native': [r'react.?native', r'react-native'],
            'Flutter': [r'\bflutter\b'],
            'iOS': [r'\bios\b', r'\bswift\b', r'\bobjective.?c\b'],
            'Android': [r'\bandroid\b', r'\bkotlin\b']
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            'high': ['microservice', 'distributed', 'scalable', 'architecture', 'performance', 'optimization'],
            'medium': ['api', 'integration', 'database', 'authentication', 'security'],
            'low': ['bug', 'fix', 'update', 'minor', 'typo']
        }
        
        logger.info("Technology Detector initialized")
    
    async def detect_technologies(self, work_story: WorkStory) -> List[str]:
        """
        Detect technologies used in a work story
        
        Args:
            work_story: Work story to analyze
            
        Returns:
            List of detected technologies
        """
        technologies = set()
        
        for item in work_story.evidence_items:
            # Detect from file extensions
            file_techs = self._detect_from_file_extensions(item)
            technologies.update(file_techs)
            
            # Detect from content patterns
            content_techs = self._detect_from_content(item)
            technologies.update(content_techs)
            
            # Detect from metadata
            metadata_techs = self._detect_from_metadata(item)
            technologies.update(metadata_techs)
        
        return list(technologies)
    
    def _detect_from_file_extensions(self, item: UnifiedEvidenceItem) -> Set[str]:
        """Detect technologies from file extensions in metadata"""
        technologies = set()
        
        # Check for file paths in metadata
        file_fields = ['files_changed', 'file_paths', 'modified_files', 'added_files']
        
        for field in file_fields:
            if field in item.metadata and item.metadata[field]:
                files = item.metadata[field]
                if isinstance(files, str):
                    files = [files]
                elif isinstance(files, list):
                    pass
                else:
                    continue
                
                for file_path in files:
                    if isinstance(file_path, str):
                        # Extract file extension
                        for ext, tech in self.file_extensions.items():
                            if file_path.lower().endswith(ext):
                                technologies.add(tech)
        
        return technologies
    
    def _detect_from_content(self, item: UnifiedEvidenceItem) -> Set[str]:
        """Detect technologies from content using pattern matching"""
        technologies = set()
        
        # Combine title and description for analysis
        content = f"{item.title} {item.description}".lower()
        
        # Check each technology pattern
        for tech, patterns in self.technology_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    technologies.add(tech)
                    break  # Found this tech, move to next
        
        return technologies
    
    def _detect_from_metadata(self, item: UnifiedEvidenceItem) -> Set[str]:
        """Detect technologies from metadata fields"""
        technologies = set()
        
        # Check labels and tags
        label_fields = ['labels', 'tags', 'components', 'categories']
        
        for field in label_fields:
            if field in item.metadata and item.metadata[field]:
                labels = item.metadata[field]
                if isinstance(labels, str):
                    labels = [labels]
                
                for label in labels:
                    if isinstance(label, str):
                        label_lower = label.lower()
                        
                        # Check if label matches any technology
                        for tech, patterns in self.technology_patterns.items():
                            for pattern in patterns:
                                if re.search(pattern, label_lower, re.IGNORECASE):
                                    technologies.add(tech)
        
        return technologies
    
    async def calculate_complexity(self, work_story: WorkStory) -> float:
        """
        Calculate complexity score for a work story
        
        Args:
            work_story: Work story to analyze
            
        Returns:
            Complexity score between 0.0 and 1.0
        """
        complexity_score = 0.0
        
        # Base complexity from number of evidence items
        item_count_score = min(len(work_story.evidence_items) / 10.0, 0.3)
        complexity_score += item_count_score
        
        # Technology diversity score
        tech_diversity_score = min(len(work_story.technology_stack) / 5.0, 0.2)
        complexity_score += tech_diversity_score
        
        # Platform diversity score
        platform_count = len(work_story.platforms_involved)
        platform_score = min(platform_count / 3.0, 0.2)
        complexity_score += platform_score
        
        # Content complexity analysis
        content_score = self._analyze_content_complexity(work_story)
        complexity_score += content_score
        
        # Duration factor
        if work_story.duration:
            duration_days = work_story.duration.days
            if duration_days > 30:
                complexity_score += 0.1  # Long projects are more complex
            elif duration_days < 3:
                complexity_score += 0.05  # Very quick work might be simple fixes
        
        # Ensure score is between 0.0 and 1.0
        return max(0.0, min(1.0, complexity_score))
    
    def _analyze_content_complexity(self, work_story: WorkStory) -> float:
        """Analyze content for complexity indicators"""
        content_score = 0.0
        all_content = ""
        
        # Combine all content
        for item in work_story.evidence_items:
            all_content += f" {item.title} {item.description}"
        
        content_lower = all_content.lower()
        
        # Check for complexity indicators
        for complexity_level, keywords in self.complexity_indicators.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            
            if complexity_level == 'high':
                content_score += matches * 0.05
            elif complexity_level == 'medium':
                content_score += matches * 0.03
            elif complexity_level == 'low':
                content_score -= matches * 0.02  # Low complexity indicators reduce score
        
        return max(0.0, min(0.3, content_score))  # Cap at 0.3
    
    async def generate_technology_insights(self, work_stories: List[WorkStory]) -> List[TechnologyInsight]:
        """Generate technology usage insights across all work stories"""
        if not work_stories:
            return []
        
        # Collect all technology usage
        tech_usage = Counter()
        tech_evidence_map = {}
        tech_dates = {}
        
        for story in work_stories:
            for tech in story.technology_stack:
                tech_usage[tech] += 1
                
                # Track evidence sources
                if tech not in tech_evidence_map:
                    tech_evidence_map[tech] = []
                tech_evidence_map[tech].extend([item.id for item in story.evidence_items])
                
                # Track dates
                if tech not in tech_dates:
                    tech_dates[tech] = []
                tech_dates[tech].extend([item.evidence_date for item in story.evidence_items])
        
        # Generate insights
        insights = []
        for tech, usage_count in tech_usage.most_common():
            dates = tech_dates[tech]
            
            insight = TechnologyInsight(
                technology=tech,
                usage_count=usage_count,
                confidence_score=min(usage_count / 10.0, 1.0),  # Higher usage = higher confidence
                evidence_sources=list(set(tech_evidence_map[tech])),  # Unique evidence IDs
                first_seen=min(dates),
                last_seen=max(dates)
            )
            insights.append(insight)
        
        return insights
    
    def detect_skill_level(self, work_story: WorkStory, technology: str) -> str:
        """
        Estimate skill level for a specific technology based on work evidence
        
        Args:
            work_story: Work story to analyze
            technology: Technology to assess skill level for
            
        Returns:
            Skill level: 'beginner', 'intermediate', 'advanced'
        """
        # Simple heuristic based on complexity and frequency
        tech_mentions = 0
        complex_work = False
        
        for item in work_story.evidence_items:
            content = f"{item.title} {item.description}".lower()
            
            # Count mentions of this technology
            if technology.lower() in content:
                tech_mentions += 1
                
                # Check for complex work indicators
                complex_indicators = ['architecture', 'optimization', 'performance', 'scalable', 'design']
                if any(indicator in content for indicator in complex_indicators):
                    complex_work = True
        
        # Determine skill level
        if complex_work and tech_mentions >= 3:
            return 'advanced'
        elif tech_mentions >= 2 or complex_work:
            return 'intermediate'
        else:
            return 'beginner' 