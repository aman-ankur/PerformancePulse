# Phase 2.2: Frontend Integration - LLM-Enhanced Manager Dashboard

## 🎯 **PHASE OVERVIEW**

**Status:** Ready for Implementation  
**Timeline:** 1-2 weeks (Backend ✅ Complete - Frontend Integration Only)  
**Dependencies:** Phase 2.1.2 LLM Correlation ✅ **PRODUCTION READY**  
**Goal:** Real-time manager dashboard with LLM-enhanced semantic correlation and cost monitoring

### **What We Have** ✅ **COMPLETE**
- **Production LLM Backend**: Cost-optimized 3-tier pipeline with $15/month budget controls
- **API Endpoints**: 5 LLM-enhanced endpoints fully tested and validated
- **Real API Testing**: Both Anthropic and OpenAI working in production ($0.03 test cost)
- **Cost Management**: Real-time tracking with graceful fallback to rule-based
- **Enhanced Pipeline**: 7-step correlation engine with semantic understanding

### **What We Need** 🔄 **NEXT**
- **Dashboard Integration**: Connect frontend to LLM-enhanced APIs  
- **Real-time Correlation UI**: Show semantic relationships with confidence scores
- **Cost Monitoring Interface**: LLM usage dashboard with budget alerts
- **Meeting Prep Enhancement**: LLM-powered discussion points and insights
- **Production Polish**: Error handling, loading states, and optimization

---

## 🚀 **IMPLEMENTATION PLAN**

### **Week 1: Core Dashboard Integration**

#### **Day 1-2: LLM Evidence Collection Interface**

Create the main evidence collection component that integrates with your production LLM backend:

```typescript
// frontend/src/components/evidence/LLMEvidenceCollector.tsx
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
```

#### **Day 3-4: Semantic Correlation Visualization**

```typescript
// frontend/src/components/correlation/SemanticCorrelationDisplay.tsx
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
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="border rounded p-3">
                      <Badge variant="outline" className="mb-2">
                        {correlation.evidence_1.source.toUpperCase()}
                      </Badge>
                      <div className="text-sm text-muted-foreground">
                        {correlation.evidence_1.description}
                      </div>
                    </div>
                    <div className="border rounded p-3">
                      <Badge variant="outline" className="mb-2">
                        {correlation.evidence_2.source.toUpperCase()}
                      </Badge>
                      <div className="text-sm text-muted-foreground">
                        {correlation.evidence_2.description}
                      </div>
                    </div>
                  </div>
                  
                  {correlation.llm_insights && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                      <div className="text-sm font-medium text-blue-800 mb-1">
                        🧠 LLM Insights:
                      </div>
                      <div className="text-sm text-blue-700">
                        {correlation.llm_insights}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
```

#### **Day 5-7: Enhanced Dashboard Integration**

Update the main dashboard to include LLM features:

```typescript
// frontend/src/app/dashboard/page.tsx (Enhanced)
'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AuthGuard } from '@/components/auth/auth-guard'
import { useAuth } from '@/lib/auth-store'
import { LLMEvidenceCollector } from '@/components/evidence/LLMEvidenceCollector'
import { SemanticCorrelationDisplay } from '@/components/correlation/SemanticCorrelationDisplay'
import { TeamMemberList } from '@/components/team/team-member-list'

export default function Dashboard() {
  return (
    <AuthGuard requiredRole="manager">
      <EnhancedDashboardContent />
    </AuthGuard>
  )
}

function EnhancedDashboardContent() {
  const { profile, signOut } = useAuth()
  const [selectedTeamMember, setSelectedTeamMember] = useState(null)
  const [correlationResults, setCorrelationResults] = useState([])
  const [activeView, setActiveView] = useState('overview')
  
  // Engine status monitoring
  const { data: engineStatus } = useQuery({
    queryKey: ['engine-status'],
    queryFn: () => fetch('/api/engine-status').then(r => r.json()),
    refetchInterval: 60000
  })
  
  const handleCorrelationComplete = (results) => {
    setCorrelationResults(results.relationships || [])
    setActiveView('correlations')
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Enhanced Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold text-gray-900">PerformancePulse</h1>
              <Badge variant="outline">🧠 LLM Enhanced</Badge>
              {engineStatus && (
                <Badge variant={engineStatus.llm_enabled ? "default" : "secondary"}>
                  {engineStatus.llm_enabled ? '🧠 LLM Active' : '🔧 Rule-based Only'}
                </Badge>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-700">Welcome, {profile?.full_name}</div>
              <Button variant="ghost" size="sm" onClick={signOut}>Sign out</Button>
            </div>
          </div>
        </div>
      </header>
      
      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { key: 'overview', label: '📊 Team Overview' },
              { key: 'evidence', label: '🔍 Evidence Collection' },
              { key: 'correlations', label: '🔗 Correlations' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveView(tab.key)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeView === tab.key
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {activeView === 'overview' && (
            <div className="space-y-6">
              <h2 className="text-3xl font-bold text-gray-900">Team Overview</h2>
              <TeamMemberList onSelectMember={setSelectedTeamMember} />
            </div>
          )}
          
          {activeView === 'evidence' && selectedTeamMember && (
            <LLMEvidenceCollector
              teamMemberId={selectedTeamMember.id}
              onCorrelationComplete={handleCorrelationComplete}
            />
          )}
          
          {activeView === 'correlations' && correlationResults.length > 0 && selectedTeamMember && (
            <SemanticCorrelationDisplay
              correlations={correlationResults}
              teamMember={selectedTeamMember}
              llmEnabled={engineStatus?.llm_enabled || false}
            />
          )}
        </div>
      </main>
    </div>
  )
}
```

---

## 🧪 **TESTING WITH REAL DATA**

### **Backend Integration Test**
```bash
# Test your production APIs
curl -X GET http://localhost:8000/api/engine-status
curl -X GET http://localhost:8000/api/llm-usage
curl -X POST http://localhost:8000/api/correlate -H "Content-Type: application/json" -d '{}'
```

### **Frontend Integration Test**
```bash
cd frontend
npm install @tanstack/react-query
npm run dev
```

Navigate to http://localhost:3000/dashboard and test:
1. Budget monitoring shows real LLM usage
2. Evidence collection connects to your backend
3. Correlation results display with confidence scores
4. LLM vs rule-based mode switching works

---

## 📊 **SUCCESS CRITERIA**

### **Week 1 Deliverables**
- [ ] LLM evidence collector working with your production backend
- [ ] Real-time cost monitoring displaying actual usage
- [ ] Semantic correlation visualization showing relationships
- [ ] Complete dashboard navigation and state management

### **Week 2 Deliverables**
- [ ] Error handling for API failures
- [ ] Mobile-responsive design
- [ ] Export functionality for meeting prep
- [ ] Production deployment

### **Final MVP Features**
- [ ] Manager can collect evidence for team members
- [ ] Real-time LLM correlation with budget controls
- [ ] Visual display of semantic relationships with confidence scores
- [ ] Automatic fallback when budget exceeded
- [ ] Professional UI suitable for actual manager use

**🎯 Goal**: Production manager dashboard showing real GitLab/JIRA correlations with your LLM-enhanced semantic understanding and full cost transparency.

This builds directly on your completed Phase 2.1.2 backend and gives managers a practical tool for performance conversations. 