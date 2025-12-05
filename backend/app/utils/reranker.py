"""Reranker utility - Cross-encoder reranking.

Pure utility for reranking documents by relevance.
No business logic, just API calls to Kaggle GPU endpoint.
"""
from abc import ABC, abstractmethod
from typing import List, Tuple
import httpx
import logging

logger = logging.getLogger(__name__)


class BaseReranker(ABC):
    """Abstract reranker interface."""
    
    @abstractmethod
    async def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int = 10
    ) -> List[Tuple[int, float]]:
        """Rerank documents by relevance to query.
        
        Args:
            query: Search query
            documents: List of document texts
            top_k: Number of top results to return
            
        Returns:
            List of (index, score) tuples sorted by relevance
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources."""
        pass


class KaggleReranker(BaseReranker):
    """Kaggle GPU-powered reranker (cross-encoder).
    
    Uses Kaggle /rerank endpoint with GPU acceleration.
    Model: BAAI/bge-reranker-v2-m3
    """
    
    def __init__(
        self,
        endpoint_url: str,
        timeout: int = 30
    ):
        """Initialize Kaggle reranker.
        
        Args:
            endpoint_url: Kaggle endpoint base URL
            timeout: Request timeout in seconds
        """
        self.endpoint_url = endpoint_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        
        logger.info(f"✅ Initialized Kaggle Reranker")
    
    async def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int = 10
    ) -> List[Tuple[int, float]]:
        """Rerank documents via Kaggle /rerank endpoint."""
        try:
            logger.info(f"🎯 Reranking {len(documents)} documents for: '{query}'")
            
            response = await self.client.post(
                f"{self.endpoint_url}/rerank",
                json={
                    "query": query,
                    "documents": documents,
                    "top_k": top_k
                }
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            # Convert to (index, score) tuples
            reranked = [(r["index"], r["score"]) for r in results]
            
            logger.info(f"✅ Reranked to top {len(reranked)} results")
            return reranked
            
        except Exception as e:
            logger.error(f"Kaggle reranking error: {e}")
            raise
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
