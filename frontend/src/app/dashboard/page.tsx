/**
 * Manager Dashboard
 * Main interface for managers to view and manage their teams
 * Now includes LLM-enhanced performance insights
 */

'use client'

import { useState } from 'react'
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

interface NewTeamMember {
  full_name: string
  email: string
  role: 'team_member'
}

// Mock team members for demo - in production this would come from the API
const MOCK_TEAM_MEMBERS = [
  {
    id: 'tm-1',
    full_name: 'Alice Johnson',
    email: 'alice.johnson@example.com',
    role: 'team_member' as const,
    created_at: '2025-01-01T10:00:00Z',
    updated_at: '2025-01-01T10:00:00Z'
  },
  {
    id: 'tm-2',
    full_name: 'Bob Smith',
    email: 'bob.smith@example.com',
    role: 'team_member' as const,
    created_at: '2025-01-01T11:00:00Z',
    updated_at: '2025-01-01T11:00:00Z'
  }
]

export default function Dashboard() {
  return (
    <AuthGuard requiredRole="manager">
      <DashboardContent />
    </AuthGuard>
  )
}

function DashboardContent() {
  const { profile, signOut } = useAuth()
  const [showAddMember, setShowAddMember] = useState(false)

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Sign out error:', error)
    }
  }

  const handleAddMember = async (memberData: NewTeamMember) => {
    // TODO: Implement actual API call
    console.log('Adding member:', memberData)
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    // In real implementation, this would call the backend API
    throw new Error('API integration pending')
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

          {/* Tabbed Interface */}
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
            <TabsContent value="performance" className="mt-8">
              <LLMPerformanceDashboard 
                teamMembers={MOCK_TEAM_MEMBERS}
                managerName={profile?.full_name || 'Manager'}
              />
            </TabsContent>

            {/* Team Management Tab */}
            <TabsContent value="team" className="mt-8">
              <div className="space-y-8">
                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <StatsCard
                    title="Team Members"
                    value={MOCK_TEAM_MEMBERS.length.toString()}
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
                    value="50%"
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

                {/* Team Management */}
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
            </TabsContent>
          </Tabs>
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
      <CardContent className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <span className="text-2xl">{icon}</span>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
              <dd className="text-lg font-medium text-gray-900">{value}</dd>
              <dd className="text-sm text-gray-500">{description}</dd>
            </dl>
          </div>
        </div>
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