import { NextResponse } from 'next/server'

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000/api'

/**
 * GET /api/entity/[id]/timeseries
 * Get time-series data for outbreaks or vaccinations
 *
 * Query params:
 * - dataType: 'outbreaks' or 'vaccinations'
 * - countries: comma-separated country codes or 'ALL'
 * - yearStart: start year filter
 * - yearEnd: end year filter
 * - aggregation: 'country' or 'total'
 */
export async function GET(request, { params }) {
  try {
    const { id } = await params
    const { searchParams } = new URL(request.url)

    const dataType = searchParams.get('dataType') || 'outbreaks'
    const countries = searchParams.get('countries') || 'ALL'
    const yearStart = searchParams.get('yearStart') || ''
    const yearEnd = searchParams.get('yearEnd') || ''
    const aggregation = searchParams.get('aggregation') || 'country'

    // Build query parameters for backend
    const queryParams = new URLSearchParams({
      dataType,
      countries,
      aggregation,
    })
    
    if (yearStart) queryParams.append('yearStart', yearStart)
    if (yearEnd) queryParams.append('yearEnd', yearEnd)

    // Call real backend API
    const response = await fetch(`${FASTAPI_URL}/entity/${id}/timeseries?${queryParams}`)
    
    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Timeseries API error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch timeseries data', details: error.message },
      { status: 500 }
    )
  }
}
