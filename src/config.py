"""Central configuration for the local multi-agent system."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Runtime settings. All inference stays local via Ollama."""

    # Ollama
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    temperature: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))

    # Researcher tool-calling loop
    max_tool_iterations: int = int(os.getenv("MAX_TOOL_ITERATIONS", "4"))

    # Wikipedia / Arxiv limits (keep context manageable for 7B models)
    wiki_top_k: int = int(os.getenv("WIKI_TOP_K", "3"))
    wiki_chars: int = int(os.getenv("WIKI_CHARS", "2500"))
    arxiv_top_k: int = int(os.getenv("ARXIV_TOP_K", "3"))
    arxiv_chars: int = int(os.getenv("ARXIV_CHARS", "2500"))

    # Checkpoint DB (SQLite, local file)
    checkpoint_db: str = os.getenv("CHECKPOINT_DB", "checkpoints.db")


settings = Settings()
