"""Chat router for RAG-based conversational interface.

Following best practices:
- Thin router delegating to chatbot service
- Session management
- Streaming support (can be added)
"""
from fastapi import APIRouter, Depends
from typing import Optional
import uuid

from ..models import ChatRequest, ChatResponse
from ..services.chatbot_service import ChatbotService
from ..core.dependencies import container

router = APIRouter()


def get_chatbot_service() -> ChatbotService:
    """Dependency injection for chatbot service."""
    return container.get_chatbot_service()


@router.post("/", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    session_id: Optional[str] = None,
    service: ChatbotService = Depends(get_chatbot_service)
):
    """Chat endpoint with RAG (Retrieval-Augmented Generation).
    
    Architecture:
    1. Retrieve relevant entities from KG
    2. Generate answer using LLM with context
    3. Return answer with sources
    
    For production, consider:
    - Streaming responses (Server-Sent Events)
    - LangGraph for complex orchestration
    - Memory/session persistence (Redis)
    """
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    response = await service.chat(
        message=req.message,
        session_id=session_id,
        include_history=True
    )
    
    return ChatResponse(**response)


@router.delete("/session/{session_id}")
async def clear_session(
    session_id: str,
    service: ChatbotService = Depends(get_chatbot_service)
):
    """Clear conversation history for a session."""
    service.clear_session(session_id)
    return {"status": "ok", "message": "Session cleared"}
