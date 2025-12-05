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
  // Load history from localStorage on mount
  const [history, setHistory] = useState(() => {
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem('query-history')
        return saved ? JSON.parse(saved) : []
      } catch (error) {
        console.error('Failed to load query history:', error)
        return []
      }
    }
    return []
  })
  
  const executeMutation = useExecuteQuery({
    onSuccess: (data, variables) => {
      // Add to history
      const newEntry = {
        query: variables.query,
        type: variables.type,
        result: data,
        timestamp: new Date().toISOString(),
      }
      
      setHistory(prev => {
        const updated = [...prev, newEntry]
        // Save to localStorage
        if (typeof window !== 'undefined') {
          try {
            localStorage.setItem('query-history', JSON.stringify(updated))
          } catch (error) {
            console.error('Failed to save query history:', error)
          }
        }
        return updated
      })
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
    if (typeof window !== 'undefined') {
      try {
        localStorage.removeItem('query-history')
      } catch (error) {
        console.error('Failed to clear query history:', error)
      }
    }
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
