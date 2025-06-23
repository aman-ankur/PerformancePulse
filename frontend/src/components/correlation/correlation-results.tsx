/**
 * Correlation Results Component
 * Displays semantic correlations between GitLab and JIRA evidence
 * Shows confidence scores, detection methods, and LLM insights
 */

'use client'

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { CorrelationResponse, WorkStory } from '@/lib/api-client'
import { 
  ArrowLeftRight, 
  Brain, 
  Search, 
  Link, 
  User, 
  Calendar,
  ExternalLink,
  Download,
  TrendingUp,
  Lightbulb
} from 'lucide-react'

interface CorrelationResultsProps {
  correlationResponse: CorrelationResponse
  teamMemberName: string
  mode: 'llm' | 'basic'
  onExport?: () => void
  onBack?: () => void
}

export function CorrelationResults({ 
  correlationResponse, 
  teamMemberName, 
  mode,
  onExport,
  onBack 
}: CorrelationResultsProps) {
  if (!correlationResponse) {
    return (
      <div className="text-center py-8">
        <h3 className="text-lg font-semibold text-red-600">No Results Available</h3>
        <p className="text-gray-600 mt-2">No correlation results to display.</p>
        {onBack && (
          <Button variant="outline" onClick={onBack} className="mt-4">
            ← Go Back
          </Button>
        )}
      </div>
    )
  }

  if (!correlationResponse.success || !correlationResponse.correlated_collection) {
    return (
      <div className="text-center py-8">
        <h3 className="text-lg font-semibold text-red-600">Correlation Failed</h3>
        <p className="text-gray-600 mt-2">Unable to process correlation results.</p>
        {onBack && (
          <Button variant="outline" onClick={onBack} className="mt-4">
            ← Try Again
          </Button>
        )}
      </div>
    )
  }

  const { work_stories, relationships } = correlationResponse.correlated_collection

  const getSourceBadgeColor = (source: string) => {
    switch (source) {
      case 'gitlab_commit':
      case 'gitlab_mr':
        return 'bg-orange-100 text-orange-800'
      case 'jira_ticket':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getDetectionMethodInfo = (method: string) => {
    switch (method) {
      case 'content_analysis':
        return {
          label: 'Semantic',
          icon: <Brain className="h-3 w-3 mr-1" />,
          color: 'bg-purple-100 text-purple-800',
          description: 'Detected through semantic content analysis'
        }
      case 'issue_key':
        return {
          label: 'Direct Reference',
          icon: <Link className="h-3 w-3 mr-1" />,
          color: 'bg-green-100 text-green-800',
          description: 'Found direct issue key reference'
        }
      default:
        return {
          label: method,
          icon: <Search className="h-3 w-3 mr-1" />,
          color: 'bg-gray-100 text-gray-800',
          description: 'Other detection method'
        }
    }
  }

  const getConfidenceDisplay = (score: number) => {
    const percentage = Math.round(score * 100)
    if (score >= 0.8) {
      return { percentage, color: 'text-green-600' }
    } else if (score >= 0.5) {
      return { percentage, color: 'text-yellow-600' }
    } else {
      return { percentage, color: 'text-red-600' }
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            🔗 Evidence Correlations: {teamMemberName}
          </h2>
          <p className="text-gray-600 mt-1">
            Found {work_stories.length} work stories with {relationships.length} relationships
            using {mode === 'llm' ? 'LLM-enhanced' : 'rule-based'} analysis
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={mode === 'llm' ? 'default' : 'secondary'}>
            {mode === 'llm' ? '🧠 LLM Enhanced' : '🔧 Rule-based'}
          </Badge>
          <Badge variant="outline">
            {work_stories.length} stories
          </Badge>
          {onExport && (
            <Button variant="outline" size="sm" onClick={onExport}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          )}
          {onBack && (
            <Button variant="outline" onClick={onBack}>
              ← Back
            </Button>
          )}
        </div>
      </div>

      {/* Work Stories */}
      <div className="grid gap-6">
        {work_stories.map((story: WorkStory, index: number) => (
          <Card key={story.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <CardTitle className="text-base">
                  <div className="flex items-center space-x-2">
                    <span>{story.title}</span>
                    <Badge variant="outline" className="ml-2">
                      {story.evidence_items.length} items
                    </Badge>
                  </div>
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm text-gray-600">{story.description}</p>
                
                {/* Evidence Items */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {story.evidence_items.map((item) => (
                    <div key={item.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <Badge 
                          variant="outline" 
                          className={getSourceBadgeColor(item.source)}
                        >
                          {item.source.toUpperCase()}
                        </Badge>
                        <span className="text-xs text-gray-500">
                          {new Date(item.evidence_date).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="font-medium mb-2">{item.title}</div>
                      <div className="text-sm text-gray-600 line-clamp-3">
                        {item.description}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Relationships */}
                {story.relationships.map((rel) => (
                  <div key={rel.id} className="border-t pt-4 mt-4">
                    <div className="flex items-center justify-between">
                      <Badge className={getDetectionMethodInfo(rel.detection_method).color}>
                        {getDetectionMethodInfo(rel.detection_method).icon}
                        {getDetectionMethodInfo(rel.detection_method).label}
                      </Badge>
                      <Badge variant="outline" className={getConfidenceDisplay(rel.confidence_score).color}>
                        {getConfidenceDisplay(rel.confidence_score).percentage}% confident
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">{rel.evidence_summary}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
} 