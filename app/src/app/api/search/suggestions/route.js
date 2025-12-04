import { NextResponse } from 'next/server'

/**
 * Next.js API Route - Search Suggestions Middleware
 * 
 * Proxies suggestion requests to FastAPI backend
 */

const FASTAPI_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url)
    const q = searchParams.get('q')
    const limit = searchParams.get('limit') || '5'

    if (!q || q.trim().length === 0) {
      return NextResponse.json(
        { error: 'Query parameter "q" is required' },
        { status: 400 }
      )
    }

    const backendUrl = new URL(`${FASTAPI_URL}/search/suggestions`)
    backendUrl.searchParams.set('q', q)
    backendUrl.searchParams.set('limit', limit)

    const response = await fetch(backendUrl.toString(), {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      return NextResponse.json(
        { error: errorData.detail || 'Suggestions failed' },
        { status: response.status }
      )
    }

    const data = await response.json()
    return NextResponse.json(data)

  } catch (error) {
    console.error('[API] Suggestions error:', error)
    return NextResponse.json(
      { error: 'Internal server error', message: error.message },
      { status: 500 }
    )
  }
}
