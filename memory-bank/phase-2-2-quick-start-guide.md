# Phase 2.2 Quick Start Guide - LLM Dashboard Integration

## 🚀 **IMMEDIATE NEXT STEPS**

Your LLM backend is production-ready! Here's how to build the frontend integration in the next 1-2 weeks:

---

## ⚡ **Day 1: Setup & Dependencies**

### **1. Install Required Dependencies**
```bash
cd frontend
npm install @tanstack/react-query lucide-react recharts
```

### **2. Verify Backend APIs Work**
```bash
# Start your backend first
cd backend
source pulse_venv/bin/activate
python -m src.main

# Test APIs in another terminal
curl http://localhost:8000/api/engine-status
curl http://localhost:8000/api/llm-usage
```

### **3. Create API Client**
```typescript
// frontend/src/lib/api-client.ts
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export const apiClient = {
  async getEngineStatus() {
    const response = await fetch(`${API_BASE}/api/engine-status`)
    return response.json()
  },
  
  async getLLMUsage() {
    const response = await fetch(`${API_BASE}/api/llm-usage`)
    return response.json()
  },
  
  async correlateEvidence(teamMemberId: string, mode: 'llm' | 'basic' = 'llm') {
    const endpoint = mode === 'llm' ? '/api/correlate' : '/api/correlate-basic'
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ team_member_id: teamMemberId })
    })
    return response.json()
  }
}
```

---

## ⚡ **Day 2-3: LLM Budget Monitor Component**

Create the core LLM monitoring component:

```typescript
// frontend/src/components/llm/LLMBudgetMonitor.tsx
'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { apiClient } from '@/lib/api-client'

export function LLMBudgetMonitor() {
  const { data: usage, isLoading } = useQuery({
    queryKey: ['llm-usage'],
    queryFn: apiClient.getLLMUsage,
    refetchInterval: 10000 // Update every 10 seconds
  })

  if (isLoading) return <div>Loading LLM usage...</div>
  if (!usage) return null

  const budgetPercentage = (usage.total_cost / 15.0) * 100
  const isNearLimit = budgetPercentage > 75
  const isAtLimit = budgetPercentage > 90

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          🧠 LLM Budget Status
          <Badge variant={isAtLimit ? "destructive" : isNearLimit ? "secondary" : "default"}>
            ${usage.total_cost?.toFixed(2) || '0.00'}/$15.00
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Progress value={budgetPercentage} className="mb-4" />
        
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="font-medium">Embeddings</div>
            <div className="text-muted-foreground">{usage.embedding_requests || 0}</div>
          </div>
          <div>
            <div className="font-medium">LLM Calls</div>
            <div className="text-muted-foreground">{usage.llm_requests || 0}</div>
          </div>
          <div>
            <div className="font-medium">Remaining</div>
            <div className="text-muted-foreground">${(15.0 - usage.total_cost).toFixed(2)}</div>
          </div>
        </div>
        
        {isNearLimit && (
          <Alert className="mt-4">
            <AlertDescription>
              {isAtLimit 
                ? "⚠️ Budget exhausted. Switching to rule-based correlation."
                : "📊 Approaching budget limit. Consider using rule-based mode."}
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}
```

---

## ⚡ **Day 4-5: Evidence Collection Interface**

```typescript
// frontend/src/components/evidence/EvidenceCollector.tsx
'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { LLMBudgetMonitor } from '@/components/llm/LLMBudgetMonitor'
import { apiClient } from '@/lib/api-client'

interface EvidenceCollectorProps {
  teamMemberId: string
  onSuccess: (results: any) => void
}

export function EvidenceCollector({ teamMemberId, onSuccess }: EvidenceCollectorProps) {
  const [mode, setMode] = useState<'llm' | 'basic'>('llm')
  
  const correlationMutation = useMutation({
    mutationFn: () => apiClient.correlateEvidence(teamMemberId, mode),
    onSuccess: onSuccess
  })

  return (
    <div className="space-y-6">
      <LLMBudgetMonitor />
      
      <Card>
        <CardHeader>
          <CardTitle>Correlation Mode</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-4">
            <Button
              variant={mode === 'llm' ? 'default' : 'outline'}
              onClick={() => setMode('llm')}
            >
              🧠 LLM Enhanced
            </Button>
            <Button
              variant={mode === 'basic' ? 'default' : 'outline'}
              onClick={() => setMode('basic')}
            >
              🔧 Rule-based (Free)
            </Button>
          </div>
          
          <Button 
            onClick={() => correlationMutation.mutate()}
            disabled={correlationMutation.isPending}
            className="w-full"
          >
            {correlationMutation.isPending 
              ? `🔄 Running ${mode.toUpperCase()} Correlation...` 
              : `🚀 Collect & Correlate Evidence`}
          </Button>
          
          {correlationMutation.error && (
            <div className="mt-4 text-sm text-red-600">
              Error: {correlationMutation.error.message}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
```

---

## ⚡ **Day 6-7: Results Display**

```typescript
// frontend/src/components/correlation/CorrelationResults.tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface CorrelationResultsProps {
  results: any[]
  teamMemberName: string
}

export function CorrelationResults({ results, teamMemberName }: CorrelationResultsProps) {
  if (!results || results.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-lg font-medium mb-2">No correlations found</h3>
          <p className="text-muted-foreground">
            Try collecting more evidence or switching correlation modes
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">
          🔗 Correlations: {teamMemberName}
        </h2>
        <Badge variant="outline">
          {results.length} correlations found
        </Badge>
      </div>
      
      <div className="grid gap-4">
        {results.map((correlation, index) => (
          <Card key={index}>
            <CardHeader>
              <CardTitle className="text-base flex items-center justify-between">
                <span>
                  {correlation.evidence_1?.title} ↔ {correlation.evidence_2?.title}
                </span>
                <Badge variant="default">
                  {Math.round((correlation.confidence_score || 0) * 100)}% confidence
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="border rounded p-3">
                  <Badge variant="outline" className="mb-2">
                    {correlation.evidence_1?.source?.toUpperCase()}
                  </Badge>
                  <div className="text-sm text-muted-foreground">
                    {correlation.evidence_1?.description}
                  </div>
                </div>
                <div className="border rounded p-3">
                  <Badge variant="outline" className="mb-2">
                    {correlation.evidence_2?.source?.toUpperCase()}
                  </Badge>
                  <div className="text-sm text-muted-foreground">
                    {correlation.evidence_2?.description}
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
        ))}
      </div>
    </div>
  )
}
```

---

## ⚡ **Day 8: Update Main Dashboard**

Update your existing dashboard to include LLM features:

```typescript
// frontend/src/app/dashboard/page.tsx (Add to existing)
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { EvidenceCollector } from '@/components/evidence/EvidenceCollector'
import { CorrelationResults } from '@/components/correlation/CorrelationResults'
import { apiClient } from '@/lib/api-client'

// Add to your existing DashboardContent component:
function EnhancedDashboardContent() {
  // ... your existing code ...
  const [correlationResults, setCorrelationResults] = useState([])
  const [activeTab, setActiveTab] = useState('overview')
  
  // Add engine status monitoring
  const { data: engineStatus } = useQuery({
    queryKey: ['engine-status'],
    queryFn: apiClient.getEngineStatus,
    refetchInterval: 60000
  })
  
  const handleCorrelationSuccess = (results: any) => {
    setCorrelationResults(results.relationships || [])
    setActiveTab('correlations')
  }
  
  // Add to your JSX:
  // Add tabs for Evidence Collection and Correlations
  // Add EvidenceCollector and CorrelationResults components
}
```

---

## 🧪 **TESTING CHECKLIST**

### **Day 9-10: Integration Testing**

1. **Backend Connection Test:**
   ```bash
   # Make sure backend is running
   curl http://localhost:8000/api/engine-status
   ```

2. **Frontend Development Test:**
   ```bash
   cd frontend
   npm run dev
   # Navigate to http://localhost:3000/dashboard
   ```

3. **Feature Test Checklist:**
   - [ ] LLM budget monitor shows real usage data
   - [ ] Mode switching between LLM and rule-based works
   - [ ] Evidence collection triggers correlation
   - [ ] Results display correlation pairs with confidence scores
   - [ ] LLM insights appear when available
   - [ ] Budget warnings appear appropriately
   - [ ] Error handling works when backend is down

---

## 🎯 **SUCCESS CRITERIA**

**By End of Week 1:**
- [ ] Manager can see real LLM budget status
- [ ] Evidence collection works with your production backend
- [ ] Correlations display with confidence scores
- [ ] LLM vs rule-based mode switching functional

**By End of Week 2:**
- [ ] Professional UI suitable for actual manager use
- [ ] Error handling for API failures
- [ ] Mobile-responsive design
- [ ] Export functionality for meeting prep

**🚀 MVP Result:** Production manager dashboard showing real GitLab/JIRA correlations with your LLM-enhanced semantic understanding and full cost transparency.

---

## 📞 **IMMEDIATE NEXT ACTIONS**

1. **Install dependencies** (5 minutes)
2. **Create API client** (15 minutes)  
3. **Build LLM budget monitor** (2 hours)
4. **Test with real backend** (30 minutes)

Your Phase 2.1.2 backend is ready - now we connect the frontend to show managers real semantic correlations with cost controls! 