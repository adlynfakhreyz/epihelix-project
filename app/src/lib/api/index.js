/**
 * API Index - Centralized API exports
 * 
 * Import all API functions from one place:
 * import { search, getEntity, sendMessage } from '@/lib/api'
 */

// Search
export { search, getSuggestions, hybridSearch } from './endpoints/search'

// Entity
export { getEntity, getEntities, getRelatedEntities } from './endpoints/entity'

// Summary
export { generateSummary, generateSummaries } from './endpoints/summary'

// Chat
export { sendMessage, clearSession, createSessionId } from './endpoints/chat'

// Query
export { executeQuery, executeCypher, executeSPARQL } from './endpoints/query'

// Client (for custom usage)
export { apiClient, APIError } from './client'
