"""Groq LLM utility - Fast, free, reliable LLM inference.

Uses Groq's API for Llama 3.1 70B inference.
Free tier: 30 req/min, 14,400 req/day
"""
from typing import List, Optional
from groq import Groq
import logging

logger = logging.getLogger(__name__)


class GroqLLM:
    """Groq-powered LLM for chat and RAG.
    
    Models available (free):
    - llama-3.1-70b-versatile (best quality)
    - llama-3.1-8b-instant (faster)
    - mixtral-8x7b-32768 (good balance)
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        """Initialize Groq LLM.
        
        Args:
            api_key: Groq API key from https://console.groq.com/
            model: Model to use
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        logger.info(f"✅ Initialized Groq LLM with model: {model}")
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate text from prompt (synchronous).
        
        Args:
            prompt: User prompt
            max_tokens: Override default max tokens
            temperature: Override default temperature
            system_prompt: Optional system message
        
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq generation error: {e}")
            raise
    
    async def agenerate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate text from prompt (async wrapper).
        
        Note: Groq SDK is sync, so we just call sync method.
        For true async, use httpx directly.
        """
        return self.generate(prompt, max_tokens, temperature, system_prompt)
    
    def generate_with_context(
        self,
        query: str,
        context: List[str],
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate answer with RAG context.
        
        Args:
            query: User question
            context: List of context snippets from knowledge graph
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated answer grounded in context
        """
        context_text = "\n\n".join(context[:5])  # Top 5 context pieces
        
        system_prompt = """You are EpiHelix AI, an expert assistant for pandemic and disease data.
You answer questions based ONLY on the provided knowledge graph context.
If the context doesn't contain enough information, say so honestly.
Be concise but informative. Use bullet points for lists."""

        prompt = f"""Based on the following knowledge graph data:

{context_text}

Question: {query}

Answer:"""
        
        return self.generate(
            prompt=prompt,
            max_tokens=max_tokens or 512,
            system_prompt=system_prompt
        )
    
    async def agenerate_with_context(
        self,
        query: str,
        context: List[str],
        max_tokens: Optional[int] = None
    ) -> str:
        """Async version of generate_with_context."""
        return self.generate_with_context(query, context, max_tokens)