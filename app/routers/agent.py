"""
Agent API router — Phase-3.

POST /api/agent/run  → run multi-agent graph
GET  /api/agent/graph → topology info (frontend helper)
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.schemas.agent import AgentRunRequest, AgentRunResponse, GraphInfoResponse
from app.services.runner import run_agent_pipeline

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post(
    "/run",
    response_model=AgentRunResponse,
    summary="Run the multi-agent research pipeline",
    response_description="Final report, intermediate artifacts, and message trail",
)
def run_agent(body: AgentRunRequest) -> AgentRunResponse:
    """
    Start the hierarchical graph for a user task.

    Body
    ----
    - **task**: research topic (`current_task`)
    - **thread_id** (optional): resume / track LangGraph checkpoint thread

    Returns `final_report`, `status`, `messages`, and intermediate fields
    (`research_findings`, `draft_report`, `critic_feedback`).
    """
    task = (body.task or "").strip()
    if not task:
        raise HTTPException(status_code=400, detail="task must not be empty")

    try:
        result = run_agent_pipeline(task, thread_id=body.thread_id)
    except Exception as exc:  # noqa: BLE001
        # Unexpected errors outside the runner's own try/except
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected server error: {exc}",
        ) from exc

    # Graph-level failures are returned as structured body (ok=false).
    # Still use 502 when the pipeline hard-failed so clients can branch easily.
    if not result.ok and result.error and "Graph invocation failed" in (result.error or ""):
        raise HTTPException(status_code=502, detail=result.error)

    return result


@router.get(
    "/graph",
    response_model=GraphInfoResponse,
    summary="Describe multi-agent graph topology",
)
def agent_graph_info() -> GraphInfoResponse:
    return GraphInfoResponse(
        phase=3,
        nodes=["supervisor", "researcher", "writer", "critic"],
        flow=(
            "START → supervisor ⇄ researcher|writer|critic → "
            "(REVISE loop writer↔critic) → END"
        ),
        max_revisions=settings.max_revisions,
        model=settings.ollama_model,
        endpoints={
            "run": "POST /api/agent/run",
            "health": "GET /health",
            "docs": "GET /docs",
        },
    )
