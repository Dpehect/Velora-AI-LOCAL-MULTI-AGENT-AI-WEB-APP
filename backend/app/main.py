"""
Velora AI Lab — FastAPI entrypoint (scaffold).

Run locally:
    uvicorn app.main:app --reload --app-dir .
    # or from backend/:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Velora AI Lab",
    version="0.3.0",
    description="Multi-agent research API (FastAPI + LangGraph + Ollama). Scaffold.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "velora-backend", "phase": "scaffold"}


# Routers will be mounted here, e.g.:
# from app.routers.agent import router as agent_router
# app.include_router(agent_router)
