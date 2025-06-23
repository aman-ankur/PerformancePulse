import { apiClient, UnifiedEvidenceItem, CorrelationRequest, CorrelationResponse, WorkStory, EvidenceRelationship } from '../api-client'
import fetchMock from 'jest-fetch-mock'

// Enable fetch mocking
fetchMock.enableMocks()

describe('API Client Tests', () => {
  beforeEach(() => {
    fetchMock.resetMocks()
  })

  describe('Evidence Correlation', () => {
    const mockEvidenceItem: UnifiedEvidenceItem = {
      id: 'test-evidence-1',
      team_member_id: 'team-1',
      source: 'gitlab_commit',
      title: 'Test Commit',
      description: 'Test description',
      category: 'technical',
      evidence_date: '2024-03-20T10:00:00Z',
      platform: 'gitlab',
      data_source: 'gitlab_api',
      created_at: '2024-03-20T10:00:00Z',
      updated_at: '2024-03-20T10:00:00Z'
    }

    const mockRequest: CorrelationRequest = {
      evidence_collection_id: 'team-1',
      confidence_threshold: 0.3,
      max_work_stories: 50,
      include_low_confidence: false,
      detect_technology_stack: true,
      analyze_work_patterns: true,
      generate_insights: true,
      min_evidence_per_story: 2,
      max_story_duration_days: 90
    }

    const mockSuccessResponse: CorrelationResponse = {
      success: true,
      correlated_collection: {
        evidence_items: [mockEvidenceItem],
        total_evidence_count: 1,
        work_stories: [{
          id: 'story-1',
          title: 'Test Story',
          description: 'Test work story',
          evidence_items: [mockEvidenceItem],
          relationships: [],
          technology_stack: ['typescript', 'react'],
          complexity_score: 0.7,
          team_members_involved: ['team-1'],
          status: 'completed',
          completion_percentage: 100,
          created_at: '2024-03-20T10:00:00Z',
          updated_at: '2024-03-20T10:00:00Z'
        }],
        relationships: [{
          id: 'rel-1',
          primary_evidence_id: 'test-evidence-1',
          related_evidence_id: 'test-evidence-2',
          relationship_type: 'solves',
          confidence_score: 0.95,
          detection_method: 'content_analysis',
          evidence_summary: 'Test relationship',
          detected_at: '2024-03-20T10:00:00Z'
        }],
        insights: {
          total_work_stories: 1,
          total_relationships: 1,
          avg_confidence_score: 0.95,
          technology_distribution: { typescript: 1, react: 1 },
          work_pattern_summary: { avg_completion_time: '2d' },
          collaboration_score: 0.9,
          cross_platform_activity: { gitlab: 1 },
          generated_at: '2024-03-20T10:00:00Z'
        }
      },
      processing_time_ms: 1000,
      items_processed: 1,
      relationships_detected: 1,
      work_stories_created: 1,
      avg_confidence_score: 0.95,
      correlation_coverage: 100
    }

    it('should properly structure correlation request', async () => {
      fetchMock.mockResponseOnce(JSON.stringify(mockSuccessResponse))

      await apiClient.correlateEvidence(mockRequest)
      const lastCall = fetchMock.mock.lastCall
      const requestBody = JSON.parse(lastCall![1]!.body as string)

      expect(requestBody).toEqual(mockRequest)
      expect(requestBody.evidence_collection_id).toBe('team-1')
      expect(requestBody.confidence_threshold).toBe(0.3)
      expect(requestBody.max_work_stories).toBe(50)
      expect(requestBody.include_low_confidence).toBe(false)
      expect(requestBody.detect_technology_stack).toBe(true)
      expect(requestBody.analyze_work_patterns).toBe(true)
      expect(requestBody.generate_insights).toBe(true)
      expect(requestBody.min_evidence_per_story).toBe(2)
      expect(requestBody.max_story_duration_days).toBe(90)
    })

    it('should properly handle correlation response', async () => {
      fetchMock.mockResponseOnce(JSON.stringify(mockSuccessResponse))
      const response = await apiClient.correlateEvidence(mockRequest)

      expect(response.success).toBe(true)
      expect(response.correlated_collection).toBeDefined()
      expect(response.processing_time_ms).toBe(1000)
      expect(response.items_processed).toBe(1)
      expect(response.relationships_detected).toBe(1)
      expect(response.work_stories_created).toBe(1)
      expect(response.avg_confidence_score).toBe(0.95)
      expect(response.correlation_coverage).toBe(100)

      // Validate evidence items
      const evidence = response.correlated_collection!.evidence_items[0]
      expect(evidence).toEqual(mockEvidenceItem)
      expect(evidence.id).toBe('test-evidence-1')
      expect(evidence.team_member_id).toBe('team-1')
      expect(evidence.source).toBe('gitlab_commit')
      expect(evidence.platform).toBe('gitlab')

      // Validate work stories
      const story = response.correlated_collection!.work_stories[0]
      expect(story.id).toBe('story-1')
      expect(story.evidence_items).toHaveLength(1)
      expect(story.technology_stack).toEqual(['typescript', 'react'])

      // Validate relationships
      const relationship = response.correlated_collection!.relationships[0]
      expect(relationship.id).toBe('rel-1')
      expect(relationship.confidence_score).toBe(0.95)
      expect(relationship.relationship_type).toBe('solves')

      // Validate insights
      const insights = response.correlated_collection!.insights!
      expect(insights.total_work_stories).toBe(1)
      expect(insights.total_relationships).toBe(1)
      expect(insights.avg_confidence_score).toBe(0.95)
      expect(insights.technology_distribution).toEqual({ typescript: 1, react: 1 })
      expect(insights.collaboration_score).toBe(0.9)
      expect(insights.cross_platform_activity).toEqual({ gitlab: 1 })
    })

    it('should validate date formats', () => {
      const dateRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/

      // Check evidence item dates
      expect(mockEvidenceItem.evidence_date).toMatch(dateRegex)
      expect(mockEvidenceItem.created_at).toMatch(dateRegex)
      expect(mockEvidenceItem.updated_at).toMatch(dateRegex)

      // Check relationship dates
      const relationship = mockSuccessResponse.correlated_collection!.relationships[0]
      expect(relationship.detected_at).toMatch(dateRegex)

      // Check work story dates
      const story = mockSuccessResponse.correlated_collection!.work_stories[0]
      expect(story.created_at).toMatch(dateRegex)
      expect(story.updated_at).toMatch(dateRegex)

      // Check insights date
      expect(mockSuccessResponse.correlated_collection!.insights!.generated_at).toMatch(dateRegex)
    })

    it('should handle various HTTP errors', async () => {
      const errorCases = [
        { status: 400, message: 'Bad Request' },
        { status: 401, message: 'Unauthorized' },
        { status: 403, message: 'Forbidden' },
        { status: 404, message: 'Not Found' },
        { status: 500, message: 'Internal Server Error' }
      ]

      for (const errorCase of errorCases) {
        fetchMock.resetMocks()
        fetchMock.mockResponseOnce('', { status: errorCase.status, statusText: errorCase.message })
        
        await expect(apiClient.correlateEvidence(mockRequest))
          .rejects
          .toThrow(`Correlation failed: ${errorCase.status} ${errorCase.message}`)
      }
    })

    it('should handle validation errors (422) with detailed response', async () => {
      const validationError = {
        detail: [
          {
            loc: ['body', 'evidence_collection_id'],
            msg: 'field required',
            type: 'value_error.missing'
          },
          {
            loc: ['body', 'confidence_threshold'],
            msg: 'ensure this value is greater than 0',
            type: 'value_error.number.not_gt'
          }
        ]
      }

      fetchMock.mockResponseOnce(JSON.stringify(validationError), { 
        status: 422, 
        statusText: 'Unprocessable Entity',
        headers: { 'Content-Type': 'application/json' }
      })

      const invalidRequest = {
        ...mockRequest,
        evidence_collection_id: '',
        confidence_threshold: -0.1
      }
      
      await expect(apiClient.correlateEvidence(invalidRequest))
        .rejects
        .toThrow('Validation error: field required (evidence_collection_id), ensure this value is greater than 0 (confidence_threshold)')
    })

    it('should handle network errors', async () => {
      fetchMock.mockReject(new Error('Network error'))
      await expect(apiClient.correlateEvidence(mockRequest))
        .rejects
        .toThrow('Network error')
    })

    it('should handle invalid JSON responses', async () => {
      fetchMock.mockResponseOnce('invalid json')
      await expect(apiClient.correlateEvidence(mockRequest))
        .rejects
        .toThrow()
    })

    it('should handle basic correlation mode', async () => {
      fetchMock.mockResponseOnce(JSON.stringify(mockSuccessResponse))

      const response = await apiClient.correlateEvidenceBasic(mockRequest)
      const lastCall = fetchMock.mock.lastCall

      expect(lastCall![0]).toBe('http://localhost:8000/api/correlate-basic')
      expect(response).toEqual(mockSuccessResponse)
    })
  })
}) 