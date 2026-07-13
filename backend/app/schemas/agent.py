"""Agent API request / response models (Phase-3)."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    """Body for POST /api/agent/run."""

    task: str = Field(
        ...,
        min_length=1,
        description="User research task / topic (maps to AgentState.current_task)",
        examples=["Retrieval Augmented Generation"],
    )
    thread_id: Optional[str] = Field(
        default=None,
        description="Optional LangGraph thread id for checkpoint continuity",
    )


class MessageOut(BaseModel):
    """Serialized LangChain message for the frontend."""

    role: str = Field(description="human | ai | tool | system | other")
    name: Optional[str] = None
    content: str


class AgentRunResponse(BaseModel):
    """Full pipeline result for frontend / clients."""

    thread_id: str
    task: str
    status: str
    next_agent: str
    supervisor_reasoning: str = ""
    research_findings: str = ""
    draft_report: str = ""
    critic_feedback: str = ""
    final_report: str = ""
    revision_count: int = 0
    messages: list[MessageOut] = Field(default_factory=list)
    message_count: int = 0
    ok: bool = True
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    model: str
    ollama_base_url: str
    phase: str = "3"
    graph_nodes: list[str] = Field(default_factory=list)


class GraphInfoResponse(BaseModel):
    phase: int = 3
    nodes: list[str]
    flow: str
    max_revisions: int
    model: str
    endpoints: dict[str, str]
