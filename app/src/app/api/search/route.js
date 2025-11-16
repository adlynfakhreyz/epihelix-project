import { NextResponse } from 'next/server'

/**
 * Mock API endpoint for search
 * This will be replaced by FastAPI backend calls
 */
export async function GET(request) {
  const { searchParams } = new URL(request.url)
  const q = searchParams.get('q')
  const limit = parseInt(searchParams.get('limit') || '10')

  // Mock data
  const mockResults = [
    {
      id: 'disease:influenza_A',
      label: 'Influenza A',
      type: 'Disease',
      score: 0.92,
      snippet: 'Influenza A virus subtype often associated with seasonal epidemics',
      source: 'wikidata:Q2840',
    },
    {
      id: 'outbreak:1918_spanish_flu',
      label: '1918 Spanish Flu Pandemic',
      type: 'Outbreak',
      score: 0.88,
      snippet: 'Global pandemic caused by H1N1 influenza A virus',
      source: 'internal:HPD_csv',
    },
  ]

  return NextResponse.json(mockResults.slice(0, limit))
}
