/**
 * Chat API Endpoints
 * 
 * RAG chatbot with conversation history
 */

import { apiClient } from '../client'

/**
 * Send chat message
 * @param {string} message - User's message
 * @param {Object} [options] - Chat options
 * @param {string} [options.sessionId] - Session ID for conversation continuity
 * @param {boolean} [options.includeHistory=true] - Use conversation history
 * @returns {Promise<Object>} Chat response with sources
 */
export async function sendMessage(message, { sessionId, includeHistory = true } = {}) {
  return apiClient.post('/chat', {
    message,
    session_id: sessionId,
    include_history: includeHistory,
  })
}

/**
 * Clear chat session (conversation history)
 * @param {string} sessionId - Session ID to clear
 * @returns {Promise<Object>} Success response
 */
export async function clearSession(sessionId) {
  return apiClient.delete('/chat', {
    session_id: sessionId,
  })
}

/**
 * Start new chat session
 * @returns {string} New session ID
 */
export function createSessionId() {
  return `session_${Date.now()}_${Math.random().toString(36).substring(7)}`
}
