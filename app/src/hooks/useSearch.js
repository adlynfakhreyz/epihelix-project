/**
 * useSearch Hook
 * 
 * React Query hook for searching entities
 */

'use client'

import { useQuery } from '@tanstack/react-query'
import { search } from '@/lib/api/endpoints/search'
import { queryKeys } from '@/lib/queryClient'

/**
 * Search entities with React Query
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @param {number} [options.limit=10] - Max results
 * @param {boolean} [options.semantic=false] - Use semantic search
 * @param {boolean} [options.enabled=true] - Enable query
 * @returns {Object} React Query result
 */
export function useSearch(query, { limit = 10, semantic = false, enabled = true } = {}) {
  return useQuery({
    queryKey: queryKeys.search(query, { limit, semantic }),
    queryFn: () => search(query, { limit, semantic }),
    enabled: enabled && Boolean(query?.trim()),
    keepPreviousData: true,
  })
}

/**
 * Get search suggestions with React Query
 * Uses the same search API with smaller limit
 * @param {string} query - Partial query
 * @param {Object} options - Options
 * @param {number} [options.limit=5] - Max suggestions
 * @param {boolean} [options.enabled=true] - Enable query
 * @returns {Object} React Query result
 */
export function useSuggestions(query, { limit = 5, enabled = true } = {}) {
  return useQuery({
    queryKey: queryKeys.suggestions(query),
    queryFn: () => search(query, { limit }),
    enabled: enabled && Boolean(query?.trim()),
    staleTime: 1 * 60 * 1000, // 1 minute
    keepPreviousData: true,
  })
}

/**
 * Hybrid search (keyword + semantic)
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @returns {Object} React Query result
 */
export function useHybridSearch(query, options = {}) {
  return useSearch(query, { ...options, semantic: true })
}

export default useSearch
