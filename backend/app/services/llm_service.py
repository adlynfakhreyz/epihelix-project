"""LLM Service - Abstraction layer for Language Models.

Follows SOLID principles:
- Strategy Pattern: Swap LLM providers without changing business logic
- Open-Closed: Extend with new providers without modifying existing code
- Dependency Inversion: Depend on abstractions (BaseLLM), not implementations

Supported Providers:
- HuggingFace Inference API (self-hosted or cloud)
- HuggingFace Spaces (Gradio endpoints)
- Mock (development/testing)
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import httpx
import logging

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """Abstract base class for LLM providers (Strategy Pattern)."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text completion from prompt."""
        pass
    
    @abstractmethod
    async def generate_with_context(
        self,
        query: str,
        context: List[str],
        max_tokens: int = 512,
        **kwargs
    ) -> str:
        """Generate answer given query and context (for RAG)."""
        pass


class HuggingFaceLLM(BaseLLM):
    """HuggingFace Inference API client.
    
    Works with:
    - HuggingFace Inference API (free tier: meta-llama/Llama-3.2-3B-Instruct)
    - Self-hosted models via HF Inference Endpoints
    - HuggingFace Spaces (Gradio apps)
    """
    
    def __init__(
        self,
        model: str = "meta-llama/Llama-3.2-3B-Instruct",
        api_key: Optional[str] = None,
        endpoint_url: Optional[str] = None
    ):
        """Initialize HuggingFace LLM.
        
        Args:
            model: HF model ID (e.g., "meta-llama/Llama-3.2-3B-Instruct")
            api_key: HF API token (optional for public models)
            endpoint_url: Custom endpoint URL (for Spaces or self-hosted)
        """
        self.model = model
        self.api_key = api_key
        
        # Use custom endpoint or default HF Inference API
        self.endpoint_url = endpoint_url or f"https://api-inference.huggingface.co/models/{model}"
        
        self.client = httpx.AsyncClient(timeout=30.0)
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text completion."""
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": kwargs.get("top_p", 0.9),
                    "do_sample": temperature > 0,
                    "return_full_text": False
                }
            }
            
            response = await self.client.post(
                self.endpoint_url,
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            elif isinstance(result, dict):
                return result.get("generated_text", "")
            
            logger.warning(f"Unexpected HuggingFace response format: {result}")
            return ""
            
        except Exception as e:
            logger.error(f"HuggingFace generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    async def generate_with_context(
        self,
        query: str,
        context: List[str],
        max_tokens: int = 512,
        **kwargs
    ) -> str:
        """Generate answer using RAG pattern."""
        # Build prompt with context
        context_str = "\n\n".join([f"Context {i+1}: {c}" for i, c in enumerate(context)])
        
        prompt = f"""You are a knowledgeable assistant for pandemic and disease information. Answer the question based on the provided context from a knowledge graph.

{context_str}

Question: {query}

Answer: Based on the context above,"""
        
        return await self.generate(prompt, max_tokens=max_tokens, **kwargs)
    
    async def close(self):
        """Clean up resources."""
        await self.client.aclose()


class HuggingFaceSpaceLLM(BaseLLM):
    """HuggingFace Spaces (Gradio) client.
    
    For self-hosted models deployed as Gradio apps.
    Example: https://huggingface.co/spaces/your-username/your-llm-space
    """
    
    def __init__(self, space_url: str, api_token: Optional[str] = None):
        """Initialize Space LLM.
        
        Args:
            space_url: Full Gradio Space URL (e.g., "https://your-space.hf.space")
            api_token: HF token for private spaces
        """
        self.space_url = space_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=60.0)
        self.headers = {}
        if api_token:
            self.headers["Authorization"] = f"Bearer {api_token}"
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Call Gradio API endpoint."""
        try:
            # Gradio API format
            payload = {
                "data": [prompt, max_tokens, temperature]
            }
            
            response = await self.client.post(
                f"{self.space_url}/api/predict",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("data", [""])[0]
            
        except Exception as e:
            logger.error(f"HuggingFace Space error: {e}")
            return f"Error: {str(e)}"
    
    async def generate_with_context(
        self,
        query: str,
        context: List[str],
        max_tokens: int = 512,
        **kwargs
    ) -> str:
        """RAG generation via Gradio Space."""
        context_str = "\n\n".join(context)
        prompt = f"Context:\n{context_str}\n\nQuestion: {query}\n\nAnswer:"
        return await self.generate(prompt, max_tokens=max_tokens, **kwargs)
    
    async def close(self):
        """Clean up resources."""
        await self.client.aclose()


class MockLLM(BaseLLM):
    """Mock LLM for development and testing."""
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Return mock response."""
        return (
            f"[Mock LLM Response] This is a simulated answer for: '{prompt[:50]}...' "
            f"In production, this would be generated by a real language model."
        )
    
    async def generate_with_context(
        self,
        query: str,
        context: List[str],
        max_tokens: int = 512,
        **kwargs
    ) -> str:
        """Mock RAG response."""
        context_preview = context[0][:100] if context else "No context"
        return (
            f"[Mock RAG Answer] Based on the knowledge graph context ({len(context)} snippets), "
            f"here's a simulated answer for '{query}': {context_preview}..."
        )
    
    async def close(self):
        """No cleanup needed."""
        pass


class LLMService:
    """High-level LLM service (Facade Pattern).
    
    Simplifies LLM operations for the rest of the application.
    """
    
    def __init__(self, llm_provider: BaseLLM):
        """Initialize with a specific LLM provider."""
        self.llm = llm_provider
    
    async def summarize_entity(
        self,
        entity_label: str,
        properties: Dict,
        relations: List[Dict]
    ) -> str:
        """Generate summary for an entity (for Google-like info box)."""
        # Build structured prompt
        props_str = "\n".join([f"- {k}: {v}" for k, v in properties.items()])
        rels_str = "\n".join([
            f"- {r.get('pred', 'relates to')} {r.get('obj', {}).get('label', 'unknown')}"
            for r in relations[:5]  # Top 5 relations
        ])
        
        prompt = f"""Provide a concise summary (2-3 sentences) for this entity:

Entity: {entity_label}

Properties:
{props_str}

Relations:
{rels_str}

Summary:"""
        
        return await self.llm.generate(prompt, max_tokens=200, temperature=0.5)
    
    async def answer_question(
        self,
        question: str,
        retrieved_facts: List[str]
    ) -> Dict:
        """Answer question using retrieved KG facts (RAG)."""
        answer = await self.llm.generate_with_context(
            query=question,
            context=retrieved_facts,
            max_tokens=300,
            temperature=0.6
        )
        
        return {
            "answer": answer,
            "sources": retrieved_facts,
            "context_used": len(retrieved_facts)
        }
    
    async def chat(
        self,
        message: str,
        context: Optional[List[str]] = None
    ) -> str:
        """Chat with optional KG context."""
        if context:
            return await self.llm.generate_with_context(
                query=message,
                context=context,
                max_tokens=400
            )
        else:
            return await self.llm.generate(message, max_tokens=400)
    
    async def close(self):
        """Clean up LLM resources."""
        await self.llm.close()
