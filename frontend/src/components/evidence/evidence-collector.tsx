/**
 * Evidence Collector Component
 * Handles evidence collection and correlation using LLM-enhanced or rule-based modes
 * Integrates with the production-ready backend correlation system
 */

'use client'

import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { LLMBudgetMonitor } from '@/components/llm/llm-budget-monitor'
import { 
  apiClient, 
  queryKeys, 
  defaultQueryOptions,
  CorrelationRequest,
  CorrelationResponse 
} from '@/lib/api-client'
import { 
  Play, 
  Zap, 
  Settings, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Brain,
  Cog
} from 'lucide-react'

interface EvidenceCollectorProps {
  teamMemberId: string
  teamMemberName: string
  onSuccess: (results: CorrelationResponse) => void
  onError?: (error: Error) => void
}

type CorrelationMode = 'llm' | 'basic'

export function EvidenceCollector({ 
  teamMemberId, 
  teamMemberName, 
  onSuccess, 
  onError 
}: EvidenceCollectorProps) {
  const [mode, setMode] = useState<CorrelationMode>('llm')
  const [isProcessing, setIsProcessing] = useState(false)

  // Get engine status to determine capabilities
  const { data: engineStatus } = useQuery({
    queryKey: queryKeys.engineStatus(),
    queryFn: apiClient.getEngineStatus,
    ...defaultQueryOptions.engineStatus,
  })

  // Get LLM usage to check budget
  const { data: llmUsage } = useQuery({
    queryKey: queryKeys.llmUsage(),
    queryFn: apiClient.getLLMUsage,
    ...defaultQueryOptions.llmUsage,
  })

  // Correlation mutation
  const correlationMutation = useMutation({
    mutationFn: async (request: CorrelationRequest) => {
      setIsProcessing(true)
      try {
        if (mode === 'llm') {
          return await apiClient.correlateEvidence(request)
        } else {
          return await apiClient.correlateEvidenceBasic(request)
        }
      } finally {
        setIsProcessing(false)
      }
    },
    onSuccess: (data) => {
      onSuccess(data)
    },
    onError: (error) => {
      console.error('Correlation failed:', error)
      if (onError) {
        onError(error as Error)
      }
    }
  })

  const handleStartCorrelation = () => {
    const request: CorrelationRequest = {
      team_member_id: teamMemberId,
      evidence_filters: {
        // For MVP, we'll collect all available evidence
        // Can be enhanced later with date ranges and source filtering
      }
    }

    correlationMutation.mutate(request)
  }

  const canUseLLM = engineStatus?.llm_enabled && 
                   llmUsage && 
                   llmUsage.budget_remaining > 0

  const isLLMForced = !canUseLLM && mode === 'llm'

  const getModeInfo = (selectedMode: CorrelationMode) => {
    if (selectedMode === 'llm') {
      return {
        icon: <Brain className="h-4 w-4" />,
        label: 'LLM Enhanced',
        description: 'AI-powered semantic understanding with 3-tier cost optimization',
        color: canUseLLM ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-500',
        disabled: !canUseLLM
      }
    } else {
      return {
        icon: <Cog className="h-4 w-4" />,
        label: 'Rule-based',
        description: 'Fast pattern matching and cross-platform references (Free)',
        color: 'bg-green-100 text-green-800',
        disabled: false
      }
    }
  }

  const getEstimatedCost = () => {
    if (mode === 'basic') return '$0.00'
    if (!llmUsage) return 'Unknown'
    
    // Rough estimation based on typical team member evidence
    const estimatedItems = 20 // Average evidence items per team member
    const estimatedEmbeddings = Math.floor(estimatedItems * 0.5) // 50% need embedding analysis
    const estimatedLLM = Math.floor(estimatedItems * 0.1) // 10% need LLM analysis
    
    const embeddingCost = estimatedEmbeddings * 0.00005
    const llmCost = estimatedLLM * 0.01
    const totalCost = embeddingCost + llmCost
    
    return `~$${totalCost.toFixed(3)}`
  }

  return (
    <div className="space-y-6">
      {/* LLM Budget Monitor */}
      <LLMBudgetMonitor 
        showDetails={true}
        onBudgetExceeded={() => {
          if (mode === 'llm') {
            setMode('basic')
          }
        }}
      />

      {/* Mode Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Correlation Mode</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {(['llm', 'basic'] as CorrelationMode[]).map((correlationMode) => {
              const modeInfo = getModeInfo(correlationMode)
              const isSelected = mode === correlationMode
              const isDisabled = modeInfo.disabled

              return (
                <button
                  key={correlationMode}
                  onClick={() => !isDisabled && setMode(correlationMode)}
                  disabled={isDisabled}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    isSelected 
                      ? 'border-blue-500 bg-blue-50' 
                      : isDisabled
                      ? 'border-gray-200 bg-gray-50 cursor-not-allowed'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {modeInfo.icon}
                      <span className="font-medium">{modeInfo.label}</span>
                    </div>
                    <Badge 
                      className={modeInfo.color}
                      variant={isSelected ? 'default' : 'outline'}
                    >
                      {correlationMode === 'llm' ? getEstimatedCost() : 'FREE'}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">
                    {modeInfo.description}
                  </p>
                  {isDisabled && correlationMode === 'llm' && (
                    <p className="text-xs text-red-600 mt-2">
                      Budget exhausted or LLM disabled
                    </p>
                  )}
                </button>
              )
            })}
          </div>

          {/* Budget Override Warning */}
          {isLLMForced && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg mb-4">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-4 w-4 text-yellow-500" />
                <span className="text-sm text-yellow-700 font-medium">
                  LLM mode unavailable. Automatically switched to rule-based correlation.
                </span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Evidence Collection Action */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="h-5 w-5" />
            <span>Evidence Collection: {teamMemberName}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Collection Button */}
            <Button 
              onClick={handleStartCorrelation}
              disabled={correlationMutation.isPending || isProcessing}
              className="w-full h-12 text-base"
              size="lg"
            >
              {correlationMutation.isPending || isProcessing ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Running {mode.toUpperCase()} Correlation...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Play className="h-5 w-5" />
                  <span>🚀 Collect & Correlate Evidence</span>
                </div>
              )}
            </Button>

            {/* Processing Steps */}
            {(correlationMutation.isPending || isProcessing) && (
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4" />
                  <span>Collecting GitLab commits and merge requests...</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4" />
                  <span>Gathering JIRA tickets and comments...</span>
                </div>
                {mode === 'llm' && (
                  <>
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4" />
                      <span>Pre-filtering evidence pairs (FREE optimization)...</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4" />
                      <span>Running embedding similarity analysis...</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4" />
                      <span>Processing LLM edge cases for complex relationships...</span>
                    </div>
                  </>
                )}
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4" />
                  <span>Generating correlation insights...</span>
                </div>
              </div>
            )}

            {/* Success Message */}
            {correlationMutation.isSuccess && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm text-green-700 font-medium">
                    Correlation completed successfully! 
                    {correlationMutation.data?.relationships.length || 0} relationships found.
                  </span>
                </div>
              </div>
            )}

            {/* Error Message */}
            {correlationMutation.isError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <span className="text-sm text-red-700 font-medium">
                    Correlation failed: {correlationMutation.error?.message}
                  </span>
                </div>
              </div>
            )}

            {/* Mode Description */}
            <div className="text-xs text-gray-500 text-center">
              {mode === 'llm' ? (
                <span>
                  Using cost-optimized 3-tier pipeline: Pre-filtering → Embeddings → LLM edge cases
                </span>
              ) : (
                <span>
                  Using rule-based algorithms: Pattern matching, cross-references, and temporal analysis
                </span>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 