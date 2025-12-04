"""Application configuration using pydantic settings.

Following Google's best practices for config management:
- Environment-based configuration
- Type validation
- Defaults for development
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # App
    app_name: str = "EpiHelix API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # API
    api_prefix: str = "/api"
    cors_origins: list[str] = ["*"]
    
    # Neo4j Aura (Knowledge Graph)
    # Get credentials from: https://console.neo4j.io/
    neo4j_uri: Optional[str] = None  # e.g., "neo4j+s://xxxxx.databases.neo4j.io"
    neo4j_user: str = "neo4j"
    neo4j_password: Optional[str] = None
    neo4j_database: str = "neo4j"
    
    # Vector DB (for semantic search)
    # Neo4j 5+ has native vector support - no separate vector DB needed
    vector_db_type: str = "neo4j"  # "neo4j" or "mock"
    
    # ===== LLM Configuration (Self-Hosted) =====
    llm_provider: str = "mock"  # "huggingface", "huggingface_space", "mock"
    
    # HuggingFace Settings
    huggingface_api_key: Optional[str] = None  # Optional for public models
    huggingface_llm_model: str = "meta-llama/Llama-3.2-3B-Instruct"
    huggingface_llm_endpoint: Optional[str] = None  # Custom endpoint URL
    
    # HuggingFace Space Settings (for self-hosted Gradio apps)
    huggingface_space_url: Optional[str] = None
    
    # LLM Generation Parameters
    llm_temperature: float = 0.7
    llm_max_tokens: int = 512
    
    # ===== Embedder Configuration (Self-Hosted) =====
    embedder_provider: str = "mock"  # "huggingface", "mock"
    
    # Embedding Model Settings
    huggingface_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    huggingface_embedding_endpoint: Optional[str] = None
    embedding_dimension: int = 384  # Must match model dimension
    
    # External data sources (optional - for future ETL)
    wikidata_endpoint: str = "https://query.wikidata.org/sparql"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
