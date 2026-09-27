from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Permission-Aware Multi-Tenant RAG"
    API_V1_STR: str = "/api/v1"
    
    # Security & JWT
    SECRET_KEY: str = "enterprise-super-secure-secret-key-change-in-production-123456"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Database
    # Defaults to SQLite for immediate local execution & pytest without requiring local Docker daemon;
    # Can be overridden by DATABASE_URL env var to postgresql+psycopg://postgres:postgres@localhost:5432/rag_db
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./rag_platform.db")
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    USE_MOCK_LLM: bool = os.getenv("USE_MOCK_LLM", "true").lower() in ("true", "1", "yes")
    
    # Embedding Settings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 384  # Standard dense embedding dimension
    
    # Retrieval & RAG
    SIMILARITY_THRESHOLD: float = 0.35
    TOP_K_CHUNKS: int = 5
    HYBRID_ALPHA: float = 0.6  # 0.6 vector, 0.4 BM25 keyword
    
    # Tenant & Cache
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 300
    
    # Classification hierarchy for ABAC (numeric value for comparison)
    CLASSIFICATION_LEVELS: dict = {
        "Public": 1,
        "Internal": 2,
        "Confidential": 3,
        "Restricted": 4,
    }

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
