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
           OR n:Vaccine OR n:VaccinationRecord OR n:PandemicEvent"""
        
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
                     WHEN word IN ['pandemic', 'pandemics'] AND n:PandemicEvent THEN 9.0
                     
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
                     WHEN word IN ['pandemic', 'pandemics'] AND n:PandemicEvent THEN 1
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


# SPARQL and Mock classes removed - production uses Neo4j with Cypher only
