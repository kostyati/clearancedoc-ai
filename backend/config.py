"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the backend service."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="CLEARANCEDOC_")

    app_name: str = "ClearanceDoc AI"
    environment: str = "development"

    # LLM provider config (Day 5+: wired up via routers/settings.py)
    llm_provider: str = "ollama"  # ollama | openai | anthropic | groq
    ollama_base_url: str = "http://ollama:11434"
    ollama_model: str = "llama3"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    groq_api_key: str | None = None

    # Storage
    chroma_persist_dir: str = "/data/chroma"
    upload_dir: str = "/data/uploads"

    # Chunking (Day 3: used by services/chunker.py)
    chunk_size: int = 512
    chunk_overlap: int = 50


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
