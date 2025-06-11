# PerformancePulse - Simple Deployment Strategy

## Philosophy: "Deploy Early, Deploy Often"

Use modern platforms with zero-config deployments. Focus on shipping features, not managing infrastructure.

---

## Deployment Stack (Zero-Config)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│    Vercel       │    │    Railway      │    │   Supabase      │
│  (Frontend)     │    │   (Backend)     │    │  (Database)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
   Next.js App              FastAPI App              PostgreSQL
   Automatic CDN            Python Runtime           Auth + Storage
   Edge Functions           Auto-scaling             Real-time
```

---

## Frontend Deployment: Vercel

### Why Vercel
- **Zero Configuration**: Automatic builds from Git
- **Global CDN**: Fast loading worldwide
- **Edge Functions**: API routes at the edge
- **Preview Deployments**: Every PR gets a URL
- **Analytics**: Built-in performance monitoring
- **Free Tier**: Generous limits for personal projects

### Setup (5 minutes)
```bash
# 1. Connect GitHub repo to Vercel
# 2. Configure environment variables
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key

# 3. Deploy automatically happens on git push
git push origin main
```

### Vercel Configuration
```json
// vercel.json (optional)
{
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 30
    }
  },
  "regions": ["iad1"]
}
```

---

## Backend Deployment: Railway

### Why Railway
- **Simple Python Deploys**: Automatic detection
- **Built-in Databases**: If needed later
- **Environment Variables**: Easy management
- **Automatic HTTPS**: SSL certificates included
- **Logs & Monitoring**: Built-in observability
- **Affordable**: Great pricing for small projects

### Setup (10 minutes)
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and create project
railway login
railway init

# 3. Add environment variables
railway variables set ANTHROPIC_API_KEY=your-claude-key
railway variables set SUPABASE_URL=your-supabase-url
railway variables set SUPABASE_SERVICE_KEY=your-service-key

# 4. Deploy
railway up
```

### Railway Configuration
```toml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Requirements.txt
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
anthropic==0.7.8
supabase==2.0.3
python-multipart==0.0.6
httpx==0.25.2
```

---

## Database: Supabase Cloud

### Why Supabase Cloud
- **Managed PostgreSQL**: No server management
- **Built-in Auth**: Google OAuth included
- **Real-time**: WebSocket connections
- **File Storage**: CDN included
- **Vector Search**: pgvector extension
- **Generous Free Tier**: Perfect for personal projects

### Setup (5 minutes)
```bash
# 1. Create project at supabase.com
# 2. Enable Google OAuth in Auth settings
# 3. Add your domain to redirect URLs
# 4. Copy connection details to apps
```

### Database Configuration
```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Enable Row Level Security
ALTER DATABASE postgres SET "app.jwt_secret" TO 'your-jwt-secret';

-- Configure real-time
ALTER PUBLICATION supabase_realtime ADD TABLE evidence;
ALTER PUBLICATION supabase_realtime ADD TABLE insights;
```

---

## Environment Variables Management

### Development (.env.local)
```bash
# Supabase
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-local-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-local-service-key

# AI
ANTHROPIC_API_KEY=your-claude-key

# GitHub (for integration)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# Backend URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production (Vercel + Railway)
```bash
# Frontend (Vercel)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-prod-anon-key
NEXT_PUBLIC_API_URL=https://your-app.railway.app

# Backend (Railway)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-prod-service-key
ANTHROPIC_API_KEY=your-claude-key
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

---

## Deployment Workflow

### Automatic Deployments
```bash
# Frontend: Vercel auto-deploys on git push to main
git push origin main
# ✅ Frontend deployed to https://your-app.vercel.app

# Backend: Railway auto-deploys on git push to main  
git push origin main
# ✅ Backend deployed to https://your-app.railway.app

# Database: Always available
# ✅ Database running at https://your-project.supabase.co
```

### Feature Development
```bash
# 1. Create feature branch
git checkout -b feature/evidence-upload

# 2. Develop and test locally
npm run dev

# 3. Push for preview deployment
git push origin feature/evidence-upload
# ✅ Vercel creates preview URL automatically

# 4. Merge to main for production
git checkout main
git merge feature/evidence-upload
git push origin main
# ✅ Automatic production deployment
```

---

## Monitoring & Health Checks

### Simple Health Checks
```typescript
// Frontend: app/api/health/route.ts
export async function GET() {
  return Response.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version
  })
}

// Backend: main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

### Built-in Monitoring
- **Vercel Analytics**: Page views and Web Vitals
- **Railway Metrics**: CPU, memory, response times  
- **Supabase Dashboard**: Database performance
- **Console Logs**: Automatically captured

---

## Security & Performance

### Security (Built-in)
- **HTTPS**: Automatic SSL certificates
- **Environment Variables**: Secure storage
- **Row Level Security**: Database access control
- **JWT Authentication**: Supabase handles tokens
- **CORS**: Configured in FastAPI

### Performance (Automatic)
- **CDN**: Global content delivery
- **Edge Functions**: Regional processing
- **Connection Pooling**: Database optimization
- **Build Optimization**: Next.js automatic optimization

---

## Cost Management

### Free Tier Limits
```bash
# Vercel Free Plan
# - 100GB bandwidth/month
# - 1000 builds/month
# - Unlimited deployments

# Railway Free Plan
# - $5/month after free trial
# - Generous compute limits

# Supabase Free Plan  
# - 2 projects
# - 50MB database storage
# - 1GB file storage
# - 2GB bandwidth
```

### Scaling Strategy
```bash
# When you need more resources:
# 1. Vercel Pro: $20/month (more bandwidth)
# 2. Railway: Pay-per-use scaling
# 3. Supabase Pro: $25/month (more storage/compute)

# All platforms have simple upgrade paths
```

---

## Backup & Recovery

### Automatic Backups
- **Database**: Supabase daily backups with point-in-time recovery
- **Code**: Git version control + GitHub remote
- **Deployments**: Vercel build history and rollbacks

### Manual Exports
```bash
# Database export
# Available in Supabase dashboard
# SQL dump or CSV format

# Code backup
git push origin main  # Always backed up to GitHub
```

---

## Development vs Production

### Local Development
```bash
# Start all services
npm run dev                    # Frontend on :3000
uvicorn main:app --reload      # Backend on :8000
# Database: Use Supabase cloud (no local setup)
```

### Production Deployment
```bash
# Single command deployment
git push origin main

# Results in:
# ✅ Frontend: https://your-app.vercel.app
# ✅ Backend: https://your-app.railway.app  
# ✅ Database: https://your-project.supabase.co
```

---

## What We're NOT Doing

❌ Complex Kubernetes deployments
❌ Manual server management
❌ Custom CI/CD pipelines
❌ Infrastructure as Code
❌ Multi-environment complexity
❌ Load balancer configuration
❌ SSL certificate management
❌ Docker orchestration

## What We ARE Doing

✅ Zero-config deployments
✅ Automatic HTTPS and CDN
✅ Built-in monitoring and logs
✅ Simple environment management
✅ Preview deployments for features
✅ Automatic scaling
✅ Focus on features, not infrastructure
✅ Cost-effective personal project hosting

This approach lets you deploy in minutes and focus entirely on building features rather than managing infrastructure. 