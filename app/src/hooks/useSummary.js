/**
 * useSummary Hook
 * 
 * React Query hook for LLM-powered entity summarization
 */

'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { generateSummary } from '@/lib/api'
import { queryKeys } from '@/lib/queryClient'

/**
 * Generate entity summary with React Query mutation
 * @param {Object} [options] - Mutation options
 * @returns {Object} React Query mutation result
 */
export function useSummary(options = {}) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ entityId, query, includeRelations }) =>
      generateSummary(entityId, { query, includeRelations }),
    
    onSuccess: (data, variables) => {
      // Cache the summary
      queryClient.setQueryData(
        queryKeys.summary(variables.entityId),
        data
      )
    },
    
    ...options,
  })
}

/**
 * Generate summary with React Query - convenience hook
 * @returns {Object} { generateSummary, isLoading, error, data }
 */
export function useGenerateSummary() {
  const mutation = useSummary()

  return {
    generateSummary: mutation.mutate,
    generateSummaryAsync: mutation.mutateAsync,
    isLoading: mutation.isLoading,
    error: mutation.error,
    data: mutation.data,
    reset: mutation.reset,
  }
}

export default useSummary
