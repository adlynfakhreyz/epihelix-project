import { NextResponse } from 'next/server'

/**
 * Next.js API Route - Summary Generation Middleware
 * 
 * Proxies summary generation requests to FastAPI backend
 * Uses LLM service on backend for entity summarization
 */

const FASTAPI_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export async function POST(request) {
  try {
    const body = await request.json()
    const { entity_id, query, include_relations = true } = body

    // Validation
    if (!entity_id) {
      return NextResponse.json(
        { error: 'entity_id is required' },
        { status: 400 }
      )
    }

    if (process.env.NODE_ENV === 'development') {
      console.log('[API] Generate summary:', { entity_id, query })
    }

    // Call FastAPI backend (supports both entity_id and entity_ids)
    const response = await fetch(`${FASTAPI_URL}/summary/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        entity_id,  // Backend accepts single entity_id
        query,
        include_relations
      }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('[API] Summary generation error:', response.status, errorData)
      
      return NextResponse.json(
        { 
          error: errorData.detail || 'Summary generation failed',
          status: response.status 
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    if (process.env.NODE_ENV === 'development') {
      console.log('[API] Summary generated for:', entity_id)
    }

    return NextResponse.json(data)

  } catch (error) {
    console.error('[API] Summary error:', error)
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: error.message 
      },
      { status: 500 }
    )
  }
}
