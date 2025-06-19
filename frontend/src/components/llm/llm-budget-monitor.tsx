/**
 * LLM Budget Monitor Component
 * Displays real-time LLM usage and budget information
 * Connects to the production LLM correlation backend
 */

'use client'

import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { apiClient, queryKeys, defaultQueryOptions } from '@/lib/api-client'
import { RefreshCw, AlertTriangle, CheckCircle, DollarSign } from 'lucide-react'

interface LLMBudgetMonitorProps {
  showDetails?: boolean
  onBudgetExceeded?: () => void
}

export function LLMBudgetMonitor({ showDetails = true, onBudgetExceeded }: LLMBudgetMonitorProps) {
  const { 
    data: usage, 
    isLoading, 
    error, 
    refetch, 
    isFetching 
  } = useQuery({
    queryKey: queryKeys.llmUsage(),
    queryFn: apiClient.getLLMUsage,
    ...defaultQueryOptions.llmUsage
  })

  // Check if budget exceeded and notify parent
  useEffect(() => {
    if (usage && usage.budget_remaining <= 0 && onBudgetExceeded) {
      onBudgetExceeded()
    }
  }, [usage, onBudgetExceeded])

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center space-x-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <div className="text-sm text-gray-600">Loading LLM usage...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="border-red-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              <span className="text-sm text-red-600">
                Failed to load LLM usage data
              </span>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => refetch()}
              disabled={isFetching}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isFetching ? 'animate-spin' : ''}`} />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!usage) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-center text-gray-500">
            <DollarSign className="h-8 w-8 mx-auto mb-2" />
            <p className="text-sm">No usage data available</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const budgetPercentage = usage.budget_limit > 0 
    ? Math.min(((usage.budget_limit - usage.budget_remaining) / usage.budget_limit) * 100, 100)
    : 0
  const isNearLimit = budgetPercentage > 75
  const isAtLimit = budgetPercentage >= 90
  const isExceeded = usage.budget_remaining <= 0

  const getBudgetStatus = () => {
    if (isExceeded) return { color: 'destructive', label: 'Budget Exceeded' }
    if (isAtLimit) return { color: 'destructive', label: 'Budget Critical' }
    if (isNearLimit) return { color: 'secondary', label: 'Budget Warning' }
    return { color: 'default', label: 'Budget Healthy' }
  }

  const budgetStatus = getBudgetStatus()

  return (
    <Card className={`${isExceeded ? 'border-red-500' : isAtLimit ? 'border-yellow-500' : ''}`}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-lg">🧠 LLM Budget Status</span>
            {isFetching && (
              <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />
            )}
          </div>
          <Badge variant={budgetStatus.color as 'default' | 'destructive' | 'secondary'}>
            ${usage.total_cost?.toFixed(2) || '0.00'}/${usage.budget_limit?.toFixed(2) || '0.00'}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* Budget Progress Bar */}
        <div className="space-y-2 mb-4">
          <div className="flex justify-between text-sm">
            <span>Budget Usage</span>
            <span className="font-mono">{budgetPercentage.toFixed(1)}%</span>
          </div>
          <Progress 
            value={budgetPercentage} 
            className={`h-3 ${isExceeded ? 'bg-red-100' : isAtLimit ? 'bg-yellow-100' : 'bg-gray-100'}`}
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>$0.00</span>
            <span>${usage.budget_limit?.toFixed(2) || '0.00'}</span>
          </div>
        </div>

        {/* Budget Status Alert */}
        {(isNearLimit || isExceeded) && (
          <div className={`p-3 rounded-lg mb-4 ${
            isExceeded 
              ? 'bg-red-50 border border-red-200' 
              : 'bg-yellow-50 border border-yellow-200'
          }`}>
            <div className="flex items-center space-x-2">
              <AlertTriangle className={`h-4 w-4 ${isExceeded ? 'text-red-500' : 'text-yellow-500'}`} />
              <div className="text-sm">
                {isExceeded ? (
                  <span className="text-red-700 font-medium">
                    Budget exhausted. System automatically switched to rule-based correlation.
                  </span>
                ) : (
                  <span className="text-yellow-700 font-medium">
                    Approaching budget limit. Consider using rule-based mode to conserve costs.
                  </span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Usage Details */}
        {showDetails && (
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Embedding Requests</span>
                <span className="font-mono">{usage.embedding_requests?.toLocaleString() || '0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">LLM Requests</span>
                <span className="font-mono">{usage.llm_requests?.toLocaleString() || '0'}</span>
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Embeddings Cost</span>
                <span className="font-mono text-green-600">
                  ${usage.cost_breakdown?.embeddings_cost?.toFixed(4) || '0.0000'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">LLM Cost</span>
                <span className="font-mono text-blue-600">
                  ${usage.cost_breakdown?.llm_cost?.toFixed(4) || '0.0000'}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Remaining Budget */}
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-sm font-medium">Budget Remaining</span>
            </div>
            <span className="font-mono text-lg font-bold text-green-600">
              ${Math.max(0, usage.budget_remaining || 0).toFixed(2)}
            </span>
          </div>
        </div>

        {/* Usage Period */}
        <div className="mt-4 text-xs text-gray-500 text-center">
          Period: {new Date(usage.usage_period?.start_date || Date.now()).toLocaleDateString()} - 
          {new Date(usage.usage_period?.end_date || Date.now()).toLocaleDateString()}
        </div>
      </CardContent>
    </Card>
  )
} 