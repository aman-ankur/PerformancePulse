/**
 * Consent Management Dialog
 * Interface for managers to update team member consent settings
 */

'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog'
import { Button } from '../ui/button'
import { Label } from '../ui/label'
import { Switch } from '../ui/switch'
import { type TeamMember, type ConsentStatus } from '@/lib/supabase'

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

  const handleSave = async () => {
    if (!member) return
    try {
      setSaving(true)
      await onSave(member.id, consent)
      onClose()
    } catch (error) {
      console.error('Error saving consent:', error)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Manage Data Access Consent</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>GitLab Data Access</Label>
            <div className="flex items-center justify-between">
              <Label htmlFor="gitlab_commits">Commits</Label>
              <Switch
                id="gitlab_commits"
                checked={consent.gitlab_commits}
                onCheckedChange={(checked) =>
                  setConsent((prev) => ({ ...prev, gitlab_commits: checked }))
                }
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="gitlab_merge_requests">Merge Requests</Label>
              <Switch
                id="gitlab_merge_requests"
                checked={consent.gitlab_merge_requests}
                onCheckedChange={(checked) =>
                  setConsent((prev) => ({ ...prev, gitlab_merge_requests: checked }))
                }
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label>Jira Data Access</Label>
            <div className="flex items-center justify-between">
              <Label htmlFor="jira_tickets">Tickets</Label>
              <Switch
                id="jira_tickets"
                checked={consent.jira_tickets}
                onCheckedChange={(checked) =>
                  setConsent((prev) => ({ ...prev, jira_tickets: checked }))
                }
              />
            </div>
            <div className="flex items-center justify-between">
              <Label htmlFor="jira_comments">Comments</Label>
              <Switch
                id="jira_comments"
                checked={consent.jira_comments}
                onCheckedChange={(checked) =>
                  setConsent((prev) => ({ ...prev, jira_comments: checked }))
                }
              />
            </div>
          </div>
        </div>
        <div className="flex justify-end space-x-2">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
} 