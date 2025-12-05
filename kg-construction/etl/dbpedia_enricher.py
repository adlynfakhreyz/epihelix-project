"""
DBpedia Enrichment Module for EpiHelix Knowledge Graph

This module fetches additional context from DBpedia to complement Wikidata enrichment.
DBpedia provides Wikipedia-based structured data with different coverage.
"""
import logging
import time
from typing import Dict, List, Optional
from SPARQLWrapper import SPARQLWrapper, JSON

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBpediaEnricher:
    """Fetch and integrate data from DBpedia into Neo4j"""

    def __init__(self, neo4j_conn):
        """
        Initialize DBpedia enricher

        Args:
            neo4j_conn: Neo4jConnection instance
        """
        self.conn = neo4j_conn
        self.dbpedia_endpoint = SPARQLWrapper("https://dbpedia.org/sparql")
        self.dbpedia_endpoint.setReturnFormat(JSON)
        self.dbpedia_endpoint.setTimeout(30)  # 30 second timeout (default is no timeout)
        self.dbpedia_endpoint.addCustomHttpHeader("User-Agent", "EpiHelix/1.0 (Educational Project)")

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
                self.dbpedia_endpoint.setQuery(query)
                results = self.dbpedia_endpoint.query().convert()
                return results
            except Exception as e:
                logger.warning(f"SPARQL query attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"SPARQL query failed after {max_retries} attempts")
                    return None

    def enrich_disease_from_dbpedia(self, disease_name: str, disease_id: str, alternative_names: List[str] = None):
        """
        Fetch disease information from DBpedia

        Args:
            disease_name: Primary disease name (e.g., 'Cholera')
            disease_id: Internal disease ID
            alternative_names: Alternative names to try if primary fails
        """
        logger.info(f"Enriching {disease_name} from DBpedia...")

        # Try primary name first, then alternatives
        names_to_try = [disease_name] + (alternative_names or [])

        for name in names_to_try:
            query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/property/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?disease ?abstract ?wikipedia ?thumbnail
                   ?causativeAgent ?specialty ?prevention
            WHERE {{
              # Find disease by name
              ?disease a dbo:Disease ;
                       rdfs:label "{name}"@en .

              # Get abstract (description)
              OPTIONAL {{ ?disease dbo:abstract ?abstract .
                          FILTER(LANG(?abstract) = "en") }}

              # Get Wikipedia URL
              OPTIONAL {{ ?disease foaf:isPrimaryTopicOf ?wikipedia . }}

              # Get thumbnail image
              OPTIONAL {{ ?disease dbo:thumbnail ?thumbnail . }}

              # Get medical information
              OPTIONAL {{ ?disease dbp:causes ?causativeAgent . }}
              OPTIONAL {{ ?disease dbo:medicalSpecialty ?specialty . }}
              OPTIONAL {{ ?disease dbp:prevention ?prevention . }}
            }}
            LIMIT 5
            """

            results = self._execute_sparql(query)
            if results and results['results']['bindings']:
                # Found results with this name
                break
        else:
            # No results found with any name
            logger.warning(f"No DBpedia results for {disease_name} (tried: {', '.join(names_to_try)})")
            return

        data = results['results']['bindings'][0]

        # Extract data
        enrichment = {
            'dbpedia_uri': data.get('disease', {}).get('value'),
            'abstract': data.get('abstract', {}).get('value'),
            'wikipedia_url': data.get('wikipedia', {}).get('value'),
            'thumbnail_url': data.get('thumbnail', {}).get('value'),
            'causative_agent': data.get('causativeAgent', {}).get('value'),
            'medical_specialty': data.get('specialty', {}).get('value'),
            'prevention': data.get('prevention', {}).get('value')
        }

        # Update Neo4j
        update_query = """
        MATCH (d:Disease {id: $disease_id})
        SET d.dbpediaUri = $dbpedia_uri,
            d.wikipediaAbstract = $abstract,
            d.wikipediaUrl = $wikipedia_url,
            d.thumbnailUrl = $thumbnail_url,
            d.causativeAgent = $causative_agent,
            d.medicalSpecialty = $medical_specialty,
            d.prevention = $prevention,
            d.dbpediaEnriched = true
        """

        self.conn.execute_write(update_query, {
            'disease_id': disease_id,
            **enrichment
        })

        logger.info(f"✓ {disease_name} enriched from DBpedia")

    def enrich_country_demographics(self, country_code: str, country_name: str, dbpedia_uri: str = None):
        """
        Fetch demographic and geographic data from DBpedia

        Args:
            country_code: ISO 3166-1 alpha-3 country code
            country_name: Full country name
            dbpedia_uri: DBpedia resource URI (from Wikidata enrichment, preferred)
        """
        logger.info(f"Enriching country {country_name} ({country_code}) from DBpedia...")

        # If we have the DBpedia URI from Wikidata, use it directly (most reliable)
        if dbpedia_uri:
            query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/property/>

            SELECT DISTINCT ?country ?abstract ?thumbnail ?populationDensity
                   ?governmentType ?currency ?timeZone ?capital ?areaTotal
            WHERE {{
              BIND(<{dbpedia_uri}> AS ?country)

              OPTIONAL {{ ?country dbo:abstract ?abstract .
                          FILTER(LANG(?abstract) = "en") }}
              OPTIONAL {{ ?country dbo:thumbnail ?thumbnail . }}
              OPTIONAL {{ ?country dbo:populationDensity ?populationDensity . }}
              OPTIONAL {{ ?country dbo:governmentType ?governmentType . }}
              OPTIONAL {{ ?country dbo:currency ?currency . }}
              OPTIONAL {{ ?country dbp:timeZone ?timeZone . }}
              OPTIONAL {{ ?country dbo:capital ?capital . }}
              OPTIONAL {{ ?country dbo:areaTotal ?areaTotal . }}
            }}
            LIMIT 1
            """
        else:
            # Fallback: search by country name if no DBpedia URI available
            query = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/property/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT DISTINCT ?country ?abstract ?thumbnail ?populationDensity
                   ?governmentType ?currency ?timeZone ?capital ?areaTotal
            WHERE {{
              ?country a dbo:Country ;
                       rdfs:label "{country_name}"@en .

              OPTIONAL {{ ?country dbo:abstract ?abstract .
                          FILTER(LANG(?abstract) = "en") }}
              OPTIONAL {{ ?country dbo:thumbnail ?thumbnail . }}
              OPTIONAL {{ ?country dbo:populationDensity ?populationDensity . }}
              OPTIONAL {{ ?country dbo:governmentType ?governmentType . }}
              OPTIONAL {{ ?country dbo:currency ?currency . }}
              OPTIONAL {{ ?country dbp:timeZone ?timeZone . }}
              OPTIONAL {{ ?country dbo:capital ?capital . }}
              OPTIONAL {{ ?country dbo:areaTotal ?areaTotal . }}
            }}
            LIMIT 1
            """

        results = self._execute_sparql(query)
        if not results or not results['results']['bindings']:
            logger.warning(f"No DBpedia results for country {country_name} ({country_code})")
            return

        data = results['results']['bindings'][0]

        update_query = """
        MATCH (c:Country {code: $code})
        SET c.dbpediaUri = $dbpedia_uri,
            c.countryAbstract = $abstract,
            c.countryThumbnail = $thumbnail,
            c.populationDensity = $population_density,
            c.governmentType = $government_type,
            c.currency = $currency,
            c.timeZone = $time_zone,
            c.capital = $capital,
            c.areaTotal = $area_total,
            c.dbpediaEnriched = true
        """

        params = {
            'code': country_code,
            'dbpedia_uri': data.get('country', {}).get('value'),
            'abstract': data.get('abstract', {}).get('value'),
            'thumbnail': data.get('thumbnail', {}).get('value'),
            'population_density': float(data.get('populationDensity', {}).get('value', 0)) if 'populationDensity' in data else None,
            'government_type': data.get('governmentType', {}).get('value'),
            'currency': data.get('currency', {}).get('value'),
            'time_zone': data.get('timeZone', {}).get('value'),
            'capital': data.get('capital', {}).get('value'),
            'area_total': float(data.get('areaTotal', {}).get('value', 0)) if 'areaTotal' in data else None
        }

        self.conn.execute_write(update_query, params)
        logger.info(f"✓ Country {country_name} ({country_code}) enriched from DBpedia")

    def add_historical_pandemics(self):
        """
        Query DBpedia for historical pandemic events and add to knowledge graph
        """
        logger.info("Adding historical pandemics from DBpedia...")

        query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

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
        """

        results = self._execute_sparql(query)
        if not results or not results['results']['bindings']:
            logger.warning("No historical pandemic events found in DBpedia")
            return

        count = 0
        for binding in results['results']['bindings']:
            event_uri = binding.get('event', {}).get('value', '')
            event_name = binding.get('eventLabel', {}).get('value', 'Unknown')

            # Create PandemicEvent node
            create_query = """
            MERGE (e:PandemicEvent {dbpediaUri: $uri})
            SET e.name = $name,
                e.abstract = $abstract,
                e.startDate = $start_date,
                e.deathToll = $death_toll,
                e.location = $location,
                e.source = 'DBpedia'
            """

            params = {
                'uri': event_uri,
                'name': event_name,
                'abstract': binding.get('abstract', {}).get('value'),
                'start_date': binding.get('startDate', {}).get('value'),
                'death_toll': binding.get('deathToll', {}).get('value'),
                'location': binding.get('locationLabel', {}).get('value')
            }

            self.conn.execute_write(create_query, params)
            count += 1

        logger.info(f"✓ Added {count} historical pandemic events from DBpedia")

    def enrich_all_hpd_diseases(self):
        """Enrich all HPD diseases from DBpedia"""
        # Disease mappings with alternative names for better DBpedia matching
        disease_mappings = {
            # From disease cases dataset
            'cholera': ('Cholera', []),
            'tuberculosis': ('Tuberculosis', []),
            'malaria': ('Malaria', []),
            'hiv_aids': ('HIV/AIDS', ['AIDS']),
            'polio': ('Poliomyelitis', ['Polio']),
            'rabies': ('Rabies', []),
            'smallpox': ('Smallpox', []),
            'yaws': ('Yaws', ['Framboesia']),
            'guinea_worm': ('Dracunculiasis', ['Guinea worm disease']),

            # From vaccination dataset (vaccine-preventable diseases)
            'diphtheria': ('Diphtheria', []),
            'pertussis': ('Pertussis', ['Whooping cough']),
            'tetanus': ('Tetanus', []),
            'measles': ('Measles', []),
            'hepatitis_b': ('Hepatitis B', []),
            'haemophilus_influenzae': ('Haemophilus influenzae', ['Hib disease']),
            'rotavirus': ('Rotavirus', ['Rotavirus infection']),
            'pneumonia': ('Pneumonia', []),
            'rubella': ('Rubella', ['German measles']),
            'mumps': ('Mumps', []),
            'yellow_fever': ('Yellow fever', []),
            'japanese_encephalitis': ('Japanese encephalitis', []),
            'typhoid': ('Typhoid fever', [])
        }

        # Query database to get existing diseases
        query = "MATCH (d:Disease) RETURN d.id as id"
        existing_diseases = self.conn.execute_query(query)
        existing_disease_ids = {d['id'] for d in existing_diseases}

        logger.info(f"Found {len(existing_disease_ids)} diseases in database")

        enriched_count = 0
        skipped_count = 0

        for disease_id, (disease_name, alternatives) in disease_mappings.items():
            # Only enrich if disease exists in database
            if disease_id not in existing_disease_ids:
                logger.debug(f"Skipping {disease_id} (not in database)")
                skipped_count += 1
                continue

            try:
                self.enrich_disease_from_dbpedia(disease_name, disease_id, alternatives)
                enriched_count += 1
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to enrich {disease_name}: {e}")
                skipped_count += 1

        logger.info(f"✓ DBpedia disease enrichment complete! Enriched: {enriched_count}, Skipped: {skipped_count}")

    def enrich_all_countries(self):
        """Enrich all countries from DBpedia"""
        logger.info("Enriching countries from DBpedia...")

        # Special codes to skip (same as Wikidata enricher)
        SKIP_CODES = {
            'OWID_WRL', 'OWID_YGS', 'OWID_SRM', 'OWID_KOS',
            'OWID_USS', 'OWID_CSK'
        }

        # Get all countries from Neo4j with code, name, and DBpedia URI (if available from Wikidata)
        query = "MATCH (c:Country) RETURN c.code as code, c.name as name, c.dbpediaUri as dbpedia_uri"
        countries = self.conn.execute_query(query)

        enriched_count = 0
        skipped_count = 0
        used_uri_count = 0

        for country in countries:
            country_code = country['code']
            country_name = country['name']
            dbpedia_uri = country.get('dbpedia_uri')

            # Skip special OWID codes
            if country_code in SKIP_CODES:
                logger.debug(f"Skipping {country_code} - special entity")
                skipped_count += 1
                continue

            try:
                if dbpedia_uri:
                    logger.debug(f"Using DBpedia URI from Wikidata: {dbpedia_uri}")
                    used_uri_count += 1
                else:
                    logger.debug(f"No DBpedia URI found, searching by name")

                self.enrich_country_demographics(country_code, country_name, dbpedia_uri)
                enriched_count += 1
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Failed to enrich country {country_name} ({country_code}): {e}")
                skipped_count += 1

        logger.info(f"✓ DBpedia country enrichment complete! Enriched: {enriched_count} ({used_uri_count} via URI), Skipped: {skipped_count}")

    def enrich_all(self):
        """Run all DBpedia enrichment methods"""
        logger.info("=== Starting DBpedia Enrichment ===\n")

        try:
            self.enrich_all_hpd_diseases()
            logger.info("")

            self.add_historical_pandemics()
            logger.info("")

            self.enrich_all_countries()
            logger.info("")

            logger.info("=== ✓ DBpedia enrichment complete! ===")
        except Exception as e:
            logger.error(f"DBpedia enrichment failed: {e}")
            raise


if __name__ == "__main__":
    from neo4j_connection import Neo4jConnection

    # Connect to Neo4j
    conn = Neo4jConnection()
    if not conn.connect():
        exit(1)

    # Run DBpedia enrichment
    enricher = DBpediaEnricher(conn)
    enricher.enrich_all()

    conn.close()
