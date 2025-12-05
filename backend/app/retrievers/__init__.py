"""Retriever pattern implementation for knowledge graph queries.

Following industry standards (LangChain, LlamaIndex):
- BaseRetriever: Abstract interface for all retrievers
- KeywordRetriever: Full-text search using Neo4j indexes
- SemanticRetriever: Vector-based semantic search
- HybridRetriever: Combines keyword + semantic with reranking

Design principles:
- Simple interface: retrieve(query, top_k)
- No business logic (pure query execution)
- Composable (hybrid uses keyword + semantic)
- LangChain compatible (can wrap for future chatbot)
"""

from .base import BaseRetriever
from .keyword import KeywordRetriever
from .semantic import SemanticRetriever
from .hybrid import HybridRetriever

__all__ = [
    "BaseRetriever",
    "KeywordRetriever",
    "SemanticRetriever",
    "HybridRetriever",
]
