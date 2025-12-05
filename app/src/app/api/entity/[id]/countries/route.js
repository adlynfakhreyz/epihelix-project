import { NextResponse } from 'next/server'

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000/api'

/**
 * GET /api/entity/[id]/countries
 * Get list of countries that have data for this entity (disease/outbreak/vaccination)
 */
export async function GET(request, { params }) {
  try {
    const { id } = await params
    const { searchParams } = new URL(request.url)
    const dataType = searchParams.get('dataType') || 'outbreaks'

    // Call real backend API
    const response = await fetch(`${FASTAPI_URL}/entity/${id}/countries?dataType=${dataType}`)
    
    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Countries API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch countries', details: error.message },
      { status: 500 }
    )
  }
}
