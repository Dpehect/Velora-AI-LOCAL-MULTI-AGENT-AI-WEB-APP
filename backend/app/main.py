"""
Velora AI Lab — FastAPI entrypoint (Phase-3).

Run:
    uvicorn app.main:app --reload
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.agent import router as agent_router
from app.schemas.agent import HealthResponse

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=(
        "Phase-3 multi-agent research API: Supervisor + Researcher + Writer + Critic "
        "via LangGraph + Ollama. Trigger the pipeline with POST /api/agent/run."
    ),
)

# CORS — open for local frontend development (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent routes: /api/agent/run, /api/agent/graph
app.include_router(agent_router)


@app.get("/", tags=["meta"])
def root() -> dict[str, Any]:
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "phase": 3,
        "docs": "/docs",
        "health": "/health",
        "run": "POST /api/agent/run",
        "graph": "GET /api/agent/graph",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["meta"],
    summary="Liveness / config probe",
)
def health() -> HealthResponse:
    """Simple health check for load balancers and frontend boot probes."""
    return HealthResponse(
        status="ok",
        model=settings.ollama_model,
        ollama_base_url=settings.ollama_base_url,
        phase="3",
        graph_nodes=["supervisor", "researcher", "writer", "critic"],
    )
