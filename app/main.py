"""
Velora AI Lab — FastAPI entrypoint (Phase-1).

Run:
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
    title=settings.api_title,
    version=settings.api_version,
    description=(
        "Phase-1 multi-agent research API: Supervisor + Researcher "
        "(Wikipedia + arXiv) via LangGraph + Ollama."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Schemas ----------


class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="Research topic / user task")
    thread_id: Optional[str] = Field(
        default=None,
        description="Optional LangGraph thread id for checkpoint continuity",
    )


class ResearchResponse(BaseModel):
    thread_id: str
    topic: str
    status: str
    next_agent: str
    supervisor_reasoning: str
    research_findings: str
    draft_report: str = ""
    critic_feedback: str = ""
    final_report: str = ""
    message_count: int = 0


class HealthResponse(BaseModel):
    status: str
    model: str
    ollama_base_url: str
    phase: str = "1"


# ---------- Routes ----------


@app.get("/", tags=["meta"])
def root() -> dict[str, Any]:
    return {
        "name": settings.api_title,
        "phase": 1,
        "docs": "/docs",
        "health": "/health",
        "research": "POST /research",
    }


@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model=settings.ollama_model,
        ollama_base_url=settings.ollama_base_url,
        phase="1",
    )


@app.post("/research", response_model=ResearchResponse, tags=["agents"])
def research(body: ResearchRequest) -> ResearchResponse:
    """
    Run the Phase-1 graph: Supervisor → Researcher → Supervisor → FINISH.
    Requires Ollama running with the configured model.
    """
    topic = body.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="topic must not be empty")

    thread_id = (body.thread_id or str(uuid.uuid4())).strip()
    graph = get_compiled_graph()

    state = initial_state(topic)
    state["messages"] = [HumanMessage(content=f"Research this topic: {topic}")]

    config = {"configurable": {"thread_id": thread_id}}

    try:
        final = graph.invoke(state, config=config)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=502,
            detail=f"Graph invocation failed: {exc}. Is Ollama running?",
        ) from exc

    findings = final.get("research_findings") or ""
    return ResearchResponse(
        thread_id=thread_id,
        topic=topic,
        status=str(final.get("status") or ""),
        next_agent=str(final.get("next_agent") or ""),
        supervisor_reasoning=str(final.get("supervisor_reasoning") or ""),
        research_findings=findings,
        draft_report=str(final.get("draft_report") or ""),
        critic_feedback=str(final.get("critic_feedback") or ""),
        final_report=str(final.get("final_report") or ""),
        message_count=len(final.get("messages") or []),
    )


@app.get("/graph", tags=["meta"])
def graph_info() -> dict[str, Any]:
    """Describe Phase-1 topology (for debugging / UI)."""
    return {
        "phase": 1,
        "nodes": ["supervisor", "researcher"],
        "flow": "START → supervisor ⇄ researcher → supervisor → END",
        "phase2_planned": ["writer", "critic"],
        "model": settings.ollama_model,
    }
