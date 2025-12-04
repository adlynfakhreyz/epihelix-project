"""Dependency injection container.

Following Google's best practices for dependency management:
- Centralized dependency creation
- Lifecycle management
- Easy testing with mock injection
"""
from typing import Optional
import logging

from ..config.settings import settings
from ..db.kg_client import (
    KnowledgeGraphClient,
    Neo4jClient,
    MockKGClient
)
from ..repositories.entity_repository import (
    EntityRepository,
    Neo4jEntityRepository,
    MockEntityRepository
)
from ..services.search_service import SearchService
from ..services.entity_service import EntityService
from ..services.summary_service import SummaryService
from ..services.chatbot_service import ChatbotService
from ..services.llm_service import (
    BaseLLM,
    HuggingFaceLLM,
    HuggingFaceSpaceLLM,
    MockLLM,
    LLMService
)
from ..services.embedder_service import (
    BaseEmbedder,
    HuggingFaceEmbedder,
    MockEmbedder,
    EmbedderService
)

logger = logging.getLogger(__name__)


class Container:
    """Dependency injection container."""
    
    def __init__(self):
        self._kg_client: Optional[KnowledgeGraphClient] = None
        self._entity_repo: Optional[EntityRepository] = None
        self._llm_service: Optional[LLMService] = None
        self._embedder_service: Optional[EmbedderService] = None
        self._search_service: Optional[SearchService] = None
        self._entity_service: Optional[EntityService] = None
        self._summary_service: Optional[SummaryService] = None
        self._chatbot_service: Optional[ChatbotService] = None
    
    async def init_resources(self):
        """Initialize all resources (call on startup)."""
        logger.info("Initializing application resources...")
        
        # Initialize KG client
        kg_client = await self._create_kg_client()
        await kg_client.connect()
        self._kg_client = kg_client
        
        # Initialize repositories
        self._entity_repo = self._create_entity_repository(kg_client)
        
        # Initialize ML services
        self._llm_service = self._create_llm_service()
        self._embedder_service = self._create_embedder_service()
        
        # Initialize business services
        self._search_service = SearchService(
            entity_repository=self._entity_repo,
            embedder_service=self._embedder_service
        )
        self._entity_service = EntityService(self._entity_repo)
        self._summary_service = SummaryService(
            entity_repository=self._entity_repo,
            llm_service=self._llm_service
        )
        self._chatbot_service = ChatbotService(
            entity_repository=self._entity_repo,
            embedder_service=self._embedder_service,
            llm_service=self._llm_service
        )
        
        logger.info("Resources initialized successfully")
    
    async def shutdown_resources(self):
        """Cleanup resources (call on shutdown)."""
        logger.info("Shutting down resources...")
        
        if self._llm_service:
            await self._llm_service.close()
        if self._embedder_service:
            await self._embedder_service.close()
        if self._kg_client:
            await self._kg_client.disconnect()
        
        logger.info("Resources shut down")
    
    async def _create_kg_client(self) -> KnowledgeGraphClient:
        """Create Neo4j client for Neo4j Aura."""
        if settings.neo4j_uri and settings.neo4j_password:
            logger.info(f"Using Neo4j Aura: {settings.neo4j_uri}")
            return Neo4jClient(
                uri=settings.neo4j_uri,
                user=settings.neo4j_user,
                password=settings.neo4j_password,
                database=settings.neo4j_database
            )
        else:
            logger.warning("Neo4j not configured - using mock KG client")
            logger.info("To use Neo4j Aura, set NEO4J_URI and NEO4J_PASSWORD")
            return MockKGClient()
    
    def _create_entity_repository(self, client: KnowledgeGraphClient) -> EntityRepository:
        """Create entity repository for Neo4j or Mock."""
        if isinstance(client, Neo4jClient):
            return Neo4jEntityRepository(client)
        else:
            return MockEntityRepository()
    
    def _create_llm_service(self) -> LLMService:
        """Create LLM service with appropriate provider."""
        llm: BaseLLM
        
        if settings.llm_provider == "huggingface":
            logger.info(f"Using HuggingFace LLM: {settings.huggingface_llm_model}")
            llm = HuggingFaceLLM(
                model=settings.huggingface_llm_model,
                api_key=settings.huggingface_api_key,
                endpoint_url=settings.huggingface_llm_endpoint
            )
        elif settings.llm_provider == "huggingface_space":
            logger.info(f"Using HuggingFace Space: {settings.huggingface_space_url}")
            llm = HuggingFaceSpaceLLM(
                space_url=settings.huggingface_space_url,
                api_token=settings.huggingface_api_key
            )
        else:
            logger.info("Using mock LLM")
            llm = MockLLM()
        
        return LLMService(llm_provider=llm)
    
    def _create_embedder_service(self) -> EmbedderService:
        """Create embedder service with appropriate provider."""
        embedder: BaseEmbedder
        
        if settings.embedder_provider == "huggingface":
            logger.info(f"Using HuggingFace Embedder: {settings.huggingface_embedding_model}")
            embedder = HuggingFaceEmbedder(
                model=settings.huggingface_embedding_model,
                api_key=settings.huggingface_api_key,
                endpoint_url=settings.huggingface_embedding_endpoint
            )
        else:
            logger.info("Using mock embedder")
            embedder = MockEmbedder(dimension=settings.embedding_dimension)
        
        return EmbedderService(embedder=embedder)
    
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
    
    def get_llm_service(self) -> LLMService:
        """Get LLM service instance."""
        if not self._llm_service:
            raise RuntimeError("LLM service not initialized")
        return self._llm_service
    
    def get_embedder_service(self) -> EmbedderService:
        """Get embedder service instance."""
        if not self._embedder_service:
            raise RuntimeError("Embedder service not initialized")
        return self._embedder_service
    
    def get_search_service(self) -> SearchService:
        """Get search service instance."""
        if not self._search_service:
            raise RuntimeError("Search service not initialized")
        return self._search_service
    
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
    
    def get_chatbot_service(self) -> ChatbotService:
        """Get chatbot service instance."""
        if not self._chatbot_service:
            raise RuntimeError("Chatbot service not initialized")
        return self._chatbot_service


# Global container instance
container = Container()
