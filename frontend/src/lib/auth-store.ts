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
        const currentState = get()
        
        // If already initialized, check if we have a valid session and profile
        if (currentState.initialized) {
          console.log('Auth store already initialized, checking current state...')
          
          // Force a session check and profile update for OAuth callbacks
          try {
            // Get current session
            const session = await auth.getSession()
            
            if (session?.user && session.user.id !== currentState.user?.id) {
              console.log('New OAuth session detected, updating auth state...')
              
              // Get user profile
              let profile = await auth.getProfile(session.user.id)
              
              // If no profile exists, create one for OAuth users
              if (!profile && session.user.email) {
                console.log('Creating profile for new OAuth user...')
                
                const newProfile = {
                  id: session.user.id,
                  full_name: session.user.user_metadata?.full_name || 
                            session.user.user_metadata?.name || 
                            session.user.email.split('@')[0],
                  email: session.user.email,
                  role: 'manager' as const, // Default to manager for OAuth users
                }
                
                profile = await auth.upsertProfile(newProfile)
                console.log('Profile created successfully for:', profile.email)
              }
              
              set({ 
                session, 
                user: session.user, 
                profile,
                loading: false 
              })
              console.log('Auth state updated successfully')
            } else if (session?.user && currentState.profile) {
              console.log('Session and profile already valid')
            } else if (!session) {
              console.log('No valid session found')
            }
          } catch (error) {
            console.error('Error during session check:', error)
            throw error
          }
          
          return
        }
        
        set({ loading: true })
        
        try {
          console.log('Initializing auth store...')
          
          // Get initial session
          const session = await auth.getSession()
          
          if (session?.user) {
            console.log('User session found, setting up profile...')
            
            // Get user profile
            let profile = await auth.getProfile(session.user.id)
            
            // If no profile exists, create one for OAuth users
            if (!profile && session.user.email) {
              console.log('Creating profile for OAuth user...')
              
              const newProfile = {
                id: session.user.id,
                full_name: session.user.user_metadata?.full_name || 
                          session.user.user_metadata?.name || 
                          session.user.email.split('@')[0],
                email: session.user.email,
                role: 'manager' as const, // Default to manager for OAuth users
              }
              
              profile = await auth.upsertProfile(newProfile)
              console.log('Profile created successfully:', profile.email)
            }
            
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

          // Listen for auth changes (this handles OAuth callbacks automatically)
          const { data: authListener } = supabase.auth.onAuthStateChange(async (event, session) => {
            console.log('Auth state changed:', event, session?.user?.email || 'No user')
            
            if (event === 'SIGNED_IN' && session?.user) {
              // User signed in - get/create profile
              try {
                set({ loading: true })
                
                let profile = await auth.getProfile(session.user.id)
                
                // If no profile exists, create one for OAuth users
                if (!profile && session.user.email) {
                  console.log('Creating profile for signed-in user...')
                  
                  const newProfile = {
                    id: session.user.id,
                    full_name: session.user.user_metadata?.full_name || 
                              session.user.user_metadata?.name || 
                              session.user.email.split('@')[0],
                    email: session.user.email,
                    role: 'manager' as const, // Default to manager for OAuth users
                  }
                  
                  profile = await auth.upsertProfile(newProfile)
                  console.log('Profile created successfully:', profile.email)
                }
                
                set({ 
                  session, 
                  user: session.user, 
                  profile,
                  loading: false 
                })
                
                console.log('Auth state updated with profile:', profile?.email)
              } catch (error) {
                console.error('Error fetching/creating profile:', error)
                
                // Still set the session even if profile creation fails
                set({ 
                  session, 
                  user: session.user, 
                  profile: null,
                  loading: false 
                })
              }
            } else if (event === 'SIGNED_OUT') {
              // User signed out
              console.log('User signed out')
              set({ 
                session: null, 
                user: null, 
                profile: null,
                loading: false 
              })
            } else if (event === 'TOKEN_REFRESHED' && session) {
              // Token refreshed, update session
              set({ 
                session, 
                user: session.user 
              })
            }
          })

          // Store the auth listener for cleanup
          // @ts-expect-error - temporary storage for cleanup
          get().authListener = authListener
          
          console.log('Auth store initialization complete')
          
        } catch (error) {
          console.error('Auth initialization error:', error)
          set({ 
            session: null, 
            user: null, 
            profile: null,
            initialized: true,
            loading: false 
          })
          throw error // Re-throw so the callback page can catch it
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