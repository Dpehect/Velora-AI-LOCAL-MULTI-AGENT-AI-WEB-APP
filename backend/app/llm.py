"""ChatOllama factory — local qwen2.5:7b via Ollama."""

from __future__ import annotations

from langchain_ollama import ChatOllama

from app.config import settings


def get_llm(*, temperature: float | None = None) -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.temperature if temperature is None else temperature,
    )
