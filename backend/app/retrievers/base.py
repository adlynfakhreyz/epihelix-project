"""Base retriever interface for knowledge graph queries."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseRetriever(ABC):
    """Abstract retriever interface.
    
    Following LangChain's BaseRetriever pattern:
    - Simple retrieve() method
    - Returns list of documents (entities)
    - Configurable top_k
    - Can be wrapped for LangChain integration
    
    Design:
    - Retriever = query strategy layer
    - No business logic (just query execution)
    - No orchestration (router handles that)
    """
    
    @abstractmethod
    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant entities from knowledge graph.
        
        Args:
            query: User query string
            top_k: Number of results to return
            **kwargs: Additional retriever-specific parameters
                - filters: Dict[str, Any] - entity type filters
                - min_score: float - minimum relevance score
        
        Returns:
            List of entity dictionaries with schema:
            {
                "id": str,           # Entity ID
                "label": str,        # Display name
                "type": str,         # Entity type (Disease, Country, etc.)
                "score": float,      # Relevance score (0-1)
                "snippet": str,      # Short description
                "properties": dict,  # Additional properties
                "source": str        # Data source
            }
        
        Raises:
            ValueError: If query is empty or invalid
            Exception: If retrieval fails
        """
        pass
    
    def _validate_query(self, query: str) -> None:
        """Validate query input."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
    
    def _normalize_score(self, raw_score: float, max_score: float = 1.0) -> float:
        """Normalize score to 0-1 range."""
        if max_score <= 0:
            return 0.0
        return min(1.0, max(0.0, raw_score / max_score))
