/**
 * Centralized query key definitions for React Query
 */
export const queryKeys = {
  engineStatus: () => ['engine', 'status'],
  correlationResults: (teamMemberId: string) => ['correlation', 'results', teamMemberId],
  llmUsage: () => ['llm-usage'],
  evidenceCollection: (teamMemberId: string) => ['evidence', 'collection', teamMemberId]
} 