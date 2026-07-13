"""ChatOllama factory — shared by Supervisor and Researcher."""

from __future__ import annotations

from langchain_ollama import ChatOllama

from app.config import settings


def get_llm(*, temperature: float | None = None, model: str | None = None) -> ChatOllama:
    """Return a configured ChatOllama client (default: qwen2.5:7b)."""
    return ChatOllama(
        model=model or settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.temperature if temperature is None else temperature,
    )
