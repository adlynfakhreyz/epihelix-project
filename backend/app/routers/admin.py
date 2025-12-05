"""Admin router for system diagnostics and maintenance.

Endpoints for checking system health, indexes, and configurations.
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any, List

from ..core.dependencies import container
from ..db.kg_client import KnowledgeGraphClient

router = APIRouter()


def get_kg_client() -> KnowledgeGraphClient:
    """Dependency injection for KG client."""
    return container.get_kg_client()


@router.get("/health")
async def health_check(client: KnowledgeGraphClient = Depends(get_kg_client)):
    """Check if Neo4j connection is healthy."""
    is_healthy = await client.health_check()
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "database": "neo4j"
    }


@router.get("/indexes")
async def list_indexes(client: KnowledgeGraphClient = Depends(get_kg_client)):
    """List all indexes in Neo4j."""
    if not client.driver:
        return {"error": "Neo4j driver not connected"}
    
    with client.driver.session(database=client.database) as session:
        result = session.run("SHOW INDEXES")
        indexes = result.data()
    
    return {
        "total": len(indexes),
        "indexes": indexes
    }


@router.get("/indexes/fulltext/test")
async def test_fulltext_index(
    query: str = "polio",
    client: KnowledgeGraphClient = Depends(get_kg_client)
):
    """Test if fulltext index 'entitySearch' works."""
    if not client.driver:
        return {"error": "Neo4j driver not connected"}
    
    try:
        with client.driver.session(database=client.database) as session:
            # Test fulltext index
            result = session.run("""
                CALL db.index.fulltext.queryNodes('entitySearch', $query)
                YIELD node, score
                RETURN node.name as name, labels(node) as labels, score
                LIMIT 5
            """, {"query": query})
            
            results = result.data()
            
            return {
                "status": "working",
                "index_name": "entitySearch",
                "test_query": query,
                "results_count": len(results),
                "results": results
            }
    except Exception as e:
        return {
            "status": "failed",
            "index_name": "entitySearch",
            "error": str(e),
            "note": "Index may not exist or fulltext search not supported"
        }


@router.get("/indexes/vector/test")
async def test_vector_index(
    client: KnowledgeGraphClient = Depends(get_kg_client)
):
    """Check if vector index exists and count nodes with embeddings."""
    if not client.driver:
        return {"error": "Neo4j driver not connected"}
    
    with client.driver.session(database=client.database) as session:
        # Count nodes with embeddings
        result = session.run("""
            MATCH (n)
            WHERE n.embedding IS NOT NULL
            RETURN count(n) as count, labels(n)[0] as type
        """)
        
        embedding_stats = result.data()
        
        # Check for vector indexes
        indexes_result = session.run("SHOW INDEXES")
        all_indexes = indexes_result.data()
        vector_indexes = [
            idx for idx in all_indexes 
            if 'vector' in idx.get('type', '').lower() or 'Embedding' in idx.get('name', '')
        ]
    
    return {
        "vector_indexes": vector_indexes,
        "nodes_with_embeddings": embedding_stats,
        "ready_for_semantic_search": len(embedding_stats) > 0 and len(vector_indexes) > 0
    }


@router.post("/indexes/create")
async def create_indexes(client: KnowledgeGraphClient = Depends(get_kg_client)):
    """Manually trigger index creation."""
    if not client.driver:
        return {"error": "Neo4j driver not connected"}
    
    try:
        await client.ensure_indexes()
        return {
            "status": "success",
            "message": "Index creation triggered. Check /admin/indexes to verify."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/stats")
async def database_stats(client: KnowledgeGraphClient = Depends(get_kg_client)):
    """Get database statistics."""
    if not client.driver:
        return {"error": "Neo4j driver not connected"}
    
    with client.driver.session(database=client.database) as session:
        # Count nodes by type
        nodes_result = session.run("""
            MATCH (n)
            RETURN labels(n)[0] as type, count(n) as count
            ORDER BY count DESC
        """)
        
        # Count relationships
        rels_result = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) as type, count(r) as count
            ORDER BY count DESC
        """)
        
        nodes = nodes_result.data()
        relationships = rels_result.data()
    
    return {
        "nodes": nodes,
        "relationships": relationships,
        "total_nodes": sum(n['count'] for n in nodes),
        "total_relationships": sum(r['count'] for r in relationships)
    }
