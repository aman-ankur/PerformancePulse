/**
 * PerformancePulse Home Page
 * Landing page with authentication integration
 */

'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { AuthGuard } from '@/components/auth/auth-guard'
import { useAuth } from '@/lib/auth-store'

export default function Home() {
  return (
    <AuthGuard requireAuth={false}>
      <HomePage />
    </AuthGuard>
  )
}

function HomePage() {
  const router = useRouter()
  const { isAuthenticated, isManager, signIn, loading } = useAuth()

  // Redirect authenticated managers to dashboard
  useEffect(() => {
    if (isAuthenticated && isManager) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, isManager, router])

  const handleGetStarted = async () => {
    if (isAuthenticated) {
      router.push('/dashboard')
    } else {
      try {
        await signIn()
      } catch (error) {
        console.error('Sign in error:', error)
      }
    }
  }

  const handleDevBypass = () => {
    // Development bypass - go directly to dashboard for testing
    router.push('/dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50">
      {/* Header */}
      <header className="relative bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">PerformancePulse</h1>
              <span className="ml-3 px-2 py-1 text-xs font-medium bg-indigo-100 text-indigo-800 rounded">
                Beta
              </span>
            </div>
            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <button
                  onClick={() => router.push('/dashboard')}
                  className="text-indigo-600 hover:text-indigo-700 font-medium"
                >
                  Go to Dashboard
                </button>
              ) : (
                <button
                  onClick={handleGetStarted}
                  disabled={loading}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50"
                >
                  {loading ? 'Loading...' : 'Sign In'}
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Transform Team Performance
            <span className="block text-indigo-600">with Evidence-Based Insights</span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            PerformancePulse automatically collects and organizes evidence from GitLab and Jira, 
            helping managers prepare for meaningful performance conversations in minutes, not hours.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <button
              onClick={handleGetStarted}
              disabled={loading}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-lg text-lg font-medium disabled:opacity-50 flex items-center justify-center"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              ) : (
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
              )}
              {isAuthenticated ? 'Go to Dashboard' : 'Get Started with Google'}
            </button>
            
            <button className="border border-gray-300 hover:border-gray-400 text-gray-700 px-8 py-4 rounded-lg text-lg font-medium">
              Learn More
            </button>
          </div>

          {/* OAuth Ready Notice */}
          <div className="mt-8 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center justify-center mb-2">
              <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <h3 className="text-lg font-semibold text-green-900">Ready to Go!</h3>
            </div>
            <p className="text-green-800 mb-3">
                             Google OAuth is configured. Click <strong>&quot;Get Started with Google&quot;</strong> above to sign in and explore your team management dashboard.
            </p>
            <button
              onClick={handleDevBypass}
              className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded text-sm"
            >
              🛠️ Dev Bypass (Keep for testing)
            </button>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
            <FeatureCard
              icon="🔍"
              title="Automated Evidence Collection"
              description="Automatically gather commits, merge requests, and Jira tickets with team member consent."
            />
            <FeatureCard
              icon="🤖"
              title="AI-Powered Insights"
              description="Claude AI analyzes evidence to highlight achievements and collaboration patterns."
            />
            <FeatureCard
              icon="📋"
              title="Meeting Preparation"
              description="Generate structured talking points for performance reviews in under 30 minutes."
            />
          </div>

          {/* Privacy Notice */}
          <div className="mt-16 p-6 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center justify-center mb-2">
              <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
              </svg>
              <h3 className="text-lg font-semibold text-green-900">Privacy First</h3>
            </div>
            <p className="text-green-800">
              All data collection requires explicit consent from team members. 
              Your team&apos;s data is secure and only accessible to authorized managers.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}

function FeatureCard({ icon, title, description }: {
  icon: string
  title: string
  description: string
}) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <div className="text-3xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  )
}
