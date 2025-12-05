"""Repository layer for data access abstraction."""
from .entity_repository import (
    EntityRepository,
    Neo4jEntityRepository
)

__all__ = [
    "EntityRepository",
    "Neo4jEntityRepository"
]
