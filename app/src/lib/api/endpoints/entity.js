/**
 * Entity API Endpoints
 * 
 * All entity-related API calls (InfoBox, details, etc.)
 */

import { apiClient } from '../client'

/**
 * Get entity details by ID
 * @param {string} id - Entity ID
 * @param {Object} [options] - Fetch options
 * @param {boolean} [options.includeRelated=false] - Include related entities
 * @returns {Promise<Object>} Entity details
 */
export async function getEntity(id, { includeRelated = false } = {}) {
  return apiClient.get(`/entity/${id}`, {
    include_related: includeRelated ? 'true' : 'false',
  })
}

/**
 * Get multiple entities by IDs
 * @param {string[]} ids - Array of entity IDs
 * @returns {Promise<Object[]>} Array of entities
 */
export async function getEntities(ids) {
  // Fetch all in parallel
  const promises = ids.map(id => getEntity(id))
  return Promise.all(promises)
}

/**
 * Get related entities for an entity
 * @param {string} id - Entity ID
 * @param {number} [depth=1] - Relationship depth
 * @param {number} [limit=20] - Max related entities
 * @returns {Promise<Object>} Related entities with relationships
 */
export async function getRelatedEntities(id, depth = 1, limit = 20) {
  return getEntity(id, { includeRelated: true })
}
