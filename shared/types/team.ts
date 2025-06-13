/**
 * Shared types for team management
 * These types are used across frontend and backend
 */

export interface TeamMember {
  id: string
  full_name: string
  email: string
  role: 'team_member' | 'manager'
  manager_id?: string
  gitlab_username?: string
  jira_username?: string
  created_at: string
  updated_at?: string
}

export interface TeamMemberCreate {
  full_name: string
  email: string
  gitlab_username?: string
  jira_username?: string
}

export interface TeamMemberUpdate {
  full_name?: string
  email?: string
  gitlab_username?: string
  jira_username?: string
}

export interface DataConsent {
  id: string
  team_member_id: string
  source_type: 'gitlab' | 'jira'
  consented: boolean
  consented_at?: string
  revoked_at?: string
}

export interface ConsentUpdate {
  source_type: 'gitlab' | 'jira'
  consented: boolean
}

export type UserRole = 'team_member' | 'manager'
export type ConsentSource = 'gitlab' | 'jira' 