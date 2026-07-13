"""Local settings (Ollama + CORS)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV) if _ENV.exists() else ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_model: str = "qwen2.5:7b"
    ollama_base_url: str = "http://localhost:11434"
    temperature: float = 0.2
    researcher_max_iters: int = 4
    # Use * for local API called from Vercel + localhost (see main.py credentials=False)
    cors_origins_raw: str = Field(
        default="*",
        validation_alias="CORS_ORIGINS",
    )

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
