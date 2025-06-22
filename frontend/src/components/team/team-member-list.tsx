/**
 * Team Member List Component
 * Displays and manages team members and their consent status
 */

'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-store'
import { team } from '@/lib/supabase'
import { type TeamMember, type ConsentStatus } from '@/lib/supabase'
import { ConsentManagementDialog } from './consent-management-dialog'
import { AddMemberDialog } from './add-member-dialog'
import { Button } from '../ui/button'
import { Card } from '../ui/card'
import { ErrorBoundary } from 'react-error-boundary'

function ErrorFallback({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) {
  return (
    <div className="p-4 bg-red-50 text-red-700 rounded-lg">
      <p>Something went wrong:</p>
      <pre className="mt-2 text-sm">{error.message}</pre>
      <Button onClick={resetErrorBoundary} className="mt-4">
        Try again
      </Button>
    </div>
  )
}

export function TeamMemberList() {
  const { profile } = useAuth()
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [consentData, setConsentData] = useState<Record<string, ConsentStatus | null>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAddMember, setShowAddMember] = useState(false)
  const [showConsentDialog, setShowConsentDialog] = useState(false)
  const [selectedMember, setSelectedMember] = useState<TeamMember | null>(null)

  // Load team members and their consent status
  const loadTeamData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load team members
      const members = await team.getTeamMembers()
      setTeamMembers(members)

      // Load consent data for all members
      const consents = await team.getTeamConsent()
      
      // Group consents by member_id, handle potential null values
      const groupedConsents = members.reduce((acc, member) => {
        const memberConsent = Array.isArray(consents) 
          ? consents.find(c => c.member_id === member.id)
          : null
        acc[member.id] = memberConsent || null
        return acc
      }, {} as Record<string, ConsentStatus | null>)
      
      setConsentData(groupedConsents)
    } catch (err) {
      console.error('Failed to load team data:', err)
      setError('Failed to load team data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTeamData()
  }, [])

  const handleAddMember = async (newMember: Omit<TeamMember, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      await team.addTeamMember(newMember)
      await loadTeamData()
      setShowAddMember(false)
    } catch (err) {
      console.error('Failed to add team member:', err)
      throw err
    }
  }

  const handleConsentUpdate = async (memberId: string, updatedConsent: Partial<ConsentStatus>) => {
    try {
      const result = await team.updateConsent(memberId, updatedConsent)
      setConsentData(prev => ({
        ...prev,
        [memberId]: result
      }))
    } catch (err) {
      console.error('Error updating consent:', err)
      throw err
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        <span className="ml-3">Loading team data...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-700 rounded-lg">
        {error}
        <Button onClick={loadTeamData} className="ml-4">
          Retry
        </Button>
      </div>
    )
  }

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback} onReset={loadTeamData}>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Team Members</h2>
          {profile?.role === 'manager' && (
            <Button onClick={() => setShowAddMember(true)}>
              Add Team Member
            </Button>
          )}
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {teamMembers.map((member) => (
            <Card key={member.id} className="p-4">
              <div className="flex flex-col space-y-2">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium">{member.full_name}</h3>
                    <p className="text-sm text-gray-600">{member.email}</p>
                  </div>
                  {profile?.role === 'manager' && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setSelectedMember(member)
                        setShowConsentDialog(true)
                      }}
                    >
                      Manage Consent
                    </Button>
                  )}
                </div>
                <div className="text-sm">
                  <p>Role: {member.role}</p>
                  {member.gitlab_username && (
                    <p>GitLab: {member.gitlab_username}</p>
                  )}
                  {member.jira_username && (
                    <p>Jira: {member.jira_username}</p>
                  )}
                </div>
                <div className="text-sm text-gray-600">
                  <p>
                    Consent Status:{' '}
                    {consentData[member.id] ? (
                      <span className="text-green-600">Active</span>
                    ) : (
                      <span className="text-yellow-600">Pending</span>
                    )}
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {showAddMember && (
          <AddMemberDialog
            isOpen={showAddMember}
            onClose={() => setShowAddMember(false)}
            onAdd={handleAddMember}
          />
        )}

        {showConsentDialog && selectedMember && (
          <ConsentManagementDialog
            isOpen={showConsentDialog}
            onClose={() => {
              setShowConsentDialog(false)
              setSelectedMember(null)
            }}
            member={selectedMember}
            currentConsent={consentData[selectedMember.id]}
            onSave={handleConsentUpdate}
          />
        )}
      </div>
    </ErrorBoundary>
  )
} 