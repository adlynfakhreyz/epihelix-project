# SPARQL Queries Documentation

This document contains all SPARQL queries used for external data enrichment in the EpiHelix Knowledge Graph project. This is required for the final project report (Section 6: External Data Integration).

---

## Table of Contents

1. [Wikidata Queries](#wikidata-queries)
   - [Country Enrichment](#country-enrichment)
   - [Disease Enrichment](#disease-enrichment)
   - [Health Organizations](#health-organizations)
   - [Vaccines](#vaccines)
2. [DBpedia Queries](#dbpedia-queries)
   - [Disease Information](#disease-information-dbpedia)
   - [Country Demographics](#country-demographics)
   - [Historical Pandemics](#historical-pandemics)

---

## Wikidata Queries

Wikidata endpoint: `https://query.wikidata.org/sparql`

### Country Enrichment

**Purpose**: Fetch comprehensive country data including population, GDP, capital, coordinates, life expectancy, and official language.

**Wikidata Properties Used**:
- `wdt:P297` - ISO 3166-1 alpha-2 code
- `wdt:P1082` - Population
- `wdt:P36` - Capital city
- `wdt:P30` - Continent
- `wdt:P625` - Coordinates
- `wdt:P298` - ISO 3166-1 alpha-3 code
- `wdt:P2131` - Nominal GDP
- `wdt:P2250` - Life expectancy
- `wdt:P2046` - Area in km²
- `wdt:P37` - Official language

**SPARQL Query**:

```sparql
SELECT ?country ?countryLabel ?population ?capital ?capitalLabel
       ?continent ?continentLabel ?coords ?iso3
       ?gdp ?lifeExpectancy ?area ?officialLanguage ?officialLanguageLabel
WHERE {
  ?country wdt:P297 "US" .  # ISO 3166-1 alpha-2 code (example: US)

  OPTIONAL { ?country wdt:P1082 ?population . }
  OPTIONAL { ?country wdt:P36 ?capital . }
  OPTIONAL { ?country wdt:P30 ?continent . }
  OPTIONAL { ?country wdt:P625 ?coords . }
  OPTIONAL { ?country wdt:P298 ?iso3 . }  # ISO 3166-1 alpha-3
  OPTIONAL { ?country wdt:P2131 ?gdp . }  # Nominal GDP
  OPTIONAL { ?country wdt:P2250 ?lifeExpectancy . }
  OPTIONAL { ?country wdt:P2046 ?area . }  # Area in km²
  OPTIONAL { ?country wdt:P37 ?officialLanguage . }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
LIMIT 1
```

**Example Result Integration**:
- Internal entity: `Country {code: "US"}`
- External data added: population, capital, continent, coordinates, GDP, life expectancy, area, language
- Relationship created: None (properties added to existing node)

---

### Disease Enrichment

**Purpose**: Enrich disease nodes with medical classifications, symptoms, transmission methods, risk factors, and treatments.

**Wikidata Properties Used**:
- `wdt:P493` - ICD-10 classification code
- `wdt:P486` - Medical Subject Headings (MeSH) ID
- `wdt:P780` - Symptoms
- `wdt:P1060` - Transmission method
- `wdt:P5642` - Risk factors
- `wdt:P2176` - Drug/treatment used
- `wdt:P3488` - Incubation period

**SPARQL Query** (Example: Cholera - Q12090):

```sparql
SELECT ?disease ?diseaseLabel ?description
       ?icd10 ?mesh ?symptoms ?symptomLabel
       ?transmission ?transmissionLabel
       ?riskFactor ?riskFactorLabel
       ?treatment ?treatmentLabel
       ?incubationPeriod
WHERE {
  BIND(wd:Q12090 AS ?disease)  # Cholera

  # Basic info
  OPTIONAL {
    ?disease schema:description ?description .
    FILTER(LANG(?description) = "en")
  }

  # Medical classifications
  OPTIONAL { ?disease wdt:P493 ?icd10 . }  # ICD-10 code
  OPTIONAL { ?disease wdt:P486 ?mesh . }   # Medical Subject Headings

  # Clinical information
  OPTIONAL { ?disease wdt:P780 ?symptoms . }  # Symptoms
  OPTIONAL { ?disease wdt:P1060 ?transmission . }  # Transmission method
  OPTIONAL { ?disease wdt:P5642 ?riskFactor . }  # Risk factors
  OPTIONAL { ?disease wdt:P2176 ?treatment . }  # Drug/treatment
  OPTIONAL { ?disease wdt:P3488 ?incubationPeriod . }  # Incubation period

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
LIMIT 50
```

**Disease-to-Wikidata ID Mappings**:

| Internal Disease ID | Wikidata ID | Disease Name |
|---------------------|-------------|--------------|
| cholera | Q12090 | Cholera |
| tuberculosis | Q12204 | Tuberculosis |
| malaria | Q12156 | Malaria |
| hiv_aids | Q12199 | HIV/AIDS |
| polio | Q12195 | Poliomyelitis |
| rabies | Q39552 | Rabies |
| smallpox | Q12214 | Smallpox |
| yaws | Q1415196 | Yaws |
| guinea_worm | Q913399 | Guinea worm disease |

**Example Result Integration**:
- Internal entity: `Disease {id: "cholera"}`
- External data added: ICD-10 code, MeSH ID, symptoms list, transmission methods, risk factors, treatments
- Relationships: None (properties added to existing node)

---

### COVID-19 Specific Enrichment

**Purpose**: Fetch detailed COVID-19 information for bonus features (RAG chatbot, semantic search).

**Wikidata Entity**: Q84263196 (COVID-19)

**SPARQL Query**:

```sparql
SELECT ?disease ?diseaseLabel ?icd10 ?mesh ?symptoms ?symptomLabel
       ?incubationPeriod ?description
WHERE {
  BIND(wd:Q84263196 AS ?disease)  # COVID-19

  OPTIONAL { ?disease wdt:P493 ?icd10 . }  # ICD-10 code
  OPTIONAL { ?disease wdt:P486 ?mesh . }   # Medical Subject Headings
  OPTIONAL { ?disease wdt:P780 ?symptoms . }  # Symptoms
  OPTIONAL { ?disease wdt:P3488 ?incubationPeriod . }  # Incubation period
  OPTIONAL {
    ?disease schema:description ?description .
    FILTER(LANG(?description) = "en")
  }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
LIMIT 10
```

---

### Health Organizations

**Purpose**: Add major health organizations monitoring pandemics.

**Organizations Queried**:
- WHO (World Health Organization) - Q7817
- CDC (Centers for Disease Control) - Q583725
- ECDC (European Centre for Disease Prevention and Control) - Q902384

**Wikidata Properties Used**:
- `wdt:P571` - Inception/founding date
- `wdt:P159` - Headquarters location
- `wdt:P856` - Official website

**SPARQL Query** (Example: WHO):

```sparql
SELECT ?org ?orgLabel ?founded ?headquarters ?hqLabel ?website
WHERE {
  BIND(wd:Q7817 AS ?org)  # WHO

  OPTIONAL { ?org wdt:P571 ?founded . }  # Inception
  OPTIONAL { ?org wdt:P159 ?headquarters . }  # Headquarters location
  OPTIONAL { ?org wdt:P856 ?website . }  # Official website

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
```

**Example Result Integration**:
- Creates: `Organization {id: "who", name: "World Health Organization"}`
- External data: founding date, headquarters, website
- Relationship created: `(Organization)-[:MONITORS]->(Disease {id: "covid19"})`

---

### Vaccines

**Purpose**: Add COVID-19 vaccines to the knowledge graph.

**Vaccines Queried**:
- Pfizer-BioNTech - Q98158256
- Moderna - Q98109286
- Oxford-AstraZeneca - Q98244340
- Johnson & Johnson - Q98843566
- Sinovac CoronaVac - Q98246648

**Wikidata Properties Used**:
- `wdt:P176` - Manufacturer
- `wdt:P571` - Inception/approval date

**SPARQL Query** (Example: Pfizer-BioNTech):

```sparql
SELECT ?vaccine ?vaccineLabel ?manufacturer ?manufacturerLabel
       ?approvalDate ?efficacy ?description
WHERE {
  BIND(wd:Q98158256 AS ?vaccine)  # Pfizer-BioNTech COVID-19 vaccine

  OPTIONAL { ?vaccine wdt:P176 ?manufacturer . }  # Manufacturer
  OPTIONAL { ?vaccine wdt:P571 ?approvalDate . }  # Inception/approval
  OPTIONAL {
    ?vaccine schema:description ?description .
    FILTER(LANG(?description) = "en")
  }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
```

**Example Result Integration**:
- Creates: `Vaccine {wikidataId: "Q98158256", name: "Pfizer-BioNTech COVID-19 vaccine"}`
- External data: manufacturer, approval date, description
- Relationship created: `(Vaccine)-[:PREVENTS]->(Disease {id: "covid19"})`

---

## DBpedia Queries

DBpedia endpoint: `https://dbpedia.org/sparql`

### Disease Information (DBpedia)

**Purpose**: Fetch Wikipedia abstracts, images, and additional context for diseases.

**DBpedia Properties Used**:
- `dbo:abstract` - Wikipedia article summary
- `foaf:isPrimaryTopicOf` - Wikipedia article URL
- `dbo:thumbnail` - Thumbnail image
- `dbp:causes` - Causative agent
- `dbo:medicalSpecialty` - Medical specialty
- `dbp:prevention` - Prevention methods

**SPARQL Query** (Example: Cholera):

```sparql
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?disease ?abstract ?wikipedia ?thumbnail
       ?causativeAgent ?specialty ?prevention
WHERE {
  # Find disease by name
  ?disease a dbo:Disease ;
           rdfs:label "Cholera"@en .

  # Get abstract (description)
  OPTIONAL { ?disease dbo:abstract ?abstract .
              FILTER(LANG(?abstract) = "en") }

  # Get Wikipedia URL
  OPTIONAL { ?disease foaf:isPrimaryTopicOf ?wikipedia . }

  # Get thumbnail image
  OPTIONAL { ?disease dbo:thumbnail ?thumbnail . }

  # Get medical information
  OPTIONAL { ?disease dbp:causes ?causativeAgent . }
  OPTIONAL { ?disease dbo:medicalSpecialty ?specialty . }
  OPTIONAL { ?disease dbp:prevention ?prevention . }
}
LIMIT 5
```

**Example Result Integration**:
- Internal entity: `Disease {id: "cholera"}`
- External data added: Wikipedia abstract, Wikipedia URL, thumbnail image, causative agent, medical specialty, prevention
- Relationship: None (properties added to existing node)

---

### Country Demographics

**Purpose**: Fetch demographic and geographic data from DBpedia.

**DBpedia Properties Used**:
- `dbo:iso31661Code` - ISO country code
- `dbo:abstract` - Country description
- `dbo:thumbnail` - Country thumbnail
- `dbo:populationDensity` - Population density
- `dbo:governmentType` - Government type
- `dbo:currency` - Currency
- `dbp:timeZone` - Time zone

**SPARQL Query**:

```sparql
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>

SELECT DISTINCT ?country ?abstract ?thumbnail ?populationDensity
       ?governmentType ?currency ?timeZone
WHERE {
  ?country a dbo:Country ;
           dbo:iso31661Code "US" .  # Example: US

  OPTIONAL { ?country dbo:abstract ?abstract .
              FILTER(LANG(?abstract) = "en") }
  OPTIONAL { ?country dbo:thumbnail ?thumbnail . }
  OPTIONAL { ?country dbo:populationDensity ?populationDensity . }
  OPTIONAL { ?country dbo:governmentType ?governmentType . }
  OPTIONAL { ?country dbo:currency ?currency . }
  OPTIONAL { ?country dbp:timeZone ?timeZone . }
}
LIMIT 1
```

---

### Historical Pandemics

**Purpose**: Discover and add historical pandemic events from DBpedia.

**DBpedia Classes Used**:
- `dbo:Disease` with category `Category:Pandemics`
- `dbo:Event` with category `Category:Disease_outbreaks`

**SPARQL Query**:

```sparql
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dct: <http://purl.org/dc/terms/>

SELECT DISTINCT ?event ?eventLabel ?abstract ?startDate ?endDate
       ?deathToll ?location ?locationLabel
WHERE {
  # Find pandemic events
  {
    ?event a dbo:Disease .
    ?event dct:subject <http://dbpedia.org/resource/Category:Pandemics> .
  } UNION {
    ?event a dbo:Event .
    ?event dct:subject <http://dbpedia.org/resource/Category:Disease_outbreaks> .
  }

  ?event rdfs:label ?eventLabel .
  FILTER(LANG(?eventLabel) = "en")

  OPTIONAL { ?event dbo:abstract ?abstract .
             FILTER(LANG(?abstract) = "en") }
  OPTIONAL { ?event dbp:date ?startDate . }
  OPTIONAL { ?event dbo:casualties ?deathToll . }
  OPTIONAL { ?event dbo:location ?location .
             ?location rdfs:label ?locationLabel .
             FILTER(LANG(?locationLabel) = "en") }
}
LIMIT 20
```

**Example Result Integration**:
- Creates: `PandemicEvent {name: "Spanish flu", dbpediaUri: "http://dbpedia.org/resource/Spanish_flu"}`
- External data: abstract, start date, death toll, location
- Potential relationships: `(PandemicEvent)-[:RELATED_TO]->(Disease)`, `(PandemicEvent)-[:OCCURRED_IN]->(Country)`

---

## Data Integration Summary

### Entity Linking Strategy

1. **Countries**: Linked via ISO 3166-1 alpha-2 codes (e.g., "US", "GB")
2. **Diseases**: Linked via Wikidata IDs and disease names
3. **Organizations**: Created as new nodes with Wikidata IDs
4. **Vaccines**: Created as new nodes with Wikidata IDs
5. **Historical Events**: Created as new nodes from DBpedia URIs

### Relationships Created

| Source | Relationship | Target |
|--------|--------------|--------|
| Organization | MONITORS | Disease |
| Vaccine | PREVENTS | Disease |
| PandemicEvent | RELATED_TO | Disease |
| PandemicEvent | OCCURRED_IN | Country |

### External Sources Used

1. **Wikidata** (`query.wikidata.org/sparql`):
   - Primary source for structured entity data
   - Medical classifications (ICD-10, MeSH)
   - Disease symptoms and treatments
   - Country demographics

2. **DBpedia** (`dbpedia.org/sparql`):
   - Wikipedia abstracts and images
   - Historical pandemic events
   - Additional country context

3. **BIO2RDF** (planned for future integration):
   - Biomedical ontologies
   - Drug-disease interactions
   - Protein and gene information

---

## Query Performance Notes

- **Rate Limiting**: 1-second delay between queries to respect endpoint limits
- **Retry Logic**: 3 attempts with exponential backoff (2^attempt seconds)
- **Batch Processing**: Not available for SPARQL; queries run sequentially
- **Typical Query Time**: 200-500ms per query to Wikidata/DBpedia

---

## References

- Wikidata Query Service: https://query.wikidata.org/
- Wikidata Property List: https://www.wikidata.org/wiki/Wikidata:List_of_properties
- DBpedia Ontology: https://dbpedia.org/ontology/
- SPARQL 1.1 Specification: https://www.w3.org/TR/sparql11-query/

---

**Last Updated**: 2025-11-26
**Project**: EpiHelix Knowledge Graph (Gasal 2025/2026)
**Dataset**: HPD (Historical Pandemic to Deaths Relations)
