"""Application settings (Ollama + runtime)."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_model: str = "qwen2.5:7b"
    ollama_base_url: str = "http://localhost:11434"
    temperature: float = 0.2
    # Researcher tool-calling budget
    researcher_max_iters: int = 4
    # Writer←Critic revision loop budget (Phase-2)
    max_revisions: int = 2
    # HTTP
    api_title: str = "Velora AI Lab"
    api_version: str = "0.3.0"
    # CORS origins (comma-separated, or * for dev). Env: CORS_ORIGINS
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
