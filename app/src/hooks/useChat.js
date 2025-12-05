/**
 * useChat Hook
 * 
 * React Query hook for RAG chatbot
 */

'use client'

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { sendMessage, clearSession, createSessionId } from '@/lib/api'
import { queryKeys } from '@/lib/queryClient'
import { useState, useCallback, useEffect, useRef } from 'react'

const SESSION_STORAGE_KEY = 'epihelix_chat_session_id'

/**
 * Get or create session ID from localStorage
 */
function getOrCreateSessionId() {
  if (typeof window === 'undefined') return null
  
  let sessionId = localStorage.getItem(SESSION_STORAGE_KEY)
  if (!sessionId) {
    sessionId = createSessionId()
    localStorage.setItem(SESSION_STORAGE_KEY, sessionId)
  }
  return sessionId
}

/**
 * Complete chat hook with session management
 */
export function useChat({ initialSessionId } = {}) {
  const [sessionId, setSessionId] = useState(initialSessionId || null)
  const [messages, setMessages] = useState([])
  const [isReady, setIsReady] = useState(false)
  
  // Use ref to always have current sessionId in mutation
  const sessionIdRef = useRef(sessionId)
  
  // Keep ref in sync
  useEffect(() => {
    sessionIdRef.current = sessionId
  }, [sessionId])

  // Get session ID from localStorage on client-side only
  useEffect(() => {
    const storedSessionId = getOrCreateSessionId()
    setSessionId(storedSessionId)
    sessionIdRef.current = storedSessionId
    setIsReady(true)
  }, [])

  const queryClient = useQueryClient()

  // Send message mutation - uses ref for current sessionId
  const sendMessageMutation = useMutation({
    mutationFn: ({ message, includeHistory }) => {
      const currentSessionId = sessionIdRef.current
      console.log('[useChat] Sending message with session:', currentSessionId)
      return sendMessage(message, { 
        sessionId: currentSessionId, 
        includeHistory 
      })
    },
    onSuccess: (data, variables) => {
      console.log('[useChat] Response received, session:', data.session_id)
      setMessages(prev => [
        ...prev,
        { role: 'user', content: variables.message },
        { role: 'assistant', content: data.message, sources: data.sources },
      ])
    },
    onError: (error) => {
      console.error('[useChat] Error:', error)
    }
  })

  // Clear session mutation
  const clearSessionMutation = useMutation({
    mutationFn: () => {
      const currentSessionId = sessionIdRef.current
      return clearSession(currentSessionId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries(queryKeys.chat(sessionIdRef.current))
      setMessages([])
    },
  })

  const send = useCallback(
    (message) => {
      if (!sessionIdRef.current) {
        console.warn('[useChat] No session ID, cannot send')
        return
      }
      sendMessageMutation.mutate({ message, includeHistory: true })
    },
    [sendMessageMutation]
  )

  const clear = useCallback(() => {
    if (!sessionIdRef.current) return
    clearSessionMutation.mutate()
  }, [clearSessionMutation])

  const reset = useCallback(() => {
    // Create new session and save to localStorage
    const newSessionId = createSessionId()
    localStorage.setItem(SESSION_STORAGE_KEY, newSessionId)
    setSessionId(newSessionId)
    sessionIdRef.current = newSessionId
    setMessages([])
  }, [])

  return {
    sessionId,
    messages,
    send,
    clear,
    reset,
    isLoading: sendMessageMutation.isPending,
    error: sendMessageMutation.error,
    isReady,
  }
}