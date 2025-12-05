"""LLM utility - Language model operations.

Pure utility for LLM text generation and summarization.
No business logic, just API calls to Kaggle GPU endpoint.
"""
from abc import ABC, abstractmethod
from typing import List, Dict
import httpx
import logging

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """Abstract LLM interface."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    async def generate_with_context(
        self,
        query: str,
        context: List[str],
        max_tokens: int = 512,
        **kwargs
    ) -> str:
        """Generate answer with context (RAG)."""
        pass
    
    @abstractmethod
    async def close(self):
        """Cleanup resources."""
        pass


class KaggleLLM(BaseLLM):
    """Kaggle GPU-powered LLM.
    
    Uses Kaggle endpoints:
    - /chat - Chat completion
    - /summarize - Text summarization
    
    Model: Qwen/Qwen2.5-3B-Instruct
    """
    
    def __init__(
        self,
        endpoint_url: str,
        timeout: int = 60
    ):
        """Initialize Kaggle LLM.
        
        Args:
            endpoint_url: Kaggle endpoint base URL
            timeout: Request timeout in seconds
        """
        self.endpoint_url = endpoint_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        
        logger.info(f"✅ Initialized Kaggle LLM")
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text via Kaggle /chat endpoint."""
        try:
            response = await self.client.post(
                f"{self.endpoint_url}/chat",
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("response", "")
            
        except Exception as e:
            logger.error(f"Kaggle generation error: {e}")
            raise
    
    async def generate_summary(
        self,
        text: str,
        max_length: int = 150,
        temperature: float = 0.5
    ) -> Dict:
        """Generate summary via Kaggle /summarize endpoint."""
        try:
            response = await self.client.post(
                f"{self.endpoint_url}/summarize",
                json={
                    "text": text,
                    "max_length": max_length,
                    "temperature": temperature
                }
            )
            response.raise_for_status()
            
            data = response.json()
            return {"summary": data.get("summary", "")}
            
        except Exception as e:
            logger.error(f"Kaggle summarization error: {e}")
            raise
    
    async def generate_with_context(
        self,
        query: str,
        context: List[str],
        max_tokens: int = 512,
        **kwargs
    ) -> str:
        """Generate answer with context (RAG)."""
        # Build RAG prompt
        context_text = "\n\n".join(context[:3])  # Top 3 context snippets
        prompt = f"""Based on the following knowledge graph information, answer the question.

Context:
{context_text}

Question: {query}

Answer:"""
        
        return await self.generate(prompt, max_tokens=max_tokens, **kwargs)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
