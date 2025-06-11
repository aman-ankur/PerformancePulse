# PerformancePulse - Simple Development Roadmap

## Philosophy: "Build Fast, Learn Fast"

Focus on getting a working product quickly for personal use. Use modern tools to minimize complexity and maximize developer experience.

---

## 2-Week MVP Sprint

### Week 1: Core Foundation (Days 1-7)

**Day 1: Project Setup**
- [ ] `npx create-next-app@latest` with TypeScript + Tailwind + App Router
- [ ] `npx shadcn-ui@latest init` and add essential components
- [ ] Create Supabase project with Google OAuth
- [ ] Set up GitHub repo with proper .env.example

**Day 2-3: Authentication & Basic UI**
- [ ] Google SSO integration with Supabase
- [ ] Simple dashboard layout with sidebar navigation
- [ ] User profile setup and onboarding flow
- [ ] Basic responsive design with dark/light mode

**Day 4-5: Evidence Collection**
- [ ] File upload component with drag-and-drop
- [ ] Manual evidence entry form
- [ ] Evidence list view with filtering
- [ ] Basic CRUD operations for evidence

**Day 6-7: FastAPI Backend Setup**
- [ ] FastAPI project with Supabase integration
- [ ] Claude API integration for text analysis
- [ ] Evidence processing endpoint
- [ ] Deploy to Railway/Render

**Week 1 Goal**: Upload evidence and see it organized nicely

### Week 2: AI Intelligence (Days 8-14)

**Day 8-9: AI Processing**
- [ ] Vector embeddings with pgvector
- [ ] Evidence categorization using Claude
- [ ] Automatic summarization of long content
- [ ] Semantic search across evidence

**Day 10-11: Insights Dashboard**
- [ ] Performance insights generation
- [ ] Strengths and improvement areas
- [ ] Evidence timeline visualization
- [ ] Goal progress tracking (if applicable)

**Day 12-13: External Integrations**
- [ ] GitLab API integration for commits/MRs (investigate Booking.com permissions)
- [ ] Jira integration using MCP server for task details
- [ ] Simple background job for data sync from both sources
- [ ] Evidence deduplication across GitLab and Jira
- [ ] Integration settings page with OAuth flows

**Day 14: Polish & Deploy**
- [ ] UI/UX improvements
- [ ] Error handling and loading states
- [ ] Production deployment
- [ ] Basic analytics setup

**Week 2 Goal**: AI-powered insights from all evidence sources

---

## Tech Stack (Modern & Simple)

**Frontend**
- Next.js 14 (App Router, Server Components)
- TypeScript (strict mode)
- Tailwind CSS + Shadcn/ui
- Framer Motion (animations)

**Backend**
- FastAPI (Python 3.11+)
- Supabase (Auth + Database + Storage + Real-time)
- PostgreSQL with pgvector extension
- Pydantic for data validation

**AI & Search**
- Claude 3.5 Sonnet (Anthropic API)
- Vector embeddings for semantic search
- Background jobs with simple Python asyncio

**Deployment**
- Vercel (Frontend)
- Railway (Backend)
- Supabase Cloud (Database)
- GitHub Actions (CI/CD)

---

## Simplified Data Model

```sql
-- Just 4 core tables
profiles (id, name, role, github_username)
evidence (id, user_id, title, content, source, embedding, tags)
insights (id, user_id, type, content, confidence, evidence_ids)
sync_jobs (id, user_id, source, last_sync, status)
```

---

## Daily Development Pattern

**Morning**: Focus on core features
**Afternoon**: Polish UI and test with real data
**Evening**: Deploy and document progress

**Weekly Review**: What's working? What's not? Adjust next week's plan.

---

## Feature Priorities

### Must Have (Week 1-2)
- [ ] Evidence upload and organization
- [ ] AI-powered categorization and insights using Claude 3.5 Sonnet
- [ ] GitLab integration for automatic evidence (with Booking.com considerations)
- [ ] Jira integration using MCP for task tracking
- [ ] Google SSO authentication only
- [ ] Clean, modern UI that feels good to use

### Nice to Have (Month 2)
- [ ] Multiple GitLab repos support
- [ ] Advanced Jira MCP integrations (epics, sprints)
- [ ] Performance trends over time
- [ ] Export to PDF/Markdown
- [ ] Slack integration for team updates

### Maybe Later
- [ ] Team collaboration features
- [ ] Advanced analytics
- [ ] Mobile app
- [ ] Slack integration

---

## Success Metrics (Personal Project)

**Week 1**: Can upload and organize evidence in < 2 minutes
**Week 2**: AI insights actually help understand performance patterns
**Month 1**: Using it regularly for actual performance tracking
**Month 2**: Sharing with friends/colleagues and getting positive feedback

---

## Keep It Simple Rules

1. **Use existing solutions**: Don't build what already exists
2. **One feature at a time**: Ship working features incrementally  
3. **Real data immediately**: Test with actual GitHub repos from day 1
4. **Beautiful defaults**: Make it look good without customization
5. **Zero config**: Should work out of the box with minimal setup

---

## Architecture Decisions

**Why Next.js 14**: Best developer experience, great for personal projects
**Why Supabase**: Eliminates backend complexity, auth + storage + database in one
**Why FastAPI**: Python ecosystem for AI, fast development, MCP integration support
**Why Claude 3.5 Sonnet**: Superior for structured analysis and categorization tasks
**Why Railway**: Simple deployment, good free tier, Python-friendly

---

## Personal Project Benefits

- **Learning**: Modern tech stack experience
- **Portfolio**: Great project to showcase
- **Utility**: Actually useful for performance reviews
- **Foundation**: Can expand if needed later

---
