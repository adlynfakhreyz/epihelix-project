"""Summary generation endpoints.

Provides AI-powered summaries for search results and entity groups.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging

from ..core.dependencies import container, get_summary_service
from ..services.summary_service import SummaryService

logger = logging.getLogger(__name__)

router = APIRouter()


class SummaryRequest(BaseModel):
    """Request for summary generation."""
    entity_id: Optional[str] = None  # Single entity (legacy)
    entity_ids: Optional[List[str]] = None  # Multiple entities
    query: Optional[str] = None  # Legacy field name
    context: Optional[str] = None
    include_relations: Optional[bool] = True


class SummaryResponse(BaseModel):
    """Summary generation response."""
    summary: str
    entity_count: int
    source_entities: List[dict]


@router.post("/generate", response_model=SummaryResponse)
async def generate_summary(
    request: SummaryRequest,
    summary_service: SummaryService = Depends(get_summary_service)
) -> SummaryResponse:
    """Generate AI summary for a group of entities.
    
    Args:
        request: Summary request with entity IDs
        
    Returns:
        Generated summary with source entities
    """
    try:
        # Handle both single entity_id and multiple entity_ids
        entity_ids = []
        if request.entity_id:
            entity_ids = [request.entity_id]
        elif request.entity_ids:
            entity_ids = request.entity_ids
        else:
            raise HTTPException(status_code=422, detail="Either entity_id or entity_ids must be provided")
        
        # Use query or context (legacy compatibility)
        context = request.context or request.query
        
        result = await summary_service.generate_summary(
            entity_ids=entity_ids,
            context=context
        )
        
        return SummaryResponse(
            summary=result["summary"],
            entity_count=len(entity_ids),
            source_entities=result.get("entities", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Summary generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")
