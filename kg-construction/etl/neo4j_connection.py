"""
Neo4j connection utilities for EpiHelix Knowledge Graph
"""
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Neo4jConnection:
    """Handle Neo4j database connections"""

    def __init__(self, uri=None, user=None, password=None):
        """
        Initialize Neo4j connection

        Args:
            uri: Neo4j connection URI (default: from .env)
            user: Neo4j username (default: from .env)
            password: Neo4j password (default: from .env)
        """
        # Load environment variables
        load_dotenv()

        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'epihelix123')

        self.driver = None

    def connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Test connection
            self.driver.verify_connectivity()
            logger.info(f"✓ Connected to Neo4j at {self.uri}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to Neo4j: {e}")
            return False

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("✓ Neo4j connection closed")

    def execute_query(self, query, parameters=None):
        """
        Execute a Cypher query

        Args:
            query: Cypher query string
            parameters: Query parameters dict

        Returns:
            Query result
        """
        if not self.driver:
            raise Exception("Not connected to Neo4j. Call connect() first.")

        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record for record in result]

    def execute_write(self, query, parameters=None):
        """
        Execute a write transaction

        Args:
            query: Cypher query string
            parameters: Query parameters dict
        """
        if not self.driver:
            raise Exception("Not connected to Neo4j. Call connect() first.")

        with self.driver.session() as session:
            session.execute_write(lambda tx: tx.run(query, parameters or {}))

    def create_constraints(self):
        """Create database constraints for data integrity"""
        constraints = [
            # Country constraints
            "CREATE CONSTRAINT country_code IF NOT EXISTS FOR (c:Country) REQUIRE c.code IS UNIQUE",

            # Disease constraints
            "CREATE CONSTRAINT disease_id IF NOT EXISTS FOR (d:Disease) REQUIRE d.id IS UNIQUE",

            # Outbreak constraints
            "CREATE CONSTRAINT outbreak_id IF NOT EXISTS FOR (o:Outbreak) REQUIRE o.id IS UNIQUE",

            # Vaccination record constraints
            "CREATE CONSTRAINT vaccination_id IF NOT EXISTS FOR (v:VaccinationRecord) REQUIRE v.id IS UNIQUE",
        ]

        logger.info("Creating database constraints...")
        for constraint in constraints:
            try:
                self.execute_write(constraint)
                logger.info(f"✓ {constraint.split('CONSTRAINT')[1].split('IF')[0].strip()}")
            except Exception as e:
                logger.warning(f"Constraint may already exist: {e}")

    def create_indexes(self):
        """Create database indexes for performance"""
        indexes = [
            "CREATE INDEX country_name IF NOT EXISTS FOR (c:Country) ON (c.name)",
            "CREATE INDEX disease_name IF NOT EXISTS FOR (d:Disease) ON (d.name)",
            "CREATE INDEX outbreak_date IF NOT EXISTS FOR (o:Outbreak) ON (o.date)",
            "CREATE INDEX outbreak_year IF NOT EXISTS FOR (o:Outbreak) ON (o.year)",
            "CREATE INDEX vaccination_year IF NOT EXISTS FOR (v:VaccinationRecord) ON (v.year)",
        ]

        logger.info("Creating database indexes...")
        for index in indexes:
            try:
                self.execute_write(index)
                logger.info(f"✓ {index.split('INDEX')[1].split('IF')[0].strip()}")
            except Exception as e:
                logger.warning(f"Index may already exist: {e}")

    def clear_database(self):
        """Clear all nodes and relationships (use with caution!)"""
        logger.warning("⚠️  Clearing database...")
        self.execute_write("MATCH (n) DETACH DELETE n")
        logger.info("✓ Database cleared")

    def get_stats(self):
        """Get database statistics"""
        queries = {
            'countries': "MATCH (c:Country) RETURN count(c) as count",
            'diseases': "MATCH (d:Disease) RETURN count(d) as count",
            'outbreaks': "MATCH (o:Outbreak) RETURN count(o) as count",
            'vaccination_records': "MATCH (v:VaccinationRecord) RETURN count(v) as count",

            'relationships': "MATCH ()-[r]->() RETURN count(r) as count"
        }

        stats = {}
        for name, query in queries.items():
            result = self.execute_query(query)
            stats[name] = result[0]['count'] if result else 0

        return stats


if __name__ == "__main__":
    # Test connection
    conn = Neo4jConnection()
    if conn.connect():
        print("Connection successful!")
        conn.create_constraints()
        conn.create_indexes()
        stats = conn.get_stats()
        print(f"\nDatabase Stats:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        conn.close()
