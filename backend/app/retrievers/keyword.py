"""Keyword retriever using Neo4j full-text search."""

from typing import List, Dict, Any, Optional
import logging

from .base import BaseRetriever
from ..repositories.entity_repository import EntityRepository

logger = logging.getLogger(__name__)


class KeywordRetriever(BaseRetriever):
    """Full-text keyword search retriever.
    
    Uses Neo4j full-text indexes for fast keyword matching.
    
    Features:
    - Full-text search on entity labels and properties
    - Configurable result limit
    - Type filtering (Disease, Country, etc.)
    - Score normalization
    
    Example:
        retriever = KeywordRetriever(entity_repo)
        results = await retriever.retrieve("covid", top_k=10)
    """
    
    def __init__(self, entity_repository: EntityRepository):
        """Initialize keyword retriever.
        
        Args:
            entity_repository: Neo4j repository for entity queries
        """
        self.entity_repo = entity_repository
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Retrieve entities using keyword search.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            **kwargs:
                - filters: Dict[str, Any] - entity type filters
                  Example: {"type": "Disease"}
        
        Returns:
            List of entities with relevance scores
        
        Example:
            results = await retriever.retrieve(
                "malaria",
                top_k=5,
                filters={"type": "Disease"}
            )
        """
        self._validate_query(query)
        
        try:
            # Use repository's search method (full-text index)
            results = await self.entity_repo.search(
                query,
                limit=top_k,
                filters=kwargs.get("filters")
            )
            
            # Normalize and enrich results
            return self._process_results(results)
            
        except Exception as e:
            logger.error(f"Keyword retrieval failed: {e}")
            raise
    
    def _process_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        """Process and normalize results.
        
        Ensures consistent schema:
        - id, label, type (required)
        - score (normalized 0-1)
        - snippet (short description)
        - properties, source (optional)
        """
        processed = []
        
        for entity in results:
            # Extract core fields
            processed_entity = {
                "id": entity.get("id", ""),
                "label": entity.get("label", "Unknown"),
                "type": entity.get("type", "Entity"),
                "score": self._normalize_score(
                    entity.get("score", 1.0),
                    max_score=5.0  # Neo4j full-text scores typically 0-5
                ),
                "snippet": self._generate_snippet(entity),
                "properties": entity.get("properties", {}),
                "source": entity.get("source", "internal")
            }
            
            processed.append(processed_entity)
        
        return processed
    
    def _generate_snippet(self, entity: Dict) -> str:
        """Generate a short description snippet.
        
        Priority:
        1. description property
        2. First few properties
        3. Type-based default
        """
        # Try description field
        props = entity.get("properties", {})
        if "description" in props:
            desc = props["description"]
            return desc[:200] + "..." if len(desc) > 200 else desc
        
        # Build from properties
        snippet_parts = []
        for key, value in list(props.items())[:3]:
            if value and key not in ["id", "label", "type"]:
                snippet_parts.append(f"{key}: {value}")
        
        if snippet_parts:
            return " | ".join(snippet_parts)
        
        # Fallback to type
        entity_type = entity.get("type", "Entity")
        return f"{entity_type} from knowledge graph"
