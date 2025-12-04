"""Service layer for search logic.

Business logic for search including:
- Keyword search (repository)
- Semantic search (embeddings + vector similarity)
- Hybrid search (keyword + semantic)
- Suggestions

Following separation of concerns and dependency injection.
"""
from typing import List, Dict, Optional
from ..repositories.entity_repository import EntityRepository
from .embedder_service import EmbedderService


class SearchService:
    """Search service with semantic capabilities."""
    
    def __init__(
        self,
        entity_repository: EntityRepository,
        embedder_service: Optional[EmbedderService] = None
    ):
        """Initialize search service.
        
        Args:
            entity_repository: Data access layer for entities
            embedder_service: Optional embedder for semantic search
        """
        self.entity_repo = entity_repository
        self.embedder = embedder_service
    
    async def search_entities(
        self,
        q: str,
        limit: int = 10,
        semantic: bool = False
    ) -> List[Dict]:
        """Search entities (keyword or semantic).
        
        Args:
            q: Search query
            limit: Max results
            semantic: Use semantic search if True
        """
        if semantic and self.embedder:
            return await self.semantic_search(q, limit=limit)
        else:
            return await self.keyword_search(q, limit=limit)
    
    async def keyword_search(self, q: str, limit: int = 10) -> List[Dict]:
        """Keyword-based search using repository."""
        return await self.entity_repo.search(q, limit=limit)
    
    async def semantic_search(self, q: str, limit: int = 10) -> List[Dict]:
        """Semantic search using embeddings.
        
        Process:
        1. Embed the query
        2. Get all entities from KG
        3. Embed entity labels
        4. Find top-K most similar
        5. Return ranked results
        """
        if not self.embedder:
            # Fallback to keyword search
            return await self.keyword_search(q, limit=limit)
        
        # Step 1: Embed query
        query_embedding = await self.embedder.embed_query(q)
        
        # Step 2: Get candidate entities (keyword pre-filter for performance)
        candidates = await self.entity_repo.search(q, limit=100)
        
        if not candidates:
            return []
        
        # Step 3: Embed candidates
        candidate_embeddings = await self.embedder.embed_entities(
            candidates,
            text_field="label"
        )
        
        # Step 4: Compute similarities
        similar_indices = await self.embedder.find_similar(
            query_embedding,
            candidate_embeddings,
            top_k=limit
        )
        
        # Step 5: Build results with scores
        results = []
        for idx, score in similar_indices:
            entity = candidates[idx].copy()
            entity["score"] = score
            results.append(entity)
        
        return results
    
    async def hybrid_search(
        self,
        q: str,
        limit: int = 10,
        keyword_weight: float = 0.5
    ) -> List[Dict]:
        """Hybrid search combining keyword and semantic.
        
        Args:
            q: Query string
            limit: Max results
            keyword_weight: Weight for keyword score (0-1)
        """
        if not self.embedder:
            return await self.keyword_search(q, limit=limit)
        
        semantic_weight = 1.0 - keyword_weight
        
        # Get both result sets
        keyword_results = await self.keyword_search(q, limit=limit*2)
        semantic_results = await self.semantic_search(q, limit=limit*2)
        
        # Merge and score
        entity_scores = {}
        
        # Add keyword scores
        for i, result in enumerate(keyword_results):
            entity_id = result.get("id")
            keyword_score = (len(keyword_results) - i) / len(keyword_results)
            entity_scores[entity_id] = {
                "entity": result,
                "score": keyword_score * keyword_weight
            }
        
        # Add semantic scores
        for result in semantic_results:
            entity_id = result.get("id")
            semantic_score = result.get("score", 0.0)
            
            if entity_id in entity_scores:
                entity_scores[entity_id]["score"] += semantic_score * semantic_weight
            else:
                entity_scores[entity_id] = {
                    "entity": result,
                    "score": semantic_score * semantic_weight
                }
        
        # Sort by combined score
        ranked = sorted(
            entity_scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )[:limit]
        
        # Return entities with scores
        results = []
        for item in ranked:
            entity = item["entity"].copy()
            entity["score"] = item["score"]
            results.append(entity)
        
        return results
    
    async def search_with_suggestions(
        self,
        q: str,
        limit: int = 10,
        semantic: bool = False
    ) -> Dict:
        """Search with autocomplete suggestions."""
        results = await self.search_entities(q, limit=limit, semantic=semantic)
        
        # Generate suggestions (entity labels)
        suggestions = []
        if results:
            suggestions = [
                r.get("label")
                for r in results[:5]
                if r.get("label")
            ]
        
        return {
            "results": results,
            "suggestions": suggestions
        }

