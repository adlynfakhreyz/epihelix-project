"""Entity router (thin HTTP layer)."""
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import List, Dict, Any, Optional
from ..models import EntityDetail
from ..services.entity_service import EntityService
from ..core.dependencies import container

router = APIRouter()


def get_entity_service() -> EntityService:
    """Dependency injection for entity service."""
    return container.get_entity_service()


@router.get("/list")
async def list_entities(
    request: Request,
    type: str = Query(..., description="Entity type (country, disease, outbreak, vaccinationrecord, organization)"),
    search: str = Query("", description="Search query for filtering"),
    sortBy: str = Query("name", description="Sort field (name, id)"),
    service: EntityService = Depends(get_entity_service)
):
    """List entities by type with optional search and filtering.

    This endpoint is used by the entity browser to display paginated entity lists.
    Accepts additional query parameters as property filters (e.g., continent=Asia).
    """
    # Extract filter parameters (anything not type, search, sortBy, or limit)
    filters = {}
    excluded_params = {'type', 'search', 'sortBy', 'limit'}
    for key, value in request.query_params.items():
        if key not in excluded_params and value:
            filters[key] = value
    
    # Get entities by type with filters
    entities = await service.get_entities_by_type(
        type, 
        search=search, 
        sort_by=sortBy,
        filters=filters
    )

    # Generate available filters based on entity type
    available_filters = generate_filters_for_type(type)

    return {
        "entities": entities,
        "availableFilters": available_filters,
        "total": len(entities),
        "type": type,
        "appliedFilters": filters
    }


def generate_filters_for_type(entity_type: str) -> List[Dict[str, Any]]:
    """Generate dynamic filters based on entity type."""
    filters_by_type = {
        "country": [
            {
                "key": "continent",
                "label": "Continent",
                "type": "select",
                "options": [
                    {"value": "Asia", "label": "Asia"},
                    {"value": "Europe", "label": "Europe"},
                    {"value": "Americas", "label": "Americas"},
                    {"value": "Africa", "label": "Africa"},
                    {"value": "Oceania", "label": "Oceania"},
                ],
            },
            {
                "key": "enriched",
                "label": "Enriched",
                "type": "select",
                "options": [
                    {"value": "true", "label": "Yes"},
                    {"value": "false", "label": "No"},
                ],
            },
        ],
        "disease": [
            {
                "key": "vaccinePreventable",
                "label": "Vaccine Preventable",
                "type": "select",
                "options": [
                    {"value": "true", "label": "Yes"},
                    {"value": "false", "label": "No"},
                ],
            },
            {
                "key": "eradicated",
                "label": "Eradicated",
                "type": "select",
                "options": [
                    {"value": "true", "label": "Yes"},
                    {"value": "false", "label": "No"},
                ],
            },
        ],
        "outbreak": [
            {"key": "year", "label": "Year", "type": "text"},
            {"key": "country", "label": "Country", "type": "text"},
            {"key": "disease", "label": "Disease", "type": "text"},
        ],
        "vaccinationrecord": [
            {"key": "year", "label": "Year", "type": "text"},
            {"key": "country", "label": "Country", "type": "text"},
            {"key": "disease", "label": "Disease", "type": "text"},
        ],
        "organization": [
            {"key": "headquarters", "label": "Headquarters", "type": "text"},
        ],
    }

    return filters_by_type.get(entity_type.lower(), [])


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


@router.get("/{entity_id}/countries")
async def get_entity_countries(
    entity_id: str,
    dataType: str = Query("outbreaks", description="Type of data: 'outbreaks' or 'vaccinations'"),
    service: EntityService = Depends(get_entity_service)
):
    """Get list of countries that have data for a specific entity (disease).
    
    Used by TimeSeriesChart to populate country selection dropdown.
    """
    countries = await service.get_countries_for_entity(
        entity_id=entity_id,
        data_type=dataType
    )
    
    return {
        "countries": countries,
        "total": len(countries)
    }


@router.get("/{entity_id}/timeseries")
async def get_entity_timeseries(
    entity_id: str,
    dataType: str = Query("outbreaks", description="Type of data: 'outbreaks' or 'vaccinations'"),
    countries: Optional[str] = Query(None, description="Comma-separated country codes (or 'ALL')"),
    yearStart: Optional[int] = Query(None, description="Start year for filtering"),
    yearEnd: Optional[int] = Query(None, description="End year for filtering"),
    aggregation: str = Query("country", description="Aggregation type: 'country' or 'total'"),
    service: EntityService = Depends(get_entity_service)
):
    """Get time-series data for outbreaks or vaccinations.
    
    Used by TimeSeriesChart to display line/bar/area charts.
    """
    # Parse countries parameter
    country_list = None
    if countries and countries != "ALL":
        country_list = [c.strip() for c in countries.split(",") if c.strip()]
    
    data = await service.get_timeseries_data(
        entity_id=entity_id,
        data_type=dataType,
        countries=country_list,
        year_start=yearStart,
        year_end=yearEnd,
        aggregation=aggregation
    )
    
    return {
        "data": data,
        "total": len(data),
        "filters": {
            "dataType": dataType,
            "countries": country_list or ["ALL"],
            "yearStart": yearStart,
            "yearEnd": yearEnd,
            "aggregation": aggregation
        }
    }
