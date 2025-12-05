"""Service layer for entity operations.

Business logic for entity retrieval and operations.
"""
from typing import Dict, Optional, List, Any
from ..repositories.entity_repository import EntityRepository


class EntityService:
    """Entity service with repository injection."""
    
    def __init__(self, entity_repo: EntityRepository):
        self.entity_repo = entity_repo
    
    async def get_entity(self, entity_id: str) -> Optional[Dict]:
        """
        Get entity by ID with formatted properties.
        
        Returns entity ready for InfoBox display with:
        - Basic info (id, label, type)
        - All properties
        - Related entities
        """
        entity = await self.entity_repo.get_by_id(entity_id)
        if not entity:
            return None
        
        # Format properties - remove id from properties since it's top-level
        properties = {**entity.get("properties", {})}
        
        # Remove redundant fields that are already at top level
        for key in ["id", "label", "name"]:
            properties.pop(key, None)
        
        # Format the response
        formatted = {
            "id": entity.get("id"),
            "label": entity.get("label"),
            "type": entity.get("type"),
            "properties": properties,
            "relations": entity.get("relations", [])
        }
        
        return formatted
    
    async def get_entity_with_related(
        self,
        entity_id: str,
        include_related: bool = True
    ) -> Optional[Dict]:
        """
        Get entity with related entities (for InfoBox with expand).
        Same as get_entity since relations are already included.
        """
        return await self.get_entity(entity_id)
