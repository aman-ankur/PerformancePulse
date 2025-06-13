/**
 * OAuth callback page
 * Handles Google OAuth redirect and session establishment
 */

'use client'

import { useEffect, useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { useAuth } from '@/lib/auth-store'

export default function AuthCallback() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <AuthCallbackContent />
    </Suspense>
  )
}

function LoadingFallback() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading callback...</p>
      </div>
    </div>
  )
}

function AuthCallbackContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { isAuthenticated, profile, loading, initialize } = useAuth()
  const [timeoutReached, setTimeoutReached] = useState(false)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    const processCallback = async () => {
      if (processing) return
      setProcessing(true)
      
      try {
        const code = searchParams.get('code')
        console.log('Processing OAuth callback with code:', code ? 'Present' : 'Missing')
        
        if (!code) {
          throw new Error('No authorization code in callback URL')
        }

        // Let Supabase process the callback automatically
        setTimeout(async () => {
          try {
            const { data: { session }, error } = await supabase.auth.getSession()
            
            if (error) throw error
            
            if (session) {
              console.log('OAuth session established, initializing auth store...')
              await initialize()
            } else {
              // Fallback: Try manual code exchange
              const { data, error: exchangeError } = await supabase.auth.exchangeCodeForSession(code)
              
              if (exchangeError) throw exchangeError
              
              if (data.session) {
                console.log('Manual exchange successful, initializing auth store...')
                await initialize()
              } else {
                throw new Error('No session from manual exchange')
              }
            }
          } catch (error) {
            console.error('Callback processing error:', error)
            setTimeout(() => {
              router.push('/?error=callback_failed')
            }, 3000)
          }
        }, 1000)

      } catch (error) {
        console.error('Fatal callback error:', error)
        setTimeout(() => {
          router.push('/?error=callback_failed')
        }, 3000)
      }
    }

    processCallback()

    // Set timeout
    const timeout = setTimeout(() => {
      setTimeoutReached(true)
    }, 15000) // Reduced to 15 seconds

    return () => clearTimeout(timeout)
  }, [searchParams, initialize, router, processing])

  useEffect(() => {
    // Monitor auth state changes and redirect when ready
    if (isAuthenticated && profile) {
      console.log('Auth complete, redirecting to dashboard...')
      setTimeout(() => {
        router.push('/dashboard')
      }, 500)
    } else if (isAuthenticated && !profile && !loading) {
      // Profile creation might have failed, try again
      console.log('User authenticated but no profile, retrying...')
      setTimeout(() => {
        initialize()
      }, 2000)
    } else if (timeoutReached && !isAuthenticated) {
      console.log('OAuth timeout, redirecting to home')
      router.push('/?error=auth_timeout')
    }
  }, [isAuthenticated, profile, loading, router, timeoutReached, initialize])

  const handleRetry = () => {
    setTimeoutReached(false)
    setProcessing(false)
    initialize()
  }

  const handleGoHome = () => {
    router.push('/')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          {!timeoutReached ? (
            <>
              <div className="animate-pulse mb-6">
                <div className="rounded-full bg-indigo-100 h-16 w-16 mx-auto flex items-center justify-center">
                  <svg className="h-8 w-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </div>
              
              <h2 className="text-3xl font-extrabold text-gray-900 mb-4">
                Completing sign in...
              </h2>
              
              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-center justify-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
                  <span>Processing authentication</span>
                </div>
                
                {isAuthenticated ? (
                  <div className="flex items-center justify-center space-x-2 text-green-600">
                    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Authenticated successfully</span>
                  </div>
                ) : (
                  <div className="text-gray-500">Authenticating with Google...</div>
                )}
                
                {isAuthenticated && !profile && (
                  <div className="flex items-center justify-center space-x-2 text-blue-600">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <span>Setting up your profile</span>
                  </div>
                )}
                
                {isAuthenticated && profile && (
                  <div className="flex items-center justify-center space-x-2 text-green-600">
                    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Profile ready - redirecting...</span>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <div className="mb-6">
                <div className="rounded-full bg-red-100 h-16 w-16 mx-auto flex items-center justify-center">
                  <svg className="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.498 0L4.316 15.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
              </div>
              
              <h2 className="text-3xl font-extrabold text-gray-900 mb-4">
                Authentication taking longer than expected
              </h2>
              
              <p className="text-gray-600 mb-6">
                The sign-in process is taking longer than usual. This might be due to a network issue.
              </p>
              
              <div className="space-y-3">
                <button
                  onClick={handleRetry}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium"
                >
                  Try Again
                </button>
                
                <button
                  onClick={handleGoHome}
                  className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-lg font-medium"
                >
                  Return to Home
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
} 