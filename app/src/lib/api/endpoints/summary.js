/**
 * Summary API Endpoints
 * 
 * LLM-powered entity summarization
 */

import { apiClient } from '../client'

/**
 * Generate summary for an entity
 * @param {string} entityId - Entity ID to summarize
 * @param {Object} [options] - Generation options
 * @param {string} [options.query] - Original search query (for context)
 * @param {boolean} [options.includeRelations=true] - Include related entities
 * @returns {Promise<Object>} Summary with metadata
 */
export async function generateSummary(entityId, { query, includeRelations = true } = {}) {
  return apiClient.post('/summary/generate', {
    entity_id: entityId,
    query,
    include_relations: includeRelations,
  })
}

/**
 * Generate summaries for multiple entities
 * @param {string[]} entityIds - Array of entity IDs
 * @param {Object} [options] - Generation options
 * @returns {Promise<Object[]>} Array of summaries
 */
export async function generateSummaries(entityIds, options = {}) {
  const promises = entityIds.map(id => generateSummary(id, options))
  return Promise.all(promises)
}
