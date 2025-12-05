"""Dependency injection container.

Following Google's best practices for dependency management:
- Centralized dependency creation
- Lifecycle management
- Easy testing with mock injection

New architecture (Retriever pattern):
- Retrievers: Search strategies (keyword, semantic, hybrid)
- Utils: Pure utilities (embedder, reranker, llm)
- Services: Business logic only (summary_service)
"""
from typing import Optional
import logging

from ..config.settings import settings
from ..db.kg_client import (
    KnowledgeGraphClient,
    Neo4jClient
)
from ..repositories.entity_repository import (
    EntityRepository,
    Neo4jEntityRepository
)
from ..retrievers import (
    BaseRetriever,
    KeywordRetriever,
    SemanticRetriever,
    HybridRetriever
)
from ..utils import (
    BaseEmbedder,
    KaggleEmbedder,
    BaseReranker,
    KaggleReranker,
    BaseLLM,
    KaggleLLM,
    GroqLLM
)
from ..services.entity_service import EntityService
from ..services.summary_service import SummaryService
from ..services.query_service import QueryService
from ..services.chatbot_service import ChatbotService

logger = logging.getLogger(__name__)


class Container:
    """Dependency injection container."""
    
    def __init__(self):
        self._kg_client: Optional[KnowledgeGraphClient] = None
        self._entity_repo: Optional[EntityRepository] = None
        
        # Utilities (direct use, no wrappers)
        self._embedder: Optional[BaseEmbedder] = None
        self._reranker: Optional[BaseReranker] = None
        self._llm: Optional[BaseLLM] = None
        self._groq_llm: Optional[GroqLLM] = None
        
        # Retriever (search strategy)
        self._retriever: Optional[BaseRetriever] = None
        
        # Services (business logic only)
        self._entity_service: Optional[EntityService] = None
        self._summary_service: Optional[SummaryService] = None
        self._query_service: Optional[QueryService] = None
        self._chatbot_service: Optional[ChatbotService] = None
    
    async def init_resources(self):
        """Initialize all resources (call on startup)."""
        logger.info("Initializing application resources...")
        
        # Initialize KG client
        kg_client = await self._create_kg_client()
        await kg_client.connect()
        self._kg_client = kg_client
        
        # Ensure required indexes exist
        await kg_client.ensure_indexes()
        
        # Initialize repositories
        self._entity_repo = self._create_entity_repository(kg_client)
        
        # Initialize utilities (direct use, no wrappers)
        self._llm = self._create_llm()
        self._embedder = self._create_embedder()
        self._reranker = self._create_reranker()
        
        # Initialize retriever (search strategy)
        self._retriever = HybridRetriever(
            entity_repository=self._entity_repo,
            embedder=self._embedder,
            reranker=self._reranker,
            use_reranking=True,
            keyword_weight=0.5
        )

        # Initialize Groq LLM (shared for chatbot and summary)
        self._groq_llm = self._create_groq_llm()

        # Initialize business services (business logic only)
        self._entity_service = EntityService(self._entity_repo)
        self._summary_service = SummaryService(
            entity_repository=self._entity_repo,
            groq_llm=self._groq_llm
        )
        self._query_service = QueryService(entity_repo=self._entity_repo)

        # Initialize chatbot service
        if self._groq_llm:
            self._chatbot_service = ChatbotService(
                retriever=self._retriever,
                llm=self._groq_llm,
                max_context_entities=5
            )
        else:
            logger.warning("ChatbotService not initialized (Groq LLM not configured)")
        
        logger.info("Resources initialized successfully")
    
    async def shutdown_resources(self):
        """Cleanup resources (call on shutdown)."""
        logger.info("Shutting down resources...")
        
        # Close utilities
        if self._embedder:
            await self._embedder.close()
        if self._reranker:
            await self._reranker.close()
        if self._llm:
            await self._llm.close()
        if self._kg_client:
            await self._kg_client.disconnect()
        
        logger.info("Resources shut down")
    
    async def _create_kg_client(self) -> KnowledgeGraphClient:
        """Create Neo4j client for Neo4j Aura."""
        if not settings.neo4j_uri or not settings.neo4j_password:
            raise ValueError(
                "Neo4j configuration required! Set NEO4J_URI and NEO4J_PASSWORD in .env file"
            )
        
        logger.info(f"Connecting to Neo4j at: {settings.neo4j_uri}")
        return Neo4jClient(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password,
            database=settings.neo4j_database
        )
    
    def _create_entity_repository(self, client: KnowledgeGraphClient) -> EntityRepository:
        """Create entity repository for Neo4j."""
        logger.info("Initializing Neo4j entity repository")
        return Neo4jEntityRepository(client)
    
    def _create_llm(self) -> Optional[BaseLLM]:
        """Create Kaggle LLM utility."""
        if settings.llm_provider == "kaggle" and settings.kaggle_ai_endpoint:
            logger.info(f"✅ Using Kaggle LLM: {settings.kaggle_ai_endpoint}")
            
            return KaggleLLM(
                endpoint_url=settings.kaggle_ai_endpoint,
                timeout=60
            )
        else:
            logger.info("⚠️ Kaggle LLM not configured")
            return None
        
    def _create_groq_llm(self) -> Optional[GroqLLM]:
        """Create Groq LLM for chatbot."""
        if settings.chatbot_llm_provider == "groq" and settings.groq_api_key:
            logger.info(f"✅ Using Groq LLM: {settings.groq_model}")
            return GroqLLM(
                api_key=settings.groq_api_key,
                model=settings.groq_model,
                temperature=settings.chatbot_temperature,
                max_tokens=settings.chatbot_max_tokens
            )
        else:
            logger.warning("⚠️ Groq LLM not configured (set GROQ_API_KEY and CHATBOT_LLM_PROVIDER=groq)")
            return None
    
    def _create_embedder(self) -> BaseEmbedder:
        """Create Kaggle embedder utility."""
        if settings.kaggle_ai_endpoint:
            logger.info(f"Using Kaggle Embedder: {settings.kaggle_ai_endpoint}")
            return KaggleEmbedder(
                endpoint_url=settings.kaggle_ai_endpoint,
                dimension=settings.embedding_dimension,
                timeout=30
            )
        else:
            raise ValueError("Kaggle AI endpoint required! Set KAGGLE_AI_ENDPOINT in .env")
    
    def _create_reranker(self) -> BaseReranker:
        """Create Kaggle reranker utility."""
        if settings.kaggle_ai_endpoint:
            logger.info(f"Using Kaggle Reranker: {settings.kaggle_ai_endpoint}")
            return KaggleReranker(
                endpoint_url=settings.kaggle_ai_endpoint,
                timeout=30
            )
        else:
            raise ValueError("Kaggle AI endpoint required! Set KAGGLE_AI_ENDPOINT in .env")
    
    # Getters for dependency injection
    
    def get_kg_client(self) -> KnowledgeGraphClient:
        """Get KG client instance."""
        if not self._kg_client:
            raise RuntimeError("KG client not initialized")
        return self._kg_client
    
    def get_entity_repository(self) -> EntityRepository:
        """Get entity repository instance."""
        if not self._entity_repo:
            raise RuntimeError("Entity repository not initialized")
        return self._entity_repo
    
    def get_embedder(self) -> BaseEmbedder:
        """Get embedder utility instance."""
        if not self._embedder:
            raise RuntimeError("Embedder not initialized")
        return self._embedder
    
    def get_reranker(self) -> BaseReranker:
        """Get reranker utility instance."""
        if not self._reranker:
            raise RuntimeError("Reranker not initialized")
        return self._reranker
    
    def get_retriever(self) -> BaseRetriever:
        """Get retriever instance (HybridRetriever)."""
        if not self._retriever:
            raise RuntimeError("Retriever not initialized")
        return self._retriever
    
    def get_entity_service(self) -> EntityService:
        """Get entity service instance."""
        if not self._entity_service:
            raise RuntimeError("Entity service not initialized")
        return self._entity_service
    
    def get_summary_service(self) -> SummaryService:
        """Get summary service instance."""
        if not self._summary_service:
            raise RuntimeError("Summary service not initialized")
        return self._summary_service
    
    def get_query_service(self) -> QueryService:
        """Get query service instance."""
        if not self._query_service:
            raise RuntimeError("Query service not initialized")
        return self._query_service
    
    def get_chatbot_service(self) -> ChatbotService:
        """Get chatbot service instance."""
        if not self._chatbot_service:
            raise RuntimeError("Chatbot service not initialized. Check GROQ_API_KEY in .env")
        return self._chatbot_service


# Global container instance
container = Container()


# FastAPI dependency injection wrappers
def get_kg_client() -> KnowledgeGraphClient:
    """FastAPI dependency: Get KG client."""
    return container.get_kg_client()


def get_entity_repository() -> EntityRepository:
    """FastAPI dependency: Get entity repository."""
    return container.get_entity_repository()


def get_embedder() -> BaseEmbedder:
    """FastAPI dependency: Get embedder utility."""
    return container.get_embedder()


def get_reranker() -> BaseReranker:
    """FastAPI dependency: Get reranker utility."""
    return container.get_reranker()


def get_retriever() -> BaseRetriever:
    """FastAPI dependency: Get retriever (HybridRetriever)."""
    return container.get_retriever()


def get_entity_service() -> EntityService:
    """FastAPI dependency: Get entity service."""
    return container.get_entity_service()


def get_summary_service() -> SummaryService:
    """FastAPI dependency: Get summary service."""
    return container.get_summary_service()


def get_query_service() -> QueryService:
    """FastAPI dependency: Get query service."""
    return container.get_query_service()

def get_chatbot_service() -> ChatbotService:
    """FastAPI dependency: Get chatbot service."""
    return container.get_chatbot_service()