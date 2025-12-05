"""
Heatmap Router

Provides endpoints for world heatmap visualization data
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional, List, Dict, Any
from app.core.dependencies import get_entity_service
from app.services.entity_service import EntityService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/heatmap", tags=["heatmap"])


@router.get("")
async def get_heatmap_data(
    diseaseId: str = Query(..., description="Disease element ID"),
    year: Optional[int] = Query(None, description="Year to filter by"),
    entity_service: EntityService = Depends(get_entity_service)
) -> Dict[str, Any]:
    """
    Get country-level outbreak data for heatmap visualization.
    
    Returns:
    - countries: List of {countryCode, countryName, cases, deaths, latitude, longitude}
    - availableYears: List of years with data
    - selectedYear: The year being displayed
    - diseaseName: Name of the disease
    """
    try:
        data = await entity_service.get_heatmap_data(diseaseId, year)
        return data
    except Exception as e:
        logger.error(f"Error getting heatmap data: {e}", exc_info=True)
        raise
