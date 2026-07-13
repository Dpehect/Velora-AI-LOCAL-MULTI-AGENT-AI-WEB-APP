"""LangGraph StateGraph assembly — Phase-2 full hierarchical routing."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.graph.critic import critic_node
from app.graph.researcher import researcher_node
from app.graph.state import AgentState
from app.graph.supervisor import route_supervisor, supervisor_node
from app.graph.writer import writer_node


def build_graph(*, checkpointer: Any | None = None):
    """
    Build and compile the Phase-2 multi-agent graph.

    Topology
    --------
        START → supervisor → (conditional)
                              ├─ researcher → supervisor
                              ├─ writer     → supervisor
                              ├─ critic     → supervisor
                              └─ FINISH → END

    Typical happy path
    ------------------
        Supervisor → Researcher → Supervisor → Writer → Supervisor
        → Critic → Supervisor → (Writer if REVISE)* → Critic → FINISH

    Specialists always return to the Supervisor (hierarchical control).
    """
    graph = StateGraph(AgentState)

    # --- nodes ---
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("critic", critic_node)

    # --- edges ---
    graph.add_edge(START, "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "researcher": "researcher",
            "writer": "writer",
            "critic": "critic",
            "FINISH": END,
        },
    )

    graph.add_edge("researcher", "supervisor")
    graph.add_edge("writer", "supervisor")
    graph.add_edge("critic", "supervisor")

    if checkpointer is None:
        checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)


@lru_cache
def get_compiled_graph():
    """Process-wide compiled graph (MemorySaver)."""
    return build_graph()
