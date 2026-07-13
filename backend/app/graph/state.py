"""Shared AgentState for the local multi-agent graph."""

from __future__ import annotations

from typing import Annotated, Literal, Sequence, TypedDict

from langchain_core.messages import AnyMessage, BaseMessage
from langgraph.graph.message import add_messages

NextAgent = Literal["researcher", "FINISH"]
Status = Literal["idle", "research", "done", "error"]


class AgentState(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage | AnyMessage], add_messages]
    current_task: str
    research_findings: str
    status: Status
    next_agent: NextAgent
    supervisor_reasoning: str


def initial_state(task: str = "") -> AgentState:
    return AgentState(
        messages=[],
        current_task=task.strip(),
        research_findings="",
        status="idle",
        next_agent="FINISH",
        supervisor_reasoning="",
    )
