/**
 * Add Team Member Dialog
 * Interface for managers to add new team members
 */

'use client'

import { useState } from 'react'
import { type NewTeamMember } from '@/lib/supabase'

interface AddMemberDialogProps {
  isOpen: boolean
  onClose: () => void
  onAdd: (member: NewTeamMember) => Promise<void>
}

export function AddMemberDialog({ isOpen, onClose, onAdd }: AddMemberDialogProps) {
  const [formData, setFormData] = useState<NewTeamMember>({
    full_name: '',
    email: '',
    role: 'team_member',
    gitlab_username: '',
    jira_username: ''
  })
  const [errors, setErrors] = useState<Partial<Record<keyof NewTeamMember, string>>>({})
  const [adding, setAdding] = useState(false)
  const [generalError, setGeneralError] = useState<string | null>(null)

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof NewTeamMember, string>> = {}

    // Full name validation
    if (!formData.full_name.trim()) {
      newErrors.full_name = 'Full name is required'
    } else if (formData.full_name.length < 2) {
      newErrors.full_name = 'Full name must be at least 2 characters'
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address'
    }

    // GitLab username validation
    if (!formData.gitlab_username.trim()) {
      newErrors.gitlab_username = 'GitLab username is required'
    } else if (!/^[a-zA-Z0-9_.-]+$/.test(formData.gitlab_username)) {
      newErrors.gitlab_username = 'Invalid GitLab username format'
    }

    // Jira username validation
    if (!formData.jira_username.trim()) {
      newErrors.jira_username = 'Jira username is required'
    } else if (!/^[a-zA-Z0-9_.-]+$/.test(formData.jira_username)) {
      newErrors.jira_username = 'Invalid Jira username format'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    try {
      setAdding(true)
      setGeneralError(null)
      await onAdd(formData)
      
      // Reset form
      setFormData({
        full_name: '',
        email: '',
        role: 'team_member',
        gitlab_username: '',
        jira_username: ''
      })
      setErrors({})
      onClose()
    } catch (err) {
      console.error('Error adding team member:', err)
      
      if (err instanceof Error) {
        const errorMessage = err.message.toLowerCase()
        
        // Handle specific error cases
        if (errorMessage.includes('duplicate key') || errorMessage.includes('unique constraint')) {
          setErrors(prev => ({
            ...prev,
            email: 'This email is already associated with a team member'
          }))
        } else if (errorMessage.includes('failed to get current user')) {
          setGeneralError('Authentication error. Please try logging out and back in.')
        } else if (errorMessage.includes('permission denied')) {
          setGeneralError('You do not have permission to add team members.')
        } else {
          setGeneralError(err.message || 'Failed to add team member. Please try again.')
        }
      } else {
        setGeneralError('An unexpected error occurred. Please try again.')
      }
    } finally {
      setAdding(false)
    }
  }

  const handleInputChange = (field: keyof NewTeamMember, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
    // Clear general error when user makes any change
    if (generalError) {
      setGeneralError(null)
    }
  }

  const handleClose = () => {
    if (!adding) {
      // Reset form state
      setFormData({
        full_name: '',
        email: '',
        role: 'team_member',
        gitlab_username: '',
        jira_username: ''
      })
      setErrors({})
      setGeneralError(null)
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-2/3 lg:w-1/2 xl:w-1/3 shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              Add Team Member
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Invite a new team member to your team
            </p>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={adding}
            type="button"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Info Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-blue-800">Team Member Setup</h4>
              <p className="text-sm text-blue-700 mt-1">
                New team members will be added to your team with default consent settings disabled.
                You can configure their data collection preferences after adding them.
              </p>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {generalError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <svg className="h-5 w-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-red-800">{generalError}</p>
            </div>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Full Name */}
          <div>
            <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-1">
              Full Name
            </label>
            <input
              type="text"
              id="full_name"
              value={formData.full_name}
              onChange={(e) => handleInputChange('full_name', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                errors.full_name 
                  ? 'border-red-300 focus:border-red-500' 
                  : 'border-gray-300 focus:border-indigo-500'
              }`}
              placeholder="Enter team member's full name"
              disabled={adding}
              required
            />
            {errors.full_name && (
              <p className="mt-1 text-sm text-red-600">{errors.full_name}</p>
            )}
          </div>

          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                errors.email 
                  ? 'border-red-300 focus:border-red-500' 
                  : 'border-gray-300 focus:border-indigo-500'
              }`}
              placeholder="Enter team member's email address"
              disabled={adding}
              required
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email}</p>
            )}
          </div>

          {/* GitLab Username */}
          <div>
            <label htmlFor="gitlab_username" className="block text-sm font-medium text-gray-700 mb-1">
              GitLab Username
            </label>
            <input
              type="text"
              id="gitlab_username"
              value={formData.gitlab_username}
              onChange={(e) => handleInputChange('gitlab_username', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                errors.gitlab_username 
                  ? 'border-red-300 focus:border-red-500' 
                  : 'border-gray-300 focus:border-indigo-500'
              }`}
              placeholder="Enter GitLab username"
              disabled={adding}
              required
            />
            {errors.gitlab_username && (
              <p className="mt-1 text-sm text-red-600">{errors.gitlab_username}</p>
            )}
          </div>

          {/* Jira Username */}
          <div>
            <label htmlFor="jira_username" className="block text-sm font-medium text-gray-700 mb-1">
              Jira Username
            </label>
            <input
              type="text"
              id="jira_username"
              value={formData.jira_username}
              onChange={(e) => handleInputChange('jira_username', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                errors.jira_username 
                  ? 'border-red-300 focus:border-red-500' 
                  : 'border-gray-300 focus:border-indigo-500'
              }`}
              placeholder="Enter Jira username"
              disabled={adding}
              required
            />
            {errors.jira_username && (
              <p className="mt-1 text-sm text-red-600">{errors.jira_username}</p>
            )}
          </div>

          {/* Role (Fixed) */}
          <div>
            <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">
              Role
            </label>
            <input
              type="text"
              id="role"
              value="Team Member"
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
              disabled
            />
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              disabled={adding}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md ${
                adding 
                  ? 'opacity-75 cursor-not-allowed'
                  : 'hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
              }`}
              disabled={adding}
            >
              {adding ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Adding...
                </span>
              ) : 'Add Member'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
} 