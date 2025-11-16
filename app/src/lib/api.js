/**
 * API Client for EpiHelix
 * Provides mock endpoints that will be replaced with real FastAPI calls
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

/**
 * Search for entities (diseases, locations, outbreaks, etc.)
 * @param {string} q - Search query
 * @param {Object} options - Search options
 * @param {number} options.limit - Max results
 * @param {boolean} options.semantic - Use semantic search
 * @returns {Promise<Array>} Search results
 */
export async function search(q, { limit = 10, semantic = false } = {}) {
  // Mock data for now
  return Promise.resolve([
    {
      id: 'disease:influenza_A',
      label: 'Influenza A',
      type: 'Disease',
      score: 0.92,
      snippet: 'Influenza A virus subtype often associated with seasonal epidemics and pandemics',
      source: 'wikidata:Q2840',
    },
    {
      id: 'outbreak:1918_spanish_flu',
      label: '1918 Spanish Flu Pandemic',
      type: 'Outbreak',
      score: 0.88,
      snippet: 'Global pandemic caused by H1N1 influenza A virus, estimated 50 million deaths',
      source: 'internal:HPD_csv',
    },
    {
      id: 'location:wuhan_china',
      label: 'Wuhan, China',
      type: 'Location',
      score: 0.75,
      snippet: 'City in Hubei Province, initial outbreak location of COVID-19',
      source: 'wikidata:Q11746',
    },
  ].slice(0, limit))

  // Real implementation (uncomment when backend is ready):
  // const params = new URLSearchParams({ q, limit: limit.toString(), semantic: semantic.toString() })
  // const response = await fetch(`${API_BASE_URL}/search?${params}`)
  // return response.json()
}

/**
 * Get entity details by ID
 * @param {string} id - Entity ID
 * @returns {Promise<Object>} Entity details
 */
export async function getEntity(id) {
  // Mock data
  return Promise.resolve({
    id,
    label: id === 'disease:influenza_A' ? 'Influenza A' : 'Sample Entity',
    type: 'Disease',
    properties: {
      icdCode: 'J09-J11',
      category: 'Respiratory Infection',
      transmission: 'Airborne',
    },
    relations: [
      { pred: 'causedBy', obj: { id: 'virus:H1N1', label: 'H1N1 Virus' } },
      { pred: 'affects', obj: { id: 'location:global', label: 'Global' } },
    ],
    provenance: [
      { source: 'wikidata', uri: 'http://www.wikidata.org/entity/Q2840' },
      { source: 'internal:HPD_csv', query: 'row#45' },
    ],
  })

  // Real implementation:
  // const response = await fetch(`${API_BASE_URL}/entity/${id}`)
  // return response.json()
}

/**
 * Get graph neighborhood for an entity
 * @param {string} id - Entity ID
 * @param {number} depth - Graph depth
 * @param {number} limit - Max nodes
 * @returns {Promise<Object>} Graph data with nodes and edges
 */
export async function getEntityGraph(id, { depth = 1, limit = 50 } = {}) {
  // Mock graph data
  return Promise.resolve({
    nodes: [
      { id, label: 'Influenza A', type: 'Disease' },
      { id: 'virus:H1N1', label: 'H1N1 Virus', type: 'Virus' },
      { id: 'outbreak:1918', label: '1918 Pandemic', type: 'Outbreak' },
    ],
    edges: [
      { source: id, target: 'virus:H1N1', label: 'causedBy' },
      { source: 'outbreak:1918', target: id, label: 'diseaseOf' },
    ],
  })

  // Real implementation:
  // const params = new URLSearchParams({ depth: depth.toString(), limit: limit.toString() })
  // const response = await fetch(`${API_BASE_URL}/entity/${id}/graph?${params}`)
  // return response.json()
}

/**
 * Execute a SPARQL or Cypher query
 * @param {string} query - Query string
 * @param {string} type - Query type ('sparql' or 'cypher')
 * @returns {Promise<Object>} Query results
 */
export async function executeQuery(query, type = 'cypher') {
  // Mock response
  return Promise.resolve({
    columns: ['id', 'label', 'type'],
    rows: [
      ['disease:influenza_A', 'Influenza A', 'Disease'],
      ['disease:covid19', 'COVID-19', 'Disease'],
    ],
  })

  // Real implementation:
  // const response = await fetch(`${API_BASE_URL}/query`, {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ query, type }),
  // })
  // return response.json()
}

/**
 * Semantic search using embeddings
 * @param {string} query - Natural language query
 * @param {number} topK - Number of results
 * @returns {Promise<Array>} Ranked results
 */
export async function semanticSearch(query, topK = 10) {
  // Mock semantic results
  return Promise.resolve([
    {
      id: 'disease:covid19',
      label: 'COVID-19',
      score: 0.94,
      snippet: 'Coronavirus disease caused by SARS-CoV-2, global pandemic since 2020',
    },
  ])

  // Real implementation:
  // const response = await fetch(`${API_BASE_URL}/semantic/search`, {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ query, top_k: topK }),
  // })
  // return response.json()
}

/**
 * Generate LLM summary for an entity/fact
 * @param {string} entityId - Entity or fact ID
 * @param {string} query - Original search query
 * @param {string} type - Result type (entity, fact, subgraph)
 * @returns {Promise<Object>} Summary data
 */
export async function generateSummary(entityId, query, type = 'entity') {
  // Mock summary generation
  await new Promise((resolve) => setTimeout(resolve, 1000)) // Simulate delay

  const mockSummaries = {
    'disease:influenza_A': 'Influenza A is a highly contagious respiratory illness caused by influenza A viruses. It affects millions of people worldwide each year and can lead to severe complications, especially in vulnerable populations. The virus is known for its ability to mutate rapidly, which is why seasonal flu vaccines are updated annually. Major pandemics in history, including the 1918 Spanish Flu, were caused by influenza A virus strains.',
    'outbreak:1918_spanish_flu': 'The 1918 Spanish Flu pandemic was one of the deadliest natural disasters in human history, infecting approximately one-third of the global population and causing an estimated 50-100 million deaths worldwide. It was caused by an H1N1 influenza A virus and spread rapidly during the final year of World War I. Unlike typical flu strains, it disproportionately affected healthy young adults.',
    'location:wuhan_china': 'Wuhan is the capital of Hubei Province in central China and gained global attention in late 2019 as the initial outbreak location of COVID-19. The city is a major transportation hub and has a population of over 11 million people. The outbreak was first identified at the Huanan Seafood Wholesale Market, though the exact origins remain under investigation.',
  }

  return Promise.resolve({
    summary: mockSummaries[entityId] || 'Summary generated using LLM based on retrieved knowledge graph context including entity properties, relations, and immediate neighborhood.',
    contextUsed: {
      entityCount: 1,
      relationCount: 5,
      neighborCount: 10,
    },
    generatedAt: new Date().toISOString(),
  })

  // Real implementation:
  // const response = await fetch(`${API_BASE_URL}/summary/generate`, {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ entity_id: entityId, query, type }),
  // })
  // return response.json()
}

/**
 * Get knowledge panel data for an entity
 * @param {string} entityId - Entity ID
 * @returns {Promise<Object>} Knowledge panel data
 */
export async function getKnowledgePanel(entityId) {
  // Mock knowledge panel data
  const mockPanels = {
    'disease:influenza_A': {
      id: 'disease:influenza_A',
      label: 'Influenza A',
      type: 'Disease',
      description: 'Influenza A virus is a respiratory pathogen that causes seasonal flu epidemics and occasional pandemics.',
      image: null,
      properties: {
        family: 'Orthomyxoviridae',
        genome: 'Negative-sense single-stranded RNA',
        transmission: 'Airborne droplets, direct contact',
        incubation: '1-4 days',
        symptoms: 'Fever, cough, sore throat, body aches',
      },
      relations: [
        { pred: 'causedBy', obj: { id: 'virus:h1n1', label: 'H1N1 subtype' } },
        { pred: 'affects', obj: { id: 'species:human', label: 'Humans' } },
        { pred: 'relatedTo', obj: { id: 'outbreak:1918_spanish_flu', label: '1918 Spanish Flu' } },
      ],
      source: 'https://www.wikidata.org/wiki/Q2840',
    },
    'outbreak:1918_spanish_flu': {
      id: 'outbreak:1918_spanish_flu',
      label: '1918 Spanish Flu Pandemic',
      type: 'Outbreak',
      description: 'Global influenza pandemic that lasted from 1918 to 1919, caused by an H1N1 virus.',
      image: null,
      properties: {
        location: 'Worldwide',
        date: '1918-1919',
        cases: 500000000,
        deaths: 50000000,
        mortality: '10-20%',
        pathogen: 'Influenza A (H1N1)',
      },
      relations: [
        { pred: 'causedBy', obj: { id: 'disease:influenza_A', label: 'Influenza A' } },
        { pred: 'occurredIn', obj: { id: 'time:1918', label: '1918' } },
      ],
      source: 'https://en.wikipedia.org/wiki/Spanish_flu',
    },
  }

  return Promise.resolve(mockPanels[entityId] || {
    id: entityId,
    label: 'Unknown Entity',
    type: 'Entity',
    description: 'No knowledge panel data available',
    properties: {},
    relations: [],
  })

  // Real implementation:
  // const response = await fetch(`${API_BASE_URL}/knowledge-panel/${entityId}`)
  // return response.json()
}
