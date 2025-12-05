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

    async def get_entities_by_type(
        self,
        entity_type: str,
        search: str = "",
        sort_by: str = "name",
        limit: int = 1000,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """
        Get all entities of a specific type with optional filtering.

        Used by the entity browser to display paginated entity lists.

        Args:
            entity_type: Type of entity (country, disease, outbreak, etc.)
            search: Optional search query to filter results
            sort_by: Sort field (name or id)
            limit: Maximum number of results
            filters: Optional property filters (e.g., {"continent": "Asia"})

        Returns:
            List of entities with id, label, type, description, and properties
        """
        entities = await self.entity_repo.get_by_type(
            entity_type=entity_type,
            search=search,
            sort_by=sort_by,
            limit=limit,
            filters=filters
        )

        return entities

    async def get_countries_for_entity(
        self,
        entity_id: str,
        data_type: str = "outbreaks"
    ) -> List[Dict]:
        """
        Get list of countries that have data for a specific entity (disease).

        Args:
            entity_id: Disease entity ID
            data_type: Type of data ('outbreaks' or 'vaccinations')

        Returns:
            List of countries with code and name
        """
        countries = await self.entity_repo.get_countries_for_entity(
            entity_id=entity_id,
            data_type=data_type
        )
        return countries

    async def get_timeseries_data(
        self,
        entity_id: str,
        data_type: str = "outbreaks",
        countries: List[str] = None,
        year_start: int = None,
        year_end: int = None,
        aggregation: str = "country"
    ) -> List[Dict]:
        """
        Get time-series data for outbreaks or vaccinations.

        Args:
            entity_id: Disease entity ID
            data_type: Type of data ('outbreaks' or 'vaccinations')
            countries: List of country codes to filter by
            year_start: Start year for filtering
            year_end: End year for filtering
            aggregation: 'country' or 'total'

        Returns:
            List of time-series data points
        """
        data = await self.entity_repo.get_timeseries_data(
            entity_id=entity_id,
            data_type=data_type,
            countries=countries,
            year_start=year_start,
            year_end=year_end,
            aggregation=aggregation
        )
        return data

    async def get_heatmap_data(
        self,
        disease_id: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get heatmap data for world map visualization.

        Args:
            disease_id: Disease entity ID
            year: Optional year to filter by (defaults to latest year with data)

        Returns:
            Dictionary with countries, availableYears, selectedYear, diseaseName
        """
        data = await self.entity_repo.get_heatmap_data(disease_id, year)
        return data
