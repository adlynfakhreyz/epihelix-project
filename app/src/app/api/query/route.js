import { NextResponse } from 'next/server'

/**
 * Next.js API Route - Query Console Middleware
 * 
 * Proxies Cypher/SPARQL query execution to FastAPI backend
 * For free-form query console feature
 */

const FASTAPI_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export async function POST(request) {
  try {
    const body = await request.json()
    const { query, type = 'cypher' } = body

    // Validation
    if (!query || query.trim().length === 0) {
      return NextResponse.json(
        { error: 'query is required' },
        { status: 400 }
      )
    }

    if (!['cypher', 'sparql'].includes(type)) {
      return NextResponse.json(
        { error: 'type must be "cypher" or "sparql"' },
        { status: 400 }
      )
    }

    if (process.env.NODE_ENV === 'development') {
      console.log('[API] Execute query:', { type, query: query.substring(0, 100) })
    }

    // Call FastAPI backend
    const response = await fetch(`${FASTAPI_URL}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, type }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('[API] Query execution error:', response.status, errorData)
      
      return NextResponse.json(
        { 
          error: errorData.detail || 'Query execution failed',
          status: response.status 
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    if (process.env.NODE_ENV === 'development') {
      console.log('[API] Query executed:', {
        rows: data.rows?.length || 0,
        columns: data.columns?.length || 0
      })
    }

    return NextResponse.json(data)

  } catch (error) {
    console.error('[API] Query error:', error)
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: error.message 
      },
      { status: 500 }
    )
  }
}
