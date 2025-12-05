/**
 * useEntity Hook
 * 
 * React Query hook for fetching entity details
 */

'use client'

import { useQuery } from '@tanstack/react-query'
import { getEntity, getRelatedEntities } from '@/lib/api'
import { queryKeys } from '@/lib/queryClient'

/**
 * Fetch entity details with React Query
 * @param {string} id - Entity ID
 * @param {Object} options - Fetch options
 * @param {boolean} [options.includeRelated=false] - Include related entities
 * @param {boolean} [options.enabled=true] - Enable query
 * @returns {Object} React Query result
 */
export function useEntity(id, { includeRelated = false, enabled = true } = {}) {
  return useQuery({
    queryKey: queryKeys.entity(id),
    queryFn: () => getEntity(id, { includeRelated }),
    enabled: enabled && Boolean(id),
    staleTime: 10 * 60 * 1000, // 10 minutes (entities don't change often)
  })
}

/**
 * Fetch related entities with React Query
 * @param {string} id - Entity ID
 * @param {Object} options - Fetch options
 * @param {number} [options.depth=1] - Relationship depth
 * @param {number} [options.limit=20] - Max related entities
 * @param {boolean} [options.enabled=true] - Enable query
 * @returns {Object} React Query result
 */
export function useRelatedEntities(id, { depth = 1, limit = 20, enabled = true } = {}) {
  return useQuery({
    queryKey: queryKeys.relatedEntities(id),
    queryFn: () => getRelatedEntities(id, depth, limit),
    enabled: enabled && Boolean(id),
    staleTime: 10 * 60 * 1000,
  })
}

export default useEntity
