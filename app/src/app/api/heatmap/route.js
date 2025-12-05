/**
 * Heatmap API Route
 * 
 * Returns country-level outbreak data for world heatmap visualization
 * Query params:
 * - diseaseId: Disease element ID (required)
 * - year: Year to filter by (optional, defaults to latest year)
 */

import { NextResponse } from 'next/server'

const FASTAPI_URL = process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000'

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url)
    const diseaseId = searchParams.get('diseaseId')
    const year = searchParams.get('year')

    if (!diseaseId) {
      return NextResponse.json(
        { error: 'diseaseId parameter is required' },
        { status: 400 }
      )
    }

    // Build query params
    const params = new URLSearchParams({ diseaseId })
    if (year) params.append('year', year)

    const response = await fetch(
      `${FASTAPI_URL}/api/heatmap?${params.toString()}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Heatmap API error:', error)
    return NextResponse.json(
      { error: error.message || 'Failed to fetch heatmap data' },
      { status: 500 }
    )
  }
}
