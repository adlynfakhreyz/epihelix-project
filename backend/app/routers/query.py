"""Query router for free-form Cypher queries.

Allows users to execute custom queries against Neo4j KG.
Security: Add query validation and rate limiting in production.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging

from ..models import QueryRequest, QueryResponse
from ..services.query_service import QueryService
from ..core.dependencies import container

logger = logging.getLogger(__name__)
router = APIRouter()


def get_query_service() -> QueryService:
    """Dependency injection for query service."""
    return container.get_query_service()


@router.post("/", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    service: QueryService = Depends(get_query_service)
) -> QueryResponse:
    """
    Execute a Cypher query against the knowledge graph.
    
    Security considerations:
    - Validates query syntax
    - Limits result size
    - Blocks destructive operations (CREATE, DELETE, SET, REMOVE)
    - Add rate limiting in production
    """
    try:
        # Only support Cypher (removed SPARQL)
        if request.type != "cypher":
            raise HTTPException(
                status_code=400,
                detail="Only Cypher queries are supported"
            )
        
        # Execute query via service
        result = await service.execute_cypher(request.query)
        
        return QueryResponse(
            columns=result["columns"],
            rows=result["rows"],
            count=len(result["rows"])
        )
        
    except ValueError as e:
        # Query validation errors
        logger.warning(f"Invalid query: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # Database or execution errors
        logger.error(f"Query execution failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}"
        )


@router.get("/examples")
async def get_query_examples() -> List[Dict[str, Any]]:
    """
    Get example Cypher queries for user reference.
    
    Returns curated queries based on actual KG schema.
    """
    from ..query_examples import CYPHER_EXAMPLES
    return CYPHER_EXAMPLES
