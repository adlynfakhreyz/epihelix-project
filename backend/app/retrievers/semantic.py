"""Semantic retriever using vector embeddings."""

from typing import List, Dict, Any, Optional
import logging
import numpy as np

from .base import BaseRetriever
from ..repositories.entity_repository import EntityRepository
from ..utils.embedder import BaseEmbedder  # ✅ Fixed import path

logger = logging.getLogger(__name__)


class SemanticRetriever(BaseRetriever):
    """Vector-based semantic search retriever.
    
    Uses text embeddings to find semantically similar entities.
    
    Process:
    1. Embed the query
    2. Get candidate entities (keyword pre-filter for performance)
    3. Embed candidate labels
    4. Compute cosine similarity
    5. Return top-k results
    
    Features:
    - Semantic similarity (understands meaning, not just keywords)
    - Configurable candidate pool size
    - Cosine similarity scoring
    
    Example:
        embedder = KaggleEmbedder(...)
        retriever = SemanticRetriever(entity_repo, embedder)
        results = await retriever.retrieve("respiratory disease", top_k=10)
    """
    
    def __init__(
        self,
        entity_repository: EntityRepository,
        embedder: BaseEmbedder,
        candidate_pool_size: int = 100
    ):
        """Initialize semantic retriever.
        
        Args:
            entity_repository: Neo4j repository for entity queries
            embedder: Embedding utility (KaggleEmbedder)
            candidate_pool_size: Max candidates to embed (performance tuning)
        """
        self.entity_repo = entity_repository
        self.embedder = embedder
        self.candidate_pool_size = candidate_pool_size
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Retrieve entities using semantic similarity.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            **kwargs:
                - filters: Dict[str, Any] - entity type filters
                - candidate_pool_size: int - override default candidate pool
        
        Returns:
            List of entities ranked by semantic similarity
        
        Example:
            results = await retriever.retrieve(
                "infectious diseases in Africa",
                top_k=5
            )
        """
        self._validate_query(query)
        
        try:
            # Override candidate pool size if provided
            pool_size = kwargs.get("candidate_pool_size", self.candidate_pool_size)
            
            # Step 1: Embed query
            query_embedding = await self.embedder.embed_text(query)
            
            # Step 2: Get candidates (keyword pre-filter for performance)
            # This reduces embedding computation from all entities to top-100
            candidates = await self.entity_repo.search(
                query,
                limit=pool_size,
                filters=kwargs.get("filters")
            )
            
            if not candidates:
                logger.warning(f"No candidates found for query: {query}")
                return []
            
            # Step 3: Embed candidate labels
            candidate_texts = [e.get("label", "") for e in candidates]
            candidate_embeddings = await self.embedder.embed_batch(candidate_texts)
            
            # Step 4: Compute cosine similarity
            similar_indices = self._find_similar(
                query_embedding,
                candidate_embeddings,
                top_k=top_k
            )
            
            # Step 5: Build results with similarity scores
            results = []
            for idx, score in similar_indices:
                entity = candidates[idx].copy()
                entity["score"] = score
                entity["snippet"] = self._generate_snippet(entity)
                results.append(entity)
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic retrieval failed: {e}")
            raise
    
    def _find_similar(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        top_k: int
    ) -> List[tuple]:
        """Find most similar candidates using cosine similarity.
        
        Args:
            query_embedding: Query vector
            candidate_embeddings: Candidate vectors
            top_k: Number of results
        
        Returns:
            List of (index, score) tuples sorted by similarity
        """
        query_vec = np.array(query_embedding)
        candidate_vecs = np.array(candidate_embeddings)
        
        # Cosine similarity: dot product of normalized vectors
        similarities = np.dot(candidate_vecs, query_vec) / (
            np.linalg.norm(candidate_vecs, axis=1) * np.linalg.norm(query_vec)
        )
        
        # Get top-k indices (highest similarity first)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [(int(idx), float(similarities[idx])) for idx in top_indices]
    
    def _generate_snippet(self, entity: Dict) -> str:
        """Generate description snippet."""
        props = entity.get("properties", {})
        
        # Try description field
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
        
        # Fallback
        return f"{entity.get('type', 'Entity')} from knowledge graph"
