"""Backend-only application settings (Ollama + HTTP).

Lives entirely under backend/. Never imports frontend code.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env next to backend/ root (not monorepo root)
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_ENV_FILE = _BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_model: str = "qwen2.5:7b"
    ollama_base_url: str = "http://localhost:11434"
    temperature: float = 0.2
    researcher_max_iters: int = 4
    max_revisions: int = 2
    api_title: str = "Velora AI Lab API"
    api_version: str = "0.3.0"
    # Comma-separated frontend origins, or *. Env: CORS_ORIGINS
    cors_origins_raw: str = Field(default="*", validation_alias="CORS_ORIGINS")

    @property
    def cors_origins(self) -> list[str]:
        raw = (self.cors_origins_raw or "*").strip()
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
