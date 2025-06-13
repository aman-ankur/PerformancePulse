/**
 * Team Member List Component
 * Displays team members with consent status and management actions
 */

'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-store'
import { ConsentManagementDialog } from './consent-management-dialog'
import { AddMemberDialog } from './add-member-dialog'

interface TeamMember {
  id: string
  full_name: string
  email: string
  role: 'manager' | 'team_member'
  created_at: string
  updated_at: string
}

interface ConsentStatus {
  member_id: string
  gitlab_commits: boolean
  gitlab_merge_requests: boolean
  jira_tickets: boolean
  jira_comments: boolean
  created_at: string
  updated_at: string
}

interface NewTeamMember {
  full_name: string
  email: string
  role: 'team_member'
}

export function TeamMemberList() {
  const { profile } = useAuth()
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [consentData, setConsentData] = useState<Record<string, ConsentStatus>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAddMember, setShowAddMember] = useState(false)
  const [showConsentDialog, setShowConsentDialog] = useState(false)
  const [selectedMember, setSelectedMember] = useState<TeamMember | null>(null)

  // Load team members and their consent status
  useEffect(() => {
    if (profile?.role === 'manager') {
      loadTeamData()
    }
  }, [profile])

  const loadTeamData = async () => {
    try {
      setLoading(true)
      // TODO: Replace with actual API calls
      // For now, we'll simulate the data structure
      
      // Simulate team members data
      const mockTeamMembers: TeamMember[] = [
        {
          id: 'tm-1',
          full_name: 'Alice Johnson',
          email: 'alice.johnson@company.com',
          role: 'team_member',
          created_at: '2025-01-01T10:00:00Z',
          updated_at: '2025-01-01T10:00:00Z'
        },
        {
          id: 'tm-2',
          full_name: 'Bob Smith',
          email: 'bob.smith@company.com',
          role: 'team_member',
          created_at: '2025-01-01T11:00:00Z',
          updated_at: '2025-01-01T11:00:00Z'
        }
      ]

      // Simulate consent data
      const mockConsentData: Record<string, ConsentStatus> = {
        'tm-1': {
          member_id: 'tm-1',
          gitlab_commits: true,
          gitlab_merge_requests: true,
          jira_tickets: false,
          jira_comments: false,
          created_at: '2025-01-01T10:00:00Z',
          updated_at: '2025-01-01T10:00:00Z'
        },
        'tm-2': {
          member_id: 'tm-2',
          gitlab_commits: false,
          gitlab_merge_requests: false,
          jira_tickets: true,
          jira_comments: true,
          created_at: '2025-01-01T11:00:00Z',
          updated_at: '2025-01-01T11:00:00Z'
        }
      }

      setTeamMembers(mockTeamMembers)
      setConsentData(mockConsentData)
    } catch (err) {
      setError('Failed to load team data')
      console.error('Error loading team data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddMember = async (memberData: NewTeamMember) => {
    // TODO: Implement actual API call
    console.log('Adding member:', memberData)
    
    // Simulate API delay and response
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // For demo purposes, add the member to local state
    const newMember: TeamMember = {
      id: `tm-${Date.now()}`,
      ...memberData,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    
    setTeamMembers(prev => [...prev, newMember])
    
    // Initialize consent data for new member
    setConsentData(prev => ({
      ...prev,
      [newMember.id]: {
        member_id: newMember.id,
        gitlab_commits: false,
        gitlab_merge_requests: false,
        jira_tickets: false,
        jira_comments: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    }))
  }

  const handleConsentUpdate = async (memberId: string, updatedConsent: Partial<ConsentStatus>) => {
    // TODO: Implement actual API call
    console.log('Updating consent for member:', memberId, updatedConsent)
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Update local state for demo
    setConsentData(prev => ({
      ...prev,
      [memberId]: {
        ...prev[memberId],
        ...updatedConsent,
        updated_at: new Date().toISOString()
      }
    }))
  }

  const handleManageConsent = (member: TeamMember) => {
    setSelectedMember(member)
    setShowConsentDialog(true)
  }

  const getConsentSummary = (memberId: string) => {
    const consent = consentData[memberId]
    if (!consent) return { total: 0, granted: 0 }
    
    const total = 4 // gitlab_commits, gitlab_merge_requests, jira_tickets, jira_comments
    const granted = [
      consent.gitlab_commits,
      consent.gitlab_merge_requests,
      consent.jira_tickets,
      consent.jira_comments
    ].filter(Boolean).length
    
    return { total, granted }
  }

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4 w-1/4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-gray-100 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <div className="text-center py-8">
          <div className="text-red-600 mb-2">⚠️</div>
          <p className="text-red-800 font-medium">Error Loading Team Data</p>
          <p className="text-red-600 text-sm mt-1">{error}</p>
          <button
            onClick={loadTeamData}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Team Members</h3>
            <button 
              onClick={() => setShowAddMember(true)}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Add Member
            </button>
          </div>
        </div>

        <div className="divide-y divide-gray-200">
          {teamMembers.length === 0 ? (
            <div className="px-6 py-8 text-center">
              <div className="text-gray-400 text-4xl mb-2">👥</div>
              <p className="text-gray-500 font-medium">No team members yet</p>
              <p className="text-gray-400 text-sm mt-1">Add team members to start collecting evidence</p>
            </div>
          ) : (
            teamMembers.map((member) => {
              const { total, granted } = getConsentSummary(member.id)
              const consentPercentage = total > 0 ? Math.round((granted / total) * 100) : 0
              
              return (
                <div key={member.id} className="px-6 py-4 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        <div className="h-10 w-10 bg-indigo-100 rounded-full flex items-center justify-center">
                          <span className="text-indigo-600 font-medium text-sm">
                            {member.full_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                          </span>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{member.full_name}</p>
                        <p className="text-sm text-gray-500">{member.email}</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      {/* Consent Status */}
                      <div className="text-right">
                        <div className="flex items-center space-x-2">
                          <div className={`h-2 w-2 rounded-full ${
                            consentPercentage === 100 ? 'bg-green-400' :
                            consentPercentage > 50 ? 'bg-yellow-400' :
                            consentPercentage > 0 ? 'bg-orange-400' : 'bg-red-400'
                          }`}></div>
                          <span className="text-sm text-gray-600">
                            {granted}/{total} consents
                          </span>
                        </div>
                        <p className="text-xs text-gray-400">
                          {consentPercentage}% coverage
                        </p>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center space-x-2">
                        <button 
                          onClick={() => handleManageConsent(member)}
                          className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                        >
                          Manage Consent
                        </button>
                        <button className="text-gray-400 hover:text-gray-600 text-sm">
                          •••
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Consent Details */}
                  <div className="mt-3 ml-14">
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(consentData[member.id] || {}).map(([key, value]) => {
                        if (typeof value !== 'boolean') return null
                        
                        const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                        return (
                          <span
                            key={key}
                            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              value
                                ? 'bg-green-100 text-green-800'
                                : 'bg-gray-100 text-gray-600'
                            }`}
                          >
                            {value ? '✓' : '○'} {label}
                          </span>
                        )
                      })}
                    </div>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>

      {/* Dialogs */}
      <AddMemberDialog
        isOpen={showAddMember}
        onClose={() => setShowAddMember(false)}
        onAdd={handleAddMember}
      />

      <ConsentManagementDialog
        isOpen={showConsentDialog}
        onClose={() => setShowConsentDialog(false)}
        member={selectedMember}
        currentConsent={selectedMember ? consentData[selectedMember.id] : null}
        onSave={handleConsentUpdate}
      />
    </>
  )
} 