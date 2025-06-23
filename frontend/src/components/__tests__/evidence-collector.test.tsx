/// <reference types="jest" />
import '@testing-library/jest-dom'
import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { EvidenceCollector } from '../evidence/evidence-collector'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { CorrelationRequest, CorrelationResponse } from '../../lib/api-client'

// Mock functions must be declared before jest.mock
const mockCorrelateEvidence = jest.fn()
const mockCorrelateEvidenceBasic = jest.fn()
const mockGetEngineStatus = jest.fn().mockResolvedValue({
  status: 'ready',
  llm_enabled: true,
  capabilities: {
    correlation: true,
    evidence_collection: true,
    work_story_generation: true
  }
})
const mockGetLLMUsage = jest.fn().mockResolvedValue({
  total_tokens: 1000,
  total_cost: 0.02,
  budget_remaining: 99.98,
  budget_limit: 100
})

// Mock the API client
jest.mock('../../lib/api-client', () => ({
  apiClient: {
    correlateEvidence: mockCorrelateEvidence,
    correlateEvidenceBasic: mockCorrelateEvidenceBasic,
    getEngineStatus: mockGetEngineStatus,
    getLLMUsage: mockGetLLMUsage
  }
}))

// Mock query keys
jest.mock('../../lib/query-keys', () => ({
  queryKeys: {
    engineStatus: () => ['engine', 'status'],
    llmUsage: () => ['llm-usage'],
    correlationResults: (teamMemberId: string) => ['correlation', 'results', teamMemberId]
  }
}))

describe('EvidenceCollector Component', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  const mockTeamMemberId = 'team-1'
  const mockTeamMemberName = 'John Doe'
  const mockOnSuccess = jest.fn()
  const mockOnError = jest.fn()

  const mockSuccessResponse: CorrelationResponse = {
    success: true,
    correlated_collection: {
      evidence_items: [{
        id: 'e1',
        team_member_id: 'team-1',
        source: 'gitlab_commit',
        title: 'Test Commit',
        description: 'Test commit description',
        category: 'technical',
        evidence_date: '2024-03-20T10:00:00Z',
        platform: 'gitlab',
        data_source: 'gitlab_api',
        created_at: '2024-03-20T10:00:00Z',
        updated_at: '2024-03-20T10:00:00Z'
      }],
      total_evidence_count: 1,
      work_stories: [{
        id: 'story-1',
        title: 'Test Story',
        description: 'Test work story',
        evidence_items: [],
        relationships: [],
        technology_stack: ['typescript', 'react'],
        complexity_score: 0.7,
        team_members_involved: ['team-1'],
        status: 'completed',
        completion_percentage: 100,
        created_at: '2024-03-20T10:00:00Z',
        updated_at: '2024-03-20T10:00:00Z'
      }],
      relationships: [{
        id: 'rel-1',
        primary_evidence_id: 'e1',
        related_evidence_id: 'e2',
        relationship_type: 'solves',
        confidence_score: 0.95,
        detection_method: 'content_analysis',
        evidence_summary: 'Test relationship',
        detected_at: '2024-03-20T10:00:00Z'
      }],
      insights: {
        total_work_stories: 1,
        total_relationships: 1,
        avg_confidence_score: 0.95,
        technology_distribution: { typescript: 1, react: 1 },
        work_pattern_summary: { avg_completion_time: '2d' },
        collaboration_score: 0.9,
        cross_platform_activity: { gitlab: 1 },
        generated_at: '2024-03-20T10:00:00Z'
      }
    },
    processing_time_ms: 1000,
    items_processed: 1,
    relationships_detected: 1,
    work_stories_created: 1,
    avg_confidence_score: 0.95,
    correlation_coverage: 100
  }

  beforeEach(() => {
    jest.clearAllMocks()
    queryClient.clear()
  })

  const renderComponent = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <EvidenceCollector
          teamMemberId={mockTeamMemberId}
          teamMemberName={mockTeamMemberName}
          onSuccess={mockOnSuccess}
          onError={mockOnError}
        />
      </QueryClientProvider>
    )
  }

  it('should render initial state correctly', () => {
    renderComponent()

    // Check for main elements
    expect(screen.getByText(/Correlation Mode/i)).toBeInTheDocument()
    expect(screen.getByText(/Evidence Collection:/i)).toBeInTheDocument()
    expect(screen.getByText(mockTeamMemberName)).toBeInTheDocument()
    expect(screen.getByText(/🚀 Collect & Correlate Evidence/i)).toBeInTheDocument()

    // Check for mode selection
    expect(screen.getByText(/LLM Enhanced/i)).toBeInTheDocument()
    expect(screen.getByText(/Rule-based/i)).toBeInTheDocument()

    // Check for budget monitor
    expect(screen.getByText(/Budget Remaining:/i)).toBeInTheDocument()
  })

  it('should handle mode switching', () => {
    renderComponent()

    // Find and click the rule-based mode button
    const ruleBasedButton = screen.getByText(/Rule-based/i).closest('button')!
    fireEvent.click(ruleBasedButton)

    // Check that mode switched
    expect(screen.getByText(/FREE/i)).toBeInTheDocument()
    expect(screen.getByText(/Using rule-based algorithms/i)).toBeInTheDocument()
  })

  it('should handle LLM correlation successfully', async () => {
    mockCorrelateEvidence.mockResolvedValueOnce(mockSuccessResponse)
    renderComponent()

    // Click the correlation button
    const button = screen.getByText(/🚀 Collect & Correlate Evidence/i)
    fireEvent.click(button)

    // Check loading state
    expect(screen.getByText(/Running LLM Correlation/i)).toBeInTheDocument()
    expect(screen.getByText(/Collecting GitLab commits/i)).toBeInTheDocument()
    expect(screen.getByText(/Running embedding similarity analysis/i)).toBeInTheDocument()

    // Wait for success state
    await waitFor(() => {
      expect(screen.getByText(/Correlation completed successfully/i)).toBeInTheDocument()
    })

    // Verify API call
    expect(mockCorrelateEvidence).toHaveBeenCalledWith({
      evidence_collection_id: mockTeamMemberId,
      confidence_threshold: 0.3,
      max_work_stories: 50,
      include_low_confidence: false,
      detect_technology_stack: true,
      analyze_work_patterns: true,
      generate_insights: true,
      min_evidence_per_story: 2,
      max_story_duration_days: 90
    })

    // Verify success callback
    expect(mockOnSuccess).toHaveBeenCalledWith(mockSuccessResponse)
  })

  it('should handle validation errors from correlation API', async () => {
    const validationError = new Error('Validation error: field required (evidence_collection_id), ensure this value is greater than 0 (confidence_threshold)')
    mockCorrelateEvidence.mockRejectedValueOnce(validationError)
    renderComponent()

    // Click the correlation button
    const button = screen.getByText(/🚀 Collect & Correlate Evidence/i)
    fireEvent.click(button)

    // Check loading state
    expect(screen.getByText(/Running LLM Correlation/i)).toBeInTheDocument()

    // Wait for error state
    await waitFor(() => {
      expect(screen.getByText(/Correlation failed/i)).toBeInTheDocument()
      expect(screen.getByText(/Validation error:/i)).toBeInTheDocument()
      expect(screen.getByText(/field required \(evidence_collection_id\)/i)).toBeInTheDocument()
      expect(screen.getByText(/ensure this value is greater than 0 \(confidence_threshold\)/i)).toBeInTheDocument()
    })

    // Verify error callback
    expect(mockOnError).toHaveBeenCalledWith(validationError)
  })

  it('should handle network errors', async () => {
    const networkError = new Error('Network error: connection refused')
    mockCorrelateEvidence.mockRejectedValueOnce(networkError)
    renderComponent()

    // Click the correlation button
    const button = screen.getByText(/🚀 Collect & Correlate Evidence/i)
    fireEvent.click(button)

    // Wait for error state
    await waitFor(() => {
      expect(screen.getByText(/Correlation failed/i)).toBeInTheDocument()
      expect(screen.getByText(/Network error:/i)).toBeInTheDocument()
      expect(screen.getByText(/connection refused/i)).toBeInTheDocument()
    })

    // Verify error callback
    expect(mockOnError).toHaveBeenCalledWith(networkError)
  })

  it('should handle basic correlation successfully', async () => {
    mockCorrelateEvidenceBasic.mockResolvedValueOnce(mockSuccessResponse)
    renderComponent()

    // Switch to basic mode
    const ruleBasedButton = screen.getByText(/Rule-based/i).closest('button')!
    fireEvent.click(ruleBasedButton)

    // Click the correlation button
    const button = screen.getByText(/🚀 Collect & Correlate Evidence/i)
    fireEvent.click(button)

    // Wait for success state
    await waitFor(() => {
      expect(screen.getByText(/Correlation completed successfully/i)).toBeInTheDocument()
    })

    // Verify API call
    expect(mockCorrelateEvidenceBasic).toHaveBeenCalledWith({
      evidence_collection_id: mockTeamMemberId,
      confidence_threshold: 0.3,
      max_work_stories: 50,
      include_low_confidence: false,
      detect_technology_stack: true,
      analyze_work_patterns: true,
      generate_insights: true,
      min_evidence_per_story: 2,
      max_story_duration_days: 90
    })
  })

  it('should handle correlation errors', async () => {
    const errorMessage = 'Test error message'
    mockCorrelateEvidence.mockRejectedValueOnce(new Error(errorMessage))
    renderComponent()

    // Click the correlation button
    const button = screen.getByText(/🚀 Collect & Correlate Evidence/i)
    fireEvent.click(button)

    // Wait for error state
    await waitFor(() => {
      expect(screen.getByText(`Correlation failed: ${errorMessage}`)).toBeInTheDocument()
    })

    // Verify error callback
    expect(mockOnError).toHaveBeenCalledWith(expect.any(Error))
  })

  it('should handle LLM budget exhaustion', async () => {
    // Mock LLM budget exhausted
    mockGetLLMUsage.mockResolvedValueOnce({
      total_tokens: 1000,
      total_cost: 20.0,
      budget_remaining: 0.0,
      budget_limit: 20.0
    })

    renderComponent()

    // Wait for budget warning
    await waitFor(() => {
      expect(screen.getByText(/Budget exhausted or LLM disabled/i)).toBeInTheDocument()
    })

    // Verify LLM mode is disabled
    const llmButton = screen.getByText(/LLM Enhanced/i).closest('button')!
    expect(llmButton).toBeDisabled()
  })

  it('should handle LLM service disabled', async () => {
    // Mock LLM service disabled
    mockGetEngineStatus.mockResolvedValueOnce({
      status: 'ready',
      llm_enabled: false,
      capabilities: {
        correlation: true,
        evidence_collection: true,
        work_story_generation: true
      }
    })

    renderComponent()

    // Wait for LLM disabled warning
    await waitFor(() => {
      expect(screen.getByText(/Budget exhausted or LLM disabled/i)).toBeInTheDocument()
    })

    // Verify LLM mode is disabled
    const llmButton = screen.getByText(/LLM Enhanced/i).closest('button')!
    expect(llmButton).toBeDisabled()
  })

  it('should show correct cost estimates', () => {
    renderComponent()

    // Check for cost badge in LLM mode
    const costBadge = screen.getByText(/~\$0\.\d+/i)
    expect(costBadge).toBeInTheDocument()

    // Switch to basic mode and check for FREE badge
    const ruleBasedButton = screen.getByText(/Rule-based/i).closest('button')!
    fireEvent.click(ruleBasedButton)
    expect(screen.getByText('FREE')).toBeInTheDocument()
  })

  it('should show processing steps correctly', async () => {
    mockCorrelateEvidence.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve(mockSuccessResponse), 100)))
    renderComponent()

    // Click the correlation button
    const button = screen.getByText(/🚀 Collect & Correlate Evidence/i)
    fireEvent.click(button)

    // Check for all processing steps
    expect(screen.getByText(/Collecting GitLab commits and merge requests/i)).toBeInTheDocument()
    expect(screen.getByText(/Gathering JIRA tickets and comments/i)).toBeInTheDocument()
    expect(screen.getByText(/Pre-filtering evidence pairs/i)).toBeInTheDocument()
    expect(screen.getByText(/Running embedding similarity analysis/i)).toBeInTheDocument()
    expect(screen.getByText(/Processing LLM edge cases/i)).toBeInTheDocument()
    expect(screen.getByText(/Generating correlation insights/i)).toBeInTheDocument()

    // Wait for completion
    await waitFor(() => {
      expect(screen.getByText(/Correlation completed successfully/i)).toBeInTheDocument()
    })
  })
}) 