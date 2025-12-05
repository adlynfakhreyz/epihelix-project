/**
 * Search API Endpoints
 * 
 * All search-related API calls
 */

import { apiClient } from '../client'

/**
 * Search entities by keyword or semantic similarity with pagination
 * @param {string} query - Search query
 * @param {Object} options - Search options
 * @param {number} [options.page=1] - Page number (1-indexed)
 * @param {number} [options.page_size=10] - Results per page
 * @param {boolean} [options.semantic=false] - Use semantic search
 * @param {boolean} [options.rerank=true] - Use cross-encoder reranking (enabled by default)
 * @param {boolean} [options.summarize=true] - Add LLM summaries (enabled by default)
 * @returns {Promise<Object>} Paginated search results { results, total, page, page_size, total_pages, has_next, has_prev }
 */
export async function search(query, { page = 1, page_size = 10, semantic = false, rerank = true, summarize = true } = {}) {
  return apiClient.get('/search', {
    q: query,
    page,
    page_size,
    semantic: semantic ? 'true' : 'false',
    rerank: rerank ? 'true' : 'false',
    summarize: summarize ? 'true' : 'false',
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
