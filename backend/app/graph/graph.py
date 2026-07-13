"""LangGraph assembly — local Phase-1: Supervisor ⇄ Researcher."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.graph.researcher import researcher_node
from app.graph.state import AgentState
from app.graph.supervisor import route_supervisor, supervisor_node


def build_graph(*, checkpointer: Any | None = None):
    """
    START → supervisor → researcher → supervisor → END
    """
    g = StateGraph(AgentState)
    g.add_node("supervisor", supervisor_node)
    g.add_node("researcher", researcher_node)
    g.add_edge(START, "supervisor")
    g.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {"researcher": "researcher", "FINISH": END},
    )
    g.add_edge("researcher", "supervisor")
    if checkpointer is None:
        checkpointer = MemorySaver()
    return g.compile(checkpointer=checkpointer)


@lru_cache
def get_compiled_graph():
    return build_graph()
