/**
 * Search API Endpoints
 * 
 * All search-related API calls
 */

import { apiClient } from '../client'

/**
 * Search entities by keyword or semantic similarity
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @param {number} [options.limit=10] - Max results
 * @param {boolean} [options.semantic=false] - Use semantic search
 * @returns {Promise<Array>} Search results
 */
export async function search(query, { limit = 10, semantic = false } = {}) {
  return apiClient.get('/search', {
    q: query,
    limit,
    semantic: semantic ? 'true' : 'false',
  })
}

/**
 * Get search suggestions for autocomplete
 * @param {string} query - Partial search query
 * @param {number} [limit=5] - Max suggestions
 * @returns {Promise<Array<string>>} Suggestions
 */
export async function getSuggestions(query, limit = 5) {
  return apiClient.get('/search/suggestions', {
    q: query,
    limit,
  })
}

/**
 * Hybrid search (keyword + semantic combined)
 * @param {string} query - Search query
 * @param {number} [limit=10] - Max results
 * @returns {Promise<Array>} Search results with combined scores
 */
export async function hybridSearch(query, limit = 10) {
  // Backend handles hybrid logic
  return search(query, { limit, semantic: true })
}
