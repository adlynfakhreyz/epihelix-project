'use client'

import { useState } from 'react'
import { search } from '../lib/api'

/**
 * Custom hook for search functionality
 * @returns {Object} Search state and methods
 */
export default function useSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function executeSearch(q, options = {}) {
    if (!q.trim()) {
      setResults([])
      return
    }

    setLoading(true)
    setError(null)
    setQuery(q)

    try {
      const data = await search(q, options)
      setResults(data)
    } catch (err) {
      setError(err.message)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  function clear() {
    setQuery('')
    setResults([])
    setError(null)
  }

  return {
    query,
    results,
    loading,
    error,
    executeSearch,
    clear,
  }
}
