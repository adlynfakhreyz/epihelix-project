"""Search router - orchestration layer.

Following Google's best practices and Retriever pattern:
- Routers handle orchestration
- Thin HTTP layer, delegates to retriever and services
- Use dependency injection

New Pipeline (Retriever pattern):
1. Retriever: HybridRetriever handles search + reranking internally
2. SummaryService: Generate summary of top result (optional)

Old Pipeline (removed):
1. SearchService: keyword/semantic search
2. RerankerService: reranking
3. SummaryService: summary
"""
from fastapi import APIRouter, Query, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ..models import EntitySummary
from ..retrievers import BaseRetriever
from ..services.summary_service import SummaryService
from ..core.dependencies import container

router = APIRouter()


def get_retriever() -> BaseRetriever:
    """Dependency injection for retriever."""
    return container.get_retriever()


def get_summary_service() -> Optional[SummaryService]:
    """Dependency injection for summary service."""
    return container.get_summary_service()


class SearchResponse(BaseModel):
    """Search response with optional summary."""
    results: List[EntitySummary]
    summary: Optional[Dict[str, Any]] = None  # Summary of top result


class PaginatedSearchResponse(BaseModel):
    """Paginated search response."""
    results: List[EntitySummary]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    summary: Optional[Dict[str, Any]] = None  # Summary of top result


@router.get("/", response_model=PaginatedSearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Results per page"),
    rerank: bool = Query(True, description="Enable cross-encoder reranking"),
    summarize: bool = Query(True, description="Generate summary of top result"),
    retriever: BaseRetriever = Depends(get_retriever),
    summary_service: Optional[SummaryService] = Depends(get_summary_service)
):
    """Search entities with AI-powered enhancements.
    
    New Pipeline (Retriever pattern):
    1. HybridRetriever: keyword + semantic + reranking (all in one)
    2. SummaryService: summarize top result with neighbors (optional)
    
    Parameters:
    - q: Search query
    - rerank: Apply cross-encoder reranking (passed to retriever)
    - summarize: Generate AI summary of top result with neighbor context
    
    Returns:
    - results: Paginated list of entities
    - summary: AI-generated summary of top result (if enabled)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    candidate_pool_size = 50  # Candidates to retrieve before reranking
    
    # Step 1: Retrieve using HybridRetriever (keyword + semantic + reranking)
    logger.info(f"🔍 Step 1: Hybrid retrieval for '{q}' (rerank={rerank})")
    all_results = await retriever.retrieve(
        query=q,
        top_k=candidate_pool_size,
        use_reranking=rerank
    )
    
    logger.info(f"   Found {len(all_results)} results")
    
    # Step 2: Summarize top result (optional)
    summary_data = None
    if summarize and summary_service and all_results:
        logger.info(f"📝 Step 2: Generating summary for top result '{all_results[0].get('label')}'")
        try:
            summary_data = await summary_service.generate_entity_summary(
                entity_id=all_results[0]['id'],
                include_relations=True  # Include neighbors as context
            )
            logger.info(f"   ✓ Summary generated: {summary_data.get('summary', '')[:50]}...")
        except Exception as e:
            logger.warning(f"   ⚠️  Summarization failed: {e}")
    
    # Calculate pagination
    total = len(all_results)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_results = all_results[start_idx:end_idx]
    
    total_pages = (total + page_size - 1) // page_size
    has_next = page < total_pages
    has_prev = page > 1
    
    return PaginatedSearchResponse(
        results=[EntitySummary(**r) for r in page_results],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
        summary=summary_data
    )


@router.get("/suggestions")
async def get_suggestions(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    retriever: BaseRetriever = Depends(get_retriever)
):
    """Get search suggestions for autocomplete.
    
    Uses keyword retriever (fast) for suggestions.
    """
    results = await retriever.retrieve(
        query=q,
        top_k=limit,
        use_reranking=False  # Skip reranking for suggestions (speed)
    )
    
    # Extract labels for autocomplete
    suggestions = [
        {
            "label": r.get("label"),
            "type": r.get("type"),
            "id": r.get("id")
        }
        for r in results
    ]
    
    return suggestions
