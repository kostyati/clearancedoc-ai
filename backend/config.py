"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the backend service."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CLEARANCEDOC_")

    app_name: str = "ClearanceDoc AI"
    environment: str = "development"

    # LLM provider config (Day 5+: provider/model selection wired up via routers/settings.py)
    llm_provider: str = "ollama"  # ollama | openai | anthropic | groq
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-haiku-latest"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    llm_timeout_seconds: float = 60.0

    # Storage
    chroma_persist_dir: str = "/data/chroma"
    upload_dir: str = "/data/uploads"
    db_path: str = "/data/clearancedoc.db"

    # Chunking (Day 3: used by services/chunker.py)
    chunk_size: int = 512
    chunk_overlap: int = 50

    # Retrieval (Day 4: used by services/rag_pipeline.py)
    retrieval_top_k: int = 5


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
