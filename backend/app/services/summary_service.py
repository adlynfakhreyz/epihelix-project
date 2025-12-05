"""Summary service - LLM-powered entity summarization.

Provides Google-like summaries for search results and entity pages.
Uses LLM to generate concise, informative summaries from KG facts.

Refactored architecture: Uses utils.llm directly (no service wrapper).
"""
from typing import Dict, List, Optional
from ..repositories.entity_repository import EntityRepository
from ..utils.llm import KaggleLLM  # ✅ Import from utils
import httpx
import logging

logger = logging.getLogger(__name__)


class SummaryService:
    """Service for generating entity summaries using Kaggle /summarize."""
    
    def __init__(
        self,
        entity_repository: EntityRepository,
        kaggle_llm=None  # KaggleLLM utility instance
    ):
        """Initialize summary service.
        
        Args:
            entity_repository: Data access for entities
            kaggle_llm: KaggleLLM utility instance (from utils.llm)
        """
        self.entity_repo = entity_repository
        self.kaggle_endpoint = kaggle_llm.endpoint_url if kaggle_llm else None
    
    async def generate_entity_summary(
        self,
        entity_id: str,
        include_relations: bool = True
    ) -> Dict:
        """Generate summary for an entity by calling Kaggle /summarize.
        
        Args:
            entity_id: Entity ID to summarize
            include_relations: Include related entities in summary
        
        Returns:
            {
                "entity_id": str,
                "summary": str,
                "context_used": {...}
            }
        """
        # Fetch entity from KG
        entity = await self.entity_repo.get_by_id(entity_id)
        
        if not entity:
            return {
                "entity_id": entity_id,
                "summary": "Entity not found.",
                "context_used": {"properties": 0, "relations": 0}
            }
        
        # Build context text
        context_parts = [
            f"Entity: {entity.get('label', 'Unknown')}",
            f"Type: {entity.get('type', 'Unknown')}"
        ]
        
        # Add properties
        props = entity.get("properties", {})
        if props:
            for key, val in list(props.items())[:5]:
                context_parts.append(f"{key}: {val}")
        
        # Add related entities using get_related (richer graph context)
        related_entities = []
        if include_relations:
            try:
                related_entities = await self.entity_repo.get_related(entity_id, max_depth=1)
            except Exception as e:
                logger.warning(f"Failed to fetch related entities: {e}")
        
        if related_entities:
            context_parts.append("\\nRelated entities:")
            # Group by type for better context
            by_type = {}
            for rel in related_entities[:10]:  # Limit to 10 for summary
                rel_type = rel.get('type', 'Unknown')
                rel_label = rel.get('label', 'Unknown')
                if rel_type not in by_type:
                    by_type[rel_type] = []
                by_type[rel_type].append(rel_label)
            
            for rel_type, labels in list(by_type.items())[:5]:  # Top 5 types
                labels_str = ", ".join(labels[:3])  # Top 3 per type
                context_parts.append(f"- {rel_type}: {labels_str}")
        
        context_text = "\\n".join(context_parts)
        
        # Call Kaggle /summarize
        if not self.kaggle_endpoint:
            summary_text = f"{entity.get('label')}: No LLM configured."
        else:
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        f"{self.kaggle_endpoint}/summarize",
                        json={
                            "text": context_text,
                            "max_length": 150,
                            "temperature": 0.7
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    summary_text = data["summary"]
            except Exception as e:
                logger.error(f"❌ Summary generation failed: {e}")
                summary_text = f"{entity.get('label')}: Summary unavailable."
        
        return {
            "entity_id": entity_id,
            "summary": summary_text,
            "context_used": {
                "properties": len(props),
                "relations": len(related_entities)
            }
        }
    
    async def generate_summary(
        self,
        entity_id: Optional[str] = None,
        entity_ids: Optional[List[str]] = None,
        context: Optional[str] = None
    ) -> Dict:
        """Generate summary for one or multiple entities.
        
        Args:
            entity_id: Single entity ID (optional)
            entity_ids: List of entity IDs (optional)
            context: Additional context string
        
        Returns:
            {"summary": str, "entities": [...]}
        """
        if entity_id:
            result = await self.generate_entity_summary(entity_id)
            return {
                "summary": result["summary"],
                "entities": [entity_id]
            }
        
        if entity_ids and len(entity_ids) > 0:
            # Fetch all entities
            entities = []
            for eid in entity_ids[:10]:  # Limit to 10
                entity = await self.entity_repo.get_by_id(eid)
                if entity:
                    entities.append(entity)
            
            if not entities:
                return {
                    "summary": "No entities found.",
                    "entities": []
                }
            
            # Build combined context
            context_parts = []
            for i, entity in enumerate(entities, 1):
                label = entity.get('label', 'Unknown')
                entity_type = entity.get('type', 'Unknown')
                context_parts.append(f"{i}. {label} ({entity_type})")
            
            if context:
                full_text = f"Context: {context}\\n\\nEntities:\\n" + "\\n".join(context_parts)
            else:
                full_text = "Entities:\\n" + "\\n".join(context_parts)
            
            # Call Kaggle /summarize
            if not self.kaggle_endpoint:
                summary_text = f"Summary of {len(entities)} entities (no LLM configured)."
            else:
                try:
                    async with httpx.AsyncClient(timeout=30) as client:
                        response = await client.post(
                            f"{self.kaggle_endpoint}/summarize",
                            json={
                                "text": full_text,
                                "max_length": 200,
                                "temperature": 0.6
                            }
                        )
                        response.raise_for_status()
                        data = response.json()
                        summary_text = data["summary"]
                except Exception as e:
                    logger.error(f"❌ Multi-entity summary failed: {e}")
                    summary_text = f"Summary of {len(entities)} entities (generation failed)."
            
            return {
                "summary": summary_text,
                "entities": entity_ids
            }
        
        return {
            "summary": "No entities provided.",
            "entities": []
        }
