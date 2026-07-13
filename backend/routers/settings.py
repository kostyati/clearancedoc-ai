"""Endpoints for configuring the active LLM provider."""

from fastapi import APIRouter, HTTPException

from config import get_settings
from models.schemas import LLMProvider, SettingsUpdateRequest
from services import generator, settings_store
from services.generator import GenerationError

router = APIRouter(prefix="/settings", tags=["settings"])

_DEFAULT_MODEL_BY_PROVIDER = {
    LLMProvider.OLLAMA: lambda s: s.ollama_model,
    LLMProvider.OPENAI: lambda s: s.openai_model,
    LLMProvider.ANTHROPIC: lambda s: s.anthropic_model,
    LLMProvider.GROQ: lambda s: s.groq_model,
}


@router.get("")
async def get_settings_status() -> dict[str, str]:
    """Return the currently active LLM provider and model."""
    override = settings_store.get_active()
    if override is not None:
        return {"provider": override.provider.value, "model": override.model}

    settings = get_settings()
    provider = LLMProvider(settings.llm_provider)
    return {"provider": provider.value, "model": _DEFAULT_MODEL_BY_PROVIDER[provider](settings)}


@router.put("")
async def update_settings(request: SettingsUpdateRequest) -> dict[str, str]:
    """Validate the given LLM provider configuration and persist it if it works."""
    try:
        await generator.test_connection(request.provider, request.model, request.api_key)
    except GenerationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    settings_store.save(request)
    return {"provider": request.provider.value, "model": request.model}
