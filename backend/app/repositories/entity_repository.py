"""Repository pattern for entity data access.

Following Google's backend best practices:
- Abstract data access from business logic
- Allow switching between KG backends
- Single responsibility principle
"""
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from datetime import datetime, date, time
import logging

from ..db.kg_client import KnowledgeGraphClient

logger = logging.getLogger(__name__)


def serialize_neo4j_types(value: Any) -> Any:
    """
    Convert Neo4j-specific types to JSON-serializable Python types.
    
    Handles:
    - neo4j.time.Date → string (ISO format)
    - neo4j.time.DateTime → string (ISO format)
    - neo4j.time.Time → string (ISO format)
    - neo4j.spatial.Point → dict with latitude/longitude
    - Node → dict of properties
    - Relationship → dict of properties
    - Lists and nested structures
    """
    # None and primitives
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    
    # Python datetime objects
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    
    # Neo4j temporal types (have iso_format method)
    if hasattr(value, 'iso_format'):
        return value.iso_format()
    
    # Neo4j Date/DateTime/Time (alternative check)
    type_name = type(value).__name__
    if type_name in ('Date', 'DateTime', 'Time', 'Duration'):
        return str(value)
    
    # Neo4j Point (spatial)
    if hasattr(value, 'latitude') and hasattr(value, 'longitude'):
        return {
            'latitude': value.latitude,
            'longitude': value.longitude
        }
    
    # Neo4j Node
    if hasattr(value, 'labels') and hasattr(value, 'items'):
        return {k: serialize_neo4j_types(v) for k, v in dict(value).items()}
    
    # Neo4j Relationship
    if hasattr(value, 'type') and hasattr(value, 'items'):
        return {k: serialize_neo4j_types(v) for k, v in dict(value).items()}
    
    # Lists
    if isinstance(value, list):
        return [serialize_neo4j_types(item) for item in value]
    
    # Dicts
    if isinstance(value, dict):
        return {k: serialize_neo4j_types(v) for k, v in value.items()}
    
    # Fallback: convert to string
    return str(value)


class EntityRepository(ABC):
    """Abstract repository for entity operations."""
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve entity by ID."""
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search entities by keyword with optional filters.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            filters: Optional filters (e.g., {"type": "Disease"})
        """
        pass
    
    @abstractmethod
    async def get_related(self, entity_id: str, max_depth: int = 1) -> List[Dict[str, Any]]:
        """Get entities related to given entity."""
        pass

    @abstractmethod
    async def get_by_type(
        self,
        entity_type: str,
        search: str = "",
        sort_by: str = "name",
        limit: int = 1000,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get all entities of a specific type with optional search and sorting."""
        pass

    @abstractmethod
    async def get_countries_for_entity(
        self,
        entity_id: str,
        data_type: str = "outbreaks"
    ) -> List[Dict[str, Any]]:
        """Get list of countries that have data for a specific entity (disease)."""
        pass

    @abstractmethod
    async def get_timeseries_data(
        self,
        entity_id: str,
        data_type: str = "outbreaks",
        countries: List[str] = None,
        year_start: int = None,
        year_end: int = None,
        aggregation: str = "country"
    ) -> List[Dict[str, Any]]:
        """Get time-series data for outbreaks or vaccinations."""
        pass

    @abstractmethod
    async def get_heatmap_data(
        self,
        disease_id: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get heatmap data for world map visualization."""
        pass


class Neo4jEntityRepository(EntityRepository):
    """Neo4j implementation of entity repository."""
    
    def __init__(self, client: KnowledgeGraphClient):
        self.client = client
    
    async def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get entity from Neo4j by elementId with full properties and relations.
        
        Returns entity with:
        - id: Entity elementId (Neo4j internal ID)
        - label: Display name
        - type: Node label (Disease, Country, Outbreak, etc.)
        - properties: All node properties as dict
        - relations: Array of {predicate, object} relationships
        """
        # Query to get node with all properties using elementId
        query = """
        MATCH (e)
        WHERE elementId(e) = $entity_id
        
        // Get all properties
        WITH e, labels(e) as nodeLabels, properties(e) as props
        
        // Get all relationships
        OPTIONAL MATCH (e)-[r]->(related)
        WITH e, nodeLabels, props, 
             collect(DISTINCT {
                 predicate: type(r),
                 direction: 'outgoing',
                 object: {
                     id: elementId(related),
                     label: COALESCE(related.name, related.label, related.id, related.code, elementId(related)),
                     type: head(labels(related))
                 }
             }) as outgoing
        
        OPTIONAL MATCH (e)<-[r2]-(related2)
        WITH e, nodeLabels, props, outgoing,
             collect(DISTINCT {
                 predicate: type(r2),
                 direction: 'incoming',
                 object: {
                     id: elementId(related2),
                     label: COALESCE(related2.name, related2.label, related2.id, related2.code, elementId(related2)),
                     type: head(labels(related2))
                 }
             }) as incoming
        
        RETURN {
            id: elementId(e),
            label: COALESCE(e.name, e.label, e.id, e.code, elementId(e)),
            type: head(nodeLabels),
            properties: props,
            relations: outgoing + incoming
        } as entity
        LIMIT 1
        """
        
        results = await self.client.execute_query(query, {"entity_id": entity_id})
        
        if not results or not results[0].get("entity"):
            return None
        
        entity = results[0]["entity"]
        
        # Serialize all Neo4j types to JSON-compatible Python types
        entity = serialize_neo4j_types(entity)
        
        # Filter out null relations and clean up
        if entity.get("relations"):
            entity["relations"] = [
                r for r in entity["relations"]
                if r.get("object") and r["object"].get("id")
            ]
        
        return entity
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Production-grade keyword search with multi-word support.
        
        Industry best practices:
        1. Create searchable text from all properties (searchText)
        2. Use Cypher pattern matching with scoring weights
        3. Handle multi-word queries efficiently in Cypher
        4. Deduplicate and rank by relevance
        
        Multi-word strategy:
        - "covid vaccine" searches for entities containing BOTH words
        - Uses AND logic + proximity scoring
        - Handles partial matches gracefully
        
        Args:
            query: Search query string
            limit: Maximum number of results
            filters: Optional filters (e.g., {"type": "Disease"})
        """
        filters = filters or {}
        query_lower = query.lower().strip()
        words = [w for w in query_lower.split() if len(w) > 0]
        
        # Build WHERE clause based on filters
        if filters.get("type"):
            # Filter by specific type
            type_filter = f"WHERE n:{filters['type']}"
        else:
            # Default: search all entity types
            type_filter = """WHERE n:Country OR n:Disease OR n:Outbreak OR n:Organization 
           OR n:Vaccine OR n:VaccinationRecord"""
        
        # Comprehensive search with efficient multi-word handling
        cypher = f"""
        MATCH (n)
        {type_filter}
        
        // Build searchable text from all important properties
        WITH n,
             toLower(COALESCE(n.name, '') + ' ' + 
                     COALESCE(n.fullName, '') + ' ' +
                     COALESCE(n.id, '') + ' ' +
                     COALESCE(n.label, '') + ' ' +
                     COALESCE(n.code, '') + ' ' +
                     COALESCE(n.description, '') + ' ' +
                     COALESCE(n.wikipediaAbstract, '') + ' ' +
                     COALESCE(n.category, '') + ' ' +
                     COALESCE(n.icd10, '') + ' ' +
                     COALESCE(n.mesh, '') + ' ' +
                     COALESCE(n.continent, '') + ' ' +
                     COALESCE(n.capital, '') + ' ' +
                     COALESCE(n.acronym, '') + ' ' +
                     COALESCE(n.vaccineName, '') + ' ' +
                     COALESCE(n.manufacturer, '') + ' ' +
                     COALESCE(n.role, '') + ' ' +
                     COALESCE(toString(n.year), '') + ' ' +
                     // Arrays as space-separated strings
                     REDUCE(s = '', x IN COALESCE(n.symptoms, []) | s + ' ' + x) + ' ' +
                     REDUCE(s = '', x IN COALESCE(n.drugs, []) | s + ' ' + x) + ' ' +
                     REDUCE(s = '', x IN COALESCE(n.treatments, []) | s + ' ' + x) + ' ' +
                     REDUCE(s = '', x IN COALESCE(n.possibleTreatments, []) | s + ' ' + x) + ' ' +
                     REDUCE(s = '', x IN COALESCE(n.transmissionMethods, []) | s + ' ' + x) + ' ' +
                     REDUCE(s = '', x IN COALESCE(n.riskFactors, []) | s + ' ' + x)
             ) as searchText
        
        // Multi-word scoring: each word must appear, sum up individual scores
        WITH n, searchText,
             REDUCE(totalScore = 0.0, word IN $words |
                 totalScore + CASE
                     // Exact entity type match
                     WHEN word IN ['disease', 'diseases'] AND n:Disease THEN 9.0
                     WHEN word IN ['country', 'countries'] AND n:Country THEN 9.0
                     WHEN word IN ['outbreak', 'outbreaks'] AND n:Outbreak THEN 9.0
                     WHEN word IN ['vaccine', 'vaccines'] AND n:Vaccine THEN 9.0
                     WHEN word IN ['vaccination', 'vaccinations'] AND n:VaccinationRecord THEN 9.0
                     WHEN word IN ['organization', 'organisations'] AND n:Organization THEN 9.0

                     
                     // Exact property matches (highest value)
                     WHEN toLower(COALESCE(n.name, '')) = word THEN 10.0
                     WHEN toLower(COALESCE(n.id, '')) = word THEN 10.0
                     WHEN toLower(COALESCE(n.code, '')) = word THEN 10.0
                     
                     // Property starts with word (high value)
                     WHEN toLower(COALESCE(n.name, '')) STARTS WITH word THEN 8.0
                     WHEN toLower(COALESCE(n.fullName, '')) STARTS WITH word THEN 8.0
                     WHEN toLower(COALESCE(n.id, '')) STARTS WITH word THEN 7.0
                     
                     // Word appears in searchText (main matching)
                     WHEN searchText CONTAINS word THEN 
                         CASE
                             // Boost if in high-priority fields
                             WHEN toLower(COALESCE(n.name, '')) CONTAINS word THEN 6.0
                             WHEN toLower(COALESCE(n.fullName, '')) CONTAINS word THEN 6.0
                             WHEN toLower(COALESCE(n.icd10, '')) CONTAINS word THEN 7.0
                             WHEN toLower(COALESCE(n.mesh, '')) CONTAINS word THEN 7.0
                             WHEN toLower(COALESCE(n.vaccineName, '')) CONTAINS word THEN 6.0
                             WHEN toLower(COALESCE(n.acronym, '')) CONTAINS word THEN 6.0
                             // Arrays
                             WHEN ANY(x IN COALESCE(n.symptoms, []) WHERE toLower(x) CONTAINS word) THEN 5.5
                             WHEN ANY(x IN COALESCE(n.drugs, []) WHERE toLower(x) CONTAINS word) THEN 5.5
                             WHEN ANY(x IN COALESCE(n.treatments, []) WHERE toLower(x) CONTAINS word) THEN 5.5
                             WHEN ANY(x IN COALESCE(n.possibleTreatments, []) WHERE toLower(x) CONTAINS word) THEN 5.5
                             // Descriptions and other fields
                             WHEN toLower(COALESCE(n.description, '')) CONTAINS word THEN 4.0
                             WHEN toLower(COALESCE(n.wikipediaAbstract, '')) CONTAINS word THEN 4.0
                             ELSE 3.0  // Found in searchText but lower priority field
                         END
                     ELSE 0.0  // Word not found
                 END
             ) as match_score,
             // Count how many query words matched (including entity type matches)
             REDUCE(matchCount = 0, word IN $words |
                 matchCount + CASE 
                     // Entity type matches
                     WHEN word IN ['disease', 'diseases'] AND n:Disease THEN 1
                     WHEN word IN ['country', 'countries'] AND n:Country THEN 1
                     WHEN word IN ['outbreak', 'outbreaks'] AND n:Outbreak THEN 1
                     WHEN word IN ['vaccine', 'vaccines'] AND n:Vaccine THEN 1
                     WHEN word IN ['vaccination', 'vaccinations'] AND n:VaccinationRecord THEN 1
                     WHEN word IN ['organization', 'organisations'] AND n:Organization THEN 1

                     // Text matches
                     WHEN searchText CONTAINS word THEN 1 
                     ELSE 0 
                 END
             ) as words_matched
        
        // Filter: Must match at least one word (OR logic)
        // Multi-word matches will naturally score higher
        WHERE match_score > 0
        
        // Boost multi-word matches where words appear close together
        WITH n, match_score, words_matched,
             CASE 
                 WHEN size($words) > 1 AND searchText CONTAINS $fullQuery 
                 THEN match_score * 1.5  // Exact phrase bonus
                 ELSE match_score
             END as final_score
        
        // Create entity representation
        WITH n, final_score,
        CASE 
            WHEN n:Disease THEN COALESCE(n.fullName, n.name, n.id)
            WHEN n:Country THEN COALESCE(n.name, n.code)
            WHEN n:Organization THEN COALESCE(n.name, n.acronym)
            WHEN n:Vaccine THEN COALESCE(n.name, n.vaccineName, n.label)
            WHEN n:Outbreak THEN COALESCE(n.id, n.label)
            WHEN n:VaccinationRecord THEN COALESCE(n.name, n.label, n.id, n.code)
            WHEN n:PandemicEvent THEN COALESCE(n.name, n.label, n.title)
            ELSE COALESCE(n.name, n.label, n.title, n.id)
        END as entity_label,
        CASE 
            WHEN n:Disease THEN 
                CASE WHEN size(COALESCE(n.symptoms, [])) > 0 
                     THEN 'Symptoms: ' + REDUCE(s = '', x IN n.symptoms[..3] | 
                          s + CASE WHEN s <> '' THEN ', ' ELSE '' END + x)
                     ELSE COALESCE(substring(n.description, 0, 150), '') END
            WHEN n:Country THEN 
                COALESCE(n.continent, '') + 
                CASE WHEN n.capital IS NOT NULL THEN ' | Capital: ' + n.capital ELSE '' END
            WHEN n:Organization THEN COALESCE(n.role, '')
            WHEN n:Vaccine THEN COALESCE('Manufacturer: ' + n.manufacturer, '')
            WHEN n:Outbreak THEN 
                CASE WHEN n.cases IS NOT NULL THEN toString(n.cases) + ' cases' ELSE '' END +
                CASE WHEN n.deaths IS NOT NULL THEN ', ' + toString(n.deaths) + ' deaths' ELSE '' END
            ELSE COALESCE(substring(n.description, 0, 150), '')
        END as entity_snippet
        
        // Return matched entities
        RETURN {{
            id: elementId(n),
            label: entity_label,
            type: head(labels(n)),
            snippet: entity_snippet,
            match_type: 'direct',
            properties: properties(n)
        }} as entity, final_score as score
        
        ORDER BY score DESC, entity_label ASC
        LIMIT $limit
        """
        
        try:
            results = await self.client.execute_query(
                cypher,
                {
                    "words": words,
                    "fullQuery": query_lower,  # For exact phrase matching
                    "limit": limit
                }
            )
            
            logger.debug(f"Keyword search for '{query}' ({len(words)} words) returned {len(results)} results")
            
            # Flatten structure and filter embedding property
            clean_results = []
            for r in results:
                entity = r.get('entity', {})
                score = r.get('score', 0)
                
                # Filter out embedding from properties
                if entity and entity.get('properties'):
                    props = entity['properties'].copy()
                    if 'embedding' in props:
                        del props['embedding']
                    entity['properties'] = props
                
                # Flatten structure: merge entity fields with score at top level
                flattened = {
                    'score': score,
                    **entity  # Spread entity fields (id, label, type, snippet, properties)
                }
                clean_results.append(flattened)
            
            logger.info(f"✓ Returned {len(clean_results)} results after filtering")
            return clean_results
            
        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            return []
    
    async def get_related(self, entity_id: str, max_depth: int = 1) -> List[Dict[str, Any]]:
        """Get related entities via relationships."""
        # Build query with literal max_depth (Neo4j doesn't allow params in relationship patterns)
        query = f"""
        MATCH (e)-[r*1..{max_depth}]-(related)
        WHERE elementId(e) = $entity_id
        RETURN DISTINCT {{
            id: elementId(related),
            label: COALESCE(related.name, related.label, related.id, related.code, elementId(related)),
            type: head(labels(related))
        }} as entity
        LIMIT 50
        """
        results = await self.client.execute_query(
            query,
            {"entity_id": entity_id}
        )

        # Serialize results
        return [serialize_neo4j_types(r["entity"]) for r in results]

    async def get_by_type(
        self,
        entity_type: str,
        search: str = "",
        sort_by: str = "name",
        limit: int = 1000,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get all entities of a specific type with optional search and sorting.

        Used by the entity browser to list entities by type.
        
        Args:
            entity_type: Type of entity (country, disease, etc.)
            search: Search query string
            sort_by: Field to sort by (name or id)
            limit: Maximum number of results
            filters: Dictionary of property filters (e.g., {"continent": "Asia"})
        """
        filters = filters or {}
        
        # Map frontend type names to Neo4j labels
        type_mapping = {
            "country": "Country",
            "disease": "Disease",
            "outbreak": "Outbreak",
            "vaccinationrecord": "VaccinationRecord",
            "organization": "Organization",
            "vaccine": "Vaccine",
            "pandemicevent": "PandemicEvent"
        }

        neo4j_label = type_mapping.get(entity_type.lower(), entity_type)

        # Build search condition
        search_condition = ""
        if search:
            search_lower = search.lower()
            search_condition = """
            AND (
                toLower(COALESCE(n.name, '')) CONTAINS $search
                OR toLower(COALESCE(n.fullName, '')) CONTAINS $search
                OR toLower(COALESCE(n.label, '')) CONTAINS $search
                OR toLower(COALESCE(n.id, '')) CONTAINS $search
                OR toLower(COALESCE(n.code, '')) CONTAINS $search
                OR toLower(COALESCE(n.description, '')) CONTAINS $search
            )
            """

        # Build property filter conditions
        filter_conditions = []
        filter_params = {}
        for key, value in filters.items():
            if value:  # Only add non-empty filters
                param_name = f"filter_{key}"
                # Handle boolean filters
                if value in ['true', 'false']:
                    filter_conditions.append(f"n.{key} = ${param_name}")
                    filter_params[param_name] = (value == 'true')
                else:
                    # String filters - exact match
                    filter_conditions.append(f"n.{key} = ${param_name}")
                    filter_params[param_name] = value
        
        filter_clause = ""
        if filter_conditions:
            filter_clause = "AND " + " AND ".join(filter_conditions)

        # Build sort expression
        if sort_by == "id":
            sort_expr = "COALESCE(n.id, n.code, elementId(n))"
        else:  # default to name
            sort_expr = "COALESCE(n.name, n.fullName, n.label, n.id, n.code, elementId(n))"

        query = f"""
        MATCH (n:{neo4j_label})
        WHERE 1=1 {search_condition} {filter_clause}

        WITH n, {sort_expr} as sortValue

        RETURN {{
            id: elementId(n),
            label: COALESCE(n.name, n.id, n.code, elementId(n)),
            type: head(labels(n)),
            description: COALESCE(n.description, n.wikipediaAbstract, ''),
            properties: properties(n)
        }} as entity

        ORDER BY sortValue ASC
        LIMIT $limit
        """

        params = {"limit": limit, **filter_params}
        if search:
            params["search"] = search.lower()

        try:
            results = await self.client.execute_query(query, params)

            # Serialize and clean up results
            clean_results = []
            for r in results:
                entity = serialize_neo4j_types(r.get('entity', {}))

                # Remove embedding from properties
                if entity.get('properties') and 'embedding' in entity['properties']:
                    del entity['properties']['embedding']

                clean_results.append(entity)

            logger.info(f"Retrieved {len(clean_results)} entities of type {entity_type} with filters {filters}")
            return clean_results

        except Exception as e:
            logger.error(f"Error getting entities by type {entity_type}: {e}", exc_info=True)
            return []

    async def get_countries_for_entity(
        self,
        entity_id: str,
        data_type: str = "outbreaks"
    ) -> List[Dict[str, Any]]:
        """Get list of countries that have outbreak or vaccination data for a specific disease.

        Args:
            entity_id: Disease entity ID (element ID)
            data_type: 'outbreaks' or 'vaccinations'

        Returns:
            List of countries with code and name
        """
        if data_type == "outbreaks":
            # Get countries with outbreak data for this disease
            query = """
            MATCH (d:Disease)
            WHERE elementId(d) = $entity_id
            MATCH (o:Outbreak)-[:CAUSED_BY]->(d)
            MATCH (o)-[:OCCURRED_IN]->(c:Country)
            RETURN DISTINCT c.code as code, c.name as name
            ORDER BY c.name
            """
        else:  # vaccinations
            # Get countries with vaccination data for this disease
            query = """
            MATCH (d:Disease)
            WHERE elementId(d) = $entity_id
            MATCH (v:VaccinationRecord)-[:PREVENTS]->(d)
            MATCH (v)-[:ADMINISTERED_IN]->(c:Country)
            RETURN DISTINCT c.code as code, c.name as name
            ORDER BY c.name
            """

        try:
            results = await self.client.execute_query(query, {"entity_id": entity_id})

            countries = [
                {"code": r["code"], "name": r["name"]}
                for r in results
                if r.get("code") and r.get("name")
            ]

            logger.info(f"Found {len(countries)} countries with {data_type} data for entity {entity_id}")
            return countries

        except Exception as e:
            logger.error(f"Error getting countries for entity {entity_id}: {e}", exc_info=True)
            return []

    async def get_timeseries_data(
        self,
        entity_id: str,
        data_type: str = "outbreaks",
        countries: List[str] = None,
        year_start: int = None,
        year_end: int = None,
        aggregation: str = "country"
    ) -> List[Dict[str, Any]]:
        """Get time-series data for outbreaks or vaccinations.

        Args:
            entity_id: Disease entity ID (element ID)
            data_type: 'outbreaks' or 'vaccinations'
            countries: List of country codes to filter by (None = all)
            year_start: Start year for filtering
            year_end: End year for filtering
            aggregation: 'country' or 'total'

        Returns:
            List of time-series data points
        """
        # Build country filter
        country_filter = ""
        if countries and len(countries) > 0 and not (len(countries) == 1 and countries[0] == "ALL"):
            country_filter = "AND c.code IN $countries"

        # Build year filter for outbreaks
        outbreak_year_filter = ""
        if year_start is not None:
            outbreak_year_filter += f" AND o.year >= {year_start}"
        if year_end is not None:
            outbreak_year_filter += f" AND o.year <= {year_end}"

        # Build year filter for vaccinations
        vaccination_year_filter = ""
        if year_start is not None:
            vaccination_year_filter += f" AND v.year >= {year_start}"
        if year_end is not None:
            vaccination_year_filter += f" AND v.year <= {year_end}"

        if data_type == "outbreaks":
            # Query outbreak data
            if aggregation == "total":
                # Aggregate across all countries by year
                query = f"""
                MATCH (d:Disease)
                WHERE elementId(d) = $entity_id
                MATCH (o:Outbreak)-[:CAUSED_BY]->(d)
                MATCH (o)-[:OCCURRED_IN]->(c:Country)
                WHERE o.year IS NOT NULL {country_filter} {outbreak_year_filter}
                WITH o.year as year, 
                     sum(COALESCE(o.cases, o.confirmedDeaths, o.excessDeaths, o.deaths, 0)) as totalCases
                RETURN year, totalCases as cases
                ORDER BY year
                """
            else:
                # By country
                query = f"""
                MATCH (d:Disease)
                WHERE elementId(d) = $entity_id
                MATCH (o:Outbreak)-[:CAUSED_BY]->(d)
                MATCH (o)-[:OCCURRED_IN]->(c:Country)
                WHERE o.year IS NOT NULL {country_filter} {outbreak_year_filter}
                RETURN o.year as year, c.code as countryCode, c.name as country, 
                       COALESCE(o.cases, o.confirmedDeaths, o.excessDeaths, o.deaths) as cases
                ORDER BY year, country
                """
        else:  # vaccinations
            # Query vaccination data
            if aggregation == "total":
                # Average coverage across all countries by year
                query = f"""
                MATCH (d:Disease)
                WHERE elementId(d) = $entity_id
                MATCH (v:VaccinationRecord)-[:PREVENTS]->(d)
                MATCH (v)-[:ADMINISTERED_IN]->(c:Country)
                WHERE v.year IS NOT NULL {country_filter} {vaccination_year_filter}
                WITH v.year as year, avg(v.coveragePercent) as avgCoverage
                RETURN year, avgCoverage as coveragePercent
                ORDER BY year
                """
            else:
                # By country
                query = f"""
                MATCH (d:Disease)
                WHERE elementId(d) = $entity_id
                MATCH (v:VaccinationRecord)-[:PREVENTS]->(d)
                MATCH (v)-[:ADMINISTERED_IN]->(c:Country)
                WHERE v.year IS NOT NULL {country_filter} {vaccination_year_filter}
                RETURN v.year as year, c.code as countryCode, c.name as country,
                       v.coveragePercent as coveragePercent
                ORDER BY year, country
                """

        params = {"entity_id": entity_id}
        if countries and len(countries) > 0 and not (len(countries) == 1 and countries[0] == "ALL"):
            params["countries"] = countries

        try:
            results = await self.client.execute_query(query, params)

            # Serialize and format results
            data = []
            for r in results:
                point = serialize_neo4j_types(r)
                # Add period field (used by frontend charts)
                if "year" in point:
                    point["period"] = str(point["year"])
                data.append(point)

            logger.info(f"Retrieved {len(data)} time-series data points for entity {entity_id}")
            return data

        except Exception as e:
            logger.error(f"Error getting timeseries data for entity {entity_id}: {e}", exc_info=True)
            return []

    async def get_heatmap_data(
        self,
        disease_id: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get heatmap data for world map visualization.
        
        Returns country-level outbreak data with geographic coordinates.
        """
        try:
            # First, get disease info
            disease_query = """
            MATCH (d:Disease)
            WHERE elementId(d) = $disease_id
            RETURN d.name as diseaseName, d.id as diseaseCode
            """
            disease_result = await self.client.execute_query(disease_query, {"disease_id": disease_id})
            
            if not disease_result:
                logger.warning(f"Disease not found: {disease_id}")
                return {
                    "countries": [],
                    "availableYears": [],
                    "selectedYear": None,
                    "diseaseName": "Unknown"
                }
            
            disease_name = disease_result[0].get("diseaseName", "Unknown")
            
            # Get available years
            years_query = """
            MATCH (d:Disease)
            WHERE elementId(d) = $disease_id
            MATCH (o:Outbreak)-[:CAUSED_BY]->(d)
            WHERE o.year IS NOT NULL
            RETURN DISTINCT o.year as year
            ORDER BY year DESC
            """
            years_result = await self.client.execute_query(years_query, {"disease_id": disease_id})
            available_years = sorted([r["year"] for r in years_result if r.get("year")], reverse=True)
            
            # Determine year to use
            selected_year = year if year else (available_years[0] if available_years else None)
            
            if not selected_year:
                return {
                    "countries": [],
                    "availableYears": [],
                    "selectedYear": None,
                    "diseaseName": disease_name
                }
            
            # Get country data for the selected year
            data_query = """
            MATCH (d:Disease)
            WHERE elementId(d) = $disease_id
            MATCH (o:Outbreak)-[:CAUSED_BY]->(d)
            MATCH (o)-[:OCCURRED_IN]->(c:Country)
            WHERE o.year = $year
            WITH c, 
                 sum(COALESCE(o.cases, o.confirmedDeaths, o.excessDeaths, o.deaths, 0)) as totalCases,
                 sum(COALESCE(o.deaths, o.confirmedDeaths, o.excessDeaths, 0)) as totalDeaths
            WHERE totalCases > 0 OR totalDeaths > 0
            RETURN c.code as countryCode,
                   c.name as countryName,
                   totalCases as cases,
                   totalDeaths as deaths,
                   c.latitude as latitude,
                   c.longitude as longitude
            ORDER BY totalCases DESC
            """
            
            params = {
                "disease_id": disease_id,
                "year": selected_year
            }
            
            results = await self.client.execute_query(data_query, params)
            
            # Serialize and format
            countries = []
            for r in results:
                country_data = serialize_neo4j_types(r)
                countries.append({
                    "countryCode": country_data.get("countryCode"),
                    "countryName": country_data.get("countryName"),
                    "cases": int(country_data.get("cases", 0)),
                    "deaths": int(country_data.get("deaths", 0)) if country_data.get("deaths") else None,
                    "latitude": float(country_data.get("latitude")) if country_data.get("latitude") else None,
                    "longitude": float(country_data.get("longitude")) if country_data.get("longitude") else None
                })
            
            logger.info(f"Retrieved heatmap data for {disease_name} in {selected_year}: {len(countries)} countries")
            
            return {
                "countries": countries,
                "availableYears": available_years,
                "selectedYear": selected_year,
                "diseaseName": disease_name
            }
            
        except Exception as e:
            logger.error(f"Error getting heatmap data: {e}", exc_info=True)
            return {
                "countries": [],
                "availableYears": [],
                "selectedYear": None,
                "diseaseName": "Error"
            }


# SPARQL and Mock classes removed - production uses Neo4j with Cypher only
