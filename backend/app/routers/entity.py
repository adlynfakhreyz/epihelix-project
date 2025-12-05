"""Entity router (thin HTTP layer)."""
from fastapi import APIRouter, HTTPException, Depends, Query
from ..models import EntityDetail
from ..services.entity_service import EntityService
from ..core.dependencies import container

router = APIRouter()


def get_entity_service() -> EntityService:
    """Dependency injection for entity service."""
    return container.get_entity_service()


@router.get("/{entity_id}", response_model=EntityDetail)
async def get_entity(
    entity_id: str,
    include_related: bool = Query(False, description="Include related entities"),
    service: EntityService = Depends(get_entity_service)
):
    """Get detailed information about an entity (InfoBox data)."""
    if include_related:
        entity = await service.get_entity_with_related(entity_id)
    else:
        entity = await service.get_entity(entity_id)
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return EntityDetail(**entity)
