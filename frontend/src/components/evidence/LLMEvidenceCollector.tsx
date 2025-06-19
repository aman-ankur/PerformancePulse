'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'

interface LLMEvidenceCollectorProps {
  teamMemberId: string
  onCorrelationComplete: (results: CorrelationResult) => void
}

export function LLMEvidenceCollector({ teamMemberId, onCorrelationComplete }: LLMEvidenceCollectorProps) {
  const [correlationMode, setCorrelationMode] = useState<'llm' | 'basic'>('llm')
  
  // Real-time LLM usage monitoring
  const { data: llmUsage } = useQuery({
    queryKey: ['llm-usage'],
    queryFn: () => fetch('/api/llm-usage').then(r => r.json()),
    refetchInterval: 10000 // Update every 10 seconds
  })
  
  // Evidence correlation mutation
  const correlationMutation = useMutation({
    mutationFn: async (evidenceData: any) => {
      const endpoint = correlationMode === 'llm' ? '/api/correlate' : '/api/correlate-basic'
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          team_member_id: teamMemberId,
          ...evidenceData
        })
      })
      if (!response.ok) throw new Error('Correlation failed')
      return response.json()
    },
    onSuccess: onCorrelationComplete
  })
  
  const budgetStatus = llmUsage ? {
    percentage: (llmUsage.total_cost / 15.0) * 100,
    isNearLimit: (llmUsage.total_cost / 15.0) > 0.75,
    isAtLimit: (llmUsage.total_cost / 15.0) > 0.90
  } : null
  
  return (
    <div className="space-y-6">
      {/* LLM Budget Monitor */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            🧠 LLM Budget Status
            <Badge variant={budgetStatus?.isAtLimit ? "destructive" : budgetStatus?.isNearLimit ? "secondary" : "default"}>
              ${llmUsage?.total_cost?.toFixed(2) || '0.00'}/$15.00
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Progress value={budgetStatus?.percentage || 0} className="mb-4" />
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="font-medium">Embedding Requests</div>
              <div className="text-muted-foreground">{llmUsage?.embedding_requests || 0}</div>
            </div>
            <div>
              <div className="font-medium">LLM Requests</div>
              <div className="text-muted-foreground">{llmUsage?.llm_requests || 0}</div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Correlation Mode Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Correlation Mode</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <Button
              variant={correlationMode === 'llm' ? 'default' : 'outline'}
              onClick={() => setCorrelationMode('llm')}
              disabled={budgetStatus?.isAtLimit}
            >
              🧠 LLM Enhanced {budgetStatus?.isAtLimit && '(Budget Limit)'}
            </Button>
            <Button
              variant={correlationMode === 'basic' ? 'default' : 'outline'}
              onClick={() => setCorrelationMode('basic')}
            >
              🔧 Rule-based (Free)
            </Button>
          </div>
          
          {budgetStatus?.isNearLimit && (
            <Alert className="mt-4">
              <AlertDescription>
                {budgetStatus.isAtLimit 
                  ? "⚠️ Budget exhausted. Using rule-based correlation only."
                  : "📊 Approaching budget limit. Consider using rule-based mode."}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
      
      {/* Evidence Collection Action */}
      <Card>
        <CardHeader>
          <CardTitle>Evidence Collection</CardTitle>
        </CardHeader>
        <CardContent>
          <Button 
            onClick={() => correlationMutation.mutate({})}
            disabled={correlationMutation.isPending}
            className="w-full"
          >
            {correlationMutation.isPending 
              ? `🔄 Running ${correlationMode.toUpperCase()} Correlation...` 
              : `🚀 Collect & Correlate Evidence`}
          </Button>
          
          {correlationMutation.isPending && (
            <div className="mt-4 text-sm text-muted-foreground">
              <div>• Collecting GitLab commits and merge requests...</div>
              <div>• Gathering JIRA tickets and comments...</div>
              {correlationMode === 'llm' && (
                <>
                  <div>• Pre-filtering evidence pairs (FREE)...</div>
                  <div>• Running embedding analysis...</div>
                  <div>• Processing LLM edge cases...</div>
                </>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
} 