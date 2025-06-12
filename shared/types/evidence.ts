/**
 * Shared types for evidence collection and processing
 */

export interface EvidenceItem {
  id: string
  team_member_id: string
  source: EvidenceSource
  title: string
  description: string
  source_url?: string
  category: EvidenceCategory
  evidence_date: string
  created_at: string
  updated_at?: string
  ai_confidence?: number
  metadata?: Record<string, any>
}

export interface EvidenceItemCreate {
  team_member_id: string
  source: EvidenceSource
  title: string
  description: string
  source_url?: string
  category: EvidenceCategory
  evidence_date: string
  metadata?: Record<string, any>
}

export interface EvidenceFilter {
  team_member_id?: string
  source?: EvidenceSource
  category?: EvidenceCategory
  date_from?: string
  date_to?: string
  search?: string
}

export interface GitLabCommit {
  id: string
  short_id: string
  title: string
  message: string
  author_name: string
  author_email: string
  authored_date: string
  committed_date: string
  web_url: string
  project_id: string
}

export interface GitLabMergeRequest {
  id: string
  title: string
  description: string
  state: string
  author: {
    name: string
    email: string
  }
  created_at: string
  updated_at: string
  merged_at?: string
  web_url: string
  source_branch: string
  target_branch: string
}

export interface JiraTicket {
  id: string
  key: string
  summary: string
  description: string
  status: string
  assignee?: {
    displayName: string
    emailAddress: string
  }
  created: string
  updated: string
  resolved?: string
  project: {
    key: string
    name: string
  }
}

export interface SyncJobStatus {
  id: string
  team_member_id: string
  source: EvidenceSource
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  started_at?: string
  completed_at?: string
  error_message?: string
  items_processed: number
}

export type EvidenceSource = 'gitlab_commit' | 'gitlab_mr' | 'jira_ticket' | 'document_upload' | 'manual_entry'
export type EvidenceCategory = 'technical' | 'collaboration' | 'delivery' | 'leadership' | 'problem_solving'
export type SyncJobType = 'gitlab' | 'jira' | 'full_sync' 