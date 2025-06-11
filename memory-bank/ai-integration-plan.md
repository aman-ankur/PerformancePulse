# PerformancePulse - Simple AI Integration

## Philosophy: "AI That Actually Helps"

Use Claude 3.5 Sonnet for intelligent evidence analysis and insights. Keep it simple, effective, and focused on real user value.

---

## AI Architecture (Simple)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Evidence      │───►│   Claude API    │───►│   Insights      │
│   Collection    │    │   Processing    │    │   Generation    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
   Text + Files            Categorization            Strengths
   GitHub Data             Summarization             Improvements
   Manual Input            Key Extraction            Achievements
```

---

## Core AI Features

### 1. Evidence Processing
**What it does**: Automatically categorize and summarize evidence

```python
# services/claude.py
import anthropic
from typing import Dict, List

class ClaudeService:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def categorize_evidence(self, title: str, content: str) -> Dict:
        """Categorize evidence into predefined categories"""
        prompt = f"""
        Analyze this work evidence and categorize it:
        
        Title: {title}
        Content: {content}
        
        Choose the best category:
        - Technical: Code, architecture, technical problem-solving
        - Collaboration: Working with others, communication, teamwork  
        - Leadership: Mentoring, decision-making, driving initiatives
        - Delivery: Project completion, meeting deadlines, results
        - Learning: Skill development, knowledge sharing
        
        Also suggest 2-3 relevant tags and create a brief summary.
        
        Respond in JSON format:
        {{
          "category": "Technical",
          "tags": ["python", "api", "performance"],
          "summary": "Brief 1-2 sentence summary",
          "confidence": 0.9
        }}
        """
        
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_json_response(response.content[0].text)
    
    async def generate_summary(self, content: str) -> str:
        """Generate a concise summary of evidence content"""
        prompt = f"""
        Create a concise, professional summary of this work evidence:
        
        {content}
        
        Keep it to 1-2 sentences, focusing on the key achievement or contribution.
        """
        
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
```

### 2. Performance Insights
**What it does**: Generate strengths, improvement areas, and achievements

```python
async def generate_insights(self, evidence_list: List[Dict]) -> List[Dict]:
    """Generate performance insights from evidence collection"""
    
    # Combine all evidence into context
    evidence_text = "\n\n".join([
        f"- {ev['title']}: {ev['summary'] or ev['content'][:200]}"
        for ev in evidence_list
    ])
    
    prompt = f"""
    Based on this work evidence, generate 3-5 performance insights:
    
    {evidence_text}
    
    Create insights in these categories:
    1. Strengths (what they do well)
    2. Achievements (notable accomplishments)  
    3. Growth Areas (potential improvements)
    
    For each insight:
    - Be specific and evidence-based
    - Keep it constructive and actionable
    - Reference specific examples when possible
    
    Respond in JSON format:
    {{
      "insights": [
        {{
          "type": "strength",
          "title": "Strong Technical Problem Solving",
          "content": "Demonstrates ability to...",
          "evidence_references": ["item1", "item2"]
        }}
      ]
    }}
    """
    
    response = await self.client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return self._parse_json_response(response.content[0].text)
```

### 3. Semantic Search
**What it does**: Find relevant evidence using vector embeddings

```python
# services/embeddings.py
from openai import OpenAI
import numpy as np

class EmbeddingService:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    async def search_similar_evidence(
        self, 
        query: str, 
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Search for evidence similar to query"""
        
        # Generate query embedding
        query_embedding = await self.generate_embedding(query)
        
        # Search database using pgvector
        from database import get_database
        db = get_database()
        
        results = await db.execute("""
            SELECT id, title, content, 
                   1 - (embedding <=> $1) as similarity
            FROM evidence 
            WHERE user_id = $2 
              AND 1 - (embedding <=> $1) > 0.7
            ORDER BY embedding <=> $1
            LIMIT $3
        """, query_embedding, user_id, limit)
        
        return results
```

---

## AI Workflow Integration

### Evidence Upload Flow
```python
# routers/evidence.py
from fastapi import APIRouter, UploadFile, File
from services.claude import ClaudeService
from services.embeddings import EmbeddingService

router = APIRouter()

@router.post("/evidence")
async def create_evidence(
    title: str,
    content: str,
    user_id: str,
    file: UploadFile = File(None)
):
    """Create new evidence with AI processing"""
    
    # 1. Extract text from file if uploaded
    if file:
        file_content = await extract_text_from_file(file)
        content = f"{content}\n\n{file_content}"
    
    # 2. AI categorization and summarization
    claude = ClaudeService(api_key=settings.ANTHROPIC_API_KEY)
    
    categorization = await claude.categorize_evidence(title, content)
    summary = await claude.generate_summary(content)
    
    # 3. Generate embedding for search
    embedding_service = EmbeddingService(api_key=settings.OPENAI_API_KEY)
    embedding = await embedding_service.generate_embedding(f"{title} {content}")
    
    # 4. Save to database
    evidence = await db.evidence.create({
        "user_id": user_id,
        "title": title,
        "content": content,
        "summary": summary,
        "category": categorization["category"],
        "tags": categorization["tags"],
        "embedding": embedding,
        "ai_metadata": categorization
    })
    
    # 5. Trigger insights regeneration in background
    await regenerate_insights_async(user_id)
    
    return evidence
```

### Background Insights Generation
```python
# services/background_jobs.py
import asyncio
from services.claude import ClaudeService

async def regenerate_insights(user_id: str):
    """Regenerate insights for user based on current evidence"""
    
    # Get all user evidence
    evidence_list = await db.evidence.find_many({
        "where": {"user_id": user_id},
        "orderBy": {"created_at": "desc"},
        "take": 50  # Limit to recent evidence
    })
    
    if len(evidence_list) < 3:
        return  # Need minimum evidence for insights
    
    # Generate insights using Claude
    claude = ClaudeService(api_key=settings.ANTHROPIC_API_KEY)
    insights_data = await claude.generate_insights(evidence_list)
    
    # Clear old insights
    await db.insights.delete_many({"where": {"user_id": user_id}})
    
    # Save new insights
    for insight in insights_data["insights"]:
        await db.insights.create({
            "user_id": user_id,
            "type": insight["type"],
            "title": insight["title"],
            "content": insight["content"],
            "confidence": insight.get("confidence", 0.8),
            "evidence_ids": insight.get("evidence_references", [])
        })

# Schedule background job
async def schedule_insights_regeneration(user_id: str):
    """Schedule insights regeneration with delay to batch updates"""
    await asyncio.sleep(10)  # Wait 10 seconds
    await regenerate_insights(user_id)
```

---

## Natural Language Interface

### Simple Chat for Evidence Queries
```python
# routers/chat.py
@router.post("/chat")
async def chat_query(query: str, user_id: str):
    """Answer questions about user's performance evidence"""
    
    # Search relevant evidence
    embedding_service = EmbeddingService(api_key=settings.OPENAI_API_KEY)
    relevant_evidence = await embedding_service.search_similar_evidence(
        query, user_id, limit=5
    )
    
    # Build context from evidence
    context = "\n".join([
        f"- {ev['title']}: {ev['content'][:200]}..."
        for ev in relevant_evidence
    ])
    
    # Generate response using Claude
    claude = ClaudeService(api_key=settings.ANTHROPIC_API_KEY)
    
    prompt = f"""
    You are a performance assistant. Answer the user's question based on their work evidence.
    
    User question: {query}
    
    Relevant evidence:
    {context}
    
    Provide a helpful, specific answer based on the evidence. If the evidence doesn't support an answer, say so.
    """
    
    response = await claude.client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return {
        "response": response.content[0].text,
        "sources": [ev["id"] for ev in relevant_evidence]
    }
```

---

## GitLab & Jira Integration with AI

### GitLab Evidence Processing (Booking.com)
```python
# services/gitlab_sync.py
async def sync_gitlab_evidence(user_id: str, gitlab_token: str):
    """Sync GitLab activity from Booking.com and process with AI"""
    
    # Configure for Booking.com's GitLab instance
    gitlab_client = gitlab.Gitlab(
        url="https://gitlab.booking.com",  # Adjust to actual URL
        private_token=gitlab_token
    )
    
    claude = ClaudeService(api_key=settings.ANTHROPIC_API_KEY)
    embedding_service = EmbeddingService(api_key=settings.OPENAI_API_KEY)
    
    # Fetch recent commits and merge requests
    projects = gitlab_client.projects.list(membership=True, archived=False)
    
    for project in projects:
        # Get user's recent commits
        commits = project.commits.list(
            author_email=user_email,
            since=last_sync_date.isoformat()
        )
        
        for commit in commits:
            # Skip if already processed
            existing = await db.evidence.find_first({
                "where": {
                    "user_id": user_id,
                    "source": "gitlab",
                    "source_id": commit.id
                }
            })
            if existing:
                continue
            
            # AI processing for GitLab content
            title = f"GitLab: {commit.title[:50]}..."
            content = f"{commit.message}\nProject: {project.name}\nStats: {commit.stats}"
            
            # Categorize and summarize with Claude
            categorization = await claude.categorize_evidence(title, content)
            summary = await claude.generate_summary(content)
            embedding = await embedding_service.generate_embedding(f"{title} {content}")
            
            # Save as evidence
            await db.evidence.create({
                "user_id": user_id,
                "title": title,
                "content": content,
                "summary": summary,
                "source": "gitlab",
                "source_id": commit.id,
                "source_url": commit.web_url,
                "category": categorization["category"],
                "tags": categorization["tags"],
                "embedding": embedding,
                "ai_metadata": {
                    **categorization,
                    "gitlab_stats": {
                        "project": project.name,
                        "additions": commit.stats.get("additions", 0),
                        "deletions": commit.stats.get("deletions", 0)
                    }
                }
            })
    
    await regenerate_insights(user_id)

### Jira Evidence Processing (MCP Integration)
```python
# services/jira_mcp_sync.py
from mcp import Client as MCPClient

async def sync_jira_evidence(user_id: str):
    """Sync Jira activity using MCP server and process with AI"""
    
    # Initialize MCP client for Jira
    mcp_client = MCPClient("jira-mcp-server")
    
    claude = ClaudeService(api_key=settings.ANTHROPIC_API_KEY)
    embedding_service = EmbeddingService(api_key=settings.OPENAI_API_KEY)
    
    # Get user's recent issues using MCP
    issues = await mcp_client.call_tool("search_issues", {
        "jql": "assignee = currentUser() AND updated >= -30d",
        "fields": ["summary", "description", "status", "project", "issuetype", "priority"]
    })
    
    for issue in issues:
        # Skip if already processed
        existing = await db.evidence.find_first({
            "where": {
                "user_id": user_id,
                "source": "jira",
                "source_id": issue["key"]
            }
        })
        if existing:
            continue
        
        # AI processing for Jira content
        title = f"{issue['key']}: {issue['fields']['summary']}"
        content = f"""
        Issue Type: {issue['fields']['issuetype']['name']}
        Status: {issue['fields']['status']['name']}
        Priority: {issue['fields']['priority']['name']}
        Project: {issue['fields']['project']['name']}
        
        Description: {issue['fields']['description'][:500]}...
        """
        
        # Categorize and summarize with Claude
        categorization = await claude.categorize_evidence(title, content)
        summary = await claude.generate_summary(content)
        embedding = await embedding_service.generate_embedding(f"{title} {content}")
        
        # Save as evidence
        await db.evidence.create({
            "user_id": user_id,
            "title": title,
            "content": content,
            "summary": summary,
            "source": "jira",
            "source_id": issue["key"],
            "source_url": f"https://booking.atlassian.net/browse/{issue['key']}",
            "category": categorization["category"],
            "tags": categorization["tags"],
            "embedding": embedding,
            "ai_metadata": {
                **categorization,
                "jira_details": {
                    "issue_type": issue['fields']['issuetype']['name'],
                    "status": issue['fields']['status']['name'],
                    "priority": issue['fields']['priority']['name'],
                    "project": issue['fields']['project']['name']
                }
            }
        })
    
    await regenerate_insights(user_id)
```

---

## Frontend AI Integration

### Real-time Insights Display
```typescript
// hooks/useInsights.ts
import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase'

export function useInsights(userId: string) {
  const [insights, setInsights] = useState([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    const supabase = createClient()
    
    // Initial load
    const loadInsights = async () => {
      const { data } = await supabase
        .from('insights')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
      
      setInsights(data || [])
      setLoading(false)
    }
    
    loadInsights()
    
    // Real-time updates
    const subscription = supabase
      .channel('insights_changes')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'insights',
        filter: `user_id=eq.${userId}`
      }, (payload) => {
        if (payload.eventType === 'INSERT') {
          setInsights(prev => [payload.new, ...prev])
        }
        // Handle other events...
      })
      .subscribe()
    
    return () => subscription.unsubscribe()
  }, [userId])
  
  return { insights, loading }
}
```

### Chat Interface Component
```typescript
// components/chat/SimpleChatInterface.tsx
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'

export function SimpleChatInterface({ userId }: { userId: string }) {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    
    setLoading(true)
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, user_id: userId })
      })
      
      const data = await res.json()
      setResponse(data.response)
    } catch (error) {
      console.error('Chat error:', error)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <Card>
      <CardContent className="p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Input
              placeholder="Ask about your performance... (e.g., 'What are my technical strengths?')"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>
          <Button type="submit" disabled={loading}>
            {loading ? 'Analyzing...' : 'Ask'}
          </Button>
        </form>
        
        {response && (
          <div className="mt-4 p-4 bg-muted rounded-lg">
            <p className="text-sm">{response}</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
```

---

## AI Cost Management

### Simple Cost Controls
```python
# config/ai_limits.py
AI_LIMITS = {
    "max_evidence_per_day": 50,
    "max_insight_regenerations_per_day": 5,
    "max_chat_queries_per_day": 20,
    "max_tokens_per_request": 4000
}

async def check_ai_usage(user_id: str, operation: str) -> bool:
    """Simple usage tracking to control costs"""
    today = datetime.now().date()
    
    usage = await db.ai_usage.find_first({
        "where": {
            "user_id": user_id,
            "date": today
        }
    })
    
    if not usage:
        usage = await db.ai_usage.create({
            "user_id": user_id,
            "date": today,
            "evidence_processed": 0,
            "insights_generated": 0,
            "chat_queries": 0
        })
    
    current_count = getattr(usage, f"{operation}_count", 0)
    limit = AI_LIMITS[f"max_{operation}_per_day"]
    
    return current_count < limit
```

---

## Implementation Timeline

### Week 1: Basic AI Setup
- Claude API integration
- Simple evidence categorization
- Basic summarization

### Week 2: Advanced Features
- Vector embeddings with OpenAI
- Semantic search implementation
- Insights generation

### Week 3: GitHub Integration
- GitHub API integration
- Automatic evidence creation
- Background processing

### Week 4: Chat Interface
- Natural language queries
- Evidence-based responses
- Frontend integration

---

## What We're NOT Building

❌ Complex multi-model AI pipeline
❌ Custom fine-tuned models
❌ Advanced NLP preprocessing
❌ Complex prompt chaining
❌ AI model training infrastructure
❌ Advanced vector database management
❌ Complex AI orchestration

## What We ARE Building

✅ Simple Claude API integration
✅ Automatic evidence categorization
✅ Performance insights generation
✅ Semantic search with embeddings
✅ Natural language chat interface
✅ GitHub integration with AI processing
✅ Real-time insights updates
✅ Cost-effective AI usage

This approach gives you powerful AI capabilities without the complexity of enterprise ML systems. Focus on user value, not AI infrastructure. 