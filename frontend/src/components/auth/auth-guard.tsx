/**
 * Authentication guard component
 * Protects routes and handles authentication requirements
 */

'use client'

import { useEffect } from 'react'
import { useAuth, useRequireAuth } from '@/lib/auth-store'

interface AuthGuardProps {
  children: React.ReactNode
  requireAuth?: boolean
  requiredRole?: 'manager' | 'team_member'
  fallback?: React.ReactNode
}

export function AuthGuard({ 
  children, 
  requireAuth = true, 
  requiredRole,
  fallback 
}: AuthGuardProps) {
  const authCheck = useRequireAuth(requiredRole)
  const { initialize, loading, initialized } = useAuth()

  // Initialize auth on mount
  useEffect(() => {
    if (!initialized) {
      initialize()
    }
  }, [initialize, initialized])

  // Show loading state while initializing
  if (!initialized || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  // If auth is not required, render children
  if (!requireAuth) {
    return <>{children}</>
  }

  // Handle auth failures
  if (!authCheck.canAccess) {
    if (fallback) {
      return <>{fallback}</>
    }

    switch (authCheck.reason) {
      case 'not_authenticated':
        return <AuthRequired />
      case 'no_profile':
        return <ProfileRequired />
      case 'insufficient_role':
        return <InsufficientRole requiredRole={requiredRole} userRole={authCheck.profile?.role} />
      default:
        return <AuthRequired />
    }
  }

  return <>{children}</>
}

// Component for unauthenticated users
function AuthRequired() {
  const { signIn, loading } = useAuth()

  const handleSignIn = async () => {
    try {
      await signIn()
    } catch (error) {
      console.error('Sign in error:', error)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Sign in to PerformancePulse
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Authentication required to access this page
          </p>
        </div>
        
        <div className="mt-8">
          <button
            onClick={handleSignIn}
            disabled={loading}
            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <>
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Continue with Google
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

// Component for users without profile
function ProfileRequired() {
  const { initialize, session, loading } = useAuth()
  
  // Auto-retry profile creation
  useEffect(() => {
    if (session && !loading) {
      const retryProfileCreation = async () => {
        try {
          console.log('Retrying profile creation...')
          await initialize()
        } catch (error) {
          console.error('Profile creation retry failed:', error)
        }
      }
      
      // Retry after 2 seconds
      const timeout = setTimeout(retryProfileCreation, 2000)
      return () => clearTimeout(timeout)
    }
  }, [session, loading, initialize])

  const handleRetry = async () => {
    try {
      await initialize()
    } catch (error) {
      console.error('Manual profile creation retry failed:', error)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <div className="animate-pulse">
            <div className="rounded-full bg-indigo-100 h-16 w-16 mx-auto mb-4 flex items-center justify-center">
              <svg className="h-8 w-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>
          
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Setting up your profile
          </h2>
          <p className="mt-2 text-sm text-gray-600">
                         We&apos;re creating your manager profile. This usually takes just a moment...
          </p>
          
          {loading && (
            <div className="mt-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600 mx-auto"></div>
            </div>
          )}
          
          <div className="mt-6 space-y-2">
            <button
              onClick={handleRetry}
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50"
            >
              {loading ? 'Creating profile...' : 'Retry setup'}
            </button>
            
            <button
              onClick={() => window.location.reload()}
              className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-lg font-medium"
            >
              Refresh page
            </button>
          </div>
          
          <p className="mt-4 text-xs text-gray-500">
            If this persists, please check your internet connection or try signing out and back in.
          </p>
        </div>
      </div>
    </div>
  )
}

// Component for insufficient role
function InsufficientRole({ requiredRole, userRole }: { requiredRole?: string, userRole?: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Access Denied
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            This page requires {requiredRole} role access.
            {userRole && ` Your current role: ${userRole}`}
          </p>
        </div>
      </div>
    </div>
  )
} 