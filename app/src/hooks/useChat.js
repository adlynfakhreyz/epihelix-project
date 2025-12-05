/**
 * useChat Hook
 * 
 * React Query hook for RAG chatbot
 */

'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { sendMessage, clearSession, createSessionId } from '@/lib/api'
import { queryKeys } from '@/lib/queryClient'
import { useState, useCallback, useMemo } from 'react'

/**
 * Send chat message with React Query mutation
 * @param {string} sessionId - Session ID
 * @param {Object} [options] - Mutation options
 * @returns {Object} React Query mutation result
 */
export function useSendMessage(sessionId, options = {}) {
  return useMutation({
    mutationFn: ({ message, includeHistory }) =>
      sendMessage(message, { sessionId, includeHistory }),
    
    ...options,
  })
}

/**
 * Clear chat session with React Query mutation
 * @param {Object} [options] - Mutation options
 * @returns {Object} React Query mutation result
 */
export function useClearSession(options = {}) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (sessionId) => clearSession(sessionId),
    
    onSuccess: (data, sessionId) => {
      // Invalidate chat queries for this session
      queryClient.invalidateQueries(queryKeys.chat(sessionId))
    },
    
    ...options,
  })
}

/**
 * Complete chat hook with session management
 * @param {Object} [options] - Chat options
 * @param {string} [options.initialSessionId] - Initial session ID
 * @returns {Object} Chat state and methods
 */
export function useChat({ initialSessionId } = {}) {
  const [sessionId, setSessionId] = useState(
    () => initialSessionId || createSessionId()
  )
  const [messages, setMessages] = useState([])

  const sendMessageMutation = useSendMessage(sessionId, {
    onSuccess: (data, variables) => {
      // Add user message and bot response to local state
      setMessages(prev => [
        ...prev,
        { role: 'user', content: variables.message },
        { role: 'assistant', content: data.reply, sources: data.sources },
      ])
    },
  })

  const clearSessionMutation = useClearSession({
    onSuccess: () => {
      setMessages([])
    },
  })

  const send = useCallback(
    (message) => {
      sendMessageMutation.mutate({ message, includeHistory: true })
    },
    [sendMessageMutation]
  )

  const clear = useCallback(() => {
    clearSessionMutation.mutate(sessionId)
  }, [clearSessionMutation, sessionId])

  const reset = useCallback(() => {
    const newSessionId = createSessionId()
    setSessionId(newSessionId)
    setMessages([])
  }, [])

  return {
    sessionId,
    messages,
    send,
    clear,
    reset,
    isLoading: sendMessageMutation.isLoading,
    error: sendMessageMutation.error,
  }
}

export default useChat
