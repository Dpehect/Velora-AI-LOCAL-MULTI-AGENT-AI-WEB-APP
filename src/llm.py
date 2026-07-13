"""Shared Ollama chat model factory."""

from __future__ import annotations

from langchain_ollama import ChatOllama

from src.config import settings


def get_llm(*, temperature: float | None = None) -> ChatOllama:
    """Create a ChatOllama instance bound to the local Ollama server."""
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.temperature if temperature is None else temperature,
    )
