/**
 * LLM Integration Test Component
 * Simple test to verify the LLM backend integration works
 */

'use client'

import { useState } from 'react'
// import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api-client'
import { CheckCircle, XCircle, Clock, RefreshCw } from 'lucide-react'

export function LLMIntegrationTest() {
  const [testResults, setTestResults] = useState<{
    health: boolean | null
    engineStatus: boolean | null
    llmUsage: boolean | null
  }>({
    health: null,
    engineStatus: null,
    llmUsage: null
  })

  const [isRunningTests, setIsRunningTests] = useState(false)

  const runTests = async () => {
    setIsRunningTests(true)
    setTestResults({ health: null, engineStatus: null, llmUsage: null })

    try {
      // Test 1: Health check
      console.log('Testing health check...')
      const healthResult = await apiClient.healthCheck()
      setTestResults(prev => ({ ...prev, health: healthResult }))
      
      // Test 2: Engine status
      console.log('Testing engine status...')
      try {
        await apiClient.getEngineStatus()
        setTestResults(prev => ({ ...prev, engineStatus: true }))
      } catch (error) {
        console.error('Engine status test failed:', error)
        setTestResults(prev => ({ ...prev, engineStatus: false }))
      }

      // Test 3: LLM usage
      console.log('Testing LLM usage...')
      try {
        await apiClient.getLLMUsage()
        setTestResults(prev => ({ ...prev, llmUsage: true }))
      } catch (error) {
        console.error('LLM usage test failed:', error)
        setTestResults(prev => ({ ...prev, llmUsage: false }))
      }

    } catch (error) {
      console.error('Test suite failed:', error)
    } finally {
      setIsRunningTests(false)
    }
  }

  const getStatusIcon = (status: boolean | null) => {
    if (status === null) return <Clock className="h-4 w-4 text-gray-400" />
    if (status === true) return <CheckCircle className="h-4 w-4 text-green-500" />
    return <XCircle className="h-4 w-4 text-red-500" />
  }

  const getStatusBadge = (status: boolean | null) => {
    if (status === null) return <Badge variant="outline">Pending</Badge>
    if (status === true) return <Badge className="bg-green-100 text-green-800">✅ Pass</Badge>
    return <Badge className="bg-red-100 text-red-800">❌ Fail</Badge>
  }

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <span>🧪 LLM Backend Integration Test</span>
          {isRunningTests && <RefreshCw className="h-5 w-5 animate-spin" />}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Test Button */}
        <div className="text-center">
          <Button 
            onClick={runTests}
            disabled={isRunningTests}
            className="bg-purple-600 hover:bg-purple-700"
          >
            {isRunningTests ? 'Running Tests...' : '🚀 Test LLM Integration'}
          </Button>
        </div>

        {/* Test Results */}
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              {getStatusIcon(testResults.health)}
              <div>
                <span className="font-medium">Backend Health Check</span>
                <div className="text-sm text-gray-600">Basic connectivity test</div>
              </div>
            </div>
            {getStatusBadge(testResults.health)}
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              {getStatusIcon(testResults.engineStatus)}
              <div>
                <span className="font-medium">Engine Status API</span>
                <div className="text-sm text-gray-600">Correlation engine capabilities</div>
              </div>
            </div>
            {getStatusBadge(testResults.engineStatus)}
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              {getStatusIcon(testResults.llmUsage)}
              <div>
                <span className="font-medium">LLM Usage API</span>
                <div className="text-sm text-gray-600">Budget monitoring and cost tracking</div>
              </div>
            </div>
            {getStatusBadge(testResults.llmUsage)}
          </div>
        </div>

        {/* Test Summary */}
        {Object.values(testResults).some(result => result !== null) && (
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">Test Summary</h4>
            <div className="text-sm text-blue-700">
              {Object.values(testResults).filter(r => r === true).length} / 3 tests passed
            </div>
            {Object.values(testResults).every(r => r === true) && (
              <div className="text-sm text-green-700 font-medium mt-1">
                ✅ All systems operational! LLM integration is ready.
              </div>
            )}
          </div>
        )}

        {/* Instructions */}
        <div className="text-xs text-gray-500 text-center">
          <p>This test verifies the connection to your LLM-enhanced backend.</p>
          <p>Make sure your backend server is running on localhost:8000</p>
        </div>
      </CardContent>
    </Card>
  )
} 