/**
 * LLM Integration Tests
 * Tests for the LLM-enhanced components
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LLMBudgetMonitor } from '@/components/llm/llm-budget-monitor'
import { EvidenceCollector } from '@/components/evidence/evidence-collector'
import { LLMIntegrationTest } from '@/components/test/llm-integration-test'

// Mock the API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    healthCheck: jest.fn(),
    getEngineStatus: jest.fn(),
    getLLMUsage: jest.fn(),
    correlateEvidence: jest.fn(),
    correlateEvidenceBasic: jest.fn(),
  },
  queryKeys: {
    llmUsage: () => ['llm-usage'],
    engineStatus: () => ['engine-status'],
  },
  defaultQueryOptions: {
    llmUsage: { refetchInterval: 30000 },
    engineStatus: { refetchInterval: 10000 },
  }
}))

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = createTestQueryClient()
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

describe('LLM Integration Components', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('LLMBudgetMonitor', () => {
    it('renders loading state initially', () => {
      render(
        <TestWrapper>
          <LLMBudgetMonitor />
        </TestWrapper>
      )

      expect(screen.getByText('Loading LLM usage...')).toBeInTheDocument()
    })

    it('renders budget information when data is loaded', async () => {
      const mockUsage = {
        budget_limit: 15.0,
        budget_remaining: 10.0,
        total_cost: 5.0,
        embedding_requests: 100,
        llm_requests: 5,
        cost_breakdown: {
          embeddings_cost: 0.005,
          llm_cost: 4.995
        },
        usage_period: {
          start_date: '2025-01-01',
          end_date: '2025-01-31'
        }
      }

      const { apiClient } = await import('@/lib/api-client')
      apiClient.getLLMUsage.mockResolvedValue(mockUsage)

      render(
        <TestWrapper>
          <LLMBudgetMonitor showDetails={true} />
        </TestWrapper>
      )

      await waitFor(() => {
        expect(screen.getByText('🧠 LLM Budget Status')).toBeInTheDocument()
      })

      expect(screen.getByText('$5.00/$15.00')).toBeInTheDocument()
      expect(screen.getByText('$10.00')).toBeInTheDocument() // Budget remaining
    })
  })

  describe('EvidenceCollector', () => {
    const mockProps = {
      teamMemberId: 'test-member-1',
      teamMemberName: 'John Doe',
      onSuccess: jest.fn(),
      onError: jest.fn()
    }

    it('renders correlation mode selection', () => {
      render(
        <TestWrapper>
          <EvidenceCollector {...mockProps} />
        </TestWrapper>
      )

      expect(screen.getByText('Correlation Mode')).toBeInTheDocument()
      expect(screen.getByText('LLM Enhanced')).toBeInTheDocument()
      expect(screen.getByText('Rule-based')).toBeInTheDocument()
    })

    it('allows mode switching', () => {
      render(
        <TestWrapper>
          <EvidenceCollector {...mockProps} />
        </TestWrapper>
      )

      const ruleBasedButton = screen.getByText('Rule-based')
      fireEvent.click(ruleBasedButton)

      expect(screen.getByText('FREE')).toBeInTheDocument()
    })

    it('shows collection button', () => {
      render(
        <TestWrapper>
          <EvidenceCollector {...mockProps} />
        </TestWrapper>
      )

      expect(screen.getByText('🚀 Collect & Correlate Evidence')).toBeInTheDocument()
    })
  })

  describe('LLMIntegrationTest', () => {
    it('renders test interface', () => {
      render(
        <TestWrapper>
          <LLMIntegrationTest />
        </TestWrapper>
      )

      expect(screen.getByText('🧪 LLM Backend Integration Test')).toBeInTheDocument()
      expect(screen.getByText('🚀 Test LLM Integration')).toBeInTheDocument()
    })

    it('runs tests when button is clicked', async () => {
      const { apiClient } = await import('@/lib/api-client')
      apiClient.healthCheck.mockResolvedValue(true)
      apiClient.getEngineStatus.mockResolvedValue({ status: 'healthy' })
      apiClient.getLLMUsage.mockResolvedValue({ budget_remaining: 10 })

      render(
        <TestWrapper>
          <LLMIntegrationTest />
        </TestWrapper>
      )

      const testButton = screen.getByText('🚀 Test LLM Integration')
      fireEvent.click(testButton)

      await waitFor(() => {
        expect(screen.getByText('✅ All systems operational! LLM integration is ready.')).toBeInTheDocument()
      })

      expect(apiClient.healthCheck).toHaveBeenCalled()
      expect(apiClient.getEngineStatus).toHaveBeenCalled()
      expect(apiClient.getLLMUsage).toHaveBeenCalled()
    })
  })
})

describe('Integration Flow', () => {
  it('supports complete evidence collection flow', async () => {
    const mockCorrelationResponse = {
      relationships: [
        {
          evidence_1: {
            id: 'e1',
            title: 'Test Commit',
            description: 'Fixed bug in auth system',
            source: 'gitlab',
            evidence_date: '2025-01-15',
            author_email: 'john@example.com'
          },
          evidence_2: {
            id: 'e2',
            title: 'AUTH-123: Fix login issue',
            description: 'Login was failing for some users',
            source: 'jira',
            evidence_date: '2025-01-15',
            author_email: 'john@example.com'
          },
          confidence_score: 0.95,
          detection_method: 'llm_semantic',
          llm_insights: 'Both items relate to authentication system improvements',
          correlation_date: '2025-01-15T10:00:00Z'
        }
      ],
      processing_time: 12.5,
      usage_report: {
        embedding_calls: 10,
        llm_calls: 2,
        cost: 0.025
      }
    }

    const { apiClient } = await import('@/lib/api-client')
    apiClient.correlateEvidence.mockResolvedValue(mockCorrelationResponse)

    const onSuccess = jest.fn()
    const props = {
      teamMemberId: 'test-member-1',
      teamMemberName: 'John Doe',
      onSuccess,
      onError: jest.fn()
    }

    render(
      <TestWrapper>
        <EvidenceCollector {...props} />
      </TestWrapper>
    )

    const collectButton = screen.getByText('🚀 Collect & Correlate Evidence')
    fireEvent.click(collectButton)

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith(mockCorrelationResponse)
    })
  })
}) 