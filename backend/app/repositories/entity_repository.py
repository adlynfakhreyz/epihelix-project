"""Repository pattern for entity data access.

Following Google's backend best practices:
- Abstract data access from business logic
- Allow switching between KG backends
- Single responsibility principle
"""
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from ..db.kg_client import KnowledgeGraphClient


class EntityRepository(ABC):
    """Abstract repository for entity operations."""
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve entity by ID."""
        pass
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search entities by keyword."""
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
        """Get entity from Neo4j by ID."""
        query = """
        MATCH (e)
        WHERE e.id = $entity_id OR id(e) = toInteger($entity_id)
        RETURN e {
            .id,
            .label,
            .type,
            .summary,
            .*
        } as entity
        LIMIT 1
        """
        results = await self.client.execute_query(query, {"entity_id": entity_id})
        return results[0]["entity"] if results else None
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Full-text search in Neo4j."""
        cypher = """
        CALL db.index.fulltext.queryNodes('entitySearch', $query)
        YIELD node, score
        RETURN node {
            .id,
            .label,
            .type,
            .summary
        } as entity, score
        ORDER BY score DESC
        LIMIT $limit
        """
        results = await self.client.execute_query(
            cypher,
            {"query": query, "limit": limit}
        )
        return [{"score": r["score"], **r["entity"]} for r in results]
    
    async def get_related(self, entity_id: str, max_depth: int = 1) -> List[Dict[str, Any]]:
        """Get related entities via relationships."""
        query = """
        MATCH (e)-[r*1..$max_depth]-(related)
        WHERE e.id = $entity_id
        RETURN DISTINCT related {
            .id,
            .label,
            .type
        } as entity
        LIMIT 50
        """
        results = await self.client.execute_query(
            query,
            {"entity_id": entity_id, "max_depth": max_depth}
        )
        return [r["entity"] for r in results]


class SPARQLEntityRepository(EntityRepository):
    """SPARQL implementation for RDF triple stores."""
    
    def __init__(self, client: KnowledgeGraphClient):
        self.client = client
    
    async def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity from SPARQL endpoint."""
        query = f"""
        PREFIX epi: <https://epihelix.example.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?label ?type ?summary WHERE {{
            <{entity_id}> rdfs:label ?label ;
                         a ?type .
            OPTIONAL {{ <{entity_id}> rdfs:comment ?summary }}
        }}
        LIMIT 1
        """
        results = await self.client.execute_query(query)
        bindings = results.get("results", {}).get("bindings", [])
        if not bindings:
            return None
        
        b = bindings[0]
        return {
            "id": entity_id,
            "label": b.get("label", {}).get("value"),
            "type": b.get("type", {}).get("value"),
            "summary": b.get("summary", {}).get("value")
        }
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search entities via SPARQL."""
        sparql = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?entity ?label ?type WHERE {{
            ?entity rdfs:label ?label ;
                   a ?type .
            FILTER(CONTAINS(LCASE(?label), LCASE("{query}")))
        }}
        LIMIT {limit}
        """
        results = await self.client.execute_query(sparql)
        bindings = results.get("results", {}).get("bindings", [])
        return [
            {
                "id": b["entity"]["value"],
                "label": b["label"]["value"],
                "type": b.get("type", {}).get("value"),
                "score": 1.0
            }
            for b in bindings
        ]
    
    async def get_related(self, entity_id: str, max_depth: int = 1) -> List[Dict[str, Any]]:
        """Get related entities (simplified - single hop)."""
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?related ?label WHERE {{
            <{entity_id}> ?p ?related .
            ?related rdfs:label ?label .
        }}
        LIMIT 50
        """
        results = await self.client.execute_query(query)
        bindings = results.get("results", {}).get("bindings", [])
        return [
            {
                "id": b["related"]["value"],
                "label": b["label"]["value"]
            }
            for b in bindings
        ]


class MockEntityRepository(EntityRepository):
    """Mock repository using in-memory data."""
    
    def __init__(self):
        from .. import mock_data
        self.mock_data = mock_data
    
    async def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity from mock data."""
        entities = self.mock_data.get_entities()
        return entities.get(entity_id)
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search mock entities."""
        ql = query.lower()
        entities = self.mock_data.get_entities()
        results = []
        
        for e in entities.values():
            score = 0.0
            if ql in (e.get("label") or "").lower():
                score += 2.0
            if ql in (e.get("summary") or "").lower():
                score += 1.0
            if score > 0:
                results.append({**e, "score": score})
        
        # Also search snippets
        for s in self.mock_data.search_snippets(query):
            ent = entities.get(s["entity_id"])
            if ent and not any(r["id"] == ent["id"] for r in results):
                results.append({**ent, "score": s.get("score", 0.5)})
        
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:limit]
    
    async def get_related(self, entity_id: str, max_depth: int = 1) -> List[Dict[str, Any]]:
        """Get related entities (simplified for mock)."""
        # In a real implementation, this would traverse relationships
        return []
