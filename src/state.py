"""Shared graph state for the hierarchical multi-agent system."""

from __future__ import annotations

from typing import Annotated, Literal, NotRequired, TypedDict

from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

# Valid pipeline statuses (Supervisor is the single source of truth).
Status = Literal["research", "write", "critic", "done"]

# Agents the Supervisor may route to. FINISH ends the graph.
NextAgent = Literal["researcher", "writer", "critic", "FINISH"]


class AgentState(TypedDict):
    """
    Shared state passed through every node of the StateGraph.

    Design notes
    ------------
    - ``messages`` uses ``add_messages`` so each node can append without
      clobbering history (LangGraph reducer pattern).
    - Domain fields (findings, draft, feedback, final) are plain strings
      overwritten by the agent that owns them.
    - ``next_agent`` is set ONLY by the Supervisor; workers clear it or
      leave routing to the Supervisor after they return.
    - ``status`` mirrors the high-level pipeline phase for observability.
    """

    # Conversation / audit trail (Human, AI, Tool messages)
    messages: Annotated[list[BaseMessage], add_messages]

    # User's research topic / goal
    current_task: str

    # Researcher output: structured notes from Wikipedia + Arxiv
    research_findings: str

    # Writer output: draft markdown report
    draft_report: str

    # Critic output: quality / accuracy / consistency review
    critic_feedback: str

    # Final accepted markdown report
    final_report: str

    # High-level pipeline phase
    status: Status

    # Supervisor routing decision for the next hop
    next_agent: NextAgent

    # Optional free-text reasoning from Supervisor (debug / logging)
    supervisor_reasoning: NotRequired[str]


def initial_state(task: str) -> AgentState:
    """Build a clean initial state for a new research run."""
    return AgentState(
        messages=[],
        current_task=task,
        research_findings="",
        draft_report="",
        critic_feedback="",
        final_report="",
        status="research",
        next_agent="researcher",
        supervisor_reasoning="",
    )
