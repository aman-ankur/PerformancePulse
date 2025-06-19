/**
 * API Client for LLM-Enhanced PerformancePulse Backend
 * Connects to the production-ready LLM correlation system
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export interface CorrelationRequest {
  team_member_id: string
  evidence_filters?: {
    start_date?: string
    end_date?: string
    sources?: string[]
  }
}

export interface EvidenceItem {
  id: string
  title: string
  description: string
  source: 'gitlab' | 'jira'
  evidence_date: string
  author_email: string
  metadata?: Record<string, unknown>
}

export interface CorrelationRelationship {
  evidence_1: EvidenceItem
  evidence_2: EvidenceItem
  confidence_score: number
  detection_method: string
  llm_insights?: string
  correlation_date: string
}

export interface CorrelationResponse {
  success: boolean
  relationships: CorrelationRelationship[]
  usage_report?: {
    total_cost: number
    embedding_requests: number
    llm_requests: number
    budget_remaining: number
  }
  performance_metrics?: {
    processing_time_seconds: number
    evidence_items_processed: number
    pre_filter_eliminated: number
  }
  message: string
}

export interface EngineStatus {
  status: string
  llm_enabled: boolean
  version: string
  available_algorithms: string[]
  last_updated: string
}

export interface LLMUsageReport {
  total_cost: number
  embedding_requests: number
  llm_requests: number
  budget_limit: number
  budget_remaining: number
  cost_breakdown: {
    embeddings_cost: number
    llm_cost: number
  }
  usage_period: {
    start_date: string
    end_date: string
  }
}

/**
 * Main API client with error handling and logging
 */
export const apiClient = {
  /**
   * Get correlation engine status and capabilities
   */
  async getEngineStatus(): Promise<EngineStatus> {
    try {
      const response = await fetch(`${API_BASE}/api/engine-status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Engine status check failed: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Failed to get engine status:', error)
      throw error
    }
  },

  /**
   * Get real-time LLM usage and cost information
   */
  async getLLMUsage(): Promise<LLMUsageReport> {
    try {
      const response = await fetch(`${API_BASE}/api/llm-usage`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`LLM usage check failed: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      
      // Extract usage report from API response structure
      if (data.success && data.usage_report) {
        return data.usage_report
      } else {
        throw new Error('Invalid LLM usage response structure')
      }
    } catch (error) {
      console.error('Failed to get LLM usage:', error)
      throw error
    }
  },

  /**
   * Correlate evidence using LLM-enhanced 3-tier pipeline
   */
  async correlateEvidence(request: CorrelationRequest): Promise<CorrelationResponse> {
    try {
      const response = await fetch(`${API_BASE}/api/correlate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        const errorMessage = errorData?.detail || `Correlation failed: ${response.status} ${response.statusText}`
        throw new Error(errorMessage)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Failed to correlate evidence:', error)
      throw error
    }
  },

  /**
   * Correlate evidence using rule-based algorithms only (free)
   */
  async correlateEvidenceBasic(request: CorrelationRequest): Promise<CorrelationResponse> {
    try {
      const response = await fetch(`${API_BASE}/api/correlate-basic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        const errorMessage = errorData?.detail || `Basic correlation failed: ${response.status} ${response.statusText}`
        throw new Error(errorMessage)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error('Failed to correlate evidence (basic):', error)
      throw error
    }
  },

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      return response.ok
    } catch (error) {
      console.error('Health check failed:', error)
      return false
    }
  }
}

/**
 * React Query key factory for consistent cache management
 */
export const queryKeys = {
  engineStatus: () => ['engine-status'] as const,
  llmUsage: () => ['llm-usage'] as const,
  correlation: (teamMemberId: string, mode: 'llm' | 'basic') => 
    ['correlation', teamMemberId, mode] as const,
  health: () => ['health'] as const,
}

/**
 * Default React Query options for LLM APIs
 */
export const defaultQueryOptions = {
  // Engine status - check every minute
  engineStatus: {
    refetchInterval: 60000,
    staleTime: 30000,
  },
  // LLM usage - check every 10 seconds for real-time monitoring
  llmUsage: {
    refetchInterval: 10000,
    staleTime: 5000,
  },
  // Health check - check every 5 minutes
  health: {
    refetchInterval: 300000,
    staleTime: 60000,
  },
} 