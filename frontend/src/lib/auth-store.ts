/**
 * Authentication state management using Zustand
 * Handles user session, profile data, and auth state
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { supabase, auth, type Profile } from './supabase'
import type { Session, User } from '@supabase/supabase-js'

interface AuthState {
  // State
  session: Session | null
  user: User | null
  profile: Profile | null
  loading: boolean
  initialized: boolean

  // Actions
  initialize: () => Promise<void>
  signIn: () => Promise<void>
  signOut: () => Promise<void>
  updateProfile: (updates: Partial<Profile>) => Promise<void>
  setSession: (session: Session | null) => void
  setProfile: (profile: Profile | null) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      session: null,
      user: null,
      profile: null,
      loading: false,
      initialized: false,

      // Initialize auth state and set up listeners
      initialize: async () => {
        if (get().initialized) return
        
        set({ loading: true })
        
        try {
          // Get initial session
          const session = await auth.getSession()
          
          if (session?.user) {
            // Get user profile
            const profile = await auth.getProfile(session.user.id)
            set({ 
              session, 
              user: session.user, 
              profile,
              initialized: true,
              loading: false 
            })
          } else {
            set({ 
              session: null, 
              user: null, 
              profile: null,
              initialized: true,
              loading: false 
            })
          }

          // Listen for auth changes
          supabase.auth.onAuthStateChange(async (event, session) => {
            console.log('Auth state changed:', event, session?.user?.email)
            
            if (session?.user) {
              // User signed in - get/create profile
              try {
                let profile = await auth.getProfile(session.user.id)
                
                // If no profile exists, create one for managers
                if (!profile && session.user.email) {
                  const newProfile = {
                    id: session.user.id,
                    full_name: session.user.user_metadata?.full_name || session.user.email,
                    email: session.user.email,
                    role: 'manager' as const, // Default to manager for OAuth users
                  }
                  
                  profile = await auth.upsertProfile(newProfile)
                }
                
                set({ 
                  session, 
                  user: session.user, 
                  profile,
                  loading: false 
                })
              } catch (error) {
                console.error('Error fetching/creating profile:', error)
                set({ 
                  session, 
                  user: session.user, 
                  profile: null,
                  loading: false 
                })
              }
            } else {
              // User signed out
              set({ 
                session: null, 
                user: null, 
                profile: null,
                loading: false 
              })
            }
          })
        } catch (error) {
          console.error('Auth initialization error:', error)
          set({ 
            session: null, 
            user: null, 
            profile: null,
            initialized: true,
            loading: false 
          })
        }
      },

      // Sign in with Google
      signIn: async () => {
        set({ loading: true })
        try {
          await auth.signInWithGoogle()
          // Note: State will be updated by the auth listener
        } catch (error) {
          console.error('Sign in error:', error)
          set({ loading: false })
          throw error
        }
      },

      // Sign out
      signOut: async () => {
        set({ loading: true })
        try {
          await auth.signOut()
          // Note: State will be updated by the auth listener
        } catch (error) {
          console.error('Sign out error:', error)
          set({ loading: false })
          throw error
        }
      },

      // Update user profile
      updateProfile: async (updates: Partial<Profile>) => {
        const { user, profile } = get()
        if (!user || !profile) throw new Error('No authenticated user')
        
        try {
          const updatedProfile = await auth.upsertProfile({
            ...profile,
            ...updates,
            id: user.id, // Ensure ID matches user
          })
          
          set({ profile: updatedProfile })
        } catch (error) {
          console.error('Profile update error:', error)
          throw error
        }
      },

      // Set session (for manual updates)
      setSession: (session: Session | null) => {
        set({ session, user: session?.user || null })
      },

      // Set profile (for manual updates)  
      setProfile: (profile: Profile | null) => {
        set({ profile })
      },
    }),
    {
      name: 'auth-store',
      // Only persist non-sensitive data
      partialize: (state) => ({
        initialized: state.initialized,
        // Don't persist session/user data for security
      }),
    }
  )
)

// Helper hooks for common auth checks
export const useAuth = () => {
  const store = useAuthStore()
  return {
    ...store,
    isAuthenticated: !!store.session,
    isManager: store.profile?.role === 'manager',
    isTeamMember: store.profile?.role === 'team_member',
  }
}

// Auth guard hook
export const useRequireAuth = (requiredRole?: 'manager' | 'team_member') => {
  const auth = useAuth()
  
  if (!auth.initialized) {
    return { ...auth, canAccess: false, reason: 'loading' }
  }
  
  if (!auth.isAuthenticated) {
    return { ...auth, canAccess: false, reason: 'not_authenticated' }
  }
  
  if (!auth.profile) {
    return { ...auth, canAccess: false, reason: 'no_profile' }
  }
  
  if (requiredRole && auth.profile.role !== requiredRole) {
    return { ...auth, canAccess: false, reason: 'insufficient_role' }
  }
  
  return { ...auth, canAccess: true, reason: 'authorized' }
} 