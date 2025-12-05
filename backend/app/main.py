"""FastAPI application following Google's backend best practices.

Architecture:
- Layered design: routers -> services -> repositories -> database
- Dependency injection via container
- Configuration management
- Lifecycle management (startup/shutdown)
- Health checks and monitoring

For production:
- Add middleware (logging, metrics, tracing)
- Add rate limiting
- Add authentication/authorization
- Add caching layer (Redis)
- Add observability (Prometheus, OpenTelemetry)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config.settings import settings
from .core.dependencies import container
from .routers import search, entity, query, admin, summary

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize resources on application startup."""
    logger.info("Starting up application...")
    
    # Initialize dependency container (connects to Neo4j)
    await container.init_resources()
    
    # Ensure required indexes exist
    kg_client = container.get_kg_client()
    await kg_client.ensure_indexes()
    
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on application shutdown."""
    logger.info("Shutting down application...")
    await container.shutdown_resources()
    logger.info("Application shut down")


# Include routers
app.include_router(
    search.router,
    prefix=f"{settings.api_prefix}/search",
    tags=["search"]
)
app.include_router(
    entity.router,
    prefix=f"{settings.api_prefix}/entity",
    tags=["entity"]
)
app.include_router(
    summary.router,
    prefix=f"{settings.api_prefix}/summary",
    tags=["summary"]
)
app.include_router(
    query.router,
    prefix=f"{settings.api_prefix}/query",
    tags=["query"]
)
app.include_router(
    admin.router,
    prefix=f"{settings.api_prefix}/admin",
    tags=["admin"]
)


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}


@app.get("/health/ready")
async def readiness_check():
    """Readiness check (includes database health)."""
    kg_client = container.get_kg_client()
    kg_healthy = await kg_client.health_check()
    
    return {
        "status": "ready" if kg_healthy else "not_ready",
        "checks": {
            "knowledge_graph": "healthy" if kg_healthy else "unhealthy"
        }
    }


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }
