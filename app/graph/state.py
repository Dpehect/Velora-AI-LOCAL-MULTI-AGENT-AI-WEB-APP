"""Shared AgentState for the hierarchical multi-agent graph."""

from __future__ import annotations

from typing import Annotated, Literal, Optional, Sequence, TypedDict

from langchain_core.messages import AnyMessage, BaseMessage
from langgraph.graph.message import add_messages

# Agent routing targets (Phase-1 implements researcher + FINISH only)
NextAgent = Literal["researcher", "writer", "critic", "FINISH"]

# Pipeline status labels
Status = Literal[
    "idle",
    "research",
    "write",
    "critic",
    "done",
    "error",
]


class AgentState(TypedDict, total=False):
    """
    Central state shared by Supervisor and specialist agents.

    Fields
    ------
    messages:
        Conversation / agent message history (append-only via reducer).
    current_task:
        User topic / research request.
    research_findings:
        Structured brief produced by the Researcher.
    draft_report:
        Writer output (Phase-2 placeholder).
    critic_feedback:
        Critic notes (Phase-2 placeholder).
    final_report:
        Deliverable after review (Phase-2 placeholder).
    status:
        High-level pipeline stage.
    next_agent:
        Supervisor routing decision.
    supervisor_reasoning:
        Short explanation of the last Supervisor decision (debug / UI).
    """

    messages: Annotated[Sequence[BaseMessage | AnyMessage], add_messages]
    current_task: str
    research_findings: str
    draft_report: str
    critic_feedback: str
    final_report: str
    status: Status
    next_agent: NextAgent
    supervisor_reasoning: str


def initial_state(task: str = "") -> AgentState:
    """Create a fresh AgentState for a new run."""
    return AgentState(
        messages=[],
        current_task=task.strip(),
        research_findings="",
        draft_report="",
        critic_feedback="",
        final_report="",
        status="idle",
        next_agent="FINISH",
        supervisor_reasoning="",
    )


# Optional: tool-call log reducer helpers used by Researcher
def merge_strings(left: Optional[str], right: Optional[str]) -> str:
    """Prefer non-empty right, else keep left."""
    if right is not None and str(right).strip():
        return str(right)
    return left or ""
