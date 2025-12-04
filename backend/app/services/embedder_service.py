"""Embedder Service - Semantic embedding generation.

Follows SOLID principles:
- Strategy Pattern: Support multiple embedding providers
- Single Responsibility: Only handles embedding generation
- Open-Closed: Easy to add new embedding models

Providers:
- HuggingFace sentence-transformers (self-hosted)
- HuggingFace Inference API
- Mock (development)
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import httpx
import numpy as np
import logging

logger = logging.getLogger(__name__)


class BaseEmbedder(ABC):
    """Abstract embedder interface."""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts."""
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding dimension size."""
        pass


class HuggingFaceEmbedder(BaseEmbedder):
    """HuggingFace Inference API embedder.
    
    Recommended models:
    - sentence-transformers/all-MiniLM-L6-v2 (384 dims, fast, good quality)
    - BAAI/bge-small-en-v1.5 (384 dims, better quality)
    - sentence-transformers/all-mpnet-base-v2 (768 dims, best quality)
    """
    
    def __init__(
        self,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
        api_key: Optional[str] = None,
        endpoint_url: Optional[str] = None
    ):
        """Initialize HuggingFace embedder.
        
        Args:
            model: HF model ID for embeddings
            api_key: HF API token (optional for public models)
            endpoint_url: Custom endpoint (for self-hosted)
        """
        self.model = model
        self.api_key = api_key
        
        # Map model to dimensions (extend as needed)
        self._dimensions = {
            "sentence-transformers/all-MiniLM-L6-v2": 384,
            "sentence-transformers/all-mpnet-base-v2": 768,
            "BAAI/bge-small-en-v1.5": 384,
            "BAAI/bge-base-en-v1.5": 768,
        }
        
        self.endpoint_url = endpoint_url or f"https://api-inference.huggingface.co/models/{model}"
        self.client = httpx.AsyncClient(timeout=30.0)
        
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimensions.get(self.model, 384)  # Default to 384
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        embeddings = await self.embed_batch([text])
        return embeddings[0] if embeddings else []
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch."""
        if not texts:
            return []
        
        try:
            # HuggingFace feature extraction endpoint
            payload = {"inputs": texts}
            
            response = await self.client.post(
                self.endpoint_url,
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            
            embeddings = response.json()
            
            # Normalize to List[List[float]]
            if isinstance(embeddings, list):
                # Handle nested array format
                if isinstance(embeddings[0], list) and isinstance(embeddings[0][0], list):
                    # Sometimes returns [[[embedding]]] - flatten once
                    embeddings = [e[0] if isinstance(e[0], list) else e for e in embeddings]
                return embeddings
            
            logger.error(f"Unexpected embedding format: {type(embeddings)}")
            return [[0.0] * self.dimension for _ in texts]  # Fallback
            
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            # Return zero vectors as fallback
            return [[0.0] * self.dimension for _ in texts]
    
    async def close(self):
        """Clean up resources."""
        await self.client.aclose()


class MockEmbedder(BaseEmbedder):
    """Mock embedder for development."""
    
    def __init__(self, dimension: int = 384):
        """Initialize with fixed dimension."""
        self._dimension = dimension
    
    @property
    def dimension(self) -> int:
        """Embedding dimension."""
        return self._dimension
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate mock embedding (deterministic based on text hash)."""
        # Simple hash-based mock embedding (deterministic)
        seed = hash(text) % 10000
        np.random.seed(seed)
        embedding = np.random.randn(self._dimension).tolist()
        # Normalize (unit vector)
        norm = np.linalg.norm(embedding)
        return (np.array(embedding) / norm).tolist()
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for batch."""
        return [await self.embed_text(t) for t in texts]
    
    async def close(self):
        """No cleanup needed."""
        pass


class EmbedderService:
    """High-level embedder service (Facade).
    
    Simplifies embedding operations for semantic search.
    """
    
    def __init__(self, embedder: BaseEmbedder):
        """Initialize with specific embedder provider."""
        self.embedder = embedder
    
    async def embed_query(self, query: str) -> List[float]:
        """Embed search query."""
        return await self.embedder.embed_text(query)
    
    async def embed_entities(
        self,
        entities: List[dict],
        text_field: str = "label"
    ) -> List[List[float]]:
        """Embed batch of entities.
        
        Args:
            entities: List of entity dicts
            text_field: Which field to embed (label, description, etc.)
        """
        texts = [e.get(text_field, "") for e in entities]
        return await self.embedder.embed_batch(texts)
    
    async def embed_kg_triples(
        self,
        triples: List[dict]
    ) -> List[List[float]]:
        """Embed KG triples as text.
        
        Converts (subject, predicate, object) to natural text:
        "Influenza A causes Spanish Flu Pandemic"
        """
        texts = []
        for triple in triples:
            subj = triple.get("subject", {}).get("label", "Unknown")
            pred = triple.get("predicate", "relates to")
            obj = triple.get("object", {}).get("label", "Unknown")
            texts.append(f"{subj} {pred} {obj}")
        
        return await self.embedder.embed_batch(texts)
    
    def cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """Compute cosine similarity between two embeddings."""
        a = np.array(embedding1)
        b = np.array(embedding2)
        
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    async def find_similar(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        top_k: int = 10
    ) -> List[tuple]:
        """Find top-K most similar embeddings.
        
        Returns:
            List of (index, score) tuples, sorted by score descending
        """
        similarities = [
            (i, self.cosine_similarity(query_embedding, emb))
            for i, emb in enumerate(candidate_embeddings)
        ]
        
        # Sort by score descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    async def close(self):
        """Clean up resources."""
        await self.embedder.close()
