"""Pydantic request/response models shared across routers."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response body for the health check endpoint."""

    status: str
    app_name: str
    environment: str


class DocumentStatus(str, Enum):
    """Lifecycle states for an uploaded document."""

    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class DocumentResponse(BaseModel):
    """Metadata returned to the client for an uploaded document."""

    id: str
    filename: str
    status: DocumentStatus
    page_count: int | None = None
    uploaded_at: datetime


class ChatRequest(BaseModel):
    """A user question scoped to one or more documents."""

    document_ids: list[str]
    question: str


class Citation(BaseModel):
    """A source snippet backing part of an answer."""

    document_id: str
    page_number: int
    text: str


class ChatResponse(BaseModel):
    """An answer with supporting citations."""

    answer: str
    citations: list[Citation]


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"


class SettingsUpdateRequest(BaseModel):
    """Payload for updating the active LLM provider configuration."""

    provider: LLMProvider
    model: str
    api_key: str | None = None
