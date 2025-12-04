"""Chatbot service with RAG (Retrieval-Augmented Generation) architecture.

Clean architecture implementation:
- Depends on abstractions (EntityRepository, EmbedderService, LLMService)
- Modular design (retrieval → generation)
- Session management for conversation context
- Open-Closed principle (easy to extend with new features)

For production: Consider LangGraph for complex multi-turn workflows
"""
from typing import List, Dict, Any, Optional
import logging
from ..repositories.entity_repository import EntityRepository
from .embedder_service import EmbedderService
from .llm_service import LLMService

logger = logging.getLogger(__name__)


class ChatbotService:
    """RAG-based chatbot service.
    
    Architecture:
    1. Retrieve relevant entities from KG (semantic search)
    2. Extract context from entities
    3. Generate answer using LLM with context
    4. Track conversation history per session
    """
    
    def __init__(
        self,
        entity_repository: EntityRepository,
        embedder_service: EmbedderService,
        llm_service: LLMService,
        max_context: int = 5
    ):
        """Initialize chatbot service.
        
        Args:
            entity_repository: Access to knowledge graph
            embedder_service: Semantic search via embeddings
            llm_service: Text generation
            max_context: Max retrieved entities per query
        """
        self.entity_repo = entity_repository
        self.embedder = embedder_service
        self.llm = llm_service
        self.max_context = max_context
        
        # Simple in-memory session store (replace with Redis for production)
        self.sessions: Dict[str, List[Dict]] = {}
    
    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        include_history: bool = True
    ) -> Dict[str, Any]:
        """Process chat message with RAG.
        
        Args:
            message: User's question
            session_id: Session ID for conversation tracking
            include_history: Use conversation history for context
        
        Returns:
            {
                "reply": str,
                "sources": List[Dict],
                "session_id": str,
                "metadata": Dict
            }
        """
        # Step 1: Retrieve relevant entities (semantic search)
        retrieved_facts = await self._retrieve_context(message)
        
        # Step 2: Prepare context for LLM
        context_snippets = self._format_context(retrieved_facts)
        
        # Step 3: Add conversation history if available
        if session_id and include_history:
            history = self._get_recent_history(session_id, turns=3)
            if history:
                context_snippets.insert(0, f"Previous conversation:\n{history}")
        
        # Step 4: Generate answer
        answer_result = await self.llm.answer_question(
            question=message,
            retrieved_facts=context_snippets
        )
        
        # Step 5: Build response
        response = {
            "reply": answer_result["answer"],
            "sources": [
                {
                    "id": fact.get("id"),
                    "label": fact.get("label"),
                    "type": fact.get("type"),
                    "snippet": fact.get("snippet", "")[:200]
                }
                for fact in retrieved_facts
            ],
            "session_id": session_id,
            "metadata": {
                "retrieved_count": len(retrieved_facts),
                "context_used": answer_result.get("context_used", 0)
            }
        }
        
        # Step 6: Store in session history
        if session_id:
            self._add_to_history(session_id, message, response["reply"], retrieved_facts)
        
        return response
    
    async def _retrieve_context(self, query: str) -> List[Dict]:
        """Retrieve relevant entities using semantic search."""
        # Embed query
        query_embedding = await self.embedder.embed_query(query)
        
        # Get candidate entities (keyword pre-filter)
        candidates = await self.entity_repo.search(query, limit=50)
        
        if not candidates:
            return []
        
        # Embed candidates
        candidate_embeddings = await self.embedder.embed_entities(
            candidates,
            text_field="label"
        )
        
        # Find most similar
        similar_indices = await self.embedder.find_similar(
            query_embedding,
            candidate_embeddings,
            top_k=self.max_context
        )
        
        # Return top results
        return [candidates[idx] for idx, score in similar_indices]
    
    def _format_context(self, entities: List[Dict]) -> List[str]:
        """Format entities as text snippets for LLM."""
        snippets = []
        for entity in entities:
            label = entity.get("label", "Unknown")
            entity_type = entity.get("type", "Entity")
            snippet = entity.get("snippet", "No description")
            
            snippets.append(f"{label} ({entity_type}): {snippet}")
        
        return snippets
    
    def _get_recent_history(self, session_id: str, turns: int = 3) -> str:
        """Get recent conversation history."""
        history = self.sessions.get(session_id, [])
        if not history:
            return ""
        
        recent = history[-turns:]
        formatted = "\n".join([
            f"User: {turn['message']}\nAssistant: {turn['reply']}"
            for turn in recent
        ])
        
        return formatted
    
    def _add_to_history(
        self,
        session_id: str,
        message: str,
        reply: str,
        sources: List[Dict]
    ):
        """Add turn to conversation history."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        self.sessions[session_id].append({
            "message": message,
            "reply": reply,
            "sources": sources
        })
    
    def clear_session(self, session_id: str) -> bool:
        """Clear conversation history."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

