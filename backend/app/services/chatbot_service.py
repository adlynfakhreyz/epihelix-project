"""Chatbot service - RAG-powered conversational AI.

Architecture:
1. Retrieve relevant entities from KG using HybridRetriever
2. Build context from entity properties and relationships
3. Generate answer using LLM (Groq) with context
4. Return answer with source entities

This implements Retrieval-Augmented Generation (RAG) pattern.
"""
from typing import Dict, List, Optional, Any
import logging

from ..retrievers import HybridRetriever, BaseRetriever
from ..utils.llm_groq import GroqLLM

logger = logging.getLogger(__name__)


class ChatbotService:
    """RAG-powered chatbot service for pandemic knowledge graph."""
    
    def __init__(
        self,
        retriever: HybridRetriever,
        llm: GroqLLM,
        max_context_entities: int = 5
    ):
        """Initialize chatbot service.
        
        Args:
            retriever: HybridRetriever for searching KG
            llm: GroqLLM for generating answers
            max_context_entities: Max entities to include in context
        """
        self.retriever = retriever
        self.llm = llm
        self.max_context_entities = max_context_entities
        
        # Simple in-memory session storage
        self._sessions: Dict[str, List[Dict[str, str]]] = {}
        
        logger.info("✅ ChatbotService initialized with RAG pipeline")
    
    async def chat(
        self,
        message: str,
        session_id: str,
        include_history: bool = True
    ) -> Dict[str, Any]:
        """Process a chat message and generate response.
        
        RAG Pipeline:
        1. Search KG for relevant entities
        2. Build context from entities
        3. Generate response with LLM
        4. Return response with sources
        
        Args:
            message: User message
            session_id: Session ID for conversation history
            include_history: Whether to include chat history
        
        Returns:
            {
                "message": str,           # AI response
                "sources": List[dict],    # Source entities
                "session_id": str         # Session ID
            }
        """
        logger.info(f"💬 Processing message: {message[:50]}...")
        
        try:
            # Step 1: Retrieve relevant entities from KG
            logger.info("🔍 Step 1: Retrieving relevant entities...")
            entities = await self.retriever.retrieve(
                query=message,
                top_k=self.max_context_entities,
                use_reranking=True
            )
            
            logger.info(f"   Found {len(entities)} relevant entities")
            
            # Step 2: Build context from entities
            logger.info("📝 Step 2: Building context...")
            context = self._build_context(entities)
            
            # Step 3: Get conversation history
            history = []
            if include_history and session_id in self._sessions:
                history = self._sessions[session_id][-6:]  # Last 3 exchanges
            
            # Step 4: Generate response with LLM
            logger.info("🤖 Step 3: Generating response with Groq LLM...")
            response_text = await self._generate_response(
                message=message,
                context=context,
                history=history
            )
            
            # Step 5: Update session history
            self._update_session(session_id, message, response_text)
            
            # Step 6: Format sources for frontend
            sources = self._format_sources(entities)
            
            logger.info(f"✅ Response generated: {response_text[:100]}...")
            
            return {
                "message": response_text,
                "sources": sources,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"❌ Chat error: {e}", exc_info=True)
            return {
                "message": f"I apologize, but I encountered an error processing your request. Please try again.",
                "sources": [],
                "session_id": session_id
            }
    
    def _build_context(self, entities: List[Dict[str, Any]]) -> List[str]:
        """Build context strings from retrieved entities.
        
        Args:
            entities: List of entity dicts from retriever
        
        Returns:
            List of context strings for LLM
        """
        context_parts = []
        
        for entity in entities:
            parts = []
            
            # Entity header
            label = entity.get("label", "Unknown")
            entity_type = entity.get("type", "Entity")
            parts.append(f"**{label}** ({entity_type})")
            
            # Key properties
            props = entity.get("properties", {})
            if props:
                for key, value in list(props.items())[:8]:  # Limit properties
                    if value and key not in ["id", "embedding"]:
                        # Clean up key name
                        clean_key = key.replace("_", " ").title()
                        parts.append(f"- {clean_key}: {value}")
            
            # Description if available
            desc = props.get("description") or props.get("abstract")
            if desc and len(desc) > 50:
                parts.append(f"- Description: {desc[:300]}...")
            
            context_parts.append("\n".join(parts))
        
        return context_parts
    
    async def _generate_response(
        self,
        message: str,
        context: List[str],
        history: List[Dict[str, str]]
    ) -> str:
        """Generate response using LLM with context and history.
        
        Args:
            message: Current user message
            context: Context from KG entities
            history: Previous conversation turns
        
        Returns:
            Generated response text
        """
        # Build history string
        history_text = ""
        if history:
            history_parts = []
            for turn in history:
                role = turn.get("role", "user")
                content = turn.get("content", "")
                history_parts.append(f"{role.title()}: {content}")
            history_text = "\n".join(history_parts)
        
        # Build full prompt
        context_text = "\n\n".join(context) if context else "No specific data found in knowledge graph."
        
        system_prompt = """You are EpiHelix AI, an expert assistant for pandemic and epidemiological data.

Your knowledge comes from a knowledge graph containing:
- 22 diseases (COVID-19, Malaria, Cholera, Tuberculosis, HIV/AIDS, etc.)
- 195+ countries with health statistics
- Outbreak data from 1980-2021
- Vaccination coverage records
- WHO and health organization data

Guidelines:
1. Answer based ONLY on the provided context from the knowledge graph
2. If context is insufficient, acknowledge it honestly
3. Use specific numbers and dates when available
4. Be concise but thorough
5. For disease questions, mention symptoms, affected regions, and statistics if available
6. Use bullet points for readability when listing multiple items"""

        prompt_parts = []
        
        if history_text:
            prompt_parts.append(f"Previous conversation:\n{history_text}\n")
        
        prompt_parts.append(f"Knowledge Graph Context:\n{context_text}\n")
        prompt_parts.append(f"User Question: {message}\n")
        prompt_parts.append("Answer:")
        
        prompt = "\n".join(prompt_parts)
        
        # Generate with Groq
        response = await self.llm.agenerate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=512,
            temperature=0.7
        )
        
        return response.strip()
    
    def _update_session(
        self,
        session_id: str,
        user_message: str,
        assistant_message: str
    ):
        """Update session history.
        
        Args:
            session_id: Session ID
            user_message: User's message
            assistant_message: Assistant's response
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        self._sessions[session_id].append({
            "role": "user",
            "content": user_message
        })
        self._sessions[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Keep only last 20 messages (10 exchanges)
        if len(self._sessions[session_id]) > 20:
            self._sessions[session_id] = self._sessions[session_id][-20:]
    
    def _format_sources(self, entities: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format entities as sources for frontend.
        
        Args:
            entities: List of entity dicts
        
        Returns:
            List of source dicts with id and label
        """
        sources = []
        for entity in entities[:5]:  # Max 5 sources
            sources.append({
                "id": entity.get("id", ""),
                "label": entity.get("label", "Unknown"),
                "type": entity.get("type", "Entity")
            })
        return sources
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session.
        
        Args:
            session_id: Session ID to clear
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"🗑️ Cleared session: {session_id}")