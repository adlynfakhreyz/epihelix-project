"""Summary service - LLM-powered entity summarization.

Provides Google-like summaries for search results and entity pages.
Uses Groq LLM to generate concise, informative summaries from KG facts.
"""
from typing import Dict, List, Optional
from ..repositories.entity_repository import EntityRepository
from ..utils.llm_groq import GroqLLM
import logging

logger = logging.getLogger(__name__)


class SummaryService:
    """Service for generating entity summaries using Groq LLM."""
    
    def __init__(
        self,
        entity_repository: EntityRepository,
        groq_llm: Optional[GroqLLM] = None
    ):
        """Initialize summary service.
        
        Args:
            entity_repository: Data access for entities
            groq_llm: GroqLLM utility instance
        """
        self.entity_repo = entity_repository
        self.llm = groq_llm
        
        if self.llm:
            logger.info("✅ SummaryService initialized with Groq LLM")
        else:
            logger.warning("⚠️ SummaryService initialized without LLM")
    
    def _build_entity_context(self, entity: Dict, relations: List[Dict] = None) -> str:
        """Build context string from entity data.
        
        Args:
            entity: Entity dict with properties
            relations: Related entities
            
        Returns:
            Formatted context string
        """
        parts = []
        
        # Basic info
        label = entity.get('label', 'Unknown')
        entity_type = entity.get('type', 'Unknown')
        parts.append(f"**{label}** ({entity_type})")
        
        # Properties
        props = entity.get("properties", {})
        if props:
            parts.append("\nKey Facts:")
            for key, val in list(props.items())[:10]:
                if val and key not in ["id", "embedding", "enriched", "enrichedAt"]:
                    clean_key = key.replace("_", " ").title()
                    # Truncate long values
                    val_str = str(val)
                    if len(val_str) > 200:
                        val_str = val_str[:200] + "..."
                    parts.append(f"- {clean_key}: {val_str}")
        
        # Relations
        if relations:
            parts.append("\nRelated Entities:")
            by_type = {}
            for rel in relations[:15]:
                rel_type = rel.get('type', 'Unknown')
                rel_label = rel.get('label', 'Unknown')
                if rel_type not in by_type:
                    by_type[rel_type] = []
                by_type[rel_type].append(rel_label)
            
            for rel_type, labels in list(by_type.items())[:5]:
                labels_str = ", ".join(labels[:5])
                parts.append(f"- {rel_type}: {labels_str}")
        
        return "\n".join(parts)
    
    async def generate_entity_summary(
        self,
        entity_id: str,
        include_relations: bool = True
    ) -> Dict:
        """Generate summary for a single entity.
        
        Args:
            entity_id: Entity ID to summarize
            include_relations: Include related entities in summary
        
        Returns:
            {"entity_id": str, "summary": str, "context_used": {...}}
        """
        # Fetch entity from KG
        entity = await self.entity_repo.get_by_id(entity_id)
        
        if not entity:
            return {
                "entity_id": entity_id,
                "summary": "Entity not found in the knowledge graph.",
                "context_used": {"properties": 0, "relations": 0}
            }
        
        # Fetch related entities
        relations = []
        if include_relations:
            try:
                relations = await self.entity_repo.get_related(entity_id, max_depth=1)
            except Exception as e:
                logger.warning(f"Failed to fetch related entities: {e}")
        
        # Build context
        context = self._build_entity_context(entity, relations)
        
        # Generate summary with LLM
        if not self.llm:
            # Fallback: simple description without LLM
            label = entity.get('label', 'Unknown')
            entity_type = entity.get('type', 'Unknown')
            props = entity.get("properties", {})
            desc = props.get("description") or props.get("wikipediaAbstract") or props.get("abstract")
            if desc:
                summary_text = f"{label} is a {entity_type.lower()}. {desc[:300]}"
            else:
                summary_text = f"{label} is a {entity_type.lower()} in the EpiHelix knowledge graph."
        else:
            try:
                system_prompt = """You are a helpful assistant that generates concise summaries about diseases, countries, outbreaks, and health data.

Guidelines:
- Write 2-3 sentences maximum
- Focus on the most important facts
- Be factual and informative
- Use simple, clear language
- Do not make up information not in the context"""

                prompt = f"""Based on the following information from a knowledge graph, write a brief summary:

{context}

Write a concise 2-3 sentence summary about this entity:"""

                summary_text = await self.llm.agenerate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    max_tokens=150,
                    temperature=0.5
                )
                summary_text = summary_text.strip()
                
            except Exception as e:
                logger.error(f"❌ Summary generation failed: {e}")
                label = entity.get('label', 'Unknown')
                summary_text = f"{label}: Summary generation failed."
        
        return {
            "entity_id": entity_id,
            "summary": summary_text,
            "context_used": {
                "properties": len(entity.get("properties", {})),
                "relations": len(relations)
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
        # Single entity
        if entity_id:
            result = await self.generate_entity_summary(entity_id)
            return {
                "summary": result["summary"],
                "entities": [entity_id]
            }
        
        # Multiple entities
        if entity_ids and len(entity_ids) > 0:
            entities_data = []
            for eid in entity_ids[:10]:  # Limit to 10
                entity = await self.entity_repo.get_by_id(eid)
                if entity:
                    entities_data.append(entity)
            
            if not entities_data:
                return {
                    "summary": "No entities found in the knowledge graph.",
                    "entities": []
                }
            
            # Build combined context
            context_parts = []
            for entity in entities_data:
                label = entity.get('label', 'Unknown')
                entity_type = entity.get('type', 'Unknown')
                props = entity.get('properties', {})
                desc = props.get("description") or props.get("abstract", "")
                if desc:
                    desc = desc[:150] + "..." if len(desc) > 150 else desc
                context_parts.append(f"- {label} ({entity_type}): {desc}" if desc else f"- {label} ({entity_type})")
            
            entities_text = "\n".join(context_parts)
            
            if not self.llm:
                summary_text = f"Summary of {len(entities_data)} entities from the knowledge graph."
            else:
                try:
                    system_prompt = """You are a helpful assistant that generates concise summaries about health-related entities.

Guidelines:
- Write 2-4 sentences maximum
- Highlight common themes or patterns
- Be factual and informative"""

                    user_context = f"User query: {context}\n\n" if context else ""
                    prompt = f"""{user_context}Summarize these entities from the knowledge graph:

{entities_text}

Write a brief summary:"""

                    summary_text = await self.llm.agenerate(
                        prompt=prompt,
                        system_prompt=system_prompt,
                        max_tokens=200,
                        temperature=0.5
                    )
                    summary_text = summary_text.strip()
                    
                except Exception as e:
                    logger.error(f"❌ Multi-entity summary failed: {e}")
                    summary_text = f"Summary of {len(entities_data)} entities (generation failed)."
            
            return {
                "summary": summary_text,
                "entities": entity_ids
            }
        
        return {
            "summary": "No entities provided.",
            "entities": []
        }