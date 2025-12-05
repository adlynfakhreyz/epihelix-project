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
 * Search entities with React Query and pagination
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @param {number} [options.page=1] - Page number
 * @param {number} [options.page_size=10] - Results per page
 * @param {boolean} [options.semantic=false] - Use semantic search
 * @param {boolean} [options.rerank=true] - Use cross-encoder reranking (enabled by default)
 * @param {boolean} [options.summarize=true] - Add LLM summaries (enabled by default)
 * @param {boolean} [options.enabled=true] - Enable query
 * @returns {Object} React Query result with pagination data
 */
export function useSearch(query, { page = 1, page_size = 10, semantic = false, rerank = true, summarize = true, enabled = true } = {}) {
  return useQuery({
    queryKey: queryKeys.search(query, { page, page_size, semantic, rerank, summarize }),
    queryFn: () => search(query, { page, page_size, semantic, rerank, summarize }),
    enabled: enabled && Boolean(query?.trim()),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    cacheTime: 10 * 60 * 1000, // Keep in memory for 10 minutes
    // This allows instant navigation between pages you've already visited
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
