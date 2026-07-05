"""Endpoints for configuring the active LLM provider."""

from fastapi import APIRouter

from models.schemas import SettingsUpdateRequest

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("")
async def get_settings_status() -> dict[str, str]:
    """Return the currently active LLM provider and model.

    TODO(Day 5): read from persisted settings rather than defaults.
    """
    return {"provider": "ollama", "model": "llama3"}


@router.put("")
async def update_settings(request: SettingsUpdateRequest) -> dict[str, str]:
    """Update the active LLM provider configuration.

    TODO(Day 5): validate API key with a test connection call, persist config.
    """
    return {"provider": request.provider.value, "model": request.model}
