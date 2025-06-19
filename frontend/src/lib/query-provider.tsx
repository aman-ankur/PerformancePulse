/**
 * React Query Provider
 * Manages API state for LLM-enhanced PerformancePulse
 */

'use client'

import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import React from 'react'

interface QueryProviderProps {
  children: React.ReactNode
}

export function QueryProvider({ children }: QueryProviderProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Stale time - how long data is considered fresh
            staleTime: 60 * 1000, // 1 minute
            // Cache time - how long data stays in cache when not used
            gcTime: 5 * 60 * 1000, // 5 minutes (previously cacheTime)
            // Retry configuration
            retry: (failureCount, error) => {
              // Don't retry on 4xx errors except 408, 429
              if (error && typeof error === 'object' && 'status' in error) {
                const status = error.status as number
                if (status >= 400 && status < 500 && ![408, 429].includes(status)) {
                  return false
                }
              }
              // Retry up to 3 times for other errors
              return failureCount < 3
            },
            retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
          },
          mutations: {
            retry: 1,
            retryDelay: 1000,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* Only include DevTools in development */}
      {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
    </QueryClientProvider>
  )
}

// Dynamically import DevTools only in development
function ReactQueryDevtools() {
  const [DevTools, setDevTools] = useState<React.ComponentType | null>(null)

  React.useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      import('@tanstack/react-query-devtools').then((mod) => {
        setDevTools(() => mod.ReactQueryDevtools)
      }).catch((error) => {
        console.warn('Failed to load React Query DevTools:', error)
      })
    }
  }, [])

  if (!DevTools) return null
  return <DevTools />
} 