import { NextResponse } from 'next/server'

/**
 * Next.js API Route - RAG Chatbot Middleware
 * 
 * Proxies chat requests to FastAPI backend
 * Handles RAG (Retrieval-Augmented Generation) chatbot
 * 
 * Features:
 * - Session management
 * - Conversation history
 * - Source citations from knowledge graph
 */

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000/api'

export async function POST(request) {
  try {
    const body = await request.json()
    const { message, session_id, include_history = true } = body

    // Validation
    if (!message || message.trim().length === 0) {
      return NextResponse.json(
        { error: 'message is required' },
        { status: 400 }
      )
    }

    if (process.env.NODE_ENV === 'development') {
      console.log('[API] Chat message:', { session_id, message: message.substring(0, 50) })
    }

    // Call FastAPI backend
    const response = await fetch(`${FASTAPI_URL}/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id,
        include_history
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('[API] Chat error:', response.status, errorData)
      
      return NextResponse.json(
        { 
          error: errorData.detail || 'Chat request failed',
          status: response.status 
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    if (process.env.NODE_ENV === 'development') {
      console.log('[API] Chat response:', {
        session: data.session_id,
        sources: data.sources?.length || 0
      })
    }

    return NextResponse.json(data)

  } catch (error) {
    console.error('[API] Chat error:', error)
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: error.message 
      },
      { status: 500 }
    )
  }
}

export async function DELETE(request) {
  try {
    const { searchParams } = new URL(request.url)
    const session_id = searchParams.get('session_id')

    if (!session_id) {
      return NextResponse.json(
        { error: 'session_id is required' },
        { status: 400 }
      )
    }

    // Call FastAPI backend to clear session
    const response = await fetch(`${FASTAPI_URL}/chat/session/${session_id}`, {
      method: 'DELETE',
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        { error: errorData.detail || 'Failed to clear session' },
        { status: response.status }
      )
    }

    return NextResponse.json({ success: true })

  } catch (error) {
    console.error('[API] Clear session error:', error)
    
    return NextResponse.json(
      { error: 'Internal server error', message: error.message },
      { status: 500 }
    )
  }
}
