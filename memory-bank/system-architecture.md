# PerformancePulse - Complete System Architecture
## Data Aggregation + Historical Context Management for Performance Conversations

---

## 🎯 Project Overview

**PerformancePulse** is a data aggregation tool that automatically collects and organizes engineering contributions from GitLab, Jira, and other sources to help managers prepare for 1:1s, performance reviews, and career discussions. Instead of spending 2-3 days manually gathering evidence across multiple systems, managers get structured insights and discussion points in 30 minutes.

### Core Value Proposition
- **Time Savings**: From 3 days to 30 minutes for performance data gathering
- **Evidence-Driven**: Every insight backed by concrete examples with source links
- **Historical Context**: Integrates past meeting notes, summaries, and discussions
- **Privacy-First**: Explicit consent for all data access with full transparency

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Manager Dashboard                        │
│               (Next.js + Tailwind)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                  Supabase Platform                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   Auth +    │ │  PostgreSQL │ │    File Storage     │   │
│  │    RLS      │ │   Database  │ │   + CDN Delivery    │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                FastAPI Backend                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ Data        │ │ Document    │ │   AI Analysis       │   │
│  │ Collectors  │ │ Processor   │ │   & Correlation     │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│              External Systems & Storage                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │ GitLab MCP  │ │  Jira MCP   │ │ Manual Uploads      │   │
│  │ Server      │ │  Server     │ │ (Transcripts, etc.) │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Product Scope

### ✅ Core Features
- **Multi-Source Data Collection**: GitLab, Jira, document uploads with user consent
- **Intelligent Correlation**: Match tickets to MRs, timeline analysis, contribution patterns
- **Performance Meeting Prep**: Generate structured discussion materials for 1:1s, quarterlies, annuals
- **Manager Dashboard**: Clean interface to track team member progress and generate insights
- **Evidence Portfolio**: Organized view of each team member's contributions over time
- **Historical Context Integration**: Upload and correlate meeting transcripts, summaries, Slack threads
- **Export Capabilities**: PDF reports, structured data for performance discussions

### ❌ What We Don't Build
- Review writing or editing tools
- Goal setting or tracking systems
- HR workflow integration
- Employee self-service features
- Real-time collaboration tools
- Performance ratings or scoring

---

## 🗄️ Database Schema

```sql
-- Team members and their configurations
CREATE TABLE team_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR NOT NULL,
  email VARCHAR NOT NULL UNIQUE,
  role VARCHAR NOT NULL,
  level VARCHAR NOT NULL, -- 'F', 'G', 'H', etc.
  target_level VARCHAR,
  manager_id UUID REFERENCES team_members(id),
  team VARCHAR,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Data source consent and configuration
CREATE TABLE data_consents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_member_id UUID REFERENCES team_members(id),
  source_type VARCHAR NOT NULL, -- 'gitlab', 'jira', 'manual_upload'
  consented BOOLEAN DEFAULT FALSE,
  config_data JSONB, -- GitLab URLs, Jira projects, etc.
  last_sync_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- All evidence items (automated + manual)
CREATE TABLE evidence_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_member_id UUID REFERENCES team_members(id),
  source VARCHAR NOT NULL, -- 'gitlab', 'jira', 'meeting_transcript', 'slack_thread', 'manual'
  source_type VARCHAR NOT NULL, -- 'commit', 'mr', 'ticket', 'transcript', 'summary', 'thread'
  title VARCHAR NOT NULL,
  content TEXT,
  file_url VARCHAR, -- Supabase storage URL for uploaded files
  source_url VARCHAR, -- Original URL (for GitLab/Jira items)
  category VARCHAR, -- 'technical', 'collaboration', 'meeting', 'feedback'
  tags TEXT[], -- Searchable tags
  metadata JSONB, -- Flexible metadata storage
  evidence_date TIMESTAMP, -- When the evidence was created
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Historical context documents (like @/sg folder)
CREATE TABLE context_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_member_id UUID REFERENCES team_members(id),
  document_type VARCHAR NOT NULL, -- 'meeting_summary', '1_1_notes', 'assessment', 'transcript'
  title VARCHAR NOT NULL,
  content TEXT,
  file_url VARCHAR, -- Supabase storage URL
  summary TEXT, -- AI-generated summary for quick reference
  key_themes TEXT[], -- Extracted themes for correlation
  date_range_start DATE, -- Time period this document covers
  date_range_end DATE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Meeting preparation sessions
CREATE TABLE meeting_preparations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_member_id UUID REFERENCES team_members(id),
  manager_id UUID REFERENCES team_members(id),
  meeting_type VARCHAR NOT NULL, -- 'weekly_1_1', 'monthly', 'quarterly', 'annual'
  timeframe_start DATE,
  timeframe_end DATE,
  generated_content JSONB, -- Structured insights and discussion points
  historical_context_used UUID[], -- References to context_documents used
  evidence_items_used UUID[], -- References to evidence_items used
  exported_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Data sync jobs and status
CREATE TABLE sync_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_member_id UUID REFERENCES team_members(id),
  source_type VARCHAR NOT NULL,
  status VARCHAR DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
  last_run_at TIMESTAMP,
  next_run_at TIMESTAMP,
  error_message TEXT,
  items_processed INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_evidence_items_team_member_date ON evidence_items(team_member_id, evidence_date);
CREATE INDEX idx_context_documents_team_member_date ON context_documents(team_member_id, date_range_start, date_range_end);
CREATE INDEX idx_evidence_items_category ON evidence_items(category);
CREATE INDEX idx_context_documents_themes ON context_documents USING GIN(key_themes);
```

---

## 🎨 User Interface Design

### Manager Dashboard Layout
```
┌─────────────────────────────────────────────────────────┐
│ PerformancePulse                    [Settings] [Profile] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ My Team (8 members)                                     │
│                                                         │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐       │
│ │ Sarah Chen  │ │ John Kumar  │ │ Alex Rivera │       │
│ │ Senior SWE  │ │ SWE II      │ │ SWE II      │       │
│ │ ────────────│ │ ────────────│ │ ────────────│       │
│ │ Last 1:1:   │ │ Last 1:1:   │ │ Last 1:1:   │       │
│ │ 3 days ago  │ │ 1 week ago  │ │ 2 weeks ago │       │
│ │             │ │             │ │             │       │
│ │ [Prep 1:1]  │ │ [Prep 1:1]  │ │ [Prep 1:1]  │       │
│ └─────────────┘ └─────────────┘ └─────────────┘       │
│                                                         │
│ Recent Activity                                         │
│ • Sarah completed MSV migration (3 MRs, 2 tickets)     │
│ • John fixed critical bug in payment flow              │
│ • Alex led frontend accessibility improvements         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Individual Context Management View
```
┌─────────────────────────────────────────────────────────┐
│ Sarah Chen - Context & Evidence                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ ┌─── Recent Evidence ──────────────────────────────┐   │
│ │ • GitLab: 5 MRs merged (auto-synced)            │   │
│ │ • Jira: 3 tickets completed (auto-synced)       │   │
│ │ • Meeting: Sprint Retro notes (manual upload)   │   │
│ │ • Slack: Architecture discussion (manual)       │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─── Historical Context ───────────────────────────┐   │
│ │ • Q3 Performance Summary (uploaded 2 weeks ago) │   │
│ │ • 1:1 Notes - August (uploaded 1 month ago)     │   │
│ │ • Career Discussion - July (uploaded 2 mo ago)  │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─── Upload New Context ───────────────────────────┐   │
│ │                                                  │   │
│ │ [📁 Drag files here or click to browse]        │   │
│ │                                                  │   │
│ │ Supported: Meeting transcripts, Slack exports,  │   │
│ │ 1:1 summaries, performance notes, PDFs, Word    │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                         │
│ [Generate Meeting Prep] [View Timeline] [Export All]   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Implementation

### Technology Stack
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Backend**: Python + FastAPI + Pydantic
- **Database**: Supabase (PostgreSQL + Auth + Storage + Real-time)
- **AI**: Claude 3.5 Sonnet for analysis and correlation
- **Integrations**: GitLab MCP + Jira MCP servers
- **Deployment**: Vercel (Frontend) + Railway (Backend) + Supabase Cloud

### Frontend Structure
```
app/
├── (dashboard)/
│   ├── page.tsx                    # Main team dashboard
│   ├── team-member/
│   │   ├── [id]/
│   │   │   ├── page.tsx           # Member overview
│   │   │   ├── evidence/
│   │   │   │   └── page.tsx       # Evidence browser
│   │   │   ├── context/
│   │   │   │   └── page.tsx       # Historical context
│   │   │   └── prepare/
│   │   │       └── [type]/
│   │   │           └── page.tsx   # Meeting preparation
└── components/
    ├── Dashboard/
    │   ├── TeamOverview.tsx
    │   ├── ActivityFeed.tsx
    │   └── MemberCard.tsx
    ├── Evidence/
    │   ├── EvidenceCard.tsx
    │   ├── EvidenceFilter.tsx
    │   └── EvidenceUpload.tsx
    ├── Context/
    │   ├── ContextDocuments.tsx
    │   ├── ContextUpload.tsx
    │   └── ContextViewer.tsx
    └── Preparation/
        ├── MeetingPrep.tsx
        ├── InsightCard.tsx
        └── ExportDialog.tsx
```

### Backend Structure
```
backend/
├── main.py                         # FastAPI application entry
├── routers/
│   ├── team.py                    # Team management endpoints
│   ├── evidence.py                # Evidence collection endpoints
│   ├── context.py                 # Document upload and processing
│   ├── analysis.py                # AI analysis endpoints
│   └── preparation.py             # Meeting preparation endpoints
├── services/
│   ├── data_collector.py          # Multi-source data collection
│   ├── document_processor.py      # File upload and text extraction
│   ├── evidence_analyzer.py       # AI analysis service
│   ├── historical_context.py      # Historical correlation service
│   ├── gitlab_service.py          # GitLab MCP integration
│   └── jira_service.py            # Jira MCP integration
├── models/
│   ├── team.py                    # Team and member Pydantic models
│   ├── evidence.py                # Evidence models
│   ├── context.py                 # Context document models
│   └── analysis.py                # Analysis result models
└── utils/
    ├── mcp_client.py              # MCP server client utilities
    ├── claude_client.py           # Claude API client
    ├── file_processor.py          # File processing utilities
    └── database.py                # Database connection and utilities
```

---

## 🤖 AI Integration Strategy

### Document Processing Pipeline
Processing uploaded files and extracting meaningful context for performance discussions.

### Historical Context Integration
Correlating current period performance with historical patterns from uploaded documents.

### Meeting Preparation Analysis
Generating structured insights for different types of performance conversations.

---

## 📁 File Storage & Processing

### Supabase Storage Configuration
- Context documents: PDFs, Word docs, text files
- Meeting transcripts: Text and audio transcriptions
- Slack exports: JSON, HTML, text formats
- Performance notes: Markdown, PDF formats

### Supported Document Types
- Meeting transcripts with speaker identification
- Slack threads with collaboration analysis
- Meeting summaries with action item extraction
- Performance notes with feedback categorization
- Project documents with contribution identification

---

## 🔗 API Design

### Core API Endpoints
```typescript
// Team Management
GET    /api/teams/{team_id}/members
POST   /api/team-members
PUT    /api/team-members/{id}

// Evidence Collection
GET    /api/team-members/{id}/evidence
POST   /api/team-members/{id}/evidence/sync

// Context Document Management
GET    /api/team-members/{id}/context
POST   /api/team-members/{id}/context/upload

// Meeting Preparation
POST   /api/team-members/{id}/prepare-meeting
GET    /api/meeting-preparations/{prep_id}

// Data Consent Management
GET    /api/team-members/{id}/consents
PUT    /api/team-members/{id}/consents/{source_type}
```

---

## 🚀 Implementation Roadmap

### Phase 1: Core Data Pipeline (Week 1-2)
**Goal: Collect and organize data from multiple sources**

- FastAPI setup with Pydantic models and automatic documentation
- Supabase integration with authentication and database setup
- GitLab MCP integration for commits, merge requests, and code reviews
- Jira MCP integration for tickets, projects, and sprint data
- File upload system with Supabase Storage integration

### Phase 2: AI Analysis & Document Processing (Week 3-4)
**Goal: Generate structured insights and process historical documents**

- Claude API integration for evidence analysis and categorization
- Document processing pipeline for transcripts, summaries, and notes
- Pattern recognition across time periods and data sources
- Discussion point generation for different meeting types
- Historical context correlation with current evidence

### Phase 3: Advanced Features & Polish (Week 5-6)
**Goal: Production-ready tool with excellent user experience**

- Responsive design optimized for mobile and tablet
- Dark/light theme with system preference detection
- Advanced filtering and search with saved queries
- Privacy dashboard for team members to manage their data
- PDF report generation and export capabilities

---

## 🔒 Privacy & Security

### Data Access Controls
Row Level Security policies ensure users only see appropriate data based on their role and explicit consent.

### Consent Management Flow
Team members have complete control over what data is shared and can revoke access at any time.

---

## 📈 Success Metrics

### Primary Metrics
- **Time Savings**: 85% reduction (from 180 minutes to 30 minutes)
- **Data Completeness**: 90% of engineering contributions captured
- **Manager Satisfaction**: 4.5/5.0 average satisfaction score
- **Usage Frequency**: 80% of 1:1s prepared using the tool

### Secondary Metrics
- Data accuracy and correlation quality
- Historical context usage frequency
- Export usage and format preferences
- Team member consent rates
- System reliability and uptime

---

## 🚢 Deployment & Operations

### Deployment Stack
- **Frontend**: Vercel (automatic deployments, edge functions, global CDN)
- **Backend**: Railway (automatic Python deployment, environment variables, auto-scaling)
- **Database**: Supabase Cloud (managed PostgreSQL, automatic backups, global edge)

### Environment Configuration
```bash
# Frontend (.env.local)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Backend (.env)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
CLAUDE_API_KEY=your_claude_api_key
GITLAB_MCP_SERVER_URL=http://localhost:8001
JIRA_MCP_SERVER_URL=http://localhost:8002
```

---

## 🔄 Development Workflow

### Local Development Setup
```bash
# Clone repository
git clone https://github.com/your-org/performance-pulse.git
cd performance-pulse

# Frontend setup
npm install
npm run dev  # Runs on localhost:3000

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload  # Runs on localhost:8000
```

---

## 🎯 Why This Architecture Works

### Technical Benefits
- **Simple**: Only 3 main components to manage
- **Scalable**: Each component can scale independently
- **Reliable**: Using proven, managed services
- **Fast**: Modern tech stack optimized for performance
- **Maintainable**: Clear separation of concerns

### Business Benefits
- **Cost-effective**: Great free tiers with pay-as-you-grow pricing
- **Quick to market**: Leverage existing MCP integrations
- **Privacy-compliant**: Built-in consent management
- **Manager-focused**: Designed specifically for performance conversation preparation
- **Evidence-driven**: Every insight backed by concrete, verifiable data

This comprehensive architecture document serves as the complete specification for building PerformancePulse - a focused data aggregation tool that transforms scattered engineering contributions into organized, factual summaries for better performance conversations. 