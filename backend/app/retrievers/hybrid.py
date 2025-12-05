"""Hybrid retriever combining keyword, semantic, and reranking."""

from typing import List, Dict, Any, Optional
import logging

from .base import BaseRetriever
from .keyword import KeywordRetriever
from .semantic import SemanticRetriever
from ..repositories.entity_repository import EntityRepository
from ..utils.embedder import BaseEmbedder  # ✅ Fixed import path
from ..utils.reranker import BaseReranker  # ✅ Fixed import path

logger = logging.getLogger(__name__)


class HybridRetriever(BaseRetriever):
    """Hybrid retrieval combining multiple strategies.
    
    Pipeline:
    1. Keyword search (fast, high recall)
    2. Semantic search (understanding, high precision)
    3. Score fusion (RRF - Reciprocal Rank Fusion)
    4. Reranking (cross-encoder, highest accuracy)
    
    This is the recommended retriever for production use.
    
    Features:
    - Combines keyword + semantic strengths
    - Optional reranking with cross-encoder
    - Configurable weights
    - Handles both keyword and semantic queries well
    
    Example:
        retriever = HybridRetriever(
            entity_repo,
            embedder,
            reranker,
            use_reranking=True
        )
        results = await retriever.retrieve("covid vaccines", top_k=10)
    """
    
    def __init__(
        self,
        entity_repository: EntityRepository,
        embedder: Optional[BaseEmbedder] = None,
        reranker: Optional[BaseReranker] = None,
        use_reranking: bool = True,
        keyword_weight: float = 0.5
    ):
        """Initialize hybrid retriever.
        
        Args:
            entity_repository: Neo4j repository
            embedder: Embedding utility (optional, enables semantic search)
            reranker: Reranking utility (optional, improves ranking)
            use_reranking: Whether to apply reranking (default True)
            keyword_weight: Weight for keyword scores (0-1, default 0.5)
        """
        self.entity_repo = entity_repository
        self.embedder = embedder
        self.reranker = reranker
        self.use_reranking = use_reranking and reranker is not None
        self.keyword_weight = keyword_weight
        self.semantic_weight = 1.0 - keyword_weight
        
        # Create sub-retrievers
        self.keyword_retriever = KeywordRetriever(entity_repository)
        self.semantic_retriever = SemanticRetriever(
            entity_repository, embedder
        ) if embedder else None
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Retrieve using hybrid strategy.
        
        Args:
            query: Search query
            top_k: Number of final results
            **kwargs:
                - filters: Dict[str, Any] - entity type filters
                - use_reranking: bool - override default reranking
                - keyword_weight: float - override default weight
                - candidate_pool_size: int - size before reranking
        
        Returns:
            Ranked list of entities
        
        Example:
            results = await retriever.retrieve(
                "pandemic response measures",
                top_k=10,
                use_reranking=True
            )
        """
        self._validate_query(query)
        
        try:
            # Override reranking if specified
            apply_reranking = kwargs.get("use_reranking", self.use_reranking)
            
            # Candidate pool size (fetch more, then rerank down to top_k)
            candidate_pool_size = kwargs.get("candidate_pool_size", top_k * 5)
            
            # Fallback to keyword-only if no embedder
            if not self.semantic_retriever:
                logger.info("Semantic retriever not available, using keyword-only")
                return await self.keyword_retriever.retrieve(
                    query, top_k=top_k, **kwargs
                )
            
            # Step 1: Get keyword results
            keyword_results = await self.keyword_retriever.retrieve(
                query,
                top_k=candidate_pool_size,
                **kwargs
            )
            
            # Step 2: Get semantic results
            semantic_results = await self.semantic_retriever.retrieve(
                query,
                top_k=candidate_pool_size,
                **kwargs
            )
            
            # Step 3: Merge using Reciprocal Rank Fusion (RRF)
            merged_results = self._merge_results(
                keyword_results,
                semantic_results,
                k=kwargs.get("keyword_weight", self.keyword_weight)
            )
            
            # Trim to candidate pool size
            merged_results = merged_results[:candidate_pool_size]
            
            # Step 4: Optional reranking
            if apply_reranking and self.reranker:
                logger.info(f"Reranking {len(merged_results)} candidates")
                merged_results = await self._rerank(
                    query,
                    merged_results,
                    top_k=top_k
                )
            else:
                # Just trim to top_k without reranking
                merged_results = merged_results[:top_k]
            
            return merged_results
            
        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {e}")
            raise
    
    def _merge_results(
        self,
        keyword_results: List[Dict],
        semantic_results: List[Dict],
        k: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Merge keyword and semantic results using RRF.
        
        Reciprocal Rank Fusion (RRF) is better than score fusion
        because it doesn't rely on score calibration.
        
        RRF formula: score = Σ(1 / (k + rank_i))
        where k is a constant (typically 60) and rank_i is position.
        
        Args:
            keyword_results: Results from keyword search
            semantic_results: Results from semantic search
            k: Keyword weight (for combining scores, not RRF k)
        
        Returns:
            Merged and sorted results
        """
        entity_scores = {}
        rrf_k = 60  # Standard RRF constant
        
        # Process keyword results
        for rank, result in enumerate(keyword_results):
            entity_id = result.get("id")
            rrf_score = 1.0 / (rrf_k + rank + 1)
            
            entity_scores[entity_id] = {
                "entity": result,
                "score": rrf_score * k  # Weight by keyword_weight
            }
        
        # Process semantic results
        for rank, result in enumerate(semantic_results):
            entity_id = result.get("id")
            rrf_score = 1.0 / (rrf_k + rank + 1)
            
            if entity_id in entity_scores:
                # Add to existing score
                entity_scores[entity_id]["score"] += rrf_score * (1.0 - k)
            else:
                # New entity
                entity_scores[entity_id] = {
                    "entity": result,
                    "score": rrf_score * (1.0 - k)
                }
        
        # Sort by combined score
        ranked = sorted(
            entity_scores.values(),
            key=lambda x: x["score"],
            reverse=True
        )
        
        # Build results with scores
        results = []
        for item in ranked:
            entity = item["entity"].copy()
            entity["score"] = item["score"]
            results.append(entity)
        
        return results
    
    async def _rerank(
        self,
        query: str,
        entities: List[Dict],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Rerank entities using cross-encoder.
        
        Args:
            query: User query
            entities: Candidate entities
            top_k: Number of results to return
        
        Returns:
            Reranked entities
        """
        # Build document texts from entities
        documents = []
        for entity in entities:
            label = entity.get("label", "")
            snippet = entity.get("snippet", "")
            doc_text = f"{label}. {snippet}" if snippet else label
            documents.append(doc_text)
        
        # Call reranker
        reranked_indices = await self.reranker.rerank(
            query=query,
            documents=documents,
            top_k=top_k
        )
        
        # Build results with rerank scores
        results = []
        for idx, score in reranked_indices:
            entity = entities[idx].copy()
            entity["score"] = score  # Replace with rerank score
            entity["rerank_score"] = score
            results.append(entity)
        
        return results
