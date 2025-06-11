# PerformancePulse - Simple Data Models

## Philosophy: "Start Simple, Grow Smart"

Design minimal database schema that covers core needs. Use JSON columns for flexibility. Leverage Supabase features for heavy lifting.

---

## Core Schema (4 Tables Only)

### 1. Profiles (Extends Supabase Auth)
```sql
CREATE TABLE profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  full_name TEXT,
  avatar_url TEXT,
  gitlab_username TEXT,
  role TEXT DEFAULT 'individual' CHECK (role IN ('individual', 'manager')),
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view and update own profile" ON profiles
  FOR ALL USING (auth.uid() = id);

-- Indexes
CREATE INDEX profiles_gitlab_username_idx ON profiles(gitlab_username);
```

### 2. Evidence (Core Data)
```sql
CREATE TABLE evidence (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) NOT NULL,
  
  -- Content
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  summary TEXT, -- AI-generated summary
  
  -- Source tracking
  source TEXT NOT NULL DEFAULT 'manual' 
    CHECK (source IN ('manual', 'gitlab', 'jira', 'upload')),
  source_id TEXT, -- External reference (commit hash, etc.)
  source_url TEXT, -- Link to original content
  
  -- Organization
  category TEXT DEFAULT 'general',
  tags TEXT[] DEFAULT '{}',
  
  -- AI features
  embedding VECTOR(1536), -- For semantic search
  ai_metadata JSONB DEFAULT '{}', -- Flexible AI analysis storage
  
  -- Files
  attachments TEXT[], -- Supabase storage URLs
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX evidence_user_id_idx ON evidence(user_id);
CREATE INDEX evidence_source_idx ON evidence(source, source_id);
CREATE INDEX evidence_category_idx ON evidence(category);
CREATE INDEX evidence_created_at_idx ON evidence(created_at DESC);

-- Vector search index
CREATE INDEX evidence_embedding_idx ON evidence 
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Row Level Security
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own evidence" ON evidence
  FOR ALL USING (user_id = auth.uid());
```

### 3. Insights (AI-Generated)
```sql
CREATE TABLE insights (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) NOT NULL,
  
  -- Insight content
  type TEXT NOT NULL CHECK (type IN ('strength', 'improvement', 'achievement', 'trend')),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  
  -- AI metadata
  confidence REAL DEFAULT 0.5 CHECK (confidence BETWEEN 0 AND 1),
  evidence_ids UUID[] DEFAULT '{}', -- Supporting evidence references
  
  -- Human validation
  validated BOOLEAN DEFAULT false,
  feedback TEXT, -- User feedback on insight quality
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX insights_user_id_idx ON insights(user_id);
CREATE INDEX insights_type_idx ON insights(type);
CREATE INDEX insights_created_at_idx ON insights(created_at DESC);

-- Row Level Security
ALTER TABLE insights ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own insights" ON insights
  FOR SELECT USING (user_id = auth.uid());

-- Only backend can create/update insights
CREATE POLICY "Service role can manage insights" ON insights
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');
```

### 4. Sync Jobs (Background Tasks)
```sql
CREATE TABLE sync_jobs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) NOT NULL,
  
  -- Job details
  source TEXT NOT NULL CHECK (source IN ('gitlab', 'jira', 'manual')),
  status TEXT DEFAULT 'pending' 
    CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  
  -- Results
  items_processed INTEGER DEFAULT 0,
  items_created INTEGER DEFAULT 0,
  error_message TEXT,
  
  -- Metadata
  last_sync_at TIMESTAMP WITH TIME ZONE,
  metadata JSONB DEFAULT '{}', -- Store API cursors, etc.
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX sync_jobs_user_id_idx ON sync_jobs(user_id);
CREATE INDEX sync_jobs_status_idx ON sync_jobs(status);
CREATE INDEX sync_jobs_source_idx ON sync_jobs(source);

-- Row Level Security
ALTER TABLE sync_jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own sync jobs" ON sync_jobs
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Service role can manage sync jobs" ON sync_jobs
  FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');
```

---

## Supabase Features Usage

### Authentication
```sql
-- Leverage built-in auth.users table
-- No custom user management needed

-- Trigger to create profile when user signs up
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profiles (id, full_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();
```

### Real-time Subscriptions
```sql
-- Enable real-time for evidence updates
ALTER PUBLICATION supabase_realtime ADD TABLE evidence;
ALTER PUBLICATION supabase_realtime ADD TABLE insights;
```

### File Storage
```sql
-- Storage bucket for evidence attachments
INSERT INTO storage.buckets (id, name, public) VALUES ('evidence', 'evidence', false);

-- RLS policy for file access
CREATE POLICY "Users can upload their own files" ON storage.objects
  FOR INSERT WITH CHECK (bucket_id = 'evidence' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can view their own files" ON storage.objects
  FOR SELECT USING (bucket_id = 'evidence' AND auth.uid()::text = (storage.foldername(name))[1]);
```

---

## Data Types & Patterns

### Flexible Metadata Pattern
```sql
-- Use JSONB for flexible, evolving data
ai_metadata JSONB DEFAULT '{
  "processing_time": null,
  "model_version": null,
  "categories_suggested": [],
  "sentiment_score": null,
  "key_phrases": []
}'

-- Query JSON fields efficiently
SELECT * FROM evidence 
WHERE ai_metadata->>'sentiment_score' IS NOT NULL;
```

### Vector Search Pattern
```sql
-- Semantic search function
CREATE OR REPLACE FUNCTION search_evidence(
  query_embedding VECTOR(1536),
  user_id_param UUID,
  similarity_threshold REAL DEFAULT 0.7,
  limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
  id UUID,
  title TEXT,
  content TEXT,
  similarity REAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    e.id,
    e.title,
    e.content,
    (1 - (e.embedding <=> query_embedding)) AS similarity
  FROM evidence e
  WHERE e.user_id = user_id_param
    AND (1 - (e.embedding <=> query_embedding)) > similarity_threshold
  ORDER BY e.embedding <=> query_embedding
  LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;
```

### Audit Trail Pattern
```sql
-- Simple audit using updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_evidence_updated_at BEFORE UPDATE ON evidence
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## Application Data Patterns

### TypeScript Types
```typescript
// Generated from database schema
export interface Profile {
  id: string
  full_name: string | null
  avatar_url: string | null
  gitlab_username: string | null
  role: 'individual' | 'manager'
  preferences: Record<string, any>
  created_at: string
  updated_at: string
}

export interface Evidence {
  id: string
  user_id: string
  title: string
  content: string
  summary: string | null
  source: 'manual' | 'gitlab' | 'jira' | 'upload'
  source_id: string | null
  source_url: string | null
  category: string
  tags: string[]
  embedding: number[] | null
  ai_metadata: Record<string, any>
  attachments: string[]
  created_at: string
  updated_at: string
}

export interface Insight {
  id: string
  user_id: string
  type: 'strength' | 'improvement' | 'achievement' | 'trend'
  title: string
  content: string
  confidence: number
  evidence_ids: string[]
  validated: boolean
  feedback: string | null
  created_at: string
  updated_at: string
}
```

### Query Patterns
```typescript
// Simple Supabase queries
const { data: evidence } = await supabase
  .from('evidence')
  .select('*')
  .eq('user_id', userId)
  .order('created_at', { ascending: false })
  .limit(20)

// Vector search
const { data: searchResults } = await supabase
  .rpc('search_evidence', {
    query_embedding: embedding,
    user_id_param: userId,
    similarity_threshold: 0.7,
    limit_count: 10
  })
```

---

## Migration Strategy

### Phase 1: Core Tables (Week 1)
- Create profiles, evidence tables
- Set up basic RLS policies
- Configure Supabase Auth integration

### Phase 2: AI Features (Week 2)
- Add vector extension and embedding column
- Create insights table
- Set up search functions

### Phase 3: Background Jobs (Week 3)
- Add sync_jobs table
- Implement GitLab and Jira MCP integrations
- Set up background processing

### Future Additions (Only if needed)
- Performance periods table
- Goals tracking
- Team/manager relationships
- Review templates

---

## Why This Schema Works

✅ **Simple**: Only 4 tables to understand and maintain
✅ **Flexible**: JSON columns for evolving requirements
✅ **Scalable**: Proper indexes and RLS policies
✅ **Modern**: Vector search, real-time subscriptions
✅ **Secure**: Row-level security built-in
✅ **Fast**: Optimized for common query patterns

## What We Avoided

❌ Over-normalization (separate category tables)
❌ Complex relationships (teams, hierarchies)
❌ Premature optimization (complex indexes)
❌ Enterprise features (audit logs, versioning)
❌ Multiple environments (dev/staging/prod schemas)