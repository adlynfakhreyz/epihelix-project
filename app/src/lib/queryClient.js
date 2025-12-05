/**
 * React Query Configuration
 * 
 * Centralized configuration for @tanstack/react-query
 */

import { QueryClient } from '@tanstack/react-query'

/**
 * Default query options
 */
const defaultOptions = {
  queries: {
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
    retry: 2,
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
  },
  mutations: {
    retry: 1,
  },
}

/**
 * Create Query Client instance
 */
export const queryClient = new QueryClient({
  defaultOptions,
})

/**
 * Query Keys - Centralized for consistency
 */
export const queryKeys = {
  search: (query, options) => ['search', query, options],
  suggestions: (query) => ['suggestions', query],
  entity: (id) => ['entity', id],
  relatedEntities: (id) => ['entity', id, 'related'],
  summary: (entityId) => ['summary', entityId],
  chat: (sessionId) => ['chat', sessionId],
}
