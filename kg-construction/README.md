# EpiHelix Knowledge Graph Construction

This directory contains the ETL pipeline for building the EpiHelix pandemic knowledge graph using Neo4j.

## 📋 Prerequisites

- Docker and Docker Compose (for Neo4j)
- Python 3.8+
- Required CSV datasets in `data/raw/`

## 🚀 Quick Start

### 1. Start Neo4j Database

```bash
# Navigate to infrastructure directory
cd ../infrastructure

# Start Neo4j with Docker Compose
docker-compose up -d

# Check if Neo4j is running
docker-compose ps
```

**Neo4j will be available at:**
- Browser UI: http://localhost:7474
- Bolt connection: bolt://localhost:7687
- **Credentials**: `neo4j` / `epihelix123`

### 2. Set Up Python Environment

```bash
# Navigate to kg-construction directory
cd ../kg-construction

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Connection

```bash
# Copy .env template
cp .env.template .env

# .env should contain:
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=epihelix123
```

### 4. Load Data into Neo4j

**⚠️  REFACTORED WORKFLOW**: The ETL pipeline now separates data loading from enrichment for better code organization.

#### Step 4a: Load Raw CSV Data

```bash
# Navigate to ETL directory
cd etl

# Load all datasets (raw CSV data only, no external API calls)
python load_all_data.py

# Or load individual datasets:
python load_disease_cases.py      # Dataset 1: Infectious disease cases (9 diseases)
python load_vaccination_data.py   # Dataset 2: Vaccination coverage data
python load_covid_data.py         # Dataset 4: COVID-19 excess deaths
python load_cholera_data.py       # Dataset 5: Cholera deaths
```

**Optional: Clear database before loading**
```bash
python load_all_data.py --clear
```

#### Step 4b: Enrich with External Data

**Run AFTER loading raw data:**

```bash
# Optional: Test DBpedia connectivity first
python test_dbpedia_connection.py

# Enrich with Wikidata + DBpedia (takes ~10-15 minutes)
python enrich_all.py
```

This enrichment step:
- ✅ **Wikidata** (Required): Disease metadata, country demographics, health organizations
  - Symptoms, treatments, medical classifications
  - Population, GDP, coordinates, borders
  - WHO, CDC, ECDC organizations
- ⚠️ **DBpedia** (Optional): May fail if endpoint is down
  - Wikipedia abstracts and images
  - Historical pandemic events
  - Enrichment will continue successfully even if DBpedia fails

**⚠️ DBpedia Connectivity Issues:**
DBpedia's public SPARQL endpoint (`https://dbpedia.org/sparql`) is frequently down or unreachable. The enrichment script now handles this gracefully:
- ✅ **Wikidata enrichment is sufficient** for project requirements
- ✅ Script continues even if DBpedia fails
- ✅ 30-second timeout prevents long hangs
- ℹ️ Run `test_dbpedia_connection.py` to check availability

**Why this separation?**
- **Loading**: Fast, predictable, uses only local CSV files
- **Enrichment**: Slower (external APIs), optional, can be run separately
- **Benefits**: Better error handling, easier debugging, cleaner code

## 📊 Datasets

The ETL pipeline processes these CSV files from `data/raw/`:

### ✅ Dataset 1: Infectious Disease Cases (HPD)
**File**: `1- the-number-of-cases-of-infectious-diseases.csv`

**Diseases covered**:
- Yaws
- Polio
- Guinea Worm Disease
- Rabies
- Malaria
- HIV/AIDS
- Tuberculosis
- Smallpox (eradicated)
- Cholera

**Size**: ~10,521 rows
**Time range**: 1980-present
**Creates**: Disease nodes, Country nodes, Outbreak nodes with case counts

### ✅ Dataset 2: Vaccination Coverage (HPD)
**File**: `2- the-worlds-number-of-vaccinated-one-year-olds.csv`

**Vaccine-preventable diseases**:
- Tuberculosis (BCG)
- Diphtheria
- Pertussis (whooping cough)
- Tetanus
- Polio
- Measles
- Hepatitis B
- Haemophilus influenzae
- Rotavirus
- Pneumonia
- Rubella
- Mumps
- Yellow Fever
- Japanese Encephalitis
- Typhoid

**Size**: Varies by vaccine
**Time range**: Historical vaccination coverage data
**Creates**: Disease nodes (if not exist), Country nodes, VaccinationRecord nodes

### ✅ Dataset 4: COVID-19 Excess Deaths (HIGH PRIORITY)
**File**: `4- excess-deaths-cumulative-economist-single-entity.csv`

**Metrics**:
- Cumulative excess deaths (estimated)
- Confirmed COVID-19 deaths
- 95% confidence intervals

**Size**: ~93,353 rows
**Time range**: 2020-01-01 to 2023-12-31 (weekly data)
**Creates**: COVID-19 outbreak nodes with temporal data

**Note**: ETL script samples weekly data to reduce volume. Remove sampling for full granularity.

### ✅ Dataset 5: Cholera Deaths
**File**: `5- number-of-reported-cholera-deaths.csv`

**Size**: ~2,854 rows
**Time range**: 1960-2019 (sparse)
**Creates**: Cholera outbreak nodes with mortality data

### ⚠️ Dataset 3: Influenza Mortality (Limited usefulness)
**File**: `3- annual-mortality-rate-from-seasonal-influenza-ages-65.csv`

**Size**: 200 rows
**Time range**: 2011 only
**Status**: Not currently loaded (single-year data, limited value)

## 🏗️ Knowledge Graph Schema

### Node Types

**Country**
```
Properties:
- code: String (unique, e.g., "AFG")
- name: String (e.g., "Afghanistan")
```

**Disease**
```
Properties:
- id: String (unique, e.g., "covid19", "cholera")
- name: String (e.g., "COVID-19")
- fullName: String
- pathogen: String
- category: String
- transmission: String
- eradicated: Boolean
- firstIdentified: Date (for COVID-19)
- pandemic: Boolean
```

**Outbreak**
```
Properties:
- id: String (unique, e.g., "covid_AFG_20200302")
- year: Integer
- date: Date (for COVID-19)
- cases: Float (disease cases)
- deaths: Integer (cholera deaths)
- excessDeaths: Float (COVID-19 excess mortality)
- confirmedDeaths: Float (COVID-19 confirmed deaths)
- confidenceIntervalTop: Float
- confidenceIntervalBottom: Float
```

### Relationships

- `(Outbreak)-[:OCCURRED_IN]->(Country)`
- `(Outbreak)-[:CAUSED_BY]->(Disease)`

## 🔍 Example Cypher Queries

### Query 1: Get all diseases in the graph
```cypher
MATCH (d:Disease)
RETURN d.name, d.pathogen, d.category
ORDER BY d.name
```

### Query 2: Find COVID-19 outbreaks in a specific country
```cypher
MATCH (o:Outbreak)-[:OCCURRED_IN]->(c:Country {code: 'USA'})
MATCH (o)-[:CAUSED_BY]->(d:Disease {id: 'covid19'})
RETURN o.date, o.excessDeaths, o.confirmedDeaths
ORDER BY o.date
LIMIT 100
```

### Query 3: Countries with highest cholera deaths
```cypher
MATCH (o:Outbreak)-[:OCCURRED_IN]->(c:Country)
MATCH (o)-[:CAUSED_BY]->(d:Disease {id: 'cholera'})
WHERE o.deaths IS NOT NULL
RETURN c.name, SUM(o.deaths) as totalDeaths
ORDER BY totalDeaths DESC
LIMIT 10
```

### Query 4: Track disease trends over time
```cypher
MATCH (o:Outbreak)-[:CAUSED_BY]->(d:Disease {id: 'polio'})
WHERE o.year >= 1990
RETURN o.year, SUM(o.cases) as totalCases
ORDER BY o.year
```

### Query 5: Graph visualization - Disease outbreak network
```cypher
MATCH (o:Outbreak)-[:OCCURRED_IN]->(c:Country)
MATCH (o)-[:CAUSED_BY]->(d:Disease)
WHERE c.code IN ['USA', 'CHN', 'IND', 'BRA']
RETURN o, c, d
LIMIT 100
```

## 📁 Directory Structure

```
kg-construction/
├── data/
│   ├── raw/                         # Raw CSV files (HPD dataset)
│   ├── processed/                   # Processed RDF triples (future)
│   └── external/                    # External data (Wikidata, DBpedia)
├── etl/
│   ├── neo4j_connection.py          # Neo4j connection utilities
│   ├── load_disease_cases.py        # ETL for dataset 1 (9 infectious diseases)
│   ├── load_vaccination_data.py     # ETL for dataset 2 (vaccination coverage)
│   ├── load_covid_data.py           # ETL for dataset 4 (COVID-19 excess deaths)
│   ├── load_cholera_data.py         # ETL for dataset 5 (cholera deaths)
│   ├── load_all_data.py             # MAIN LOADER: All raw CSV datasets
│   ├── wikidata_enricher.py         # Wikidata enrichment (diseases, countries, orgs, vaccines)
│   ├── dbpedia_enricher.py          # DBpedia enrichment (Wikipedia data, historical events)
│   ├── enrich_all.py                # MAIN ENRICHER: Wikidata + DBpedia
│   └── test_dbpedia_connection.py   # Test DBpedia endpoint connectivity
├── notebooks/                       # Jupyter notebooks for exploration (future)
├── ontology/                        # RDF ontology definitions (future)
├── scripts/                         # Utility scripts
├── SPARQL_QUERIES.md                # Documentation of all SPARQL queries (for report)
├── REFACTORING_SUMMARY.md           # Summary of refactoring changes
├── requirements.txt                 # Python dependencies
├── .env.template                    # Environment variables template
└── README.md                        # This file
```

## 🛠️ Troubleshooting

### Neo4j won't start
```bash
# Check Docker status
docker ps

# Check Neo4j logs
docker logs epihelix-neo4j

# Restart Neo4j
cd infrastructure
docker-compose restart
```

### Connection refused error
- Ensure Neo4j is running: `docker-compose ps`
- Check credentials in `.env` file
- Wait 10-30 seconds after starting Neo4j

### Out of memory errors
- Increase Neo4j memory in `infrastructure/docker-compose.yml`:
  ```yaml
  NEO4J_dbms_memory_heap_max__size=4G
  NEO4J_dbms_memory_pagecache_size=2G
  ```
- Restart: `docker-compose down && docker-compose up -d`

### Dataset files not found
- Ensure CSV files are in `kg-construction/data/raw/`
- Check file names match exactly (including spaces and hyphens)

## 🌐 External Data Enrichment (Wikidata + DBpedia)

**⚠️  REFACTORED**: Enrichment is now a separate step that runs AFTER loading raw data.

The ETL pipeline supports **comprehensive external data enrichment** from multiple knowledge bases:
- **Wikidata**: Medical classifications, symptoms, treatments, demographics
- **DBpedia**: Wikipedia abstracts, images, historical pandemic events

All SPARQL queries used for enrichment are documented in [`SPARQL_QUERIES.md`](./SPARQL_QUERIES.md) (required for final project report).

### What Gets Enriched?

#### 1. **All HPD Diseases** (from Wikidata + DBpedia)
Enriches every disease in your dataset (from both disease cases and vaccination datasets):

**Disease Cases Dataset:**
- **Cholera** (Q12090)
- **Tuberculosis** (Q12204)
- **Malaria** (Q12156)
- **HIV/AIDS** (Q12199)
- **Poliomyelitis** (Q12195)
- **Rabies** (Q39552)
- **Smallpox** (Q12214)
- **Yaws** (Q1415196)
- **Guinea Worm Disease** (Q913399)

**Vaccination Dataset (Vaccine-Preventable):**
- **Diphtheria** (Q134041)
- **Pertussis** (Q37933)
- **Tetanus** (Q81133)
- **Measles** (Q8274)
- **Hepatitis B** (Q6853)
- **Haemophilus influenzae** (Q165663)
- **Rotavirus** (Q808)
- **Pneumonia** (Q12192)
- **Rubella** (Q48143)
- **Mumps** (Q36956)
- **Yellow Fever** (Q154874)
- **Japanese Encephalitis** (Q190711)
- **Typhoid** (Q161549)

**Wikidata properties fetched:**
- **Medical Classifications**: ICD-10 codes, MeSH identifiers
- **Clinical Data**: Symptoms, transmission methods, risk factors
- **Treatment**: Drugs and treatment options
- **Epidemiology**: Incubation periods
- **Context**: Detailed descriptions

**DBpedia properties fetched:**
- **Wikipedia Integration**: Full article abstracts, article URLs
- **Media**: Thumbnail images
- **Medical Context**: Causative agents, medical specialties, prevention methods

#### 2. **Countries** (All countries in your data)
**Wikidata enrichment:**
- **Geographic**: Population, capital city, continent, coordinates (lat/lon)
- **Economic**: GDP, area in km²
- **Health**: Life expectancy, official language
- **Identifiers**: Wikidata ID, ISO 3166-1 alpha-3 code

**DBpedia enrichment:**
- **Demographics**: Population density
- **Political**: Government type
- **Economic**: Currency
- **Other**: Time zones, country abstracts, thumbnails

#### 3. **Health Organizations**
- **WHO** (World Health Organization)
- **CDC** (Centers for Disease Control)
- **ECDC** (European Centre for Disease Prevention and Control)
- Properties: Founding date, headquarters, official website
- Relationships: `(Organization)-[:MONITORS]->(Disease)`

#### 4. **COVID-19 Vaccines** (Bonus for advanced features)
- Pfizer-BioNTech, Moderna, AstraZeneca, Johnson & Johnson, Sinovac
- Properties: Manufacturer, approval dates, descriptions
- Relationships: `(Vaccine)-[:PREVENTS]->(Disease)`

#### 5. **Historical Pandemic Events** (from DBpedia)
Automatically discovers and adds historical pandemics:
- **Spanish flu**, **Black Death**, **1918 flu pandemic**, etc.
- Properties: Death tolls, locations, dates, descriptions
- Creates `PandemicEvent` nodes
- Relationships: `(PandemicEvent)-[:RELATED_TO]->(Disease)`, `(PandemicEvent)-[:OCCURRED_IN]->(Country)`

### How to Use Enrichment

**⚠️  IMPORTANT**: Run enrichment AFTER loading raw data with `load_all_data.py`

#### **Workflow:**
```bash
cd etl

# Step 1: Load raw CSV data (fast, no external API calls)
python load_all_data.py

# Step 2: Enrich with external data (Wikidata + DBpedia)
python enrich_all.py
```

#### **What `enrich_all.py` Does:**
1. ✅ Enrich ALL HPD diseases (22+ diseases from both datasets)
2. ✅ Enrich all countries with demographics, coordinates, GDP, life expectancy
3. ✅ Add health organizations (WHO, CDC, ECDC)
4. ✅ Add COVID-19 vaccines
5. ✅ Add historical pandemic events from DBpedia
6. ✅ Fetch Wikipedia abstracts and images for all diseases

**Time required**: ~10-15 minutes (rate-limited to respect external servers)

#### **Alternative: Run Individual Enrichment Scripts**
```bash
cd etl

# Wikidata enrichment only (diseases, countries, orgs, vaccines)
python wikidata_enricher.py

# DBpedia enrichment only (Wikipedia data, historical events)
python dbpedia_enricher.py
```

#### **Benefits of Separate Enrichment:**
- **Faster development**: Load raw data quickly for testing
- **Reproducible**: Raw data loading is deterministic
- **Flexible**: Run enrichment only when needed
- **Error handling**: External API failures don't affect data loading
- **Clean code**: Clear separation of concerns

### Enriched Schema Updates

After enrichment, nodes have additional properties:

**Country (enriched)**
```
Additional Properties:
- wikidataId: String (e.g., "Q30" for United States)
- population: Integer
- capital: String
- continent: String (e.g., "North America")
- latitude: Float
- longitude: Float
- iso3: String (ISO 3166-1 alpha-3, e.g., "USA")
- gdp: Float (nominal GDP)
- lifeExpectancy: Float
- areaKm2: Float
- officialLanguage: String
- enriched: Boolean (true)
- enrichedAt: DateTime
```

**Disease (enriched)**
```
Wikidata Properties:
- wikidataId: String (e.g., "Q12090" for Cholera)
- icd10: String (ICD-10 code, e.g., "A00")
- mesh: String (Medical Subject Headings ID)
- symptoms: List<String> (e.g., ["diarrhea", "dehydration", "vomiting"])
- transmissionMethods: List<String> (e.g., ["waterborne", "foodborne"])
- riskFactors: List<String>
- treatments: List<String> (e.g., ["oral rehydration therapy", "antibiotics"])
- incubationPeriod: String
- description: String (from Wikidata)
- enriched: Boolean
- enrichedAt: DateTime
- externalSource: String ("Wikidata")

DBpedia Properties:
- dbpediaUri: String
- wikipediaAbstract: String (full Wikipedia summary)
- wikipediaUrl: String
- thumbnailUrl: String (disease/pathogen image)
- causativeAgent: String
- medicalSpecialty: String
- prevention: String
- dbpediaEnriched: Boolean
```

**New Node Types:**
```
Organization:
- id: String (e.g., "who", "cdc")
- name: String
- acronym: String
- wikidataId: String
- role: String
- founded: Date
- headquarters: String
- website: String

Vaccine:
- wikidataId: String (unique)
- name: String
- manufacturer: String
- approvalDate: Date
- description: String

PandemicEvent:
- dbpediaUri: String (unique)
- name: String
- abstract: String
- startDate: String
- deathToll: String
- location: String
- source: String ("DBpedia")
```

**New Relationships:**
- `(Organization)-[:MONITORS]->(Disease)`
- `(Vaccine)-[:PREVENTS]->(Disease)`
- `(PandemicEvent)-[:RELATED_TO]->(Disease)`
- `(PandemicEvent)-[:OCCURRED_IN]->(Country)`

### Example Queries with Enriched Data

#### Query 1: Countries by population with COVID deaths
```cypher
MATCH (o:Outbreak)-[:OCCURRED_IN]->(c:Country)
MATCH (o)-[:CAUSED_BY]->(d:Disease {id: 'covid19'})
WHERE c.population IS NOT NULL
WITH c, SUM(o.excessDeaths) as totalDeaths
RETURN c.name, c.population, totalDeaths,
       (totalDeaths / c.population * 100000) as deathsPer100k
ORDER BY deathsPer100k DESC
LIMIT 20
```

#### Query 2: Geographic visualization data
```cypher
MATCH (c:Country)
WHERE c.latitude IS NOT NULL AND c.longitude IS NOT NULL
OPTIONAL MATCH (o:Outbreak)-[:OCCURRED_IN]->(c)
WHERE o.year = 2021
WITH c, SUM(o.cases) as totalCases
RETURN c.name, c.latitude, c.longitude, c.population, totalCases
```

#### Query 3: Continental disease analysis
```cypher
MATCH (o:Outbreak)-[:OCCURRED_IN]->(c:Country)
MATCH (o)-[:CAUSED_BY]->(d:Disease)
WHERE c.continent IS NOT NULL
RETURN c.continent, d.name, COUNT(o) as outbreakCount,
       SUM(o.cases) as totalCases
ORDER BY c.continent, totalCases DESC
```

#### Query 4: Health organizations and their monitored diseases
```cypher
MATCH (org:Organization)-[:MONITORS]->(d:Disease)
RETURN org.name, org.acronym, org.headquarters,
       collect(d.name) as diseases
```

#### Query 5: Vaccine information
```cypher
MATCH (v:Vaccine)-[:PREVENTS]->(d:Disease {id: 'covid19'})
RETURN v.name, v.manufacturer, v.approvalDate
ORDER BY v.approvalDate
```

### Enrichment Performance

- **Country enrichment**: ~1 second per country (rate-limited to respect Wikidata servers)
- **Full enrichment** (all features): ~5-10 minutes for typical dataset
- **Data source**: Wikidata SPARQL endpoint (https://query.wikidata.org/sparql)

### Implementation Details

The enrichment system uses:
- **SPARQLWrapper**: Query Wikidata's SPARQL endpoint
- **Retry logic**: Handles temporary failures with exponential backoff
- **Rate limiting**: Respectful 1-second delay between requests
- **Batch updates**: Efficient Neo4j writes

Files added:
- `etl/wikidata_enricher.py` - Main enrichment module
- `etl/test_enrichment.py` - Test and demonstration script

## 🔗 Next Steps

1. ✅ **Enrich with Wikidata** - COMPLETED!
   - Countries enriched with population, GDP, coordinates
   - Diseases enriched with ICD-10 codes, symptoms
   - Organizations and vaccines added

2. **Add Vaccination Data**
   - Load dataset 2: `2- the-worlds-number-of-vaccinated-one-year-olds.csv`
   - Create `Vaccination` nodes and relationships

3. **Semantic Search**
   - Generate embeddings for entities
   - Implement vector similarity search

4. **Connect to Backend API**
   - Build FastAPI service in `services/api/`
   - Expose Cypher query endpoints
   - Integrate with frontend app

## 📚 Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)
- [Python Neo4j Driver](https://neo4j.com/docs/python-manual/current/)
- [Neo4j Browser Guide](https://neo4j.com/docs/browser-manual/current/)
