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
        self.max_connection_pool_size = 50
        self.connection_timeout = 30.0
    
    async def connect(self) -> None:
        """Establish connection to Neo4j."""
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_pool_size=self.max_connection_pool_size,
                connection_timeout=self.connection_timeout,
                max_transaction_retry_time=10.0
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
    
    async def ensure_indexes(self) -> None:
        """Create required indexes if they don't exist."""
        if not self.driver:
            logger.warning("Cannot create indexes - driver not connected")
            return
        
        try:
            with self.driver.session(database=self.database) as session:
                # Check if fulltext index exists
                existing_indexes = session.run("SHOW INDEXES").data()
                index_names = [idx.get("name") for idx in existing_indexes]
                
                if "entitySearch" not in index_names:
                    logger.info("Creating fulltext index 'entitySearch'...")
                    # Use CREATE FULLTEXT INDEX syntax (compatible with Neo4j Aura)
                    # Index all searchable text properties for comprehensive search
                    session.run("""
                        CREATE FULLTEXT INDEX entitySearch IF NOT EXISTS
                        FOR (n:Country|Disease|Outbreak|VaccinationRecord|Organization|Vaccine)
                        ON EACH [n.name, n.fullName, n.label, n.description, n.summary, n.title, 
                                 n.code, n.iso_code, n.icd10, n.mesh, n.category, n.pathogen,
                                 n.causativeAgent, n.medicalSpecialty, n.prevention,
                                 n.acronym, n.role, n.vaccineName, n.manufacturer,
                                 n.capital, n.continent, n.wikipediaAbstract]
                    """)
                    logger.info("✓ Fulltext index 'entitySearch' created with comprehensive properties")
                else:
                    logger.info("✓ Fulltext index 'entitySearch' already exists")
                
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")


# Global client instance (will be initialized in main.py)
kg_client: Optional[KnowledgeGraphClient] = None


def get_kg_client() -> KnowledgeGraphClient:
    """Dependency injection for KG client."""
    if kg_client is None:
        raise RuntimeError("KG client not initialized")
    return kg_client
