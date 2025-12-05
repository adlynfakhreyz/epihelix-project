/**
 * Entity List API Route
 * 
 * Returns list of entities by type
 * Query params:
 * - type: Entity type (required)
 * - search: Search query (optional)
 * - sortBy: Sort field (optional)
 * - Other params: Property filters
 */

import { NextResponse } from 'next/server'

const FASTAPI_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000'

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url)
    
    // Forward all query params to backend
    const response = await fetch(
      `${FASTAPI_URL}/api/entity/list?${searchParams.toString()}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(`Backend returned ${response.status}: ${JSON.stringify(errorData)}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Entity list API error:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to fetch entities' },
      { status: 500 }
    )
  }
}
