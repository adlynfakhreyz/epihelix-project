"""
Real Cypher Query Examples
Based on actual Neo4j schema from kg-construction/
"""

# ============================================================================
# EXAMPLE CYPHER QUERIES (for Query Console)
# ============================================================================

CYPHER_EXAMPLES = [
    {
        "name": "All Diseases",
        "description": "Get list of all diseases in the knowledge graph",
        "category": "Basic",
        "query": """
MATCH (d:Disease)
RETURN d.id, d.name, d.eradicated, d.dataSource, d.wikidataId
ORDER BY d.name
        """.strip()
    },
    {
        "name": "COVID-19 Excess Deaths by Country",
        "description": "Top 20 countries by COVID-19 excess deaths",
        "category": "COVID-19",
        "query": """
MATCH (o:Outbreak)-[:OCCURRED_IN]->(c:Country)
MATCH (o)-[:CAUSED_BY]->(d:Disease {id: 'covid19'})
WHERE o.excessDeaths IS NOT NULL
WITH c, SUM(o.excessDeaths) as totalDeaths
RETURN c.name, c.code, totalDeaths
ORDER BY totalDeaths DESC
LIMIT 20
        """.strip()
    },
    {
        "name": "Malaria Cases Over Time",
        "description": "Track malaria cases from 1980 to present",
        "category": "Disease Trends",
        "query": """
MATCH (o:Outbreak)-[:CAUSED_BY]->(d:Disease {id: 'malaria'})
WHERE o.year >= 1980 AND o.cases IS NOT NULL
RETURN o.year, SUM(o.cases) as totalCases
ORDER BY o.year
        """.strip()
    },
    {
        "name": "Cholera Deaths by Country",
        "description": "Countries with highest cholera death tolls",
        "category": "Cholera",
        "query": """
MATCH (o:Outbreak)-[:OCCURRED_IN]->(c:Country)
MATCH (o)-[:CAUSED_BY]->(d:Disease {id: 'cholera'})
WHERE o.deaths IS NOT NULL
RETURN c.name, SUM(o.deaths) as totalDeaths
ORDER BY totalDeaths DESC
LIMIT 10
        """.strip()
    },
    {
        "name": "Geographic Disease Distribution",
        "description": "Countries with coordinates and disease outbreaks (for map visualization)",
        "category": "Geography",
        "query": """
MATCH (c:Country)
WHERE c.latitude IS NOT NULL AND c.longitude IS NOT NULL
OPTIONAL MATCH (o:Outbreak)-[:OCCURRED_IN]->(c)
WHERE o.year = 2021
WITH c, COUNT(DISTINCT o) as outbreakCount
RETURN c.name, c.code, c.latitude, c.longitude, c.population, outbreakCount
ORDER BY outbreakCount DESC
        """.strip()
    },
    {
        "name": "Disease Clinical Information",
        "description": "Get symptoms, treatments, and transmission methods for a disease",
        "category": "Clinical Data",
        "query": """
MATCH (d:Disease {id: 'cholera'})
RETURN d.name, d.symptoms, d.treatments, d.transmissionMethods,
       d.wikipediaAbstract, d.thumbnailUrl, d.icd10
        """.strip()
    },
    {
        "name": "Vaccination Coverage by Country",
        "description": "Latest measles vaccination coverage",
        "category": "Vaccination",
        "query": """
MATCH (v:VaccinationRecord)-[:IN_COUNTRY]->(c:Country)
WHERE v.vaccineName = 'Measles' AND v.year = 2020
RETURN c.name, v.coverage, v.totalVaccinated
ORDER BY v.coverage DESC
LIMIT 20
        """.strip()
    },
    {
        "name": "Health Organizations",
        "description": "Get all health organizations and monitored diseases",
        "category": "Organizations",
        "query": """
MATCH (org:Organization)
OPTIONAL MATCH (org)-[:MONITORS]->(d:Disease)
RETURN org.name, org.acronym, org.headquarters, org.website,
       collect(d.name) as monitoredDiseases
        """.strip()
    },
    {
        "name": "COVID-19 Vaccines",
        "description": "List of COVID-19 vaccines with manufacturers",
        "category": "COVID-19",
        "query": """
MATCH (v:Vaccine)-[:PREVENTS]->(d:Disease {id: 'covid19'})
RETURN v.name, v.manufacturer, v.approvalDate
ORDER BY v.approvalDate
        """.strip()
    },
    {
        "name": "Eradicated Diseases",
        "description": "Diseases that have been eradicated (e.g., Smallpox)",
        "category": "Basic",
        "query": """
MATCH (d:Disease)
WHERE d.eradicated = true
RETURN d.id, d.name, d.description
        """.strip()
    },
    {
        "name": "Country Demographics",
        "description": "Enriched country data with population, GDP, life expectancy",
        "category": "Geography",
        "query": """
MATCH (c:Country)
WHERE c.enriched = true
RETURN c.name, c.population, c.gdp, c.lifeExpectancy, 
       c.continent, c.capital
ORDER BY c.population DESC
LIMIT 20
        """.strip()
    },
    {
        "name": "Disease Outbreak Network",
        "description": "Graph visualization: outbreaks connecting countries and diseases",
        "category": "Graph Visualization",
        "query": """
MATCH (o:Outbreak)-[:OCCURRED_IN]->(c:Country)
MATCH (o)-[:CAUSED_BY]->(d:Disease)
WHERE c.code IN ['USA', 'CHN', 'IND', 'BRA', 'GBR']
  AND o.year >= 2020
RETURN o, c, d
LIMIT 100
        """.strip()
    },
    {
        "name": "Tuberculosis Global Cases",
        "description": "Total tuberculosis cases by year globally",
        "category": "Disease Trends",
        "query": """
MATCH (o:Outbreak)-[:CAUSED_BY]->(d:Disease {id: 'tuberculosis'})
WHERE o.cases IS NOT NULL
RETURN o.year, SUM(o.cases) as totalCases
ORDER BY o.year DESC
LIMIT 30
        """.strip()
    },
    {
        "name": "Continental Disease Analysis",
        "description": "Disease distribution by continent",
        "category": "Geography",
        "query": """
MATCH (o:Outbreak)-[:OCCURRED_IN]->(c:Country)
MATCH (o)-[:CAUSED_BY]->(d:Disease)
WHERE c.continent IS NOT NULL AND o.year >= 2015
RETURN c.continent, d.name, COUNT(o) as outbreakCount,
       SUM(o.cases) as totalCases
ORDER BY c.continent, totalCases DESC
        """.strip()
    },
    {
        "name": "Countries Bordering High-Risk Areas",
        "description": "Find countries sharing borders (if enriched)",
        "category": "Geography",
        "query": """
MATCH (c1:Country)-[:BORDERS]-(c2:Country)
RETURN c1.name, collect(c2.name) as borderingCountries
LIMIT 20
        """.strip()
    },
    {
        "name": "Historical Pandemic Events",
        "description": "Get historical pandemics from DBpedia",
        "category": "Historical",
        "query": """
MATCH (pe:PandemicEvent)
OPTIONAL MATCH (pe)-[:RELATED_TO]->(d:Disease)
RETURN pe.name, pe.abstract, pe.startDate, pe.deathToll,
       pe.location, d.name as relatedDisease
ORDER BY pe.startDate
        """.strip()
    }
]


def get_example_queries(category=None):
    """
    Get example Cypher queries
    
    Args:
        category: Optional category filter
        
    Returns:
        List of query examples
    """
    if category:
        return [q for q in CYPHER_EXAMPLES if q["category"] == category]
    return CYPHER_EXAMPLES


def get_query_categories():
    """Get list of unique query categories"""
    return list(set(q["category"] for q in CYPHER_EXAMPLES))
