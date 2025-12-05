"""
Wikidata and DBpedia Enrichment Module for EpiHelix Knowledge Graph

This module fetches external data from Wikidata to enrich the knowledge graph
with additional context about countries, diseases, organizations, and more.
"""
import logging
import time
from typing import Dict, List, Optional
from SPARQLWrapper import SPARQLWrapper, JSON
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WikidataEnricher:
    """Fetch and integrate data from Wikidata into Neo4j"""

    def __init__(self, neo4j_conn):
        """
        Initialize Wikidata enricher

        Args:
            neo4j_conn: Neo4jConnection instance
        """
        self.conn = neo4j_conn
        self.wikidata_endpoint = SPARQLWrapper("https://query.wikidata.org/sparql")
        self.wikidata_endpoint.setReturnFormat(JSON)
        self.wikidata_endpoint.addCustomHttpHeader("User-Agent", "EpiHelix/1.0 (Educational Project)")

    def _execute_sparql(self, query: str, max_retries: int = 3) -> Optional[Dict]:
        """
        Execute SPARQL query with retry logic

        Args:
            query: SPARQL query string
            max_retries: Maximum number of retry attempts

        Returns:
            Query results as dict or None if failed
        """
        for attempt in range(max_retries):
            try:
                self.wikidata_endpoint.setQuery(query)
                results = self.wikidata_endpoint.query().convert()
                return results
            except Exception as e:
                logger.warning(f"SPARQL query attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"SPARQL query failed after {max_retries} attempts")
                    return None

    def enrich_country(self, country_code: str) -> Dict:
        """
        Fetch comprehensive country data from Wikidata

        Args:
            country_code: ISO 3166-1 alpha-3 country code (e.g., 'USA', 'GBR')

        Returns:
            Dictionary with country enrichment data
        """
        query = f"""
        SELECT ?country ?countryLabel ?population ?capital ?capitalLabel
               ?continent ?continentLabel ?coords ?iso2
               ?gdp ?lifeExpectancy ?area ?officialLanguage ?officialLanguageLabel
               ?borderingCountry ?borderingCountryLabel ?borderingCountryIso3
               ?article
        WHERE {{
          ?country wdt:P298 "{country_code}" .  # ISO 3166-1 alpha-3 code

          OPTIONAL {{ ?country wdt:P1082 ?population . }}
          OPTIONAL {{ ?country wdt:P36 ?capital . }}
          OPTIONAL {{ ?country wdt:P30 ?continent . }}
          OPTIONAL {{ ?country wdt:P625 ?coords . }}
          OPTIONAL {{ ?country wdt:P297 ?iso2 . }}  # ISO 3166-1 alpha-2
          OPTIONAL {{ ?country wdt:P2131 ?gdp . }}  # Nominal GDP
          OPTIONAL {{ ?country wdt:P2250 ?lifeExpectancy . }}
          OPTIONAL {{ ?country wdt:P2046 ?area . }}  # Area in km²
          OPTIONAL {{ ?country wdt:P37 ?officialLanguage . }}

          # Get English Wikipedia article URL
          OPTIONAL {{
            ?article schema:about ?country ;
                     schema:isPartOf <https://en.wikipedia.org/> .
          }}

          # Bordering countries
          OPTIONAL {{
            ?country wdt:P47 ?borderingCountry .  # Shares border with
            ?borderingCountry wdt:P298 ?borderingCountryIso3 .  # Get ISO3 code
          }}

          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
        }}
        """

        results = self._execute_sparql(query)
        if not results or not results['results']['bindings']:
            logger.warning(f"No Wikidata results for country code: {country_code}")
            return {}

        bindings = results['results']['bindings']
        data = bindings[0]

        # Parse coordinates if available
        coords = None
        if 'coords' in data:
            coord_str = data['coords']['value']
            # Format: "Point(longitude latitude)"
            if 'Point' in coord_str:
                coord_str = coord_str.replace('Point(', '').replace(')', '')
                lon, lat = map(float, coord_str.split())
                coords = {'latitude': lat, 'longitude': lon}

        # Collect bordering countries from all result rows
        bordering_countries = []
        for binding in bindings:
            if 'borderingCountryIso3' in binding:
                border_code = binding['borderingCountryIso3']['value']
                border_name = binding.get('borderingCountryLabel', {}).get('value', border_code)
                if border_code not in [b['code'] for b in bordering_countries]:
                    bordering_countries.append({
                        'code': border_code,
                        'name': border_name
                    })

        # Extract Wikipedia article URL and construct DBpedia URI
        wikipedia_url = data.get('article', {}).get('value')
        dbpedia_uri = None
        if wikipedia_url:
            # Convert Wikipedia URL to DBpedia URI
            # Example: https://en.wikipedia.org/wiki/Germany -> http://dbpedia.org/resource/Germany
            article_title = wikipedia_url.split('/wiki/')[-1]
            dbpedia_uri = f"http://dbpedia.org/resource/{article_title}"

        enrichment = {
            'wikidata_id': data['country']['value'].split('/')[-1],
            'wikipedia_url': wikipedia_url,
            'dbpedia_uri': dbpedia_uri,
            'population': int(float(data['population']['value'])) if 'population' in data else None,
            'capital': data.get('capitalLabel', {}).get('value'),
            'continent': data.get('continentLabel', {}).get('value'),
            'coordinates': coords,
            'iso2': data.get('iso2', {}).get('value'),
            'gdp': float(data['gdp']['value']) if 'gdp' in data else None,
            'life_expectancy': float(data['lifeExpectancy']['value']) if 'lifeExpectancy' in data else None,
            'area_km2': float(data['area']['value']) if 'area' in data else None,
            'official_language': data.get('officialLanguageLabel', {}).get('value'),
            'bordering_countries': bordering_countries
        }

        logger.info(f"✓ Enriched country: {country_code} - {data.get('countryLabel', {}).get('value')} ({len(bordering_countries)} borders)")
        return enrichment

    def enrich_all_countries(self):
        """Enrich all countries in the database with Wikidata data"""
        logger.info("Starting country enrichment from Wikidata...")

        # Special codes to skip (aggregates, historical countries, disputed territories)
        SKIP_CODES = {
            'OWID_WRL',  # World (global aggregate)
            'OWID_YGS',  # Yugoslavia (historical, dissolved 1992)
            'OWID_SRM',  # Serbia and Montenegro (historical, dissolved 2006)
            'OWID_KOS',  # Kosovo (disputed territory, non-standard codes)
            'OWID_USS',  # USSR (historical)
            'OWID_CSK',  # Czechoslovakia (historical)
        }

        # Get all countries from Neo4j
        query = "MATCH (c:Country) RETURN c.code as code, c.name as name"
        countries = self.conn.execute_query(query)

        enriched_count = 0
        failed_count = 0
        skipped_count = 0

        for country in countries:
            country_code = country['code']
            country_name = country['name']

            # Skip special OWID codes
            if country_code in SKIP_CODES:
                logger.debug(f"Skipping {country_name} ({country_code}) - special aggregate/historical entity")
                skipped_count += 1
                continue

            logger.info(f"Enriching {country_name} ({country_code})...")

            # Fetch Wikidata enrichment
            enrichment = self.enrich_country(country_code)

            if enrichment:
                # Update Neo4j with enrichment data
                update_query = """
                MATCH (c:Country {code: $code})
                SET c.wikidataId = $wikidata_id,
                    c.wikipediaUrl = $wikipedia_url,
                    c.dbpediaUri = $dbpedia_uri,
                    c.population = $population,
                    c.capital = $capital,
                    c.continent = $continent,
                    c.latitude = $latitude,
                    c.longitude = $longitude,
                    c.iso2 = $iso2,
                    c.gdp = $gdp,
                    c.lifeExpectancy = $life_expectancy,
                    c.areaKm2 = $area_km2,
                    c.officialLanguage = $official_language,
                    c.enriched = true,
                    c.enrichedAt = datetime()
                """

                params = {
                    'code': country_code,
                    'wikidata_id': enrichment.get('wikidata_id'),
                    'wikipedia_url': enrichment.get('wikipedia_url'),
                    'dbpedia_uri': enrichment.get('dbpedia_uri'),
                    'population': enrichment.get('population'),
                    'capital': enrichment.get('capital'),
                    'continent': enrichment.get('continent'),
                    'latitude': enrichment.get('coordinates', {}).get('latitude') if enrichment.get('coordinates') else None,
                    'longitude': enrichment.get('coordinates', {}).get('longitude') if enrichment.get('coordinates') else None,
                    'iso2': enrichment.get('iso2'),
                    'gdp': enrichment.get('gdp'),
                    'life_expectancy': enrichment.get('life_expectancy'),
                    'area_km2': enrichment.get('area_km2'),
                    'official_language': enrichment.get('official_language')
                }

                self.conn.execute_write(update_query, params)

                # Create border relationships with neighboring countries
                bordering_countries = enrichment.get('bordering_countries', [])
                if bordering_countries:
                    border_query = """
                    MATCH (c1:Country {code: $country_code})
                    UNWIND $borders as border
                    MATCH (c2:Country {code: border.code})
                    MERGE (c1)-[r:SHARES_BORDER_WITH]->(c2)
                    """

                    border_params = {
                        'country_code': country_code,
                        'borders': bordering_countries
                    }

                    self.conn.execute_write(border_query, border_params)
                    logger.info(f"  ✓ Created {len(bordering_countries)} border relationships")

                enriched_count += 1
            else:
                failed_count += 1

            # Rate limiting - be respectful to Wikidata servers
            time.sleep(1)

        logger.info(f"✓ Country enrichment complete! Enriched: {enriched_count}, Failed: {failed_count}, Skipped: {skipped_count} (special entities)")

    def enrich_disease_covid19(self):
        """Enrich COVID-19 disease node with Wikidata information"""
        logger.info("Enriching COVID-19 disease node from Wikidata...")

        query = """
        SELECT ?disease ?diseaseLabel ?icd10 ?mesh ?symptom ?symptomLabel
               ?drug ?drugLabel ?possibleTreatment ?possibleTreatmentLabel
               ?incubationPeriod ?description
        WHERE {
          BIND(wd:Q84263196 AS ?disease)  # COVID-19

          OPTIONAL { ?disease wdt:P493 ?icd10 . }  # ICD-10 code
          OPTIONAL { ?disease wdt:P486 ?mesh . }   # Medical Subject Headings
          OPTIONAL { ?disease wdt:P780 ?symptom . }  # Symptoms
          OPTIONAL { ?disease wdt:P2176 ?drug . }  # Drug used for treatment (specific)
          OPTIONAL { ?disease wdt:P924 ?possibleTreatment . }  # Possible treatment (broader)
          OPTIONAL { ?disease wdt:P3488 ?incubationPeriod . }  # Incubation period
          OPTIONAL {
            ?disease schema:description ?description .
            FILTER(LANG(?description) = "en")
          }

          SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
        }
        LIMIT 10
        """

        results = self._execute_sparql(query)
        if not results or not results['results']['bindings']:
            logger.warning("No Wikidata results for COVID-19")
            return

        # Collect symptoms, drugs, and treatments
        symptoms = []
        drugs = []
        possible_treatments = []
        icd10 = None
        mesh = None
        incubation = None
        description = None

        for binding in results['results']['bindings']:
            if 'icd10' in binding:
                icd10 = binding['icd10']['value']
            if 'mesh' in binding:
                mesh = binding['mesh']['value']
            if 'incubationPeriod' in binding:
                incubation = binding['incubationPeriod']['value']
            if 'description' in binding:
                description = binding['description']['value']
            if 'symptomLabel' in binding:
                symptom = binding['symptomLabel']['value']
                if symptom not in symptoms:
                    symptoms.append(symptom)
            if 'drugLabel' in binding:
                drug = binding['drugLabel']['value']
                if drug not in drugs:
                    drugs.append(drug)
            if 'possibleTreatmentLabel' in binding:
                treatment = binding['possibleTreatmentLabel']['value']
                if treatment not in possible_treatments:
                    possible_treatments.append(treatment)

        # Update Neo4j
        update_query = """
        MATCH (d:Disease {id: 'covid19'})
        SET d.wikidataId = 'Q84263196',
            d.icd10 = $icd10,
            d.mesh = $mesh,
            d.symptoms = $symptoms,
            d.drugs = $drugs,
            d.possibleTreatments = $possible_treatments,
            d.incubationPeriod = $incubation,
            d.description = $description,
            d.enriched = true,
            d.enrichedAt = datetime()
        """

        params = {
            'icd10': icd10,
            'mesh': mesh,
            'symptoms': symptoms if symptoms else None,
            'drugs': drugs if drugs else None,
            'possible_treatments': possible_treatments if possible_treatments else None,
            'incubation': incubation,
            'description': description
        }

        self.conn.execute_write(update_query, params)
        logger.info(f"✓ COVID-19 enriched with {len(symptoms)} symptoms, {len(drugs)} drugs, {len(possible_treatments)} treatments")

    def add_health_organizations(self):
        """Add major health organizations to the knowledge graph"""
        logger.info("Adding health organizations from Wikidata...")

        organizations = [
            {
                'id': 'who',
                'wikidata_id': 'Q7817',
                'name': 'World Health Organization',
                'acronym': 'WHO',
                'role': 'Global health coordination'
            },
            {
                'id': 'cdc',
                'wikidata_id': 'Q583725',
                'name': 'Centers for Disease Control and Prevention',
                'acronym': 'CDC',
                'role': 'US public health agency'
            },
            {
                'id': 'ecdc',
                'wikidata_id': 'Q902384',
                'name': 'European Centre for Disease Prevention and Control',
                'acronym': 'ECDC',
                'role': 'EU public health agency'
            }
        ]

        for org in organizations:
            # Query Wikidata for organization details
            query = f"""
            SELECT ?org ?orgLabel ?founded ?headquarters ?hqLabel ?website
            WHERE {{
              BIND(wd:{org['wikidata_id']} AS ?org)

              OPTIONAL {{ ?org wdt:P571 ?founded . }}  # Inception
              OPTIONAL {{ ?org wdt:P159 ?headquarters . }}  # Headquarters location
              OPTIONAL {{ ?org wdt:P856 ?website . }}  # Official website

              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
            }}
            """

            results = self._execute_sparql(query)
            if results and results['results']['bindings']:
                data = results['results']['bindings'][0]

                create_query = """
                MERGE (o:Organization {id: $id})
                SET o.name = $name,
                    o.acronym = $acronym,
                    o.wikidataId = $wikidata_id,
                    o.role = $role,
                    o.founded = date($founded),
                    o.headquarters = $headquarters,
                    o.website = $website
                """

                params = {
                    'id': org['id'],
                    'name': org['name'],
                    'acronym': org['acronym'],
                    'wikidata_id': org['wikidata_id'],
                    'role': org['role'],
                    'founded': data.get('founded', {}).get('value', '').split('T')[0] if 'founded' in data else None,
                    'headquarters': data.get('hqLabel', {}).get('value'),
                    'website': data.get('website', {}).get('value')
                }

                self.conn.execute_write(create_query, params)
                logger.info(f"✓ Added organization: {org['name']}")

                # Create relationship to COVID-19
                rel_query = """
                MATCH (o:Organization {id: $org_id})
                MATCH (d:Disease {id: 'covid19'})
                MERGE (o)-[:MONITORS]->(d)
                """
                self.conn.execute_write(rel_query, {'org_id': org['id']})

            time.sleep(1)  # Rate limiting

        logger.info(f"✓ Added {len(organizations)} health organizations")

    def add_vaccines(self):
        """Add COVID-19 vaccines to the knowledge graph"""
        logger.info("Adding COVID-19 vaccines from Wikidata...")

        vaccines = [
            {'wikidata_id': 'Q98158256', 'name': 'Pfizer-BioNTech COVID-19 vaccine'},
            {'wikidata_id': 'Q98109286', 'name': 'Moderna COVID-19 vaccine'},
            {'wikidata_id': 'Q98244340', 'name': 'Oxford-AstraZeneca COVID-19 vaccine'},
            {'wikidata_id': 'Q98843566', 'name': 'Johnson & Johnson COVID-19 vaccine'},
            {'wikidata_id': 'Q98246648', 'name': 'Sinovac CoronaVac'}
        ]

        for vaccine in vaccines:
            # Query with explicit rdfs:label instead of relying on label service
            query = f"""
            SELECT ?vaccine ?vaccineName ?manufacturer ?manufacturerName
                   ?approvalDate ?efficacy ?description
            WHERE {{
              BIND(wd:{vaccine['wikidata_id']} AS ?vaccine)

              # Get label explicitly (more reliable than SERVICE wikibase:label)
              OPTIONAL {{
                ?vaccine rdfs:label ?vaccineName .
                FILTER(LANG(?vaccineName) = "en")
              }}

              OPTIONAL {{
                ?vaccine wdt:P176 ?manufacturer .
                ?manufacturer rdfs:label ?manufacturerName .
                FILTER(LANG(?manufacturerName) = "en")
              }}  # Manufacturer
              OPTIONAL {{ ?vaccine wdt:P571 ?approvalDate . }}  # Inception/approval
              OPTIONAL {{
                ?vaccine schema:description ?description .
                FILTER(LANG(?description) = "en")
              }}
            }}
            """

            results = self._execute_sparql(query)
            if results and results['results']['bindings']:
                data = results['results']['bindings'][0]

                create_query = """
                MERGE (v:Vaccine {wikidataId: $wikidata_id})
                SET v.name = $name,
                    v.manufacturer = $manufacturer,
                    v.approvalDate = date($approval_date),
                    v.description = $description
                """

                params = {
                    'wikidata_id': vaccine['wikidata_id'],
                    'name': data.get('vaccineName', {}).get('value', vaccine['name']),
                    'manufacturer': data.get('manufacturerName', {}).get('value'),
                    'approval_date': data.get('approvalDate', {}).get('value', '').split('T')[0] if 'approvalDate' in data else None,
                    'description': data.get('description', {}).get('value')
                }

                self.conn.execute_write(create_query, params)
                logger.info(f"✓ Added vaccine: {params['name']}")

                # Create relationship to COVID-19
                rel_query = """
                MATCH (v:Vaccine {wikidataId: $wikidata_id})
                MATCH (d:Disease {id: 'covid19'})
                MERGE (v)-[:PREVENTS]->(d)
                """
                self.conn.execute_write(rel_query, {'wikidata_id': vaccine['wikidata_id']})

            time.sleep(1)  # Rate limiting

        logger.info(f"✓ Added {len(vaccines)} vaccines")

    def enrich_disease_by_id(self, disease_id: str, wikidata_id: str):
        """
        Enrich any disease node with Wikidata information

        Args:
            disease_id: Internal disease ID (e.g., 'cholera', 'malaria')
            wikidata_id: Wikidata entity ID (e.g., 'Q12090' for cholera)
        """
        logger.info(f"Enriching disease: {disease_id} (Wikidata: {wikidata_id})...")

        query = f"""
        SELECT ?disease ?diseaseLabel ?description
               ?icd10 ?mesh ?symptom ?symptomLabel
               ?transmission ?transmissionLabel
               ?riskFactor ?riskFactorLabel
               ?drug ?drugLabel
               ?possibleTreatment ?possibleTreatmentLabel
               ?incubationPeriod
        WHERE {{
          BIND(wd:{wikidata_id} AS ?disease)

          # Basic info
          OPTIONAL {{
            ?disease schema:description ?description .
            FILTER(LANG(?description) = "en")
          }}

          # Medical classifications
          OPTIONAL {{ ?disease wdt:P493 ?icd10 . }}  # ICD-10 code
          OPTIONAL {{ ?disease wdt:P486 ?mesh . }}   # Medical Subject Headings

          # Clinical information
          OPTIONAL {{ ?disease wdt:P780 ?symptom . }}  # Symptoms
          OPTIONAL {{ ?disease wdt:P1060 ?transmission . }}  # Transmission method
          OPTIONAL {{ ?disease wdt:P5642 ?riskFactor . }}  # Risk factors
          OPTIONAL {{ ?disease wdt:P2176 ?drug . }}  # Drug used for treatment (specific)
          OPTIONAL {{ ?disease wdt:P924 ?possibleTreatment . }}  # Possible treatment (broader)
          OPTIONAL {{ ?disease wdt:P3488 ?incubationPeriod . }}  # Incubation period

          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en" . }}
        }}
        LIMIT 50
        """

        results = self._execute_sparql(query)
        if not results or not results['results']['bindings']:
            logger.warning(f"No Wikidata results for {disease_id}")
            return

        # Aggregate data from multiple rows (due to multiple symptoms/treatments)
        symptoms = []
        transmissions = []
        risk_factors = []
        drugs = []
        possible_treatments = []
        icd10 = None
        mesh = None
        incubation = None
        description = None

        for binding in results['results']['bindings']:
            if 'icd10' in binding and not icd10:
                icd10 = binding['icd10']['value']
            if 'mesh' in binding and not mesh:
                mesh = binding['mesh']['value']
            if 'incubationPeriod' in binding and not incubation:
                incubation = binding['incubationPeriod']['value']
            if 'description' in binding and not description:
                description = binding['description']['value']

            # Collect lists
            if 'symptomLabel' in binding:
                symptom = binding['symptomLabel']['value']
                if symptom not in symptoms:
                    symptoms.append(symptom)

            if 'transmissionLabel' in binding:
                trans = binding['transmissionLabel']['value']
                if trans not in transmissions:
                    transmissions.append(trans)

            if 'riskFactorLabel' in binding:
                risk = binding['riskFactorLabel']['value']
                if risk not in risk_factors:
                    risk_factors.append(risk)

            if 'drugLabel' in binding:
                drug = binding['drugLabel']['value']
                if drug not in drugs:
                    drugs.append(drug)

            if 'possibleTreatmentLabel' in binding:
                treatment = binding['possibleTreatmentLabel']['value']
                if treatment not in possible_treatments:
                    possible_treatments.append(treatment)

        # Update Neo4j
        update_query = """
        MATCH (d:Disease {id: $disease_id})
        SET d.wikidataId = $wikidata_id,
            d.description = $description,
            d.icd10 = $icd10,
            d.mesh = $mesh,
            d.symptoms = $symptoms,
            d.transmissionMethods = $transmissions,
            d.riskFactors = $risk_factors,
            d.drugs = $drugs,
            d.possibleTreatments = $possible_treatments,
            d.incubationPeriod = $incubation,
            d.enriched = true,
            d.enrichedAt = datetime(),
            d.externalSource = 'Wikidata'
        """

        params = {
            'disease_id': disease_id,
            'wikidata_id': wikidata_id,
            'description': description,
            'icd10': icd10,
            'mesh': mesh,
            'symptoms': symptoms if symptoms else None,
            'transmissions': transmissions if transmissions else None,
            'risk_factors': risk_factors if risk_factors else None,
            'drugs': drugs if drugs else None,
            'possible_treatments': possible_treatments if possible_treatments else None,
            'incubation': incubation
        }

        self.conn.execute_write(update_query, params)
        logger.info(f"✓ {disease_id} enriched: {len(symptoms)} symptoms, {len(drugs)} drugs, {len(possible_treatments)} treatments")

    def enrich_all_hpd_diseases(self):
        """Enrich all diseases from HPD dataset with Wikidata data"""
        logger.info("Enriching all HPD diseases from Wikidata...")

        # Mapping: internal disease ID -> Wikidata ID
        # Includes diseases from:
        # - Disease cases dataset (cholera, tuberculosis, malaria, etc.)
        # - Vaccination dataset (diphtheria, pertussis, tetanus, measles, etc.)
        disease_mappings = {
            # From disease cases dataset
            'cholera': 'Q12090',           # Cholera
            'tuberculosis': 'Q12204',      # Tuberculosis
            'malaria': 'Q12156',           # Malaria
            'hiv_aids': 'Q12199',          # HIV/AIDS
            'polio': 'Q12195',             # Poliomyelitis
            'rabies': 'Q39222',            # Rabies (CORRECTED)
            'smallpox': 'Q12214',          # Smallpox
            'yaws': 'Q76973',              # Yaws (CORRECTED)
            'guinea_worm': 'Q388646',      # Guinea worm disease / Dracunculiasis (CORRECTED)

            # From vaccination dataset (vaccine-preventable diseases)
            'diphtheria': 'Q134649',       # Diphtheria (CORRECTED)
            'pertussis': 'Q37933',         # Pertussis (whooping cough)
            'tetanus': 'Q81133',           # Tetanus
            'measles': 'Q79793',           # Measles (CORRECTED)
            'hepatitis_b': 'Q6853',        # Hepatitis B
            'haemophilus_influenzae': 'Q1141979',  # Haemophilus influenzae (CORRECTED)
            'rotavirus': 'Q808',           # Rotavirus
            'pneumonia': 'Q12192',         # Pneumonia
            'rubella': 'Q48143',           # Rubella
            'mumps': 'Q36956',             # Mumps
            'yellow_fever': 'Q154874',     # Yellow fever
            'japanese_encephalitis': 'Q190711',  # Japanese encephalitis
            'typhoid': 'Q161549'           # Typhoid fever
        }

        # Query database to get existing diseases
        query = "MATCH (d:Disease) RETURN d.id as id"
        existing_diseases = self.conn.execute_query(query)
        existing_disease_ids = {d['id'] for d in existing_diseases}

        logger.info(f"Found {len(existing_disease_ids)} diseases in database")

        enriched_count = 0
        skipped_count = 0

        for disease_id, wikidata_id in disease_mappings.items():
            # Only enrich if disease exists in database
            if disease_id not in existing_disease_ids:
                logger.debug(f"Skipping {disease_id} (not in database)")
                skipped_count += 1
                continue

            try:
                self.enrich_disease_by_id(disease_id, wikidata_id)
                enriched_count += 1
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to enrich {disease_id}: {e}")

        logger.info(f"✓ Disease enrichment complete! Enriched: {enriched_count}, Skipped: {skipped_count}")

    def enrich_all(self):
        """Run all enrichment methods"""
        logger.info("=== Starting Full Wikidata Enrichment ===\n")

        try:
            # Enrich all HPD diseases
            self.enrich_all_hpd_diseases()
            logger.info("")

            # Keep COVID-19 enrichment for bonus features
            self.enrich_disease_covid19()
            logger.info("")

            self.add_health_organizations()
            logger.info("")

            # Vaccine enrichment skipped - not needed for historical pandemic analysis
            # self.add_vaccines()
            # logger.info("")

            self.enrich_all_countries()
            logger.info("")

            logger.info("=== ✓ Full enrichment complete! ===")
        except Exception as e:
            logger.error(f"Enrichment failed: {e}")
            raise


if __name__ == "__main__":
    from neo4j_connection import Neo4jConnection

    # Connect to Neo4j
    conn = Neo4jConnection()
    if not conn.connect():
        exit(1)

    # Run enrichment
    enricher = WikidataEnricher(conn)
    enricher.enrich_all()

    # Show updated stats
    stats = conn.get_stats()
    print("\n=== Updated Database Statistics ===")
    for key, value in stats.items():
        print(f"{key.capitalize()}: {value:,}")

    conn.close()
