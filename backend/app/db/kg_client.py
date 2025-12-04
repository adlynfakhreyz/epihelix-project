"""Database connection managers for Knowledge Graph backends.

Following Google's best practices:
- Connection pooling
- Lifecycle management (startup/shutdown)
- Health checks
- Graceful error handling
"""
from typing import Optional, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class KnowledgeGraphClient(ABC):
    """Abstract base class for KG database clients."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the database."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if database is healthy."""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: Optional[dict] = None) -> Any:
        """Execute a query and return results."""
        pass


class Neo4jClient(KnowledgeGraphClient):
    """Neo4j database client with connection pooling."""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self.driver = None
    
    async def connect(self) -> None:
        """Establish connection to Neo4j."""
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            logger.info(f"Connected to Neo4j at {self.uri}")
        except ImportError:
            logger.warning("neo4j driver not installed, using mock mode")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    async def health_check(self) -> bool:
        """Check Neo4j health."""
        if not self.driver:
            return False
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 AS health")
                return result.single()["health"] == 1
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            return False
    
    async def execute_query(self, query: str, params: Optional[dict] = None) -> Any:
        """Execute Cypher query."""
        if not self.driver:
            raise RuntimeError("Neo4j driver not connected")
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters=params or {})
            return [record.data() for record in result]


class SPARQLClient(KnowledgeGraphClient):
    """SPARQL endpoint client for RDF triple stores."""
    
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.session = None
    
    async def connect(self) -> None:
        """Initialize HTTP session for SPARQL queries."""
        try:
            import httpx
            self.session = httpx.AsyncClient(timeout=30.0)
            logger.info(f"SPARQL client initialized for {self.endpoint}")
        except ImportError:
            logger.warning("httpx not installed, using mock mode")
    
    async def disconnect(self) -> None:
        """Close HTTP session."""
        if self.session:
            await self.session.aclose()
            logger.info("SPARQL client closed")
    
    async def health_check(self) -> bool:
        """Check SPARQL endpoint health."""
        if not self.session:
            return False
        try:
            response = await self.session.get(self.endpoint)
            return response.status_code < 500
        except Exception as e:
            logger.error(f"SPARQL health check failed: {e}")
            return False
    
    async def execute_query(self, query: str, params: Optional[dict] = None) -> Any:
        """Execute SPARQL query."""
        if not self.session:
            raise RuntimeError("SPARQL client not connected")
        
        response = await self.session.post(
            self.endpoint,
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"}
        )
        response.raise_for_status()
        return response.json()


class MockKGClient(KnowledgeGraphClient):
    """Mock KG client for development and testing."""
    
    def __init__(self):
        self.connected = False
    
    async def connect(self) -> None:
        self.connected = True
        logger.info("Mock KG client connected")
    
    async def disconnect(self) -> None:
        self.connected = False
        logger.info("Mock KG client disconnected")
    
    async def health_check(self) -> bool:
        return self.connected
    
    async def execute_query(self, query: str, params: Optional[dict] = None) -> Any:
        """Return mock results."""
        logger.debug(f"Mock query: {query}")
        return []


# Global client instance (will be initialized in main.py)
kg_client: Optional[KnowledgeGraphClient] = None


def get_kg_client() -> KnowledgeGraphClient:
    """Dependency injection for KG client."""
    if kg_client is None:
        raise RuntimeError("KG client not initialized")
    return kg_client
