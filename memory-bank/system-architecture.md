# PerformancePulse - Simple System Architecture

## Philosophy: "Minimal Complexity, Maximum Value"

Build the simplest system that works. Use managed services to eliminate operational overhead. Focus on features, not infrastructure.

---

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Next.js App   │◄──►│    Supabase     │◄──►│   FastAPI       │
│   (Frontend)    │    │  (Database)     │    │  (AI Backend)   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
   User Browser            Auth + Data              Claude API
                          Real-time                GitHub API
                          File Storage             Background Jobs
```

## Core Components

### Frontend: Next.js 14 App
**Purpose**: Beautiful, responsive UI for evidence management

**Key Features**:
- Server Components for fast initial loads
- Client Components for interactions
- Real-time updates via Supabase subscriptions
- File upload with drag-and-drop
- Responsive design with dark/light theme

**Simple Structure**:
```
app/
├── (dashboard)/
│   ├── page.tsx           # Main dashboard
│   ├── evidence/          # Evidence management
│   ├── insights/          # AI insights
│   └── settings/          # User settings
├── auth/                  # Authentication pages
├── api/                   # API routes (minimal)
└── components/            # Reusable UI components
```

### Database: Supabase (PostgreSQL)
**Purpose**: Single source of truth for all data

**Why Supabase**:
- Built-in authentication (Google OAuth)
- Row Level Security (automatic data isolation)
- Real-time subscriptions (live updates)
- Vector search with pgvector
- File storage with CDN
- No server management needed

**Core Tables**:
```sql
-- User profiles (extends auth.users)
profiles (
  id, full_name, avatar_url, github_username,
  role, created_at, updated_at
)

-- Performance evidence
evidence (
  id, user_id, title, content, source, source_url,
  category, tags, embedding, metadata,
  created_at, updated_at
)

-- AI-generated insights
insights (
  id, user_id, type, title, content,
  confidence, evidence_ids, validated,
  created_at, updated_at
)

-- Background sync jobs
sync_jobs (
  id, user_id, source, last_sync_at,
  status, error_message, metadata
)
```

### Backend: FastAPI (Python)
**Purpose**: AI processing and external integrations

**Core Responsibilities**:
- Process evidence with Claude API
- Generate embeddings for semantic search
- Sync data from GitHub/Jira
- Run background jobs
- Provide AI insights

**Simple Structure**:
```
backend/
├── main.py               # FastAPI app entry point
├── routers/
│   ├── evidence.py       # Evidence processing
│   ├── insights.py       # AI insights generation
│   └── sync.py           # External data sync
├── services/
│   ├── claude.py         # Claude API client
│   ├── gitlab.py         # GitLab integration
│   ├── jira_mcp.py       # Jira MCP integration
│   └── embeddings.py     # Vector embeddings
└── models/               # Pydantic models
```

---

## Data Flow (Simplified)

### Evidence Collection Flow
```
1. User uploads file/text → Next.js
2. Next.js saves to Supabase → Database
3. Webhook triggers FastAPI → AI processing
4. Claude analyzes content → Insights generated
5. Results saved to Supabase → Real-time update to UI
```

### External Sync Flow
```
1. Background job runs → FastAPI
2. Fetch GitLab commits/MRs + Jira tasks → APIs/MCP
3. Process with Claude → Categorize and summarize
4. Save as evidence → Supabase
5. Generate insights → Claude API
6. Update dashboard → Real-time to user
```

---

## AI Integration (Simple)

### Claude API Usage
```python
# Simple Claude client
class ClaudeService:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def categorize_evidence(self, content: str) -> dict:
        """Categorize evidence into predefined categories"""
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"Categorize this work evidence:\n\n{content}"
            }]
        )
        return parse_response(response.content)
    
    async def generate_insights(self, evidence_list: list) -> list:
        """Generate performance insights from evidence"""
        # Simple prompt engineering for insights
        pass
```

### Vector Search (Simple)
```sql
-- Semantic search for evidence
SELECT 
    id, title, content,
    1 - (embedding <=> $1) as similarity
FROM evidence 
WHERE user_id = $2 
    AND 1 - (embedding <=> $1) > 0.7
ORDER BY embedding <=> $1
LIMIT 20;
```

---

## External Integrations

### GitLab Integration (Booking.com)
```python
# GitLab sync with corporate considerations
async def sync_gitlab_activity(user_id: str, gitlab_token: str):
    """Sync recent GitLab activity as evidence"""
    
    # Configure for Booking.com's GitLab instance
    gitlab_client = gitlab.Gitlab(
        url="https://gitlab.booking.com",  # Adjust to actual URL
        private_token=gitlab_token
    )
    
    # Get recent commits and merge requests
    projects = gitlab_client.projects.list(membership=True, archived=False)
    evidence_items = []
    
    for project in projects:
        # Get user's recent commits
        commits = project.commits.list(
            author_email=user_email,
            since=last_sync_date.isoformat()
        )
        
        for commit in commits:
            evidence_items.append({
                'title': f"GitLab: {commit.title[:50]}...",
                'content': f"{commit.message}\nProject: {project.name}",
                'source': 'gitlab',
                'source_url': commit.web_url,
                'category': 'technical'
            })
    
    await save_evidence_batch(user_id, evidence_items)

### Jira Integration (MCP Server)
```python
# Jira MCP integration for rich task data
async def sync_jira_activity(user_id: str):
    """Sync Jira activity using MCP server connection"""
    
    # Use MCP client to connect to Jira
    from mcp import Client
    
    mcp_client = Client("jira-mcp-server")
    
    # Get user's assigned and completed issues
    jql_query = f'assignee = currentUser() AND updated >= -30d'
    
    issues = await mcp_client.call_tool("search_issues", {
        "jql": jql_query,
        "fields": ["summary", "description", "status", "project", "issuetype"]
    })
    
    evidence_items = []
    for issue in issues:
        evidence_items.append({
            'title': f"{issue['key']}: {issue['fields']['summary']}",
            'content': f"Status: {issue['fields']['status']['name']}\n{issue['fields']['description'][:200]}...",
            'source': 'jira',
            'source_url': f"https://booking.atlassian.net/browse/{issue['key']}",
            'category': 'delivery'
        })
    
    await save_evidence_batch(user_id, evidence_items)
```

---

## Deployment (Zero-Config)

### Frontend: Vercel
- Automatic deployments from Git
- Edge functions for API routes
- Global CDN
- Zero configuration needed

### Backend: Railway
- Automatic Python deployments
- Built-in environment variables
- Automatic HTTPS
- Simple scaling

### Database: Supabase Cloud
- Managed PostgreSQL
- Automatic backups
- Global edge network
- Built-in monitoring

---

## Security (Built-in)

### Authentication  
- Google SSO only (via Supabase Auth)
- JWT tokens with automatic refresh
- No password management needed
- Simple one-click authentication flow

### Data Access
- Row Level Security policies
- Users only see their own data
- Managers can see reports' data (if configured)

### API Security
- CORS properly configured
- Rate limiting on FastAPI
- API keys in environment variables

---

## Monitoring (Simple)

### Basic Metrics
- Supabase dashboard for database metrics
- Vercel analytics for frontend performance
- Railway logs for backend monitoring
- Simple error tracking with Sentry (optional)

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

---

## Development Workflow

### Local Development
```bash
# Frontend
npm run dev               # Next.js on localhost:3000

# Backend  
uvicorn main:app --reload # FastAPI on localhost:8000

# Database
# Use Supabase cloud instance (no local setup needed)
```

### Testing Strategy
- Jest for frontend unit tests
- Playwright for E2E testing
- Pytest for backend testing
- Manual testing with real data

---

## Why This Architecture Works

**Simple**: Only 3 main components to manage
**Scalable**: Each component can scale independently
**Reliable**: Using proven, managed services
**Fast**: Modern tech stack with good performance
**Maintainable**: Clear separation of concerns
**Cost-effective**: Great free tiers, pay-as-you-grow

---

## What We're NOT Building

❌ Complex microservices architecture
❌ Custom authentication system  
❌ Manual database management
❌ Complex CI/CD pipelines
❌ Custom monitoring solutions
❌ Multi-tenant architecture
❌ Advanced caching layers

## What We ARE Building

✅ Simple, modern full-stack app
✅ AI-powered insights that actually help
✅ Beautiful, responsive user interface
✅ Automatic data collection from GitLab and Jira
✅ Zero-maintenance deployment
✅ Great developer experience 