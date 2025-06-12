# PerformancePulse - Manager-Focused Data Models

## Philosophy: "Manager-First, Privacy-Aware, Context-Rich"

Design database schema optimized for manager workflows: team oversight, evidence aggregation, historical context integration, and meeting preparation. Emphasize consent management and multi-source data correlation.

---

## Core Schema (6 Tables for Manager Workflows)

### 1. Profiles (Manager & Team Member Roles)
```sql
CREATE TABLE profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL,
  avatar_url TEXT,
  
  -- Role and hierarchy
  role TEXT DEFAULT 'team_member' CHECK (role IN ('team_member', 'manager', 'admin')),
  manager_id UUID REFERENCES profiles(id), -- Who manages this person
  level TEXT, -- Engineering level (L3, L4, Senior, Staff, etc.)
  title TEXT, -- Job title
  
  -- Integration identifiers
  gitlab_username TEXT,
  jira_username TEXT,
  
  -- Manager preferences
  preferences JSONB DEFAULT '{
    "meeting_prep_defaults": {
      "include_historical_context": true,
      "default_timeframe_days": 7,
      "focus_areas": ["technical_contributions", "collaboration_patterns"]
    },
    "notification_settings": {
      "sync_completion": true,
      "overdue_meetings": true
    }
  }',
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX profiles_manager_id_idx ON profiles(manager_id);
CREATE INDEX profiles_gitlab_username_idx ON profiles(gitlab_username);
CREATE INDEX profiles_jira_username_idx ON profiles(jira_username);

-- Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Managers can view their team members" ON profiles
  FOR SELECT USING (
    auth.uid() = id OR 
    auth.uid() = manager_id OR
    auth.uid() IN (
      SELECT id FROM profiles WHERE role = 'manager' AND id = auth.uid()
    )
  );

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);
```

### 2. Team Members (Manager-Team Relationships)
```sql
CREATE TABLE team_members (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  manager_id UUID REFERENCES profiles(id) NOT NULL,
  member_id UUID REFERENCES profiles(id) NOT NULL,
  
  -- Relationship metadata
  start_date DATE DEFAULT CURRENT_DATE,
  end_date DATE, -- For when people change teams
  is_active BOOLEAN DEFAULT true,
  
  -- Meeting cadence
  one_on_one_frequency TEXT DEFAULT 'weekly' 
    CHECK (one_on_one_frequency IN ('weekly', 'biweekly', 'monthly')),
  last_one_on_one DATE,
  next_one_on_one DATE,
  
  -- Manager notes (private)
  manager_notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(manager_id, member_id, is_active)
);

-- Indexes
CREATE INDEX team_members_manager_id_idx ON team_members(manager_id);
CREATE INDEX team_members_member_id_idx ON team_members(member_id);
CREATE INDEX team_members_active_idx ON team_members(is_active) WHERE is_active = true;

-- Row Level Security
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Managers can manage their team relationships" ON team_members
  FOR ALL USING (manager_id = auth.uid());

CREATE POLICY "Team members can view their manager relationship" ON team_members
  FOR SELECT USING (member_id = auth.uid());
```

### 3. Evidence Items (Multi-Source Technical Contributions)
```sql
CREATE TABLE evidence_items (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  team_member_id UUID REFERENCES profiles(id) NOT NULL,
  
  -- Content
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  summary TEXT, -- AI-generated summary
  
  -- Source tracking
  source TEXT NOT NULL CHECK (source IN ('gitlab_commit', 'gitlab_mr', 'jira_ticket', 'manual_entry', 'document_upload')),
  source_id TEXT, -- External reference (commit hash, ticket ID, etc.)
  source_url TEXT, -- Link to original content
  source_metadata JSONB DEFAULT '{}', -- Flexible source-specific data
  
  -- Categorization
  category TEXT DEFAULT 'technical' CHECK (category IN ('technical', 'collaboration', 'leadership', 'delivery', 'mentoring')),
  tags TEXT[] DEFAULT '{}',
  impact_level TEXT DEFAULT 'medium' CHECK (impact_level IN ('low', 'medium', 'high', 'critical')),
  
  -- AI analysis
  embedding VECTOR(1536), -- For semantic search and correlation
  ai_analysis JSONB DEFAULT '{}', -- AI-generated insights about this evidence
  
  -- Correlation with other evidence
  related_evidence_ids UUID[] DEFAULT '{}',
  
  -- Timestamps
  evidence_date DATE NOT NULL, -- When the work actually happened
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for manager queries
CREATE INDEX evidence_items_team_member_id_idx ON evidence_items(team_member_id);
CREATE INDEX evidence_items_source_idx ON evidence_items(source, source_id);
CREATE INDEX evidence_items_category_idx ON evidence_items(category);
CREATE INDEX evidence_items_evidence_date_idx ON evidence_items(evidence_date DESC);
CREATE INDEX evidence_items_impact_level_idx ON evidence_items(impact_level);

-- Vector search index
CREATE INDEX evidence_items_embedding_idx ON evidence_items 
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Row Level Security
ALTER TABLE evidence_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Team members can view own evidence" ON evidence_items
  FOR SELECT USING (team_member_id = auth.uid());

CREATE POLICY "Managers can view their team's evidence" ON evidence_items
  FOR SELECT USING (
    team_member_id IN (
      SELECT member_id FROM team_members 
      WHERE manager_id = auth.uid() AND is_active = true
    )
  );

CREATE POLICY "Service role can manage evidence" ON evidence_items
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');
```

### 4. Context Documents (Historical Context Integration)
```sql
CREATE TABLE context_documents (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  team_member_id UUID REFERENCES profiles(id) NOT NULL,
  uploaded_by UUID REFERENCES profiles(id) NOT NULL, -- Usually the manager
  
  -- Document metadata
  title TEXT NOT NULL,
  document_type TEXT NOT NULL CHECK (document_type IN ('meeting_transcript', '1_1_notes', 'slack_thread', 'performance_summary', 'peer_feedback')),
  file_path TEXT, -- Supabase storage path
  file_size INTEGER,
  file_type TEXT, -- MIME type
  
  -- Content and analysis
  extracted_text TEXT, -- OCR/parsed content
  summary TEXT, -- AI-generated summary
  key_themes TEXT[], -- AI-extracted themes
  embedding VECTOR(1536), -- For semantic search
  
  -- Time context
  date_range_start DATE,
  date_range_end DATE,
  
  -- Processing status
  processing_status TEXT DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
  processing_error TEXT,
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX context_documents_team_member_id_idx ON context_documents(team_member_id);
CREATE INDEX context_documents_uploaded_by_idx ON context_documents(uploaded_by);
CREATE INDEX context_documents_document_type_idx ON context_documents(document_type);
CREATE INDEX context_documents_date_range_idx ON context_documents(date_range_start, date_range_end);
CREATE INDEX context_documents_embedding_idx ON context_documents 
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Row Level Security
ALTER TABLE context_documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Managers can manage context documents for their team" ON context_documents
  FOR ALL USING (
    uploaded_by = auth.uid() AND
    team_member_id IN (
      SELECT member_id FROM team_members 
      WHERE manager_id = auth.uid() AND is_active = true
    )
  );
```

### 5. Meeting Preparations (AI-Generated Meeting Content)
```sql
CREATE TABLE meeting_preparations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  manager_id UUID REFERENCES profiles(id) NOT NULL,
  team_member_id UUID REFERENCES profiles(id) NOT NULL,
  
  -- Meeting details
  meeting_type TEXT NOT NULL CHECK (meeting_type IN ('weekly_1_1', 'monthly_review', 'quarterly_review', 'annual_review', 'performance_discussion')),
  timeframe_start DATE NOT NULL,
  timeframe_end DATE NOT NULL,
  
  -- Configuration
  focus_areas TEXT[] DEFAULT '{}', -- Areas to emphasize
  include_historical_context BOOLEAN DEFAULT true,
  
  -- Generated content
  summary JSONB NOT NULL DEFAULT '{}', -- Technical work summary, collaboration metrics, etc.
  historical_patterns JSONB DEFAULT '{}', -- Patterns from context documents
  discussion_points JSONB DEFAULT '[]', -- Structured discussion topics with evidence
  suggested_questions TEXT[] DEFAULT '{}',
  
  -- Evidence correlation
  evidence_item_ids UUID[] DEFAULT '{}', -- Supporting evidence
  context_document_ids UUID[] DEFAULT '{}', -- Related historical context
  
  -- Status and feedback
  status TEXT DEFAULT 'generated' CHECK (status IN ('generated', 'reviewed', 'used', 'archived')),
  manager_feedback TEXT, -- Manager's notes on usefulness
  
  -- Export tracking
  exported_formats TEXT[] DEFAULT '{}', -- pdf, markdown, etc.
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX meeting_preparations_manager_id_idx ON meeting_preparations(manager_id);
CREATE INDEX meeting_preparations_team_member_id_idx ON meeting_preparations(team_member_id);
CREATE INDEX meeting_preparations_meeting_type_idx ON meeting_preparations(meeting_type);
CREATE INDEX meeting_preparations_timeframe_idx ON meeting_preparations(timeframe_start, timeframe_end);
CREATE INDEX meeting_preparations_status_idx ON meeting_preparations(status);

-- Row Level Security
ALTER TABLE meeting_preparations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Managers can manage their meeting preparations" ON meeting_preparations
  FOR ALL USING (manager_id = auth.uid());
```

### 6. Data Consents (Privacy & Compliance)
```sql
CREATE TABLE data_consents (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  team_member_id UUID REFERENCES profiles(id) NOT NULL,
  manager_id UUID REFERENCES profiles(id) NOT NULL,
  
  -- Consent details
  data_source TEXT NOT NULL CHECK (data_source IN ('gitlab', 'jira', 'documents', 'meeting_notes')),
  consent_granted BOOLEAN NOT NULL DEFAULT false,
  consent_date TIMESTAMP WITH TIME ZONE,
  
  -- Scope and limitations
  data_scope JSONB DEFAULT '{}', -- What specific data is consented to
  retention_period_days INTEGER DEFAULT 365, -- How long to keep the data
  
  -- Revocation
  revoked BOOLEAN DEFAULT false,
  revoked_date TIMESTAMP WITH TIME ZONE,
  revocation_reason TEXT,
  
  -- Compliance tracking
  consent_version TEXT DEFAULT '1.0', -- For tracking consent policy changes
  ip_address INET, -- For audit trail
  user_agent TEXT, -- For audit trail
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(team_member_id, manager_id, data_source)
);

-- Indexes
CREATE INDEX data_consents_team_member_id_idx ON data_consents(team_member_id);
CREATE INDEX data_consents_manager_id_idx ON data_consents(manager_id);
CREATE INDEX data_consents_data_source_idx ON data_consents(data_source);
CREATE INDEX data_consents_consent_granted_idx ON data_consents(consent_granted) WHERE consent_granted = true;

-- Row Level Security
ALTER TABLE data_consents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Team members can manage their own consents" ON data_consents
  FOR ALL USING (team_member_id = auth.uid());

CREATE POLICY "Managers can view consents for their team" ON data_consents
  FOR SELECT USING (
    manager_id = auth.uid() AND
    team_member_id IN (
      SELECT member_id FROM team_members 
      WHERE manager_id = auth.uid() AND is_active = true
    )
  );
```

---

## Manager-Focused Query Functions

### Team Dashboard Queries
```sql
-- Get team overview for manager dashboard
CREATE OR REPLACE FUNCTION get_team_overview(manager_id_param UUID)
RETURNS TABLE (
  total_members INTEGER,
  active_members INTEGER,
  upcoming_one_on_ones INTEGER,
  overdue_one_on_ones INTEGER,
  recent_commits INTEGER,
  recent_merge_requests INTEGER,
  recent_tickets INTEGER
) AS $$
BEGIN
  RETURN QUERY
  WITH team_stats AS (
    SELECT 
      COUNT(*) as total_members,
      COUNT(*) FILTER (WHERE tm.last_one_on_one >= CURRENT_DATE - INTERVAL '7 days') as active_members,
      COUNT(*) FILTER (WHERE tm.next_one_on_one BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days') as upcoming_one_on_ones,
      COUNT(*) FILTER (WHERE tm.next_one_on_one < CURRENT_DATE) as overdue_one_on_ones
    FROM team_members tm
    WHERE tm.manager_id = manager_id_param AND tm.is_active = true
  ),
  activity_stats AS (
    SELECT 
      COUNT(*) FILTER (WHERE ei.source = 'gitlab_commit' AND ei.evidence_date >= CURRENT_DATE - INTERVAL '7 days') as recent_commits,
      COUNT(*) FILTER (WHERE ei.source = 'gitlab_mr' AND ei.evidence_date >= CURRENT_DATE - INTERVAL '7 days') as recent_merge_requests,
      COUNT(*) FILTER (WHERE ei.source = 'jira_ticket' AND ei.evidence_date >= CURRENT_DATE - INTERVAL '7 days') as recent_tickets
    FROM evidence_items ei
    WHERE ei.team_member_id IN (
      SELECT member_id FROM team_members 
      WHERE manager_id = manager_id_param AND is_active = true
    )
  )
  SELECT 
    ts.total_members::INTEGER,
    ts.active_members::INTEGER,
    ts.upcoming_one_on_ones::INTEGER,
    ts.overdue_one_on_ones::INTEGER,
    ast.recent_commits::INTEGER,
    ast.recent_merge_requests::INTEGER,
    ast.recent_tickets::INTEGER
  FROM team_stats ts, activity_stats ast;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### Evidence Correlation Function
```sql
-- Correlate evidence with historical context
CREATE OR REPLACE FUNCTION correlate_evidence_with_context(
  team_member_id_param UUID,
  timeframe_start_param DATE,
  timeframe_end_param DATE
)
RETURNS TABLE (
  evidence_id UUID,
  evidence_title TEXT,
  evidence_category TEXT,
  context_document_id UUID,
  context_title TEXT,
  correlation_score REAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    ei.id as evidence_id,
    ei.title as evidence_title,
    ei.category as evidence_category,
    cd.id as context_document_id,
    cd.title as context_title,
    (1 - (ei.embedding <=> cd.embedding)) as correlation_score
  FROM evidence_items ei
  CROSS JOIN context_documents cd
  WHERE ei.team_member_id = team_member_id_param
    AND cd.team_member_id = team_member_id_param
    AND ei.evidence_date BETWEEN timeframe_start_param AND timeframe_end_param
    AND (cd.date_range_start IS NULL OR cd.date_range_start <= timeframe_end_param)
    AND (cd.date_range_end IS NULL OR cd.date_range_end >= timeframe_start_param)
    AND ei.embedding IS NOT NULL
    AND cd.embedding IS NOT NULL
    AND (1 - (ei.embedding <=> cd.embedding)) > 0.7
  ORDER BY correlation_score DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

---

## TypeScript Types (Manager-Focused)

```typescript
export interface Profile {
  id: string
  full_name: string
  email: string
  avatar_url: string | null
  role: 'team_member' | 'manager' | 'admin'
  manager_id: string | null
  level: string | null
  title: string | null
  gitlab_username: string | null
  jira_username: string | null
  preferences: {
    meeting_prep_defaults: {
      include_historical_context: boolean
      default_timeframe_days: number
      focus_areas: string[]
    }
    notification_settings: {
      sync_completion: boolean
      overdue_meetings: boolean
    }
  }
  created_at: string
  updated_at: string
}

export interface TeamMember {
  id: string
  manager_id: string
  member_id: string
  start_date: string
  end_date: string | null
  is_active: boolean
  one_on_one_frequency: 'weekly' | 'biweekly' | 'monthly'
  last_one_on_one: string | null
  next_one_on_one: string | null
  manager_notes: string | null
  created_at: string
  updated_at: string
}

export interface EvidenceItem {
  id: string
  team_member_id: string
  title: string
  description: string
  summary: string | null
  source: 'gitlab_commit' | 'gitlab_mr' | 'jira_ticket' | 'manual_entry' | 'document_upload'
  source_id: string | null
  source_url: string | null
  source_metadata: Record<string, any>
  category: 'technical' | 'collaboration' | 'leadership' | 'delivery' | 'mentoring'
  tags: string[]
  impact_level: 'low' | 'medium' | 'high' | 'critical'
  embedding: number[] | null
  ai_analysis: Record<string, any>
  related_evidence_ids: string[]
  evidence_date: string
  created_at: string
  updated_at: string
}

export interface ContextDocument {
  id: string
  team_member_id: string
  uploaded_by: string
  title: string
  document_type: 'meeting_transcript' | '1_1_notes' | 'slack_thread' | 'performance_summary' | 'peer_feedback'
  file_path: string | null
  file_size: number | null
  file_type: string | null
  extracted_text: string | null
  summary: string | null
  key_themes: string[]
  embedding: number[] | null
  date_range_start: string | null
  date_range_end: string | null
  processing_status: 'pending' | 'processing' | 'completed' | 'failed'
  processing_error: string | null
  created_at: string
  updated_at: string
}

export interface MeetingPreparation {
  id: string
  manager_id: string
  team_member_id: string
  meeting_type: 'weekly_1_1' | 'monthly_review' | 'quarterly_review' | 'annual_review' | 'performance_discussion'
  timeframe_start: string
  timeframe_end: string
  focus_areas: string[]
  include_historical_context: boolean
  summary: {
    technical_work: {
      commits: number
      merge_requests: number
      code_reviews: number
      projects: string[]
    }
    collaboration: {
      cross_team_contributions: number
      mentoring_activities: number
      documentation_contributions: number
    }
  }
  historical_patterns: {
    consistent_strengths: string[]
    development_progress: string[]
    career_progression: string[]
  }
  discussion_points: Array<{
    topic: string
    context: string
    evidence: string[]
    suggested_questions: string[]
  }>
  evidence_item_ids: string[]
  context_document_ids: string[]
  status: 'generated' | 'reviewed' | 'used' | 'archived'
  manager_feedback: string | null
  exported_formats: string[]
  created_at: string
  updated_at: string
}

export interface DataConsent {
  id: string
  team_member_id: string
  manager_id: string
  data_source: 'gitlab' | 'jira' | 'documents' | 'meeting_notes'
  consent_granted: boolean
  consent_date: string | null
  data_scope: Record<string, any>
  retention_period_days: number
  revoked: boolean
  revoked_date: string | null
  revocation_reason: string | null
  consent_version: string
  ip_address: string | null
  user_agent: string | null
  created_at: string
  updated_at: string
}
```

---

## Migration Strategy

### Phase 1: Core Manager Tables (Week 1)
- Create profiles with manager hierarchy
- Set up team_members relationship table
- Configure basic RLS policies for manager access

### Phase 2: Evidence & Context (Week 2)
- Add evidence_items with multi-source support
- Create context_documents for historical integration
- Set up vector search capabilities

### Phase 3: Meeting Preparation (Week 3)
- Add meeting_preparations table
- Implement evidence correlation functions
- Create manager dashboard queries

### Phase 4: Privacy & Compliance (Week 4)
- Add data_consents table
- Implement consent checking in RLS policies
- Set up sync_jobs for background processing

---

## Why This Manager-Focused Schema Works

✅ **Manager-Centric**: Optimized for manager workflows and team oversight
✅ **Privacy-First**: Built-in consent management and data governance
✅ **Context-Rich**: Historical document integration with AI correlation
✅ **Evidence-Driven**: Multi-source technical contribution tracking
✅ **Meeting-Ready**: Structured preparation with AI-generated insights
✅ **Scalable**: Proper indexes and RLS for team-based access patterns
✅ **Compliant**: Audit trails and consent tracking for enterprise use

## What We Avoided

❌ Employee self-service complexity
❌ Complex HR workflow tables
❌ Performance rating/scoring systems
❌ Real-time collaboration features
❌ Over-normalized relationship tables
❌ Complex approval workflows

This schema focuses exclusively on helping managers prepare for performance conversations through evidence aggregation and historical context correlation. 