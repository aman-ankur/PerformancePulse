-- PerformancePulse Database Schema
-- Phase 1.1.2: Core MVP Schema with Row Level Security

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Core manager-team relationship
CREATE TABLE profiles (
  id UUID REFERENCES auth.users(id) PRIMARY KEY,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  role TEXT DEFAULT 'team_member' CHECK (role IN ('team_member', 'manager')),
  manager_id UUID REFERENCES profiles(id),
  gitlab_username TEXT,
  jira_username TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Evidence collection with consent
CREATE TABLE evidence_items (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  team_member_id UUID REFERENCES profiles(id) NOT NULL,
  source TEXT NOT NULL CHECK (source IN ('gitlab_commit', 'gitlab_mr', 'jira_ticket', 'document')),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  source_url TEXT,
  category TEXT DEFAULT 'technical' CHECK (category IN ('technical', 'collaboration', 'delivery')),
  evidence_date DATE NOT NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Consent tracking
CREATE TABLE data_consents (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  team_member_id UUID REFERENCES profiles(id) NOT NULL,
  source_type TEXT NOT NULL CHECK (source_type IN ('gitlab', 'jira', 'documents')),
  consented BOOLEAN DEFAULT FALSE,
  consented_at TIMESTAMP WITH TIME ZONE,
  revoked_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(team_member_id, source_type)
);

-- Indexes for performance
CREATE INDEX idx_profiles_manager_id ON profiles(manager_id);
CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_evidence_items_team_member_id ON evidence_items(team_member_id);
CREATE INDEX idx_evidence_items_evidence_date ON evidence_items(evidence_date DESC);
CREATE INDEX idx_evidence_items_source ON evidence_items(source);
CREATE INDEX idx_data_consents_team_member_id ON data_consents(team_member_id);

-- Row Level Security Policies
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_consents ENABLE ROW LEVEL SECURITY;

-- Profiles RLS: Users can see their own profile and team members can see their manager
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Managers can view their team members" ON profiles
  FOR SELECT USING (auth.uid() = manager_id);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Managers can insert team members" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = manager_id);

-- Evidence Items RLS: Only team members and their managers can access evidence
CREATE POLICY "Team members can view own evidence" ON evidence_items
  FOR SELECT USING (auth.uid() = team_member_id);

CREATE POLICY "Managers can view team evidence" ON evidence_items
  FOR SELECT USING (
    auth.uid() IN (
      SELECT manager_id FROM profiles WHERE id = evidence_items.team_member_id
    )
  );

CREATE POLICY "System can insert evidence" ON evidence_items
  FOR INSERT WITH CHECK (
    auth.uid() = team_member_id OR 
    auth.uid() IN (
      SELECT manager_id FROM profiles WHERE id = evidence_items.team_member_id
    )
  );

-- Data Consents RLS: Only team members and their managers can manage consent
CREATE POLICY "Team members can manage own consent" ON data_consents
  FOR ALL USING (auth.uid() = team_member_id);

CREATE POLICY "Managers can view team consent" ON data_consents
  FOR SELECT USING (
    auth.uid() IN (
      SELECT manager_id FROM profiles WHERE id = data_consents.team_member_id
    )
  );

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_profiles_updated_at 
  BEFORE UPDATE ON profiles 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_evidence_items_updated_at 
  BEFORE UPDATE ON evidence_items 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_data_consents_updated_at 
  BEFORE UPDATE ON data_consents 
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column(); 