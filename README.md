# PerformancePulse

**Manager-Focused Performance Data Aggregation Assistant**

PerformancePulse transforms performance conversation preparation from 3 days of manual data gathering to 30 minutes of structured insights. Built specifically for engineering managers, it automatically aggregates technical contributions from GitLab and Jira while integrating historical context from meeting notes, transcripts, and past discussions.

## 🎯 What It Does

- **Manager-First Design**: Built specifically for manager workflows and team oversight
- **Multi-Source Data Aggregation**: Automatically collects commits, MRs, tickets, and project contributions
- **Historical Context Integration**: Processes meeting transcripts, 1:1 notes, and performance summaries
- **AI-Powered Correlation**: Connects current work with past discussions and development themes
- **Meeting Preparation Engine**: Generates structured discussion points for any meeting type
- **Evidence-Driven Insights**: Every discussion point backed by concrete examples with source links
- **Privacy-First Architecture**: Explicit consent required with granular data controls

## 🔒 Privacy & Consent

- **Explicit Consent Required**: Team members must authorize data access for each source
- **Granular Controls**: Separate permissions for GitLab, Jira, and document uploads
- **Transparent Process**: Clear audit trails showing what data is processed when
- **Easy Revocation**: Team members can revoke access and delete data at any time
- **Manager-Team Boundaries**: Row-level security ensures managers only see their team's data
- **GDPR Compliant**: Built-in data export and deletion workflows

## 📊 Core Capabilities

### Technical Contribution Analysis
- GitLab commits, merge requests, and code review participation
- Jira ticket completion, sprint performance, and project delivery
- Cross-platform correlation (matching tickets to code changes)
- AI-powered categorization by contribution type and impact level

### Historical Context Management
- Meeting transcript processing and theme extraction
- 1:1 summary analysis and development pattern recognition
- Slack thread integration for collaboration insights
- Performance summary correlation with current work

### Meeting Preparation Intelligence
- **Weekly 1:1s**: Recent work with historical context integration
- **Monthly Reviews**: Pattern recognition and growth trajectory analysis
- **Quarterly Assessments**: Comprehensive contribution portfolio with evidence
- **Annual Reviews**: Long-term development themes and career progression

### Manager Dashboard Features
- Team overview with activity summaries and consent status
- Individual team member profiles with contribution timelines
- Meeting preparation workflow with configurable focus areas
- Export capabilities (PDF reports, structured summaries)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (for Next.js frontend)
- Python 3.11+ (for FastAPI backend with AI processing)
- GitLab access token (for automated data collection)
- Jira workspace access (for ticket and project data)
- Claude API key (for AI analysis and correlation)
- Google OAuth setup (for manager authentication)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/PerformancePulse.git
cd PerformancePulse

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration
```

### Environment Setup

```bash
# Frontend (.env.local)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000

# Backend (.env)
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key
ANTHROPIC_API_KEY=your_claude_api_key
GITLAB_MCP_TOKEN=your_gitlab_access_token
JIRA_MCP_TOKEN=your_jira_access_token
```

### Running Locally

```bash
# Start the backend (AI processing and data collection)
cd backend
uvicorn main:app --reload

# Start the frontend (manager dashboard) in another terminal
npm run dev
```

Visit `http://localhost:3000` to access the manager dashboard.

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Next.js 14 with App Router, TypeScript, and Tailwind CSS
- **UI Components**: Shadcn/ui optimized for manager workflows
- **Backend**: Python FastAPI with async processing and Pydantic validation
- **Database**: Supabase (PostgreSQL + Auth + Storage + Real-time + Vector search)
- **AI**: Claude 3.5 Sonnet for evidence correlation and meeting preparation
- **Integrations**: GitLab MCP and Jira MCP servers for automated data collection
- **Deployment**: Vercel (Frontend) + Render (Backend) + Supabase Cloud

### System Flow
```
Manager Dashboard (Next.js + Shadcn/ui)
↕ Real-time team data updates
Supabase (Auth + Team RLS + Vector Search)
↕ Evidence aggregation and processing
AI Correlation Engine (FastAPI + Claude)
↕ Multi-source data collection
GitLab MCP + Jira MCP + Document Uploads
```

## 📁 Project Structure

```
PerformancePulse/
├── app/                    # Next.js app router pages
│   ├── (dashboard)/       # Manager dashboard routes
│   ├── api/               # Frontend API routes
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── ui/               # Shadcn/ui base components
│   ├── manager/          # Manager-specific components
│   └── evidence/         # Evidence display components
├── lib/                  # Utilities and configurations
│   ├── supabase.ts       # Database client
│   ├── ai.ts             # AI service integration
│   └── utils.ts          # Helper functions
├── backend/              # Python FastAPI backend
│   ├── services/         # Integration services
│   │   ├── gitlab_mcp.py # GitLab data collection
│   │   ├── jira_mcp.py   # Jira data collection
│   │   └── ai_service.py # Claude API integration
│   ├── models/           # Pydantic data models
│   └── api/              # API endpoints
├── memory-bank/          # Project documentation
│   ├── projectbrief.md   # Vision and requirements
│   ├── system-architecture.md # Technical architecture
│   ├── data-models.md    # Database schema
│   ├── ai-integration-plan.md # AI features
│   └── development-roadmap.md # Implementation plan
└── docs/                 # Additional documentation
```

## 🔧 Key Features

### Manager-Focused Workflows
- **Team Management**: Hierarchical team structure with consent tracking
- **Evidence Browser**: Organized view of all team member contributions
- **Meeting Prep Engine**: AI-generated preparation for any meeting type
- **Historical Integration**: Correlation between current work and past discussions
- **Privacy Dashboard**: Consent management and audit trails

### AI-Powered Intelligence
- **Evidence Correlation**: Match Jira tickets to GitLab MRs automatically
- **Pattern Recognition**: Identify consistent strengths and development areas
- **Historical Analysis**: Process uploaded documents for themes and insights
- **Discussion Generation**: Create structured talking points with evidence backing
- **Export Capabilities**: Professional PDF reports and structured summaries

### Multi-Source Integration
- **GitLab**: Commits, merge requests, code reviews, project contributions
- **Jira**: Tickets, sprint performance, project delivery, collaboration patterns
- **Document Uploads**: Meeting transcripts, 1:1 notes, Slack exports, performance summaries
- **Manual Entries**: Additional context and observations

## 🗺️ Development Roadmap

### Phase 1: Core Data Pipeline (Weeks 1-2) ✅
- [x] Team management and authentication system
- [x] GitLab and Jira MCP integration
- [x] Basic evidence collection and categorization
- [x] Document upload and processing pipeline

### Phase 2: AI Analysis & Meeting Preparation (Weeks 3-4)
- [ ] Claude API integration for evidence correlation
- [ ] Historical context analysis and pattern recognition
- [ ] Meeting preparation engine for different meeting types
- [ ] Evidence-context correlation with confidence scoring

### Phase 3: Production Polish (Weeks 5-6)
- [ ] Advanced UI/UX with mobile responsiveness
- [ ] Privacy dashboard and consent management
- [ ] Export capabilities (PDF, Markdown)
- [ ] Performance optimization and monitoring

### Future Enhancements
- [ ] Slack integration for additional collaboration context
- [ ] Advanced analytics and team-level insights
- [ ] Calendar integration for meeting scheduling
- [ ] Mobile app for on-the-go access


## 🆘 Support

- **Documentation**: Comprehensive specs in `/memory-bank` folder
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join our community discussions for Q&A

---

**Note**: PerformancePulse is designed to support performance conversations, not replace them. It provides factual data and historical context to help managers and team members have more informed, evidence-based discussions about contributions, growth, and career development.
