"""Generates cited answers from retrieved chunks using the configured LLM provider."""

from __future__ import annotations

import httpx

from config import Settings, get_settings
from services.retriever import RetrievedChunk

_SYSTEM_PROMPT = (
    "You are a document analysis assistant. Answer the question using only the "
    "provided context. Cite sources inline as (Page N). If the context does not "
    "contain the answer, say so explicitly."
)


class GenerationError(Exception):
    """Raised when the configured LLM provider fails to produce an answer."""


def _build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n\n".join(f"[Page {chunk.page_number}] {chunk.text}" for chunk in chunks)
    return f"{_SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"


async def generate_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    """Generate an answer to `question` grounded in `chunks` via the active LLM provider."""
    settings = get_settings()
    prompt = _build_prompt(question, chunks)

    if settings.llm_provider == "ollama":
        return await _generate_ollama(prompt, settings)
    if settings.llm_provider == "openai":
        return await _generate_openai_compatible(
            prompt,
            settings,
            base_url="https://api.openai.com/v1",
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )
    if settings.llm_provider == "groq":
        return await _generate_openai_compatible(
            prompt,
            settings,
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.groq_api_key,
            model=settings.groq_model,
        )
    if settings.llm_provider == "anthropic":
        return await _generate_anthropic(prompt, settings)

    raise GenerationError(f"Unsupported LLM provider: {settings.llm_provider}")


async def _generate_ollama(prompt: str, settings: Settings) -> str:
    async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
        try:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise GenerationError(f"Ollama request failed: {exc}") from exc
    return response.json()["response"].strip()


async def _generate_openai_compatible(
    prompt: str, settings: Settings, *, base_url: str, api_key: str | None, model: str
) -> str:
    if not api_key:
        raise GenerationError("Missing API key for the configured LLM provider")

    async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
        try:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}]},
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise GenerationError(f"LLM provider request failed: {exc}") from exc
    return response.json()["choices"][0]["message"]["content"].strip()


async def _generate_anthropic(prompt: str, settings: Settings) -> str:
    if not settings.anthropic_api_key:
        raise GenerationError("Missing API key for the configured LLM provider")

    async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
        try:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.anthropic_model,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise GenerationError(f"Anthropic request failed: {exc}") from exc
    return response.json()["content"][0]["text"].strip()
