"""Summary service - LLM-powered entity summarization.

Provides Google-like summaries for search results and entity pages.
Uses LLM to generate concise, informative summaries from KG facts.

Following clean architecture:
- Depends on abstractions (EntityRepository, LLMService)
- Single responsibility (summarization only)
- Easy to test (inject mocks)
"""
from typing import Dict, List
from ..repositories.entity_repository import EntityRepository
from .llm_service import LLMService


class SummaryService:
    """Service for generating entity summaries."""
    
    def __init__(
        self,
        entity_repository: EntityRepository,
        llm_service: LLMService
    ):
        """Initialize summary service.
        
        Args:
            entity_repository: Data access for entities
            llm_service: LLM for text generation
        """
        self.entity_repo = entity_repository
        self.llm = llm_service
    
    async def generate_entity_summary(
        self,
        entity_id: str,
        include_relations: bool = True
    ) -> Dict:
        """Generate comprehensive summary for an entity.
        
        Args:
            entity_id: Entity ID to summarize
            include_relations: Include related entities in summary
        
        Returns:
            {
                "entity_id": str,
                "summary": str,
                "context_used": {
                    "properties": int,
                    "relations": int
                }
            }
        """
        # Fetch entity details
        entity = await self.entity_repo.get_by_id(entity_id)
        
        if not entity:
            return {
                "entity_id": entity_id,
                "summary": "Entity not found.",
                "context_used": {"properties": 0, "relations": 0}
            }
        
        # Extract info
        label = entity.get("label", "Unknown")
        properties = entity.get("properties", {})
        relations = entity.get("relations", []) if include_relations else []
        
        # Generate summary using LLM
        summary_text = await self.llm.summarize_entity(
            entity_label=label,
            properties=properties,
            relations=relations
        )
        
        return {
            "entity_id": entity_id,
            "summary": summary_text,
            "context_used": {
                "properties": len(properties),
                "relations": len(relations)
            }
        }
    
    async def generate_search_result_summary(
        self,
        query: str,
        entity_id: str
    ) -> Dict:
        """Generate query-specific summary for search result.
        
        Explains why this entity is relevant to the query.
        
        Args:
            query: Original search query
            entity_id: Entity to summarize
        
        Returns:
            {
                "entity_id": str,
                "query": str,
                "summary": str
            }
        """
        entity = await self.entity_repo.get_by_id(entity_id)
        
        if not entity:
            return {
                "entity_id": entity_id,
                "query": query,
                "summary": "Entity not found."
            }
        
        # Build contextual prompt
        label = entity.get("label", "Unknown")
        entity_type = entity.get("type", "Entity")
        snippet = entity.get("snippet", "No description available.")
        
        prompt = f"""Given the search query "{query}", explain why this entity is relevant:

Entity: {label} ({entity_type})
Description: {snippet}

Provide a 1-2 sentence explanation of relevance:"""
        
        summary_text = await self.llm.llm.generate(
            prompt,
            max_tokens=150,
            temperature=0.6
        )
        
        return {
            "entity_id": entity_id,
            "query": query,
            "summary": summary_text.strip()
        }


# Legacy utility function (kept for backward compatibility)
def summarize_text(text: str, max_sentences: int = 2) -> str:
    """Very small extractive summarizer: returns the first N sentences.

    Replace with an LLM or proper summarization model in production.
    """
    if not text:
        return ""
    # naive sentence split
    sentences: List[str] = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
    if not sentences:
        return text
    out = sentences[:max_sentences]
    return '. '.join(out) + ('.' if out else '')

