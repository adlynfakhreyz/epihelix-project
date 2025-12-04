"""Service layer for entity operations.

Business logic for entity retrieval and operations.
"""
from typing import Dict, Optional, List
from ..repositories.entity_repository import EntityRepository


class EntityService:
    """Entity service with repository injection."""
    
    def __init__(self, entity_repo: EntityRepository):
        self.entity_repo = entity_repo
    
    async def get_entity(self, entity_id: str) -> Optional[Dict]:
        """Get entity by ID."""
        return await self.entity_repo.get_by_id(entity_id)
    
    async def get_entity_with_related(
        self,
        entity_id: str,
        include_related: bool = True
    ) -> Optional[Dict]:
        """Get entity with related entities (for InfoBox)."""
        entity = await self.entity_repo.get_by_id(entity_id)
        if not entity:
            return None
        
        result = {**entity}
        
        if include_related:
            related = await self.entity_repo.get_related(entity_id, max_depth=1)
            result["related"] = related
        
        return result
