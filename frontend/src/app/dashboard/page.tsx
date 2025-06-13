/**
 * Manager Dashboard
 * Main interface for managers to view and manage their teams
 */

'use client'

import { useState } from 'react'
import { AuthGuard } from '@/components/auth/auth-guard'
import { useAuth } from '@/lib/auth-store'
import { TeamMemberList } from '@/components/team/team-member-list'

import { AddMemberDialog } from '@/components/team/add-member-dialog'

interface NewTeamMember {
  full_name: string
  email: string
  role: 'team_member'
}

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
              <h1 className="text-2xl font-bold text-gray-900">PerformancePulse</h1>
              <span className="ml-4 px-3 py-1 text-xs font-medium bg-indigo-100 text-indigo-800 rounded-full">
                Manager Dashboard
              </span>
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
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Welcome to your dashboard, {profile?.full_name?.split(' ')[0]}!
            </h2>
            <p className="text-lg text-gray-600">
              Manage your team&apos;s performance evidence and prepare for meaningful conversations.
            </p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <StatsCard
              title="Team Members"
              value="2"
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
          <div className="bg-white shadow rounded-lg p-6 mb-8">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <ActionButton
                title="Add Team Member"
                description="Invite a new team member"
                icon="➕"
                onClick={() => setShowAddMember(true)}
              />
              <ActionButton
                title="Collect Evidence"
                description="Gather performance data"
                icon="🔍"
                onClick={() => console.log('Collect evidence')}
              />
              <ActionButton
                title="Generate Report"
                description="Create meeting preparation"
                icon="📄"
                onClick={() => console.log('Generate report')}
              />
            </div>
          </div>

          {/* Team Management */}
          <div className="mb-8">
            <TeamMemberList />
          </div>

          {/* Recent Activity */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
            <div className="text-center py-8 text-gray-500">
              <p>No recent activity</p>
              <p className="text-sm mt-2">Start by adding team members to see activity here.</p>
            </div>
          </div>
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
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
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
      </div>
    </div>
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
      <div className="flex items-center mb-2">
        <span className="text-xl mr-3">{icon}</span>
        <h4 className="font-medium text-gray-900">{title}</h4>
      </div>
      <p className="text-sm text-gray-600">{description}</p>
    </button>
  )
} 