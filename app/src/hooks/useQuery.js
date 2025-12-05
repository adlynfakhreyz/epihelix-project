/**
 * useQuery Hook
 * 
 * React Query hook for query console (Cypher/SPARQL execution)
 */

'use client'

import { useState, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { executeQuery, executeCypher, executeSPARQL } from '@/lib/api'

/**
 * Execute query with React Query mutation
 * @param {Object} [options] - Mutation options
 * @returns {Object} React Query mutation result
 */
export function useExecuteQuery(options = {}) {
  return useMutation({
    mutationFn: ({ query, type }) => executeQuery(query, type),
    ...options,
  })
}

/**
 * Execute Cypher query
 * @param {Object} [options] - Mutation options
 * @returns {Object} React Query mutation result
 */
export function useExecuteCypher(options = {}) {
  return useMutation({
    mutationFn: (query) => executeCypher(query),
    ...options,
  })
}

/**
 * Execute SPARQL query
 * @param {Object} [options] - Mutation options
 * @returns {Object} React Query mutation result
 */
export function useExecuteSPARQL(options = {}) {
  return useMutation({
    mutationFn: (query) => executeSPARQL(query),
    ...options,
  })
}

/**
 * Complete query console hook with history
 * @returns {Object} Query console state and methods
 */
export function useQueryConsole() {
  const [history, setHistory] = useState([])
  
  const executeMutation = useExecuteQuery({
    onSuccess: (data, variables) => {
      // Add to history
      setHistory(prev => [
        ...prev,
        {
          query: variables.query,
          type: variables.type,
          result: data,
          timestamp: new Date().toISOString(),
        },
      ])
    },
  })

  const execute = useCallback(
    (query, type = 'cypher') => {
      executeMutation.mutate({ query, type })
    },
    [executeMutation]
  )

  const clearHistory = useCallback(() => {
    setHistory([])
  }, [])

  return {
    execute,
    clearHistory,
    history,
    isLoading: executeMutation.isLoading,
    error: executeMutation.error,
    data: executeMutation.data,
  }
}

export default useExecuteQuery
