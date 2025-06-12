# PerformancePulse - Manager-Focused Deployment Strategy

## Philosophy: "Deploy Early, Deploy Often"

Use modern platforms with zero-config deployments. Focus on shipping manager efficiency features, not managing infrastructure.

---

## Deployment Stack (Zero-Config)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│    Vercel       │    │     Render      │    │   Supabase      │
│  (Frontend)     │    │   (Backend)     │    │  (Database)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
   Next.js App              FastAPI App              PostgreSQL
   Automatic CDN            Python Runtime           Auth + Storage
   Edge Functions           Auto-scaling             Real-time + Vector
```

---

## Frontend Deployment: Vercel

### Why Vercel for Manager Dashboards
- **Zero Configuration**: Automatic builds from Git
- **Global CDN**: Fast loading for distributed teams
- **Edge Functions**: API routes for team data aggregation
- **Preview Deployments**: Every PR gets a URL for manager testing
- **Analytics**: Built-in performance monitoring for dashboard usage
- **Free Tier**: Generous limits for team management tools

### Setup (5 minutes)
```bash
# 1. Connect GitHub repo to Vercel
# 2. Configure environment variables for manager workflows
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
NEXT_PUBLIC_API_URL=your-render-backend-url

# 3. Deploy automatically happens on git push
git push origin main
```

### Vercel Configuration for Team Management
```json
// vercel.json
{
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 30
    }
  },
  "regions": ["iad1"],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "*"
        }
      ]
    }
  ]
}
```

---

## Backend Deployment: Render

### Why Render for AI Processing
- **Simple Python Deploys**: Automatic FastAPI detection
- **Built-in Load Balancing**: Handle multiple manager requests
- **Environment Variables**: Secure AI API key management
- **Automatic HTTPS**: SSL certificates for secure team data
- **Health Checks**: Monitor AI processing pipeline
- **Affordable**: Great pricing for AI-intensive workloads
- **Better Performance**: More reliable than Railway for AI processing

### Setup (10 minutes)
```bash
# 1. Connect GitHub repo to Render dashboard
# 2. Create new Web Service
# 3. Configure build and start commands:

# Build Command:
pip install -r requirements.txt

# Start Command:
uvicorn main:app --host 0.0.0.0 --port $PORT

# 4. Add environment variables in Render dashboard
ANTHROPIC_API_KEY=your-claude-key
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_KEY=your-service-key
GITLAB_MCP_TOKEN=your-gitlab-token
JIRA_MCP_TOKEN=your-jira-token
```

### Render Configuration
```yaml
# render.yaml (optional)
services:
  - type: web
    name: performancepulse-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

### Requirements.txt for Manager-Focused Features
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
anthropic==0.7.8
supabase==2.0.3
python-multipart==0.0.6
httpx==0.25.2
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
aiofiles==23.2.1
python-docx==1.1.0
PyPDF2==3.0.1
pandas==2.1.4
numpy==1.24.3
scikit-learn==1.3.2
```

---

## Database: Supabase Cloud

### Why Supabase for Team Data Management
- **Managed PostgreSQL**: No server management for team databases
- **Built-in Auth**: Google OAuth for manager and team member access
- **Row Level Security**: Team-based data isolation
- **Real-time**: Live updates for manager dashboards
- **Vector Search**: pgvector for evidence correlation
- **File Storage**: Document uploads with CDN
- **Generous Free Tier**: Perfect for team management tools

### Setup for Team Management (5 minutes)
```bash
# 1. Create project at supabase.com
# 2. Enable Google OAuth in Auth settings
# 3. Add your domain to redirect URLs
# 4. Configure Row Level Security for team isolation
# 5. Copy connection details to apps
```

### Database Configuration for Manager Workflows
```sql
-- Enable required extensions for evidence correlation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Enable Row Level Security for team isolation
ALTER DATABASE postgres SET "app.jwt_secret" TO 'your-jwt-secret';

-- Configure real-time for manager dashboards
ALTER PUBLICATION supabase_realtime ADD TABLE team_members;
ALTER PUBLICATION supabase_realtime ADD TABLE evidence_items;
ALTER PUBLICATION supabase_realtime ADD TABLE meeting_preparations;
ALTER PUBLICATION supabase_realtime ADD TABLE data_consents;

-- Create RLS policies for manager-team access
CREATE POLICY "Managers can view their team members" ON team_members
  FOR SELECT USING (manager_id = auth.uid());

CREATE POLICY "Team members can view their own data" ON evidence_items
  FOR SELECT USING (team_member_id IN (
    SELECT id FROM team_members WHERE user_id = auth.uid()
  ));
```

---

## Environment Variables Management

### Development (.env.local)
```bash
# Supabase for team data
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-local-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-local-service-key

# AI for evidence correlation
ANTHROPIC_API_KEY=your-claude-key

# MCP Servers for data collection
GITLAB_MCP_TOKEN=your-gitlab-token
JIRA_MCP_TOKEN=your-jira-token

# Backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Manager workflow configuration
NEXT_PUBLIC_DEFAULT_MEETING_PREP_DAYS=7
NEXT_PUBLIC_EVIDENCE_RETENTION_MONTHS=24
```

### Production (Vercel + Render)
```bash
# Frontend (Vercel) - Manager Dashboard
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-prod-anon-key
NEXT_PUBLIC_API_URL=https://your-app.onrender.com
NEXT_PUBLIC_DEFAULT_MEETING_PREP_DAYS=7
NEXT_PUBLIC_EVIDENCE_RETENTION_MONTHS=24

# Backend (Render) - AI Processing Pipeline
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-prod-service-key
ANTHROPIC_API_KEY=your-claude-key
GITLAB_MCP_TOKEN=your-gitlab-token
JIRA_MCP_TOKEN=your-jira-token
OPENAI_API_KEY=your-openai-key
```

---

## Deployment Workflow for Manager Features

### Automatic Deployments
```bash
# Frontend: Vercel auto-deploys manager dashboard on git push
git push origin main
# ✅ Manager dashboard deployed to https://your-app.vercel.app

# Backend: Render auto-deploys AI processing on git push
git push origin main
# ✅ AI backend deployed to https://your-app.onrender.com

# Database: Always available for team data
# ✅ Team database running at https://your-project.supabase.co
```

### Feature Development for Manager Workflows
```bash
# 1. Create feature branch for manager feature
git checkout -b feature/team-member-consent-ui

# 2. Develop and test locally with sample team data
npm run dev

# 3. Push for preview deployment
git push origin feature/team-member-consent-ui
# ✅ Vercel creates preview URL for manager testing

# 4. Merge to main for production
git checkout main
git merge feature/team-member-consent-ui
git push origin main
# ✅ Automatic production deployment
```

---

## Monitoring & Health Checks for Manager Workflows

### Manager-Focused Health Checks
```typescript
// Frontend: app/api/health/route.ts
export async function GET() {
  return Response.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version,
    features: {
      teamManagement: 'active',
      evidenceCorrelation: 'active',
      meetingPreparation: 'active'
    }
  })
}

// Backend: main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "ai_services": {
            "claude": "connected",
            "embeddings": "connected"
        },
        "data_sources": {
            "gitlab_mcp": "connected",
            "jira_mcp": "connected"
        }
    }
```

### Built-in Monitoring for Team Management
- **Vercel Analytics**: Manager dashboard usage and performance
- **Render Metrics**: AI processing times and success rates
- **Supabase Dashboard**: Team database performance and consent tracking
- **Console Logs**: Evidence processing and correlation activities

---

## Security & Performance for Team Data

### Security (Built-in for Team Management)
- **HTTPS**: Automatic SSL certificates for secure team data
- **Environment Variables**: Secure storage of AI API keys and MCP tokens
- **Row Level Security**: Team-based database access control
- **JWT Authentication**: Supabase handles manager and team member tokens
- **CORS**: Configured in FastAPI for manager dashboard access
- **Consent Management**: Granular data access controls per team member

### Performance (Automatic for Manager Workflows)
- **CDN**: Global content delivery for distributed teams
- **Edge Functions**: Regional processing for team data aggregation
- **Connection Pooling**: Database optimization for team queries
- **Build Optimization**: Next.js automatic optimization for dashboard loading
- **AI Caching**: Render persistent storage for processed evidence

---

## Cost Management for Team Tools

### Free Tier Limits
```bash
# Vercel Free Plan (Manager Dashboard)
# - 100GB bandwidth/month (sufficient for team dashboards)
# - 1000 builds/month (plenty for feature development)
# - Unlimited deployments

# Render Free Plan (AI Processing)
# - 750 hours/month free compute
# - Automatic sleep after 15 minutes of inactivity
# - Perfect for development and small teams

# Supabase Free Plan (Team Database)
# - 2 projects (development + production)
# - 50MB database storage (sufficient for team metadata)
# - 1GB file storage (for document uploads)
# - 2GB bandwidth (adequate for team usage)
```

### Scaling Strategy for Growing Teams
```bash
# When managing larger teams:
# 1. Vercel Pro: $20/month (more bandwidth for distributed teams)
# 2. Render Starter: $7/month (always-on service, no sleep)
# 3. Supabase Pro: $25/month (more storage for evidence and documents)

# All platforms have simple upgrade paths as team size grows
```

---

## Backup & Recovery for Team Data

### Automatic Backups
- **Team Database**: Supabase daily backups with point-in-time recovery
- **Code**: Git version control + GitHub remote
- **Manager Dashboards**: Vercel build history and rollbacks
- **Evidence Processing**: Render deployment history

### Manual Exports for Compliance
```bash
# Team database export (for compliance audits)
# Available in Supabase dashboard
# SQL dump or CSV format for evidence and consent records

# Code backup
git push origin main  # Always backed up to GitHub

# Document storage backup
# Supabase Storage API for bulk document export
```

---

## Development vs Production for Manager Tools

### Local Development
```bash
# Start all services for manager workflow testing
npm run dev                    # Manager dashboard on :3000
uvicorn main:app --reload      # AI processing on :8000
# Database: Use Supabase cloud (no local setup needed)

# Test with sample team data
# Mock GitLab/Jira responses for development
```

### Production Deployment
```bash
# Single command deployment for manager tools
git push origin main

# Results in:
# ✅ Manager Dashboard: https://your-app.vercel.app
# ✅ AI Processing: https://your-app.onrender.com
# ✅ Team Database: https://your-project.supabase.co
```

---

## MCP Server Integration for Data Collection

### GitLab MCP Configuration
```bash
# Environment variables for GitLab data collection
GITLAB_MCP_TOKEN=your-gitlab-personal-access-token
GITLAB_MCP_URL=https://gitlab.com/api/v4

# Render environment configuration
# Add these in Render dashboard for secure token management
```

### Jira MCP Configuration
```bash
# Environment variables for Jira data collection
JIRA_MCP_TOKEN=your-jira-api-token
JIRA_MCP_URL=https://your-company.atlassian.net
JIRA_MCP_EMAIL=your-jira-email

# Render environment configuration
# Add these in Render dashboard for secure integration
```

---

## What We're NOT Doing

❌ Complex Kubernetes deployments for team tools
❌ Manual server management for AI processing
❌ Custom CI/CD pipelines for manager features
❌ Infrastructure as Code complexity
❌ Multi-environment complexity for team data
❌ Load balancer configuration
❌ SSL certificate management
❌ Docker orchestration for simple team tools

## What We ARE Doing

✅ Zero-config deployments for manager efficiency
✅ Automatic HTTPS and CDN for secure team data
✅ Built-in monitoring for AI processing and team usage
✅ Simple environment management for MCP tokens
✅ Preview deployments for manager feature testing
✅ Automatic scaling for growing teams
✅ Focus on manager workflows, not infrastructure
✅ Cost-effective team management tool hosting
✅ Privacy-compliant team data handling
✅ Seamless MCP integration for evidence collection

This deployment strategy is specifically optimized for PerformancePulse's manager-focused data aggregation platform, ensuring reliable AI processing, secure team data handling, and efficient manager workflows while keeping infrastructure management minimal. 