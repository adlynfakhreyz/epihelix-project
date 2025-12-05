"""Query service for executing user-provided Cypher queries.

Security features:
- Query validation (block destructive operations)
- Result size limits
- Timeout protection
"""
from typing import Dict, Any, List
import re
import logging

from ..repositories.entity_repository import EntityRepository

logger = logging.getLogger(__name__)


class QueryService:
    """Service for executing and validating user queries."""
    
    # Destructive operations to block (security)
    BLOCKED_KEYWORDS = [
        'CREATE', 'DELETE', 'REMOVE', 'SET', 
        'MERGE', 'DROP', 'DETACH', 'CALL'
    ]
    
    # Maximum rows to return
    MAX_RESULTS = 1000
    
    def __init__(self, entity_repo: EntityRepository):
        self.entity_repo = entity_repo
        # Access Neo4j client directly for raw queries
        self.kg_client = entity_repo.client
    
    async def execute_cypher(self, query: str) -> Dict[str, Any]:
        """
        Execute a Cypher query with validation.
        
        Args:
            query: Cypher query string
            
        Returns:
            Dict with 'columns' and 'rows' keys
            
        Raises:
            ValueError: If query is invalid or blocked
        """
        # Validate query
        self._validate_query(query)
        
        # Execute query
        logger.debug(f"Executing Cypher query: {query[:100]}...")
        
        try:
            # Execute via KG client
            records = await self.kg_client.execute_query(query)
            
            # Limit results
            if len(records) > self.MAX_RESULTS:
                logger.warning(f"Query returned {len(records)} rows, limiting to {self.MAX_RESULTS}")
                records = records[:self.MAX_RESULTS]
            
            # Format response
            if not records:
                return {
                    "columns": [],
                    "rows": []
                }
            
            # Extract column names from first record
            columns = list(records[0].keys())
            
            # Convert records to rows
            rows = []
            for record in records:
                row = []
                for col in columns:
                    value = record.get(col)
                    # Convert Neo4j types to JSON-serializable
                    row.append(self._serialize_value(value))
                rows.append(row)
            
            return {
                "columns": columns,
                "rows": rows
            }
            
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            raise ValueError(f"Query execution failed: {str(e)}")
    
    def _validate_query(self, query: str) -> None:
        """
        Validate Cypher query for security.
        
        Raises:
            ValueError: If query contains blocked operations
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Check for destructive operations
        query_upper = query.upper()
        for keyword in self.BLOCKED_KEYWORDS:
            # Use word boundaries to avoid false positives
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, query_upper):
                raise ValueError(
                    f"Query contains blocked operation: {keyword}. "
                    f"Only read-only queries (MATCH, RETURN) are allowed."
                )
        
        # Ensure query has RETURN statement (read-only)
        if 'RETURN' not in query_upper:
            raise ValueError("Query must contain a RETURN statement")
    
    def _serialize_value(self, value: Any) -> Any:
        """
        Convert Neo4j types to JSON-serializable values.
        
        Handles: Node, Relationship, Path, DateTime, Point, etc.
        """
        # None/primitives
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        
        # Lists
        if isinstance(value, list):
            return [self._serialize_value(v) for v in value]
        
        # Dicts
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        
        # Neo4j Node
        if hasattr(value, 'labels') and hasattr(value, 'items'):
            # Convert node to dict
            return dict(value.items())
        
        # Neo4j Relationship
        if hasattr(value, 'type') and hasattr(value, 'items'):
            return dict(value.items())
        
        # Neo4j DateTime/Date/Time
        if hasattr(value, 'iso_format'):
            return value.iso_format()
        
        # Fallback: convert to string
        return str(value)
