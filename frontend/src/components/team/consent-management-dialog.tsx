/**
 * Consent Management Dialog
 * Interface for managers to update team member consent settings
 */

'use client'

import { useState } from 'react'

interface ConsentStatus {
  member_id: string
  gitlab_commits: boolean
  gitlab_merge_requests: boolean
  jira_tickets: boolean
  jira_comments: boolean
  created_at: string
  updated_at: string
}

interface TeamMember {
  id: string
  full_name: string
  email: string
  role: 'manager' | 'team_member'
}

interface ConsentManagementDialogProps {
  isOpen: boolean
  onClose: () => void
  member: TeamMember | null
  currentConsent: ConsentStatus | null
  onSave: (memberId: string, updatedConsent: Partial<ConsentStatus>) => Promise<void>
}

export function ConsentManagementDialog({
  isOpen,
  onClose,
  member,
  currentConsent,
  onSave
}: ConsentManagementDialogProps) {
  const [consent, setConsent] = useState<Partial<ConsentStatus>>(
    currentConsent || {
      gitlab_commits: false,
      gitlab_merge_requests: false,
      jira_tickets: false,
      jira_comments: false
    }
  )
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSave = async () => {
    if (!member) return

    try {
      setSaving(true)
      setError(null)
      await onSave(member.id, consent)
      onClose()
    } catch (err) {
      setError('Failed to update consent settings')
      console.error('Error updating consent:', err)
    } finally {
      setSaving(false)
    }
  }

  const consentOptions = [
    {
      key: 'gitlab_commits' as keyof ConsentStatus,
      title: 'GitLab Commits',
      description: 'Collect commit history and code contribution data',
      icon: '🔧'
    },
    {
      key: 'gitlab_merge_requests' as keyof ConsentStatus,
      title: 'GitLab Merge Requests',
      description: 'Collect merge request activity and code review participation',
      icon: '🔀'
    },
    {
      key: 'jira_tickets' as keyof ConsentStatus,
      title: 'Jira Tickets',
      description: 'Collect ticket creation, assignment, and completion data',
      icon: '🎫'
    },
    {
      key: 'jira_comments' as keyof ConsentStatus,
      title: 'Jira Comments',
      description: 'Collect comments and collaboration on tickets',
      icon: '💬'
    }
  ]

  if (!isOpen || !member) return null

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              Manage Data Consent
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Configure data collection permissions for {member.full_name}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Privacy Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-blue-800">Privacy & Consent</h4>
              <p className="text-sm text-blue-700 mt-1">
                Data collection requires explicit consent. Team members can revoke consent at any time.
                Only anonymized and aggregated data is used for performance insights.
              </p>
            </div>
          </div>
        </div>

        {/* Error Message */}
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

        {/* Consent Options */}
        <div className="space-y-4 mb-6">
          {consentOptions.map((option) => (
            <div key={option.key} className="flex items-start space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
              <div className="flex-shrink-0 mt-1">
                <span className="text-xl">{option.icon}</span>
              </div>
              <div className="flex-grow">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">{option.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{option.description}</p>
                  </div>
                  <div className="ml-4">
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={Boolean(consent[option.key]) || false}
                        onChange={(e) => setConsent(prev => ({
                          ...prev,
                          [option.key]: e.target.checked
                        }))}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Consent Summary</h4>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-600">
              <span className="font-medium">
                {Object.values(consent).filter(Boolean).length} of {consentOptions.length}
              </span> data sources enabled
            </div>
            <div className="flex-grow bg-gray-200 rounded-full h-2">
              <div 
                className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                style={{ 
                  width: `${(Object.values(consent).filter(Boolean).length / consentOptions.length) * 100}%` 
                }}
              ></div>
            </div>
            <div className="text-sm font-medium text-gray-900">
              {Math.round((Object.values(consent).filter(Boolean).length / consentOptions.length) * 100)}%
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end space-x-3">
          <button
            onClick={onClose}
            disabled={saving}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Saving...
              </>
            ) : (
              'Save Changes'
            )}
          </button>
        </div>
      </div>
    </div>
  )
} 