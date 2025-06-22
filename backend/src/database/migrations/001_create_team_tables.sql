-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create team members table
CREATE TABLE IF NOT EXISTS team_members (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  full_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  role TEXT NOT NULL CHECK (role IN ('manager', 'team_member')),
  gitlab_username TEXT,
  jira_username TEXT,
  manager_id UUID REFERENCES team_members(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create consent table
CREATE TABLE IF NOT EXISTS member_consent (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  member_id UUID REFERENCES team_members(id) ON DELETE CASCADE,
  gitlab_commits BOOLEAN DEFAULT false,
  gitlab_merge_requests BOOLEAN DEFAULT false,
  jira_tickets BOOLEAN DEFAULT false,
  jira_comments BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(member_id)
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_team_members_updated_at
  BEFORE UPDATE ON team_members
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_member_consent_updated_at
  BEFORE UPDATE ON member_consent
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Add RLS policies
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE member_consent ENABLE ROW LEVEL SECURITY;

-- Allow first user to create the first manager
CREATE POLICY "first_manager_creation" ON team_members
  FOR INSERT
  WITH CHECK (
    NOT EXISTS (SELECT 1 FROM team_members) AND
    NEW.role = 'manager'
  );

-- Managers can read all team members they manage
CREATE POLICY "managers_read_team_members" ON team_members
  FOR SELECT
  USING (
    auth.uid() = manager_id OR
    auth.uid() IN (
      SELECT id FROM team_members 
      WHERE role = 'manager'
    )
  );

-- Managers can create team members
CREATE POLICY "managers_create_team_members" ON team_members
  FOR INSERT
  WITH CHECK (
    auth.uid() IN (
      SELECT id FROM team_members 
      WHERE role = 'manager'
    )
  );

-- Managers can update their team members
CREATE POLICY "managers_update_team_members" ON team_members
  FOR UPDATE
  USING (
    auth.uid() = manager_id OR
    auth.uid() IN (
      SELECT id FROM team_members 
      WHERE role = 'manager'
    )
  );

-- Consent policies
CREATE POLICY "managers_read_consent" ON member_consent
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM team_members
      WHERE team_members.id = member_consent.member_id
      AND (team_members.manager_id = auth.uid() OR
           auth.uid() IN (SELECT id FROM team_members WHERE role = 'manager'))
    )
  );

CREATE POLICY "managers_manage_consent" ON member_consent
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM team_members
      WHERE team_members.id = member_consent.member_id
      AND (team_members.manager_id = auth.uid() OR
           auth.uid() IN (SELECT id FROM team_members WHERE role = 'manager'))
    )
  ); 