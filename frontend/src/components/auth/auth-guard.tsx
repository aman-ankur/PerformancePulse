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
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Profile Setup Required
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Your profile is being created. Please wait a moment and refresh the page.
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