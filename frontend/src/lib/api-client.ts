/**
 * API Client for LLM-Enhanced PerformancePulse Backend
 * Connects to the production-ready LLM correlation system
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export interface UnifiedEvidenceItem {
  id: string
  team_member_id: string
  source: 'gitlab_commit' | 'gitlab_mr' | 'jira_ticket' | 'document'
  title: string
  description: string
  category: 'technical' | 'collaboration' | 'delivery'
  evidence_date: string
  source_url?: string
  platform: 'gitlab' | 'jira' | 'document'
  data_source: string
  fallback_used?: boolean
  created_at?: string
  updated_at?: string
  correlation_id?: string
  confidence_score?: number
  metadata?: Record<string, any>
}

export interface CorrelationRequest {
  evidence_collection_id?: string
  team_member_id?: string
  evidence_items?: UnifiedEvidenceItem[]
  confidence_threshold?: number
  max_work_stories?: number
  include_low_confidence?: boolean
  detect_technology_stack?: boolean
  analyze_work_patterns?: boolean
  generate_insights?: boolean
  min_evidence_per_story?: number
  max_story_duration_days?: number
}

export interface EvidenceRelationship {
  id: string
  primary_evidence_id: string
  related_evidence_id: string
  relationship_type: 'solves' | 'references' | 'related_to' | 'duplicate' | 'sequential' | 'causal'
  confidence_score: number
  detection_method: 'issue_key' | 'branch_name' | 'content_analysis' | 'temporal_proximity' | 'author_correlation' | 'manual'
  evidence_summary: string
  detected_at: string
  metadata?: Record<string, any>
}

export interface WorkStory {
  id: string
  title: string
  description: string
  evidence_items: UnifiedEvidenceItem[]
  relationships: EvidenceRelationship[]
  primary_jira_ticket?: string
  primary_platform?: 'gitlab' | 'jira' | 'document'
  timeline?: Record<string, string>
  duration?: string
  technology_stack: string[]
  complexity_score: number
  team_members_involved: string[]
  status: 'in_progress' | 'completed' | 'blocked' | 'cancelled' | 'unknown'
  completion_percentage: number
  created_at: string
  updated_at: string
  metadata?: Record<string, any>
}

export interface CorrelationResponse {
  success: boolean
  correlated_collection?: {
    evidence_items: UnifiedEvidenceItem[]
    total_evidence_count: number
    work_stories: WorkStory[]
    relationships: EvidenceRelationship[]
    insights?: {
      total_work_stories: number
      total_relationships: number
      avg_confidence_score: number
      technology_distribution: Record<string, number>
      work_pattern_summary: Record<string, any>
      collaboration_score: number
      cross_platform_activity: Record<string, number>
      generated_at: string
    }
  }
  processing_time_ms: number
  items_processed: number
  relationships_detected: number
  work_stories_created: number
  avg_confidence_score: number
  correlation_coverage: number
  errors?: string[]
  warnings?: string[]
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
      console.log('Sending correlation request:', request)
      const response = await fetch(`${API_BASE}/api/correlate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        console.error('Correlation request failed:', response.status, response.statusText)
        throw new Error(`Correlation failed: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      console.log('Received correlation response:', data)
      
      if (!data.success) {
        console.error('Correlation unsuccessful:', data.errors || 'No error details provided')
      }
      
      if (!data.correlated_collection) {
        console.error('No correlated collection in response')
      } else {
        console.log('Work stories count:', data.correlated_collection.work_stories?.length || 0)
        console.log('Relationships count:', data.correlated_collection.relationships?.length || 0)
      }

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
  // LLM usage - check every 60 seconds to reduce backend load
  llmUsage: {
    refetchInterval: 60000,
    staleTime: 30000,
  },
  // Health check - check every 5 minutes
  health: {
    refetchInterval: 300000,
    staleTime: 60000,
  },
} 