# PerformancePulse - Manager-Focused AI Integration

## Philosophy: "AI for Manager Efficiency, Not Employee Surveillance"

Use Claude 3.5 Sonnet to help managers prepare for performance conversations by correlating technical evidence with historical context, generating structured discussion points, and identifying patterns across team members.

---

## AI Architecture (Manager-Centric)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Multi-Source  │───►│   Claude 3.5    │───►│   Meeting       │
│   Evidence      │    │   Correlation   │    │   Preparation   │
│   Collection    │    │   & Analysis    │    │   Generation    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
   GitLab/Jira            Historical Context         Discussion Points
   Documents              Pattern Recognition        Evidence Links
   Manual Uploads         Strength Identification    Suggested Questions
```

---

## Core AI Features for Managers

### 1. Evidence Correlation & Analysis
**What it does**: Correlate technical contributions with historical context and identify patterns

```python
# services/manager_ai.py
import anthropic
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class ManagerAIService:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def correlate_evidence_with_context(
        self, 
        evidence_items: List[Dict],
        context_documents: List[Dict],
        team_member_name: str
    ) -> Dict:
        """Correlate recent technical work with historical context"""
        
        # Build evidence summary
        evidence_summary = "\n".join([
            f"- {item['title']} ({item['source']}): {item['description'][:200]}"
            for item in evidence_items
        ])
        
        # Build historical context
        context_summary = "\n".join([
            f"- {doc['title']} ({doc['document_type']}): {doc['summary'] or doc['extracted_text'][:200]}"
            for doc in context_documents
        ])
        
        prompt = f"""
        You are an AI assistant helping an engineering manager prepare for a performance conversation.
        
        Team Member: {team_member_name}
        
        RECENT TECHNICAL WORK (Last 30 days):
        {evidence_summary}
        
        HISTORICAL CONTEXT (Past conversations, notes, feedback):
        {context_summary}
        
        Please analyze and provide:
        
        1. CORRELATION ANALYSIS: How does recent work relate to past discussions, goals, or feedback?
        2. PATTERN RECOGNITION: What consistent strengths or development areas emerge?
        3. PROGRESS INDICATORS: Evidence of growth or improvement since last review?
        4. DISCUSSION PRIORITIES: Top 3 topics that would be most valuable to discuss
        
        Format as JSON:
        {{
          "correlations": [
            {{
              "recent_work": "specific evidence item",
              "historical_context": "related past discussion/goal",
              "connection": "how they relate",
              "significance": "why this matters for the conversation"
            }}
          ],
          "patterns": {{
            "consistent_strengths": ["strength 1", "strength 2"],
            "development_areas": ["area 1", "area 2"],
            "growth_evidence": ["evidence of improvement"]
          }},
          "discussion_priorities": [
            {{
              "topic": "discussion topic",
              "rationale": "why discuss this",
              "evidence": ["supporting evidence"],
              "suggested_approach": "how to bring this up"
            }}
          ]
        }}
        """
        
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_json_response(response.content[0].text)
    
    async def generate_meeting_preparation(
        self,
        team_member_name: str,
        meeting_type: str,
        timeframe_days: int,
        evidence_items: List[Dict],
        context_documents: List[Dict],
        focus_areas: List[str]
    ) -> Dict:
        """Generate comprehensive meeting preparation"""
        
        # Get correlation analysis first
        correlation_analysis = await self.correlate_evidence_with_context(
            evidence_items, context_documents, team_member_name
        )
        
        # Build focus areas context
        focus_context = ", ".join(focus_areas) if focus_areas else "general performance discussion"
        
        prompt = f"""
        Generate a comprehensive meeting preparation for a {meeting_type} with {team_member_name}.
        
        Focus Areas: {focus_context}
        Timeframe: Last {timeframe_days} days
        
        CORRELATION ANALYSIS:
        {correlation_analysis}
        
        RECENT EVIDENCE SUMMARY:
        {self._summarize_evidence(evidence_items)}
        
        Generate a structured meeting preparation with:
        
        1. EXECUTIVE SUMMARY: 2-3 sentences on overall performance this period
        2. KEY ACHIEVEMENTS: Specific accomplishments with evidence links
        3. COLLABORATION HIGHLIGHTS: Cross-team work, mentoring, knowledge sharing
        4. DEVELOPMENT OPPORTUNITIES: Areas for growth with specific suggestions
        5. DISCUSSION QUESTIONS: 5-7 open-ended questions to drive conversation
        6. HISTORICAL CONTEXT INTEGRATION: How current work relates to past goals/feedback
        
        Format as structured JSON for easy consumption.
        """
        
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_json_response(response.content[0].text)
```

### 2. Historical Pattern Recognition
**What it does**: Analyze uploaded documents to identify long-term patterns and growth trajectories

```python
async def analyze_historical_patterns(
    self,
    context_documents: List[Dict],
    team_member_name: str,
    analysis_period_months: int = 12
) -> Dict:
    """Analyze historical documents to identify patterns and growth"""
    
    # Group documents by type and time period
    document_summary = self._group_documents_by_period(context_documents)
    
    prompt = f"""
    Analyze historical performance context for {team_member_name} over {analysis_period_months} months.
    
    DOCUMENT TIMELINE:
    {document_summary}
    
    Identify:
    
    1. CONSISTENT STRENGTHS: What strengths appear repeatedly across time periods?
    2. DEVELOPMENT TRAJECTORY: How has this person grown over time?
    3. RECURRING THEMES: What topics/challenges come up repeatedly?
    4. CAREER PROGRESSION INDICATORS: Evidence of increasing responsibility/impact
    5. FEEDBACK INTEGRATION: How well do they act on feedback over time?
    
    Provide specific examples and quotes where relevant.
    
    Format as JSON:
    {{
      "consistent_strengths": [
        {{
          "strength": "technical problem solving",
          "evidence": ["specific examples from documents"],
          "evolution": "how this strength has developed"
        }}
      ],
      "development_trajectory": {{
        "technical_growth": "progression in technical skills",
        "leadership_growth": "progression in leadership/influence",
        "collaboration_growth": "progression in teamwork/communication"
      }},
      "recurring_themes": [
        {{
          "theme": "theme name",
          "frequency": "how often it appears",
          "evolution": "how it has changed over time"
        }}
      ],
      "career_progression_indicators": ["evidence of growing impact/responsibility"],
      "feedback_integration_score": "assessment of how well they act on feedback"
    }}
    """
    
    response = await self.client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return self._parse_json_response(response.content[0].text)
```

### 3. Team-Level Insights
**What it does**: Generate insights across team members for manager dashboard

```python
async def generate_team_insights(
    self,
    team_members: List[Dict],
    team_evidence: Dict[str, List[Dict]],
    manager_focus_areas: List[str]
) -> Dict:
    """Generate team-level insights for manager dashboard"""
    
    # Build team summary
    team_summary = []
    for member in team_members:
        member_evidence = team_evidence.get(member['id'], [])
        evidence_count = len(member_evidence)
        recent_activity = len([e for e in member_evidence if self._is_recent(e['evidence_date'])])
        
        team_summary.append(f"""
        {member['full_name']} ({member['level']}):
        - {evidence_count} total contributions
        - {recent_activity} recent activities
        - Primary areas: {', '.join(self._extract_categories(member_evidence))}
        """)
    
    prompt = f"""
    Generate team-level insights for an engineering manager.
    
    TEAM COMPOSITION:
    {chr(10).join(team_summary)}
    
    MANAGER FOCUS AREAS: {', '.join(manager_focus_areas)}
    
    Provide insights on:
    
    1. TEAM PERFORMANCE TRENDS: Overall team productivity and quality patterns
    2. COLLABORATION PATTERNS: How well the team works together
    3. SKILL DISTRIBUTION: Team strengths and gaps
    4. DEVELOPMENT OPPORTUNITIES: Team-wide growth areas
    5. INDIVIDUAL STANDOUTS: Team members who need attention (positive or developmental)
    6. WORKLOAD BALANCE: Distribution of work and potential burnout indicators
    
    Format as JSON with actionable insights for the manager.
    """
    
    response = await self.client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return self._parse_json_response(response.content[0].text)
```

---

## Document Processing Pipeline

### Context Document Analysis
```python
# services/document_processor.py
import asyncio
from typing import Dict, List
import fitz  # PyMuPDF for PDF processing
import docx  # python-docx for Word documents

class DocumentProcessor:
    def __init__(self, ai_service: ManagerAIService):
        self.ai_service = ai_service
    
    async def process_uploaded_document(
        self,
        file_path: str,
        document_metadata: Dict,
        team_member_id: str
    ) -> Dict:
        """Process uploaded context document and extract insights"""
        
        # 1. Extract text based on file type
        extracted_text = await self._extract_text(file_path, document_metadata['file_type'])
        
        # 2. AI analysis for themes and summary
        analysis = await self._analyze_document_content(
            extracted_text, 
            document_metadata['document_type'],
            document_metadata['title']
        )
        
        # 3. Generate embedding for correlation
        embedding = await self._generate_embedding(f"{document_metadata['title']} {extracted_text}")
        
        return {
            'extracted_text': extracted_text,
            'summary': analysis['summary'],
            'key_themes': analysis['key_themes'],
            'embedding': embedding,
            'processing_status': 'completed'
        }
    
    async def _analyze_document_content(
        self, 
        text: str, 
        document_type: str, 
        title: str
    ) -> Dict:
        """Analyze document content for themes and summary"""
        
        prompt = f"""
        Analyze this {document_type} document for performance management context.
        
        Title: {title}
        Content: {text[:3000]}...
        
        Extract:
        1. SUMMARY: 2-3 sentence summary of key points
        2. KEY THEMES: 3-5 main themes/topics discussed
        3. PERFORMANCE INDICATORS: Any mentions of strengths, improvements, goals, or feedback
        4. ACTION ITEMS: Any commitments or next steps mentioned
        
        Format as JSON:
        {{
          "summary": "concise summary",
          "key_themes": ["theme1", "theme2", "theme3"],
          "performance_indicators": {{
            "strengths": ["mentioned strengths"],
            "improvements": ["areas for improvement"],
            "goals": ["goals or objectives"],
            "feedback": ["feedback given or received"]
          }},
          "action_items": ["action item 1", "action item 2"]
        }}
        """
        
        response = await self.ai_service.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self.ai_service._parse_json_response(response.content[0].text)
```

---

## Integration with Data Sources

### GitLab MCP Integration
```python
# services/gitlab_ai_sync.py
async def sync_gitlab_with_ai_analysis(
    manager_id: str,
    team_member_id: str,
    gitlab_mcp_client,
    ai_service: ManagerAIService
):
    """Sync GitLab data with AI analysis for manager insights"""
    
    # Get team member's GitLab username
    team_member = await db.profiles.find_unique({"where": {"id": team_member_id}})
    
    # Fetch recent merge requests and commits
    recent_mrs = await gitlab_mcp_client.call_tool("get_merge_requests", {
        "project_id": "team-project",
        "author_username": team_member.gitlab_username,
        "state": "merged",
        "created_after": (datetime.now() - timedelta(days=30)).isoformat()
    })
    
    for mr in recent_mrs:
        # Get detailed MR information
        mr_details = await gitlab_mcp_client.call_tool("get_merge_request_diffs", {
            "project_id": mr["project_id"],
            "merge_request_iid": mr["iid"]
        })
        
        # AI analysis of the merge request
        mr_analysis = await ai_service.analyze_technical_contribution(
            title=mr["title"],
            description=mr["description"],
            changes=mr_details["changes"],
            discussion_notes=mr.get("notes", [])
        )
        
        # Store as evidence item
        await db.evidence_items.create({
            "team_member_id": team_member_id,
            "title": f"GitLab MR: {mr['title']}",
            "description": mr["description"],
            "summary": mr_analysis["summary"],
            "source": "gitlab_mr",
            "source_id": str(mr["iid"]),
            "source_url": mr["web_url"],
            "category": mr_analysis["category"],
            "impact_level": mr_analysis["impact_level"],
            "ai_analysis": mr_analysis,
            "evidence_date": mr["merged_at"]
        })
```

### Jira MCP Integration
```python
# services/jira_ai_sync.py
async def sync_jira_with_ai_analysis(
    manager_id: str,
    team_member_id: str,
    jira_mcp_client,
    ai_service: ManagerAIService
):
    """Sync Jira data with AI analysis for manager insights"""
    
    team_member = await db.profiles.find_unique({"where": {"id": team_member_id}})
    
    # Search for team member's recent tickets
    recent_issues = await jira_mcp_client.call_tool("search_issues", {
        "searchString": f"assignee = '{team_member.jira_username}' AND updated >= -30d"
    })
    
    for issue in recent_issues["issues"]:
        # Get detailed issue information including comments
        issue_details = await jira_mcp_client.call_tool("get_issue", {
            "issueId": issue["key"]
        })
        
        # AI analysis of the ticket
        ticket_analysis = await ai_service.analyze_delivery_contribution(
            title=issue_details["fields"]["summary"],
            description=issue_details["fields"]["description"],
            issue_type=issue_details["fields"]["issuetype"]["name"],
            priority=issue_details["fields"]["priority"]["name"],
            comments=issue_details.get("comments", [])
        )
        
        # Store as evidence item
        await db.evidence_items.create({
            "team_member_id": team_member_id,
            "title": f"Jira: {issue_details['fields']['summary']}",
            "description": issue_details["fields"]["description"],
            "summary": ticket_analysis["summary"],
            "source": "jira_ticket",
            "source_id": issue["key"],
            "source_url": f"{jira_base_url}/browse/{issue['key']}",
            "category": ticket_analysis["category"],
            "impact_level": ticket_analysis["impact_level"],
            "ai_analysis": ticket_analysis,
            "evidence_date": issue_details["fields"]["updated"]
        })
```

---

## Frontend AI Integration

### Meeting Preparation Interface
```typescript
// components/meetings/MeetingPrepGenerator.tsx
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Sparkles, Clock, Download } from 'lucide-react'

interface MeetingPrepGeneratorProps {
  teamMemberId: string
  onPrepGenerated: (prep: MeetingPreparation) => void
}

export function MeetingPrepGenerator({ teamMemberId, onPrepGenerated }: MeetingPrepGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [config, setConfig] = useState({
    meetingType: 'weekly_1_1',
    timeframeDays: 7,
    focusAreas: ['technical_contributions'],
    includeHistoricalContext: true
  })
  
  const handleGenerate = async () => {
    setIsGenerating(true)
    try {
      const response = await fetch('/api/meetings/prepare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          team_member_id: teamMemberId,
          ...config
        })
      })
      
      const preparation = await response.json()
      onPrepGenerated(preparation)
    } catch (error) {
      console.error('Failed to generate meeting prep:', error)
    } finally {
      setIsGenerating(false)
    }
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          AI Meeting Preparation
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Configuration UI */}
        <div className="space-y-4 mb-6">
          {/* Meeting type, timeframe, focus areas selectors */}
        </div>
        
        <Button 
          onClick={handleGenerate} 
          disabled={isGenerating}
          className="w-full"
        >
          {isGenerating ? (
            <>
              <Clock className="h-4 w-4 mr-2 animate-spin" />
              Analyzing evidence and context...
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4 mr-2" />
              Generate Meeting Preparation
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  )
}
```

---

## Privacy & Consent Integration

### AI Processing with Consent Checks
```python
# services/consent_aware_ai.py
async def process_with_consent_check(
    manager_id: str,
    team_member_id: str,
    data_sources: List[str],
    ai_operation: callable
) -> Optional[Dict]:
    """Only process AI operations if proper consent is granted"""
    
    # Check consent for each data source
    for source in data_sources:
        consent = await db.data_consents.find_first({
            "where": {
                "team_member_id": team_member_id,
                "manager_id": manager_id,
                "data_source": source,
                "consent_granted": True,
                "revoked": False
            }
        })
        
        if not consent:
            raise ConsentError(f"No consent for {source} data processing")
    
    # Proceed with AI operation
    return await ai_operation()

# Usage in meeting preparation
async def generate_meeting_prep_with_consent(
    manager_id: str,
    team_member_id: str,
    config: Dict
) -> Dict:
    """Generate meeting preparation respecting consent boundaries"""
    
    required_sources = ['gitlab', 'jira']
    if config.get('include_historical_context'):
        required_sources.append('documents')
    
    return await process_with_consent_check(
        manager_id,
        team_member_id,
        required_sources,
        lambda: ai_service.generate_meeting_preparation(
            team_member_id=team_member_id,
            **config
        )
    )
```

---

## Implementation Roadmap

### Week 1-2: Core AI Infrastructure
- Claude 3.5 Sonnet integration
- Evidence correlation algorithms
- Basic meeting preparation generation

### Week 3-4: Historical Context Integration
- Document processing pipeline
- Pattern recognition across time periods
- Context-evidence correlation

### Week 5-6: Team-Level Insights
- Multi-member analysis
- Team dashboard AI features
- Manager workflow optimization

---

## What We're NOT Building

❌ Employee-facing AI chat interfaces
❌ Performance scoring/rating algorithms
❌ Real-time AI monitoring of work
❌ Predictive performance models
❌ AI-driven goal setting
❌ Automated feedback generation

## What We ARE Building

✅ Manager meeting preparation assistance
✅ Evidence-context correlation analysis
✅ Historical pattern recognition
✅ Team-level insight generation
✅ Privacy-aware AI processing
✅ Structured discussion point generation
✅ Multi-source data integration with AI

This AI integration focuses exclusively on helping managers be more effective in performance conversations, not on automating or replacing human judgment in performance management. 