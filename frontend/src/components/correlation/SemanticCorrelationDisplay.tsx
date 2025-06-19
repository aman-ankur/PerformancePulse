import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface CorrelationDisplayProps {
  correlations: CorrelationResult[]
  teamMember: TeamMember
  llmEnabled: boolean
}

export function SemanticCorrelationDisplay({ correlations, teamMember, llmEnabled }: CorrelationDisplayProps) {
  const getDetectionMethodInfo = (method: string) => {
    const methods = {
      'llm_semantic': { icon: '🧠', label: 'LLM Semantic', color: 'bg-purple-100 text-purple-800' },
      'embedding_similarity': { icon: '🔍', label: 'Embedding', color: 'bg-blue-100 text-blue-800' },
      'issue_key_reference': { icon: '🔗', label: 'Issue Key', color: 'bg-green-100 text-green-800' },
      'assignee_author_match': { icon: '👤', label: 'Author Match', color: 'bg-yellow-100 text-yellow-800' }
    }
    return methods[method] || { icon: '❓', label: method, color: 'bg-gray-100 text-gray-800' }
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">
          🔗 Evidence Correlations: {teamMember.full_name}
        </h2>
        <div className="flex items-center gap-2">
          <Badge variant={llmEnabled ? "default" : "secondary"}>
            {llmEnabled ? '🧠 LLM Enhanced' : '🔧 Rule-based'}
          </Badge>
          <Badge variant="outline">
            {correlations.length} correlations found
          </Badge>
        </div>
      </div>
      
      {correlations.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-lg font-medium mb-2">No correlations found</h3>
            <p className="text-muted-foreground">
              Try collecting more evidence or using {llmEnabled ? 'rule-based' : 'LLM-enhanced'} correlation
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {correlations.map((correlation, index) => {
            const methodInfo = getDetectionMethodInfo(correlation.detection_method)
            const confidencePercentage = Math.round(correlation.confidence_score * 100)
            
            return (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-base">
                      {correlation.evidence_1.title} ↔ {correlation.evidence_2.title}
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge className={methodInfo.color}>
                        {methodInfo.icon} {methodInfo.label}
                      </Badge>
                      <span className="font-mono text-sm font-bold text-green-600">
                        {confidencePercentage}%
                      </span>
                    </div>
                  </div>
                </CardHeader>
                {/* ... existing code ... */}
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
} 