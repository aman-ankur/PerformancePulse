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
    
    if (error) throw error
    return data
  }
} 