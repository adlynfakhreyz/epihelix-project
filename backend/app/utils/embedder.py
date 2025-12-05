"""Embedder utility - Text embedding generation.

Pure utility for generating text embeddings.
No business logic, just API calls to Kaggle GPU endpoint.
"""
from abc import ABC, abstractmethod
from typing import List
import httpx
import logging

logger = logging.getLogger(__name__)


class BaseEmbedder(ABC):
    """Abstract embedder interface."""
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return embedding dimension."""
        pass
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Embed single text string."""
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed batch of texts."""
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources."""
        pass


class KaggleEmbedder(BaseEmbedder):
    """Kaggle GPU-powered embedder (Qwen2.5 embeddings).
    
    Uses Kaggle /embed endpoint with GPU acceleration.
    Model: Alibaba-NLP/gte-Qwen2-1.5B-instruct
    """
    
    def __init__(
        self,
        endpoint_url: str,
        dimension: int = 1536,
        timeout: int = 30
    ):
        """Initialize Kaggle embedder.
        
        Args:
            endpoint_url: Kaggle endpoint base URL
            dimension: Embedding dimension (1536 for gte-Qwen2)
            timeout: Request timeout in seconds
        """
        self.endpoint_url = endpoint_url.rstrip('/')
        self._dimension = dimension
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        
        logger.info(f"✅ Initialized Kaggle Embedder (dim={dimension})")
    
    @property
    def dimension(self) -> int:
        """Embedding dimension."""
        return self._dimension
    
    async def embed_text(self, text: str) -> List[float]:
        """Embed single text via Kaggle /embed endpoint."""
        try:
            response = await self.client.post(
                f"{self.endpoint_url}/embed",
                json={
                    "texts": [text],  # ✅ Fixed: Kaggle expects list of texts
                    "normalize": True
                }
            )
            response.raise_for_status()
            
            data = response.json()
            embeddings = data.get("embeddings", [])
            
            if not embeddings or len(embeddings) == 0:
                raise ValueError("No embeddings returned from API")
            
            # Return first embedding (we only sent one text)
            embedding = embeddings[0]
            
            if len(embedding) != self._dimension:
                raise ValueError(f"Invalid embedding dimension: {len(embedding)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Kaggle embedding error: {e}")
            raise
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed batch of texts (uses Kaggle batch endpoint)."""
        try:
            response = await self.client.post(
                f"{self.endpoint_url}/embed",
                json={
                    "texts": texts,  # ✅ Already correct format
                    "normalize": True
                }
            )
            response.raise_for_status()
            
            data = response.json()
            embeddings = data.get("embeddings", [])
            
            if not embeddings or len(embeddings) != len(texts):
                raise ValueError(f"Expected {len(texts)} embeddings, got {len(embeddings)}")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Kaggle batch embedding error: {e}")
            raise
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
