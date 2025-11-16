'use client'

import { useState, useEffect } from 'react'
import { getEntity } from '../lib/api'

/**
 * Custom hook for fetching entity data
 * @param {string} id - Entity ID
 * @returns {Object} Entity state
 */
export default function useEntity(id) {
  const [entity, setEntity] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!id) return

    async function fetchEntity() {
      setLoading(true)
      setError(null)

      try {
        const data = await getEntity(id)
        setEntity(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchEntity()
  }, [id])

  return { entity, loading, error }
}
