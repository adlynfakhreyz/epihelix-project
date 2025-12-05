import { NextResponse } from 'next/server'

/**
 * Next.js API Route - Search Middleware
 * 
 * Proxies search requests to FastAPI backend with:
 * - Request validation
 * - Error handling
 * - Response transformation
 * - Logging (development)
 */

const FASTAPI_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url)
    const q = searchParams.get('q')
    const page = searchParams.get('page') || '1'
    const page_size = searchParams.get('page_size') || '10'
    const semantic = searchParams.get('semantic') || 'false'
    const rerank = searchParams.get('rerank') || 'true'
    const summarize = searchParams.get('summarize') || 'true'

    // Validation
    if (!q || q.trim().length === 0) {
      return NextResponse.json(
        { error: 'Query parameter "q" is required' },
        { status: 400 }
      )
    }

    // Build backend URL
    const backendUrl = new URL(`${FASTAPI_URL}/search`)
    backendUrl.searchParams.set('q', q)
    backendUrl.searchParams.set('page', page)
    backendUrl.searchParams.set('page_size', page_size)
    if (semantic === 'true') {
      backendUrl.searchParams.set('semantic', 'true')
    }
    if (rerank === 'true') {
      backendUrl.searchParams.set('rerank', 'true')
    }
    if (summarize === 'true') {
      backendUrl.searchParams.set('summarize', 'true')
    }

    // Log in development
    if (process.env.NODE_ENV === 'development') {
      console.log('[API] Search:', { q, page, page_size, semantic, rerank, summarize })
    }

    // Call FastAPI backend
    const response = await fetch(backendUrl.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('[API] Backend error:', response.status, errorData)
      
      return NextResponse.json(
        { 
          error: errorData.detail || 'Search failed',
          status: response.status 
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    // Log success in development
    if (process.env.NODE_ENV === 'development') {
      console.log('[API] Search results:', data.length, 'items')
    }

    return NextResponse.json(data)

  } catch (error) {
    console.error('[API] Search error:', error)
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: error.message 
      },
      { status: 500 }
    )
  }
}
