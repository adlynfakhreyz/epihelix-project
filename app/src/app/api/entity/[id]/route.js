import { NextResponse } from 'next/server'

/**
 * Next.js API Route - Entity Details Middleware
 * 
 * Proxies entity detail requests to FastAPI backend
 */

const FASTAPI_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export async function GET(request, { params }) {
  try {
    const { id } = params
    const { searchParams } = new URL(request.url)
    const includeRelated = searchParams.get('include_related') === 'true'

    if (!id) {
      return NextResponse.json(
        { error: 'Entity ID is required' },
        { status: 400 }
      )
    }

    // Build backend URL
    const backendUrl = new URL(`${FASTAPI_URL}/entity/${id}`)
    if (includeRelated) {
      backendUrl.searchParams.set('include_related', 'true')
    }

    if (process.env.NODE_ENV === 'development') {
      console.log('[API] Get entity:', id, { includeRelated })
    }

    // Call FastAPI backend
    const response = await fetch(backendUrl.toString(), {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('[API] Backend error:', response.status, errorData)
      
      return NextResponse.json(
        { 
          error: errorData.detail || 'Failed to fetch entity',
          status: response.status 
        },
        { status: response.status }
      )
    }

    const data = await response.json()
    
    if (process.env.NODE_ENV === 'development') {
      console.log('[API] Entity fetched:', data.id)
    }

    return NextResponse.json(data)

  } catch (error) {
    console.error('[API] Entity error:', error)
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: error.message 
      },
      { status: 500 }
    )
  }
}
