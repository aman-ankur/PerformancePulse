/**
 * Supabase client configuration for PerformancePulse frontend
 * Handles authentication and database operations
 */

import { createClient } from '@supabase/supabase-js'

// Environment variables needed:
// NEXT_PUBLIC_SUPABASE_URL=https://jewpkwlteiendvfhslml.supabase.co
// NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impld3Brd2x0ZWllbmR2ZmhzbG1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTEwMjEsImV4cCI6MjA2NTMyNzAyMX0.jGrNVK5pbAX4-9VbUv6LutFUoKbzddmKYQA7_Rw2nlg

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://jewpkwlteiendvfhslml.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Impld3Brd2x0ZWllbmR2ZmhzbG1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk3NTEwMjEsImV4cCI6MjA2NTMyNzAyMX0.jGrNVK5pbAX4-9VbUv6LutFUoKbzddmKYQA7_Rw2nlg'

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

// Create Supabase client with auth configuration
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    flowType: 'pkce'
  }
})

// Type definitions for auth
export type AuthUser = {
  id: string
  email: string
  user_metadata: {
    full_name?: string
    picture?: string
  }
}

export type Profile = {
  id: string
  full_name: string
  email: string
  role: 'manager' | 'team_member'
  manager_id?: string
  gitlab_username?: string
  jira_username?: string
  created_at: string
  updated_at: string
}

// Type definitions for team members
export type TeamMember = {
  id: string
  full_name: string
  email: string
  role: 'manager' | 'team_member'
  gitlab_username: string
  jira_username: string
  manager_id?: string
  created_at: string
  updated_at: string
}

export type ConsentStatus = {
  id: string
  member_id: string
  gitlab_commits: boolean
  gitlab_merge_requests: boolean
  jira_tickets: boolean
  jira_comments: boolean
  created_at: string
  updated_at: string
}

export type NewTeamMember = {
  full_name: string
  email: string
  role: 'manager' | 'team_member'
  gitlab_username: string
  jira_username: string
}

// Auth helper functions
export const auth = {
  /**
   * Sign in with Google OAuth
   */
  async signInWithGoogle() {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
        queryParams: {
          access_type: 'offline',
          prompt: 'consent',
        }
      }
    })
    
    if (error) throw error
    return data
  },

  /**
   * Sign out current user
   */
  async signOut() {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  },

  /**
   * Get current user session
   */
  async getSession() {
    const { data: { session }, error } = await supabase.auth.getSession()
    if (error) throw error
    return session
  },

  /**
   * Get current user profile from database
   */
  async getProfile(userId: string): Promise<Profile | null> {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .single()
    
    if (error) {
      if (error.code === 'PGRST116') return null // Not found
      console.error('Error fetching profile:', error.message)
      throw error
    }
    
    return data
  },

  /**
   * Create or update user profile
   */
  async upsertProfile(profile: Partial<Profile>): Promise<Profile> {
    const { data, error } = await supabase
      .from('profiles')
      .upsert(profile)
      .select()
      .single()
    
    if (error) {
      console.error('Error upserting profile:', error.message)
      throw error
    }
    
    return data
  }
}

// Team management functions
export const team = {
  /**
   * Get all team members for the current manager
   */
  async getTeamMembers(): Promise<TeamMember[]> {
    const { data: { user }, error: userError } = await supabase.auth.getUser()
    if (userError) throw userError

    const { data, error } = await supabase
      .from('team_members')
      .select('*')
      .eq('manager_id', user.id)
      .order('created_at', { ascending: false })
    
    if (error) {
      console.error('Error fetching team members:', error.message)
      throw error
    }
    
    return data
  },

  /**
   * Add a new team member
   */
  async addTeamMember(member: NewTeamMember): Promise<TeamMember> {
    const { data: { user }, error: userError } = await supabase.auth.getUser()
    if (userError || !user?.id) throw new Error('Failed to get current user')

    // Check if this is the first team member (who will be a manager)
    const { data: existingMembers, error: countError } = await supabase
      .from('team_members')
      .select('id')
      .limit(1)

    if (countError) {
      console.error('Error checking existing members:', countError)
      throw new Error('Failed to check existing members')
    }

    // If no existing members, this will be the first manager
    const isFirstMember = existingMembers?.length === 0
    
    // Prepare the team member data
    const teamMemberData = {
      full_name: member.full_name,
      email: member.email,
      role: isFirstMember ? 'manager' : member.role || 'team_member',
      gitlab_username: member.gitlab_username,
      jira_username: member.jira_username,
      manager_id: isFirstMember ? null : user.id
    }

    // Add team member
    const { data: teamMember, error: insertError } = await supabase
      .from('team_members')
      .insert([teamMemberData])
      .select()
      .single()
    
    if (insertError) {
      console.error('Error adding team member:', insertError)
      throw new Error(insertError.message)
    }

    if (!teamMember) {
      throw new Error('Failed to create team member')
    }

    try {
      // Initialize consent status
      const { error: consentError } = await supabase
        .from('member_consent')
        .insert([{
          member_id: teamMember.id,
          gitlab_commits: false,
          gitlab_merge_requests: false,
          jira_tickets: false,
          jira_comments: false
        }])
      
      if (consentError) {
        console.error('Error initializing consent:', consentError)
        // Don't throw here, as the team member was created successfully
      }
    } catch (err) {
      console.error('Error in consent initialization:', err)
      // Don't throw here, as the team member was created successfully
    }
    
    return teamMember
  },

  /**
   * Get consent status for all team members
   */
  async getTeamConsent(): Promise<ConsentStatus[]> {
    const { data, error } = await supabase
      .from('member_consent')
      .select('*')
    
    if (error) {
      console.error('Error fetching consent status:', error.message)
      throw error
    }
    
    return data
  },

  /**
   * Update consent status for a team member
   */
  async updateConsent(memberId: string, consent: Partial<ConsentStatus>): Promise<ConsentStatus> {
    const { data, error } = await supabase
      .from('member_consent')
      .upsert({
        member_id: memberId,
        gitlab_commits: consent.gitlab_commits,
        gitlab_merge_requests: consent.gitlab_merge_requests,
        jira_tickets: consent.jira_tickets,
        jira_comments: consent.jira_comments,
        updated_at: new Date().toISOString()
      })
      .select()
      .single()
    
    if (error) {
      console.error('Error updating consent status:', error.message)
      throw error
    }
    
    return data
  },

  /**
   * Subscribe to team member changes
   */
  subscribeToTeamChanges(callback: (payload: any) => void) {
    return supabase
      .channel('team_changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'team_members'
        },
        callback
      )
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'member_consent'
        },
        callback
      )
      .subscribe()
  }
} 