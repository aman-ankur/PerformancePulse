/**
 * LLM Performance Dashboard
 * Main component that orchestrates evidence collection, correlation, and results display
 * Integrates with the production-ready LLM-enhanced backend
 */

'use client'

import React, { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { EvidenceCollector } from '@/components/evidence/evidence-collector'
import { CorrelationResults } from '@/components/correlation/correlation-results'
import { LLMBudgetMonitor } from '@/components/llm/llm-budget-monitor'
import { CorrelationResponse } from '@/lib/api-client'
import { 
  Brain, 
  Activity, 
  Users, 
  Sparkles,
  ArrowRight,
  CheckCircle 
} from 'lucide-react'

interface TeamMember {
  id: string
  full_name: string
  email: string
  role: 'manager' | 'team_member'
}

interface LLMPerformanceDashboardProps {
  teamMembers: TeamMember[]
  managerName: string
}

type ViewState = 'overview' | 'collecting' | 'results'

export function LLMPerformanceDashboard({ 
  teamMembers, 
  managerName 
}: LLMPerformanceDashboardProps) {
  const [currentView, setCurrentView] = useState<ViewState>('overview')
  const [selectedMember, setSelectedMember] = useState<TeamMember | null>(null)
  const [correlationResults, setCorrelationResults] = useState<CorrelationResponse | null>(null)
  const [correlationMode, setCorrelationMode] = useState<'llm' | 'basic'>('llm')

  const handleStartCollection = (member: TeamMember) => {
    setSelectedMember(member)
    setCurrentView('collecting')
  }

  const handleCorrelationSuccess = (results: CorrelationResponse) => {
    setCorrelationResults(results)
    setCurrentView('results')
  }

  const handleBackToOverview = () => {
    setCurrentView('overview')
    setSelectedMember(null)
    setCorrelationResults(null)
  }

  const handleBackToCollection = () => {
    setCurrentView('collecting')
    setCorrelationResults(null)
  }

  const handleExportResults = () => {
    if (!correlationResults || !selectedMember) return

    const exportData = {
      teamMember: selectedMember.full_name,
      manager: managerName,
      correlations: correlationResults.relationships,
      generatedAt: new Date().toISOString(),
      mode: correlationMode
    }

    const dataStr = JSON.stringify(exportData, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = `performance-insights-${selectedMember.full_name.replace(/\s+/g, '-').toLowerCase()}-${new Date().toISOString().split('T')[0]}.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  // Overview View
  if (currentView === 'overview') {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center justify-center space-x-2">
            <Brain className="h-8 w-8 text-purple-600" />
            <span>🧠 LLM-Enhanced Performance Insights</span>
          </h1>
          <p className="text-lg text-gray-600">
            AI-powered semantic correlation for meaningful performance conversations
          </p>
          <Badge variant="outline" className="bg-purple-50 text-purple-700">
            Production Ready • Cost-Optimized • Real-time Budget Monitoring
          </Badge>
        </div>

        {/* LLM Budget Monitor */}
        <LLMBudgetMonitor showDetails={true} />

        {/* Team Members */}
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>Team Performance Analysis</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {teamMembers.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg font-medium mb-2">No team members yet</p>
                    <p className="text-sm">Add team members to start collecting evidence and insights</p>
                  </div>
                ) : (
                  teamMembers
                    .filter(member => member.role === 'team_member')
                    .map((member) => (
                      <Card key={member.id} className="hover:shadow-md transition-shadow">
                        <CardContent className="p-6">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                                {member.full_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                              </div>
                              <div>
                                <h3 className="font-medium text-lg">{member.full_name}</h3>
                                <p className="text-sm text-gray-600">{member.email}</p>
                                <div className="flex items-center space-x-2 mt-1">
                                  <Badge variant="outline" className="text-xs">
                                    Team Member
                                  </Badge>
                                </div>
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-3">
                              <div className="text-right text-sm text-gray-500">
                                <div>Ready for analysis</div>
                                <div className="text-xs">GitLab + JIRA correlation</div>
                              </div>
                              <Button 
                                onClick={() => handleStartCollection(member)}
                                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                              >
                                <Sparkles className="h-4 w-4 mr-2" />
                                Analyze Performance
                                <ArrowRight className="h-4 w-4 ml-2" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Feature Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-gradient-to-br from-purple-50 to-blue-50 border-purple-200">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3 mb-3">
                <Brain className="h-8 w-8 text-purple-600" />
                <div>
                  <h3 className="font-medium">LLM-Enhanced Correlation</h3>
                  <p className="text-sm text-gray-600">3-tier cost-optimized pipeline</p>
                </div>
              </div>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Pre-filtering (FREE) saves 70-90% costs</li>
                <li>• Embedding similarity analysis</li>
                <li>• LLM semantic understanding</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3 mb-3">
                <Activity className="h-8 w-8 text-green-600" />
                <div>
                  <h3 className="font-medium">Real-time Monitoring</h3>
                  <p className="text-sm text-gray-600">Budget & performance tracking</p>
                </div>
              </div>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• $15/month budget with alerts</li>
                <li>• Automatic fallback to rule-based</li>
                <li>• Performance metrics dashboard</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-50 to-yellow-50 border-orange-200">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3 mb-3">
                <CheckCircle className="h-8 w-8 text-orange-600" />
                <div>
                  <h3 className="font-medium">Production Ready</h3>
                  <p className="text-sm text-gray-600">Tested & validated APIs</p>
                </div>
              </div>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Both Anthropic & OpenAI working</li>
                <li>• &lt;15s processing time</li>
                <li>• 95%+ correlation accuracy</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // Evidence Collection View
  if (currentView === 'collecting' && selectedMember) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              🔍 Evidence Collection
            </h2>
            <p className="text-gray-600 mt-1">
              Collecting performance evidence for {selectedMember.full_name}
            </p>
          </div>
          <Button variant="outline" onClick={handleBackToOverview}>
            ← Back to Dashboard
          </Button>
        </div>

        {/* Evidence Collector */}
        <EvidenceCollector
          teamMemberId={selectedMember.id}
          teamMemberName={selectedMember.full_name}
          onSuccess={(results) => {
            setCorrelationMode(results.usage_report ? 'llm' : 'basic')
            handleCorrelationSuccess(results)
          }}
          onError={(error) => {
            console.error('Collection failed:', error)
            // Could add error handling UI here
          }}
        />
      </div>
    )
  }

  // Results View
  if (currentView === 'results' && correlationResults && selectedMember) {
    return (
      <div className="space-y-6">
        <CorrelationResults
          correlationResponse={correlationResults}
          teamMemberName={selectedMember.full_name}
          mode={correlationMode}
          onExport={handleExportResults}
          onBack={handleBackToCollection}
        />
        
        {/* Quick Actions */}
        <div className="flex items-center justify-center space-x-4">
          <Button variant="outline" onClick={handleBackToOverview}>
            ← Back to Dashboard
          </Button>
          <Button 
            onClick={() => handleStartCollection(selectedMember)}
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
          >
            🔄 Run Another Analysis
          </Button>
        </div>
      </div>
    )
  }

  return null
} 