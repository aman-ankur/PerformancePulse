/**
 * Manager Dashboard
 * Main interface for managers to view and manage their teams
 * Now includes LLM-enhanced performance insights
 */

'use client'

import { useState, useEffect } from 'react'
import { AuthGuard } from '@/components/auth/auth-guard'
import { useAuth } from '@/lib/auth-store'
import { TeamMemberList } from '@/components/team/team-member-list'
import { LLMPerformanceDashboard } from '@/components/dashboard/llm-performance-dashboard'
import { AddMemberDialog } from '@/components/team/add-member-dialog'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
// import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Brain, Users, Settings, Sparkles } from 'lucide-react'
import { team } from '@/lib/supabase'
import { ErrorBoundary } from 'react-error-boundary'

interface NewTeamMember {
  full_name: string
  email: string
  role: 'team_member'
}

function ErrorFallback({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) {
  return (
    <div className="p-4 bg-red-50 text-red-700 rounded-lg">
      <p>Something went wrong:</p>
      <pre className="mt-2 text-sm">{error.message}</pre>
      <button
        onClick={resetErrorBoundary}
        className="mt-4 px-4 py-2 bg-red-100 text-red-800 rounded hover:bg-red-200"
      >
        Try again
      </button>
    </div>
  )
}

function DashboardContent() {
  const { profile, signOut } = useAuth()
  const [showAddMember, setShowAddMember] = useState(false)
  const [teamMembers, setTeamMembers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadTeamData()
  }, [])

  const loadTeamData = async () => {
    try {
      setLoading(true)
      setError(null)
      const members = await team.getTeamMembers()
      setTeamMembers(members)
    } catch (err) {
      console.error('Error loading team data:', err)
      setError('Failed to load team data')
    } finally {
      setLoading(false)
    }
  }

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Sign out error:', error)
    }
  }

  const handleAddMember = async (memberData: NewTeamMember) => {
    try {
      await team.addTeamMember(memberData)
      await loadTeamData()
      setShowAddMember(false)
    } catch (error) {
      console.error('Error adding team member:', error)
      throw error
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
                <Brain className="h-8 w-8 text-purple-600" />
                <span>PerformancePulse</span>
              </h1>
              <div className="ml-4 flex items-center space-x-2">
                <Badge className="bg-purple-100 text-purple-800">
                  Manager Dashboard
                </Badge>
                <Badge variant="outline" className="bg-green-50 text-green-700">
                  LLM Enhanced
                </Badge>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-700">
                Welcome, {profile?.full_name}
              </div>
              <button
                onClick={handleSignOut}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome Section */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
              <span>Welcome to your dashboard, {profile?.full_name?.split(' ')[0]}!</span>
              <Sparkles className="h-8 w-8 text-yellow-500" />
            </h2>
            <p className="text-lg text-gray-600">
              AI-powered performance insights for meaningful team conversations.
            </p>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex items-center justify-center p-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
              <span className="ml-3">Loading team data...</span>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="flex items-center">
                <svg className="h-5 w-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          )}

          {/* Tabbed Interface */}
          {!loading && !error && (
            <Tabs defaultValue="performance" className="w-full">
              <TabsList className="grid w-full grid-cols-2 lg:w-[400px]">
                <TabsTrigger value="performance" className="flex items-center space-x-2">
                  <Brain className="h-4 w-4" />
                  <span>Performance Insights</span>
                </TabsTrigger>
                <TabsTrigger value="team" className="flex items-center space-x-2">
                  <Users className="h-4 w-4" />
                  <span>Team Management</span>
                </TabsTrigger>
              </TabsList>

              {/* Performance Insights Tab */}
              <TabsContent value="performance" className="mt-6">
                <ErrorBoundary FallbackComponent={ErrorFallback} onReset={loadTeamData}>
                  <LLMPerformanceDashboard 
                    teamMembers={teamMembers}
                    managerName={profile?.full_name || ''}
                  />
                </ErrorBoundary>
              </TabsContent>

              {/* Team Management Tab */}
              <TabsContent value="team" className="mt-6">
                <ErrorBoundary FallbackComponent={ErrorFallback} onReset={loadTeamData}>
                  <div className="space-y-8">
                    {/* Quick Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <StatsCard
                        title="Team Members"
                        value={teamMembers.length.toString()}
                        description="Active team members"
                        icon="👥"
                      />
                      <StatsCard
                        title="Evidence Items"
                        value="0"
                        description="Collected this month"
                        icon="📊"
                      />
                      <StatsCard
                        title="Consent Rate"
                        value={`${Math.round((teamMembers.filter(m => m.role === 'team_member').length / Math.max(teamMembers.length, 1)) * 100)}%`}
                        description="Team members consented"
                        icon="✅"
                      />
                    </div>

                    {/* Quick Actions */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                          <Settings className="h-5 w-5" />
                          <span>Quick Actions</span>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                          <ActionButton
                            title="Add Team Member"
                            description="Invite a new team member"
                            icon="➕"
                            onClick={() => setShowAddMember(true)}
                          />
                          <ActionButton
                            title="View Consents"
                            description="Manage data collection consent"
                            icon="🔒"
                            onClick={() => console.log('View consents')}
                          />
                          <ActionButton
                            title="Export Data"
                            description="Download team performance data"
                            icon="📄"
                            onClick={() => console.log('Export data')}
                          />
                        </div>
                      </CardContent>
                    </Card>

                    {/* Team Member List */}
                    <TeamMemberList />

                    {/* Recent Activity */}
                    <Card>
                      <CardHeader>
                        <CardTitle>Recent Activity</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-center py-8 text-gray-500">
                          <p>No recent activity</p>
                          <p className="text-sm mt-2">Activity will appear here as you use the LLM features.</p>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </ErrorBoundary>
              </TabsContent>
            </Tabs>
          )}
        </div>
      </main>

      {/* Dialogs */}
      <AddMemberDialog
        isOpen={showAddMember}
        onClose={() => setShowAddMember(false)}
        onAdd={handleAddMember}
      />
    </div>
  )
}

function StatsCard({ title, value, description, icon }: {
  title: string
  value: string
  description: string
  icon: string
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          {title}
        </CardTitle>
        <div className="h-4 w-4 text-muted-foreground">
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">
          {description}
        </p>
      </CardContent>
    </Card>
  )
}

function ActionButton({ title, description, icon, onClick }: {
  title: string
  description: string
  icon: string
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="text-left p-4 border border-gray-200 rounded-lg hover:border-indigo-300 hover:shadow-md transition-all duration-200"
    >
      <div className="flex items-center space-x-3">
        <span className="text-xl">{icon}</span>
        <div>
          <h3 className="text-sm font-medium text-gray-900">{title}</h3>
          <p className="text-xs text-gray-500">{description}</p>
        </div>
      </div>
    </button>
  )
}

export default function Dashboard() {
  return (
    <AuthGuard>
      <ErrorBoundary FallbackComponent={ErrorFallback}>
        <DashboardContent />
      </ErrorBoundary>
    </AuthGuard>
  )
} 