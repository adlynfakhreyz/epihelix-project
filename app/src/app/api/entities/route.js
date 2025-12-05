import { NextResponse } from 'next/server'

/**
 * GET /api/entities
 * Get list of entities by type with search and filtering
 *
 * Query params:
 * - type: Entity type (country, disease, outbreak, vaccinationrecord, organization)
 * - search: Search query
 * - sortBy: Sort field (name, id)
 * - [property filters]: Dynamic property filters
 */

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000/api'

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url)
    const type = searchParams.get('type')
    const search = searchParams.get('search') || ''
    const sortBy = searchParams.get('sortBy') || 'name'

    // Validation
    if (!type) {
      return NextResponse.json(
        { error: 'Query parameter "type" is required' },
        { status: 400 }
      )
    }

    // Build backend URL with all query parameters
    const backendUrl = new URL(`${FASTAPI_URL}/entity/list`)
    backendUrl.searchParams.set('type', type)
    if (search) backendUrl.searchParams.set('search', search)
    if (sortBy) backendUrl.searchParams.set('sortBy', sortBy)

    // Forward all filter parameters
    for (const [key, value] of searchParams.entries()) {
      if (!['type', 'search', 'sortBy'].includes(key)) {
        backendUrl.searchParams.set(key, value)
      }
    }

    // Log in development
    if (process.env.NODE_ENV === 'development') {
      console.log('[API] Entities:', { type, search, sortBy })
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

      // If backend returns 404 or 500, fall back to mock data for development
      if (process.env.NODE_ENV === 'development') {
        console.warn('[API] Falling back to mock data')
        return getMockEntitiesResponse(type, search, sortBy, searchParams)
      }

      return NextResponse.json(
        {
          error: errorData.detail || 'Failed to fetch entities',
          status: response.status
        },
        { status: response.status }
      )
    }

    const data = await response.json()

    // Log success in development
    if (process.env.NODE_ENV === 'development') {
      console.log('[API] Entities results:', data.entities?.length || 0, 'items')
    }

    return NextResponse.json(data)

  } catch (error) {
    console.error('[API] Entities error:', error)

    // Fall back to mock data in development
    if (process.env.NODE_ENV === 'development') {
      console.warn('[API] Connection error, falling back to mock data')
      const { searchParams } = new URL(request.url)
      const type = searchParams.get('type')
      const search = searchParams.get('search') || ''
      const sortBy = searchParams.get('sortBy') || 'name'
      return getMockEntitiesResponse(type, search, sortBy, searchParams)
    }

    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error.message
      },
      { status: 500 }
    )
  }
}

// Fallback mock data function (used when backend is unavailable in development)
function getMockEntitiesResponse(type, search, sortBy, searchParams) {

    // Mock data generator
    const generateMockEntities = () => {
      const mockData = {
        country: [
          { code: 'USA', name: 'United States', continent: 'Americas', population: 331900000 },
          { code: 'GBR', name: 'United Kingdom', continent: 'Europe', population: 67220000 },
          { code: 'DEU', name: 'Germany', continent: 'Europe', population: 83240000 },
          { code: 'FRA', name: 'France', continent: 'Europe', population: 67390000 },
          { code: 'ITA', name: 'Italy', continent: 'Europe', population: 59550000 },
          { code: 'ESP', name: 'Spain', continent: 'Europe', population: 47350000 },
          { code: 'CAN', name: 'Canada', continent: 'Americas', population: 38250000 },
          { code: 'AUS', name: 'Australia', continent: 'Oceania', population: 25690000 },
          { code: 'JPN', name: 'Japan', continent: 'Asia', population: 125800000 },
          { code: 'CHN', name: 'China', continent: 'Asia', population: 1412000000 },
          { code: 'IND', name: 'India', continent: 'Asia', population: 1380000000 },
          { code: 'BRA', name: 'Brazil', continent: 'Americas', population: 212600000 },
          { code: 'MEX', name: 'Mexico', continent: 'Americas', population: 128900000 },
          { code: 'RUS', name: 'Russia', continent: 'Europe', population: 144100000 },
          { code: 'KOR', name: 'South Korea', continent: 'Asia', population: 51780000 },
          { code: 'IDN', name: 'Indonesia', continent: 'Asia', population: 273500000 },
          { code: 'TUR', name: 'Turkey', continent: 'Asia', population: 84340000 },
          { code: 'NLD', name: 'Netherlands', continent: 'Europe', population: 17440000 },
          { code: 'SAU', name: 'Saudi Arabia', continent: 'Asia', population: 34810000 },
          { code: 'CHE', name: 'Switzerland', continent: 'Europe', population: 8670000 },
          { code: 'ARG', name: 'Argentina', continent: 'Americas', population: 45380000 },
          { code: 'SWE', name: 'Sweden', continent: 'Europe', population: 10350000 },
          { code: 'POL', name: 'Poland', continent: 'Europe', population: 37970000 },
          { code: 'BEL', name: 'Belgium', continent: 'Europe', population: 11590000 },
          { code: 'NOR', name: 'Norway', continent: 'Europe', population: 5420000 },
          { code: 'AUT', name: 'Austria', continent: 'Europe', population: 8920000 },
          { code: 'ISR', name: 'Israel', continent: 'Asia', population: 9220000 },
          { code: 'ARE', name: 'United Arab Emirates', continent: 'Asia', population: 9890000 },
          { code: 'SGP', name: 'Singapore', continent: 'Asia', population: 5850000 },
          { code: 'DNK', name: 'Denmark', continent: 'Europe', population: 5830000 },
          { code: 'PHL', name: 'Philippines', continent: 'Asia', population: 109600000 },
          { code: 'MYS', name: 'Malaysia', continent: 'Asia', population: 32370000 },
          { code: 'ZAF', name: 'South Africa', continent: 'Africa', population: 59310000 },
          { code: 'EGY', name: 'Egypt', continent: 'Africa', population: 102300000 },
          { code: 'PAK', name: 'Pakistan', continent: 'Asia', population: 220900000 },
          { code: 'CHL', name: 'Chile', continent: 'Americas', population: 19120000 },
          { code: 'FIN', name: 'Finland', continent: 'Europe', population: 5540000 },
          { code: 'COL', name: 'Colombia', continent: 'Americas', population: 50880000 },
          { code: 'BGD', name: 'Bangladesh', continent: 'Asia', population: 164700000 },
          { code: 'VNM', name: 'Vietnam', continent: 'Asia', population: 97340000 },
          { code: 'CZE', name: 'Czech Republic', continent: 'Europe', population: 10700000 },
          { code: 'ROU', name: 'Romania', continent: 'Europe', population: 19240000 },
          { code: 'PRT', name: 'Portugal', continent: 'Europe', population: 10310000 },
          { code: 'NZL', name: 'New Zealand', continent: 'Oceania', population: 5080000 },
          { code: 'GRC', name: 'Greece', continent: 'Europe', population: 10720000 },
          { code: 'PER', name: 'Peru', continent: 'Americas', population: 32970000 },
          { code: 'QAT', name: 'Qatar', continent: 'Asia', population: 2880000 },
          { code: 'IRQ', name: 'Iraq', continent: 'Asia', population: 40220000 },
          { code: 'DZA', name: 'Algeria', continent: 'Africa', population: 43850000 },
          { code: 'KAZ', name: 'Kazakhstan', continent: 'Asia', population: 18750000 },
        ].map(country => ({
          id: country.code,
          label: country.name,
          type: 'Country',
          description: `${country.name} is a country in ${country.continent} with a population of ${(country.population / 1000000).toFixed(1)} million`,
          properties: {
            code: country.code,
            continent: country.continent,
            population: country.population,
            enriched: true,
          },
        })),
        disease: [
          { id: 'covid19', name: 'COVID-19', vaccinePreventable: true, eradicated: false },
          { id: 'measles', name: 'Measles', vaccinePreventable: true, eradicated: false },
          { id: 'tuberculosis', name: 'Tuberculosis', vaccinePreventable: true, eradicated: false },
          { id: 'cholera', name: 'Cholera', vaccinePreventable: true, eradicated: false },
          { id: 'malaria', name: 'Malaria', vaccinePreventable: false, eradicated: false },
          { id: 'hiv_aids', name: 'HIV/AIDS', vaccinePreventable: false, eradicated: false },
          { id: 'polio', name: 'Polio', vaccinePreventable: true, eradicated: false },
          { id: 'rabies', name: 'Rabies', vaccinePreventable: true, eradicated: false },
          { id: 'smallpox', name: 'Smallpox', vaccinePreventable: true, eradicated: true },
          { id: 'yaws', name: 'Yaws', vaccinePreventable: false, eradicated: false },
          { id: 'guinea_worm', name: 'Guinea Worm Disease', vaccinePreventable: false, eradicated: false },
          { id: 'diphtheria', name: 'Diphtheria', vaccinePreventable: true, eradicated: false },
          { id: 'pertussis', name: 'Pertussis', vaccinePreventable: true, eradicated: false },
          { id: 'tetanus', name: 'Tetanus', vaccinePreventable: true, eradicated: false },
          { id: 'hepatitis_b', name: 'Hepatitis B', vaccinePreventable: true, eradicated: false },
          { id: 'haemophilus_influenzae', name: 'Haemophilus Influenzae', vaccinePreventable: true, eradicated: false },
          { id: 'rotavirus', name: 'Rotavirus', vaccinePreventable: true, eradicated: false },
          { id: 'pneumonia', name: 'Pneumonia', vaccinePreventable: true, eradicated: false },
          { id: 'rubella', name: 'Rubella', vaccinePreventable: true, eradicated: false },
          { id: 'mumps', name: 'Mumps', vaccinePreventable: true, eradicated: false },
          { id: 'yellow_fever', name: 'Yellow Fever', vaccinePreventable: true, eradicated: false },
          { id: 'japanese_encephalitis', name: 'Japanese Encephalitis', vaccinePreventable: true, eradicated: false },
          { id: 'typhoid', name: 'Typhoid', vaccinePreventable: true, eradicated: false },
          { id: 'dengue', name: 'Dengue', vaccinePreventable: false, eradicated: false },
          { id: 'ebola', name: 'Ebola', vaccinePreventable: false, eradicated: false },
        ].map(disease => ({
          id: disease.id,
          label: disease.name,
          type: 'Disease',
          description: `${disease.name} is an infectious disease${disease.vaccinePreventable ? ' that can be prevented with vaccination' : ''}${disease.eradicated ? ' that has been eradicated' : ''}`,
          properties: {
            vaccinePreventable: disease.vaccinePreventable,
            eradicated: disease.eradicated,
            enriched: true,
          },
        })),
        outbreak: Array.from({ length: 100 }, (_, i) => {
          const diseases = ['covid19', 'cholera', 'measles', 'tuberculosis', 'malaria']
          const countryCodes = ['USA', 'GBR', 'DEU', 'IND', 'BRA', 'CHN']
          const countryNames = ['United States', 'United Kingdom', 'Germany', 'India', 'Brazil', 'China']
          const years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

          const disease = diseases[i % diseases.length]
          const countryCode = countryCodes[i % countryCodes.length]
          const countryName = countryNames[i % countryNames.length]
          const year = years[i % years.length]

          return {
            id: `${disease}_${countryCode}_${year}`,
            label: `${disease.toUpperCase()} outbreak in ${countryName} (${year})`,
            type: 'Outbreak',
            description: `Outbreak record for ${disease} in ${countryName} during ${year}`,
            properties: {
              year,
              cases: Math.floor(Math.random() * 10000) + 100,
              country: countryName,
              countryCode: countryCode,
              disease,
            },
          }
        }),
        vaccinationrecord: Array.from({ length: 80 }, (_, i) => {
          const diseases = ['measles', 'polio', 'diphtheria', 'pertussis', 'tetanus']
          const countryCodes = ['USA', 'GBR', 'DEU', 'FRA', 'IND', 'CHN', 'BRA', 'JPN']
          const countryNames = ['United States', 'United Kingdom', 'Germany', 'France', 'India', 'China', 'Brazil', 'Japan']
          const years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

          const disease = diseases[i % diseases.length]
          const countryCode = countryCodes[i % countryCodes.length]
          const countryName = countryNames[i % countryNames.length]
          const year = years[i % years.length]

          return {
            id: `vax_${disease}_${countryCode}_${year}`,
            label: `${disease.charAt(0).toUpperCase() + disease.slice(1)} vaccination in ${countryName} (${year})`,
            type: 'VaccinationRecord',
            description: `Vaccination coverage data for ${disease} in ${countryName} during ${year}`,
            properties: {
              year,
              coveragePercent: Math.floor(Math.random() * 40) + 60, // 60-100%
              country: countryName,
              countryCode: countryCode,
              disease,
            },
          }
        }),
        organization: [
          {
            id: 'who',
            label: 'World Health Organization',
            type: 'Organization',
            description: 'The United Nations agency that coordinates international public health',
            properties: {
              acronym: 'WHO',
              founded: 1948,
              headquarters: 'Geneva, Switzerland',
            },
          },
          {
            id: 'cdc',
            label: 'Centers for Disease Control and Prevention',
            type: 'Organization',
            description: 'The national public health agency of the United States',
            properties: {
              acronym: 'CDC',
              founded: 1946,
              headquarters: 'Atlanta, USA',
            },
          },
          {
            id: 'ecdc',
            label: 'European Centre for Disease Prevention and Control',
            type: 'Organization',
            description: 'EU agency aimed at strengthening Europe\'s defenses against infectious diseases',
            properties: {
              acronym: 'ECDC',
              founded: 2005,
              headquarters: 'Stockholm, Sweden',
            },
          },
        ],
      }

      return mockData[type] || []
    }

    let entities = generateMockEntities()

    // Generate available filters based on entity type
    const generateFilters = () => {
      const filtersByType = {
        country: [
          {
            key: 'continent',
            label: 'Continent',
            type: 'select',
            options: [
              { value: 'Asia', label: 'Asia' },
              { value: 'Europe', label: 'Europe' },
              { value: 'Americas', label: 'Americas' },
              { value: 'Africa', label: 'Africa' },
              { value: 'Oceania', label: 'Oceania' },
            ],
          },
          {
            key: 'enriched',
            label: 'Enriched',
            type: 'select',
            options: [
              { value: 'true', label: 'Yes' },
              { value: 'false', label: 'No' },
            ],
          },
        ],
        disease: [
          {
            key: 'vaccinePreventable',
            label: 'Vaccine Preventable',
            type: 'select',
            options: [
              { value: 'true', label: 'Yes' },
              { value: 'false', label: 'No' },
            ],
          },
          {
            key: 'eradicated',
            label: 'Eradicated',
            type: 'select',
            options: [
              { value: 'true', label: 'Yes' },
              { value: 'false', label: 'No' },
            ],
          },
          {
            key: 'enriched',
            label: 'Enriched',
            type: 'select',
            options: [
              { value: 'true', label: 'Yes' },
              { value: 'false', label: 'No' },
            ],
          },
        ],
        outbreak: [
          {
            key: 'year',
            label: 'Year',
            type: 'text',
          },
          {
            key: 'country',
            label: 'Country',
            type: 'text',
          },
          {
            key: 'disease',
            label: 'Disease',
            type: 'text',
          },
        ],
        vaccinationrecord: [
          {
            key: 'year',
            label: 'Year',
            type: 'text',
          },
          {
            key: 'country',
            label: 'Country',
            type: 'text',
          },
          {
            key: 'disease',
            label: 'Disease',
            type: 'text',
          },
        ],
        organization: [
          {
            key: 'headquarters',
            label: 'Headquarters',
            type: 'text',
          },
        ],
      }

      return filtersByType[type] || []
    }

    // Apply search filter
    if (search) {
      entities = entities.filter((entity) =>
        entity.label.toLowerCase().includes(search.toLowerCase()) ||
        entity.id.toLowerCase().includes(search.toLowerCase()) ||
        (entity.description && entity.description.toLowerCase().includes(search.toLowerCase()))
      )
    }

    // Sort entities
    entities.sort((a, b) => {
      if (sortBy === 'name') {
        return a.label.localeCompare(b.label)
      } else if (sortBy === 'id') {
        return a.id.localeCompare(b.id)
      }
      return 0
    })

    return NextResponse.json({
      entities,
      availableFilters: generateFilters(),
      total: entities.length,
      type,
    })
}
