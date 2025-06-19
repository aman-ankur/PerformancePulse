/**
 * Correlation Results Component
 * Displays semantic correlations between GitLab and JIRA evidence
 * Shows confidence scores, detection methods, and LLM insights
 */

'use client'

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { CorrelationRelationship } from '@/lib/api-client'
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
  relationships: CorrelationRelationship[]
  teamMemberName: string
  mode: 'llm' | 'basic'
  onExport?: () => void
  onBack?: () => void
}

export function CorrelationResults({ 
  relationships, 
  teamMemberName, 
  mode,
  onExport,
  onBack 
}: CorrelationResultsProps) {
  const getDetectionMethodInfo = (method: string) => {
    const methods: Record<string, {
      icon: React.ReactElement;
      label: string;
      color: string;
      description: string;
    }> = {
      'llm_semantic': { 
        icon: <Brain className="h-4 w-4" />, 
        label: 'LLM Semantic', 
        color: 'bg-purple-100 text-purple-800',
        description: 'AI-powered semantic understanding'
      },
      'embedding_similarity': { 
        icon: <Search className="h-4 w-4" />, 
        label: 'Embedding', 
        color: 'bg-blue-100 text-blue-800',
        description: 'Text similarity analysis'
      },
      'issue_key_reference': { 
        icon: <Link className="h-4 w-4" />, 
        label: 'Issue Key', 
        color: 'bg-green-100 text-green-800',
        description: 'Cross-platform issue references'
      },
      'assignee_author_match': { 
        icon: <User className="h-4 w-4" />, 
        label: 'Author Match', 
        color: 'bg-yellow-100 text-yellow-800',
        description: 'Same person across platforms'
      },
      'temporal_proximity': {
        icon: <Calendar className="h-4 w-4" />,
        label: 'Temporal',
        color: 'bg-orange-100 text-orange-800',
        description: 'Time-based correlation'
      }
    }
    return methods[method] || { 
      icon: <TrendingUp className="h-4 w-4" />, 
      label: method, 
      color: 'bg-gray-100 text-gray-800',
      description: 'Custom detection method'
    }
  }

  const getConfidenceDisplay = (confidence: number) => {
    const percentage = Math.round(confidence * 100)
    let color = 'text-red-600'
    let label = 'Low'
    
    if (confidence >= 0.9) {
      color = 'text-green-600'
      label = 'Very High'
    } else if (confidence >= 0.7) {
      color = 'text-blue-600'
      label = 'High'
    } else if (confidence >= 0.5) {
      color = 'text-yellow-600'
      label = 'Medium'
    }
    
    return { percentage, color, label }
  }

  const getSourceBadgeColor = (source: string) => {
    switch (source?.toLowerCase()) {
      case 'gitlab':
        return 'bg-orange-100 text-orange-800'
      case 'jira':
        return 'bg-blue-100 text-blue-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (!relationships || relationships.length === 0) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">
            🔗 Correlations: {teamMemberName}
          </h2>
          {onBack && (
            <Button variant="outline" onClick={onBack}>
              ← Back to Collection
            </Button>
          )}
        </div>

        {/* No Results Card */}
        <Card>
          <CardContent className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-lg font-medium mb-2">No correlations found</h3>
            <p className="text-muted-foreground mb-4">
              {mode === 'llm' ? (
                'Try collecting more evidence or using rule-based correlation for different insights'
              ) : (
                'Try collecting more evidence or using LLM-enhanced mode for semantic understanding'
              )}
            </p>
            {onBack && (
              <Button onClick={onBack}>
                Try Different Mode
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    )
  }

  const sortedRelationships = relationships.sort((a, b) => b.confidence_score - a.confidence_score)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            🔗 Evidence Correlations: {teamMemberName}
          </h2>
          <p className="text-gray-600 mt-1">
            Showing {relationships.length} correlation{relationships.length !== 1 ? 's' : ''} 
            using {mode === 'llm' ? 'LLM-enhanced' : 'rule-based'} analysis
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={mode === 'llm' ? 'default' : 'secondary'}>
            {mode === 'llm' ? '🧠 LLM Enhanced' : '🔧 Rule-based'}
          </Badge>
          <Badge variant="outline">
            {relationships.length} found
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

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {sortedRelationships.filter(r => r.confidence_score >= 0.9).length}
            </div>
            <div className="text-sm text-gray-600">Very High Confidence</div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {sortedRelationships.filter(r => r.confidence_score >= 0.7 && r.confidence_score < 0.9).length}
            </div>
            <div className="text-sm text-gray-600">High Confidence</div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {sortedRelationships.filter(r => r.llm_insights).length}
            </div>
            <div className="text-sm text-gray-600">With LLM Insights</div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {Math.round((sortedRelationships.reduce((sum, r) => sum + r.confidence_score, 0) / sortedRelationships.length) * 100)}%
            </div>
            <div className="text-sm text-gray-600">Avg Confidence</div>
          </div>
        </Card>
      </div>

      {/* Correlation Cards */}
      <div className="grid gap-6">
        {sortedRelationships.map((correlation, index) => {
          const methodInfo = getDetectionMethodInfo(correlation.detection_method)
          const confidenceDisplay = getConfidenceDisplay(correlation.confidence_score)
          
          return (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-base flex-1 pr-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <ArrowLeftRight className="h-4 w-4 text-gray-400" />
                      <span>{correlation.evidence_1.title}</span>
                      <span className="text-gray-400">↔</span>
                      <span>{correlation.evidence_2.title}</span>
                    </div>
                  </CardTitle>
                  <div className="flex items-center space-x-2 flex-shrink-0">
                    <Badge className={methodInfo.color} title={methodInfo.description}>
                      {methodInfo.icon}
                      {methodInfo.label}
                    </Badge>
                    <Badge variant="outline" className={`font-mono ${confidenceDisplay.color}`}>
                      {confidenceDisplay.percentage}%
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Evidence 1 */}
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Badge 
                        variant="outline" 
                        className={getSourceBadgeColor(correlation.evidence_1.source)}
                      >
                        {correlation.evidence_1.source?.toUpperCase()}
                      </Badge>
                      <span className="text-xs text-gray-500">
                        {new Date(correlation.evidence_1.evidence_date).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="font-medium mb-2">{correlation.evidence_1.title}</div>
                    <div className="text-sm text-gray-600 line-clamp-3 mb-2">
                      {correlation.evidence_1.description}
                    </div>
                    <div className="text-xs text-gray-500">
                      Author: {correlation.evidence_1.author_email}
                    </div>
                    {correlation.evidence_1.metadata?.url ? (
                      <a 
                        href={correlation.evidence_1.metadata.url as string}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-xs text-blue-600 hover:text-blue-800 mt-2"
                      >
                        <ExternalLink className="h-3 w-3 mr-1" />
                        View Source
                      </a>
                    ) : null}
                  </div>
                  
                  {/* Evidence 2 */}
                  <div className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Badge 
                        variant="outline" 
                        className={getSourceBadgeColor(correlation.evidence_2.source)}
                      >
                        {correlation.evidence_2.source?.toUpperCase()}
                      </Badge>
                      <span className="text-xs text-gray-500">
                        {new Date(correlation.evidence_2.evidence_date).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="font-medium mb-2">{correlation.evidence_2.title}</div>
                    <div className="text-sm text-gray-600 line-clamp-3 mb-2">
                      {correlation.evidence_2.description}
                    </div>
                    <div className="text-xs text-gray-500">
                      Author: {correlation.evidence_2.author_email}
                    </div>
                    {correlation.evidence_2.metadata?.url ? (
                      <a 
                        href={correlation.evidence_2.metadata.url as string}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-xs text-blue-600 hover:text-blue-800 mt-2"
                      >
                        <ExternalLink className="h-3 w-3 mr-1" />
                        View Source
                      </a>
                    ) : null}
                  </div>
                </div>
                
                {/* Detection Method Info */}
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2 mb-1">
                    {methodInfo.icon}
                    <span className="text-sm font-medium">
                      Detection Method: {methodInfo.label}
                    </span>
                    <Badge variant="outline" className={confidenceDisplay.color}>
                      {confidenceDisplay.label} Confidence
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-600">
                    {methodInfo.description}
                  </div>
                </div>

                {/* LLM Insights */}
                {correlation.llm_insights && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                    <div className="flex items-center space-x-2 mb-2">
                      <Lightbulb className="h-4 w-4 text-blue-600" />
                      <span className="text-sm font-medium text-blue-800">
                        🧠 LLM Semantic Insights:
                      </span>
                    </div>
                    <div className="text-sm text-blue-700">
                      {correlation.llm_insights}
                    </div>
                  </div>
                )}

                {/* Correlation Metadata */}
                <div className="mt-4 text-xs text-gray-500 text-center">
                  Correlated on {new Date(correlation.correlation_date).toLocaleDateString()} at{' '}
                  {new Date(correlation.correlation_date).toLocaleTimeString()}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Meeting Prep Suggestion */}
      <Card className="bg-green-50 border-green-200">
        <CardContent className="p-6">
          <div className="flex items-start space-x-3">
            <Lightbulb className="h-6 w-6 text-green-600 mt-1" />
            <div>
              <h3 className="font-medium text-green-900 mb-2">
                Ready for Performance Discussion
              </h3>
              <p className="text-sm text-green-700 mb-3">
                These correlations provide concrete evidence of {teamMemberName}&apos;s work patterns 
                and cross-platform contributions. Use them to have meaningful conversations about:
              </p>
              <ul className="text-sm text-green-700 space-y-1 ml-4">
                <li>• Work quality and attention to detail</li>
                <li>• Cross-functional collaboration</li>
                <li>• Problem-solving approach</li>
                <li>• Technical documentation practices</li>
              </ul>
              {onExport && (
                <Button variant="outline" size="sm" onClick={onExport} className="mt-3">
                  <Download className="h-4 w-4 mr-2" />
                  Export for Meeting Prep
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 