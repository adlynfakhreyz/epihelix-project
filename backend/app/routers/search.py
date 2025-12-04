"""Search router (thin HTTP layer).

Following Google's best practices:
- Routers should be thin, delegating to services
- Use dependency injection
- Handle HTTP-specific concerns only
"""
from fastapi import APIRouter, Query, Depends
from typing import List

from ..models import EntitySummary
from ..services.search_service import SearchService
from ..core.dependencies import container

router = APIRouter()


def get_search_service() -> SearchService:
    """Dependency injection for search service."""
    return container.get_search_service()


@router.get("/", response_model=List[EntitySummary])
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Maximum results"),
    service: SearchService = Depends(get_search_service)
):
    """Search entities by keyword or semantic similarity."""
    results = await service.search_entities(q, limit=limit)
    return [EntitySummary(**r) for r in results]


@router.get("/suggestions")
async def get_suggestions(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    service: SearchService = Depends(get_search_service)
):
    """Get search suggestions for autocomplete."""
    result = await service.search_with_suggestions(q, limit=limit)
    return result["suggestions"]
