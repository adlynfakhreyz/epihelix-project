/**
 * Query API Endpoints
 * 
 * Free-form query console (Cypher/SPARQL)
 */

import { apiClient } from '../client'

/**
 * Execute Cypher or SPARQL query
 * @param {string} query - Query string
 * @param {('cypher'|'sparql')} [type='cypher'] - Query language
 * @returns {Promise<Object>} Query results with columns and rows
 */
export async function executeQuery(query, type = 'cypher') {
  return apiClient.post('/query', {
    query,
    type,
  })
}

/**
 * Execute Cypher query
 * @param {string} query - Cypher query string
 * @returns {Promise<Object>} Query results
 */
export async function executeCypher(query) {
  return executeQuery(query, 'cypher')
}

/**
 * Execute SPARQL query
 * @param {string} query - SPARQL query string
 * @returns {Promise<Object>} Query results
 */
export async function executeSPARQL(query) {
  return executeQuery(query, 'sparql')
}
