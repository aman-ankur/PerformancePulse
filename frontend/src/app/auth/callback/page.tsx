/**
 * OAuth callback page
 * Handles Google OAuth redirect and session establishment
 */

'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'
import { useAuthStore } from '@/lib/auth-store'

export default function AuthCallback() {
  const router = useRouter()
  const { setSession } = useAuthStore()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const handleAuthCallback = async () => {
      try {
        // Handle the OAuth callback
        const { data, error } = await supabase.auth.getSession()
        
        if (error) {
          throw error
        }
        
        if (data.session) {
          // Update auth store
          setSession(data.session)
          setStatus('success')
          
          // Redirect to dashboard after short delay
          setTimeout(() => {
            router.push('/dashboard')
          }, 2000)
        } else {
          throw new Error('No session found')
        }
      } catch (err) {
        console.error('Auth callback error:', err)
        setError(err instanceof Error ? err.message : 'Authentication failed')
        setStatus('error')
        
        // Redirect to home page after error
        setTimeout(() => {
          router.push('/')
        }, 3000)
      }
    }

    handleAuthCallback()
  }, [router, setSession])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            {status === 'loading' && 'Completing sign in...'}
            {status === 'success' && 'Sign in successful!'}
            {status === 'error' && 'Sign in failed'}
          </h2>
          
          <div className="mt-4">
            {status === 'loading' && (
              <div className="flex justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              </div>
            )}
            
            {status === 'success' && (
              <div className="text-green-600">
                <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <p className="mt-2 text-sm text-gray-600">
                  Redirecting to dashboard...
                </p>
              </div>
            )}
            
            {status === 'error' && (
              <div className="text-red-600">
                <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                <p className="mt-2 text-sm text-gray-600">
                  {error || 'An error occurred during authentication'}
                </p>
                <p className="mt-1 text-xs text-gray-500">
                  Redirecting to home page...
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
} 