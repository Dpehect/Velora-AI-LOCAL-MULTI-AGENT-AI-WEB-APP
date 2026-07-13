"""
Velora backend — local FastAPI + LangGraph + Ollama.

Not for cloud deploy. Run on your machine:

    cd backend
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from app.config import settings
from app.graph.graph import get_compiled_graph
from app.graph.state import initial_state

app = FastAPI(
    title="Velora Local API",
    version="0.1.0",
    description="Local multi-agent research (Supervisor + Researcher). Ollama required.",
)

# CORS open for local Next.js (and optional Vercel UI → local API via tunnel)
_origins = settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins if _origins else ["*"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    task: str = Field(..., min_length=1, description="Research topic")
    thread_id: Optional[str] = Field(default=None, description="Optional thread id")


class RunResponse(BaseModel):
    thread_id: str
    task: str
    status: str
    next_agent: str
    supervisor_reasoning: str = ""
    research_findings: str = ""
    ok: bool = True
    error: Optional[str] = None


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "velora-backend-local",
        "docs": "/docs",
        "health": "/health",
        "run": "POST /run",
        "model": settings.ollama_model,
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "model": settings.ollama_model,
        "ollama_base_url": settings.ollama_base_url,
        "mode": "local",
        "nodes": ["supervisor", "researcher"],
    }


@app.post("/run", response_model=RunResponse)
def run(body: RunRequest) -> RunResponse:
    """
    Run Supervisor → Researcher → Supervisor → done on this machine.
    Requires Ollama with the configured model.
    """
    task = body.task.strip()
    if not task:
        raise HTTPException(status_code=400, detail="task must not be empty")

    thread_id = (body.thread_id or str(uuid.uuid4())).strip()
    graph = get_compiled_graph()
    state = initial_state(task)
    state["messages"] = [HumanMessage(content=f"Research this topic: {task}")]
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": 20,
    }

    try:
        final = graph.invoke(state, config=config)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"Graph failed: {exc}. Is Ollama running? (ollama serve / pull qwen2.5:7b)",
        ) from exc

    findings = str(final.get("research_findings") or "")
    status = str(final.get("status") or "")
    ok = bool(findings.strip()) and status != "error"

    return RunResponse(
        thread_id=thread_id,
        task=task,
        status=status,
        next_agent=str(final.get("next_agent") or "FINISH"),
        supervisor_reasoning=str(final.get("supervisor_reasoning") or ""),
        research_findings=findings,
        ok=ok,
        error=None if ok else "No research findings produced.",
    )
