"""LangGraph StateGraph assembly — Phase-1 hierarchical routing."""

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
    Build and compile the Phase-1 multi-agent graph.

    Topology
    --------
        START → supervisor → (conditional)
                              ├─ researcher → supervisor
                              └─ FINISH → END

    Writer / Critic nodes will plug into the same Supervisor routing table
    in Phase-2 without changing the state schema.
    """
    graph = StateGraph(AgentState)

    # --- nodes ---
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("researcher", researcher_node)
    # Phase-2 placeholders:
    # graph.add_node("writer", writer_node)
    # graph.add_node("critic", critic_node)

    # --- edges ---
    graph.add_edge(START, "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "researcher": "researcher",
            # Phase-2:
            # "writer": "writer",
            # "critic": "critic",
            "FINISH": END,
        },
    )

    # Hierarchical control: specialists always return to Supervisor
    graph.add_edge("researcher", "supervisor")
    # graph.add_edge("writer", "supervisor")
    # graph.add_edge("critic", "supervisor")

    if checkpointer is None:
        checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)


@lru_cache
def get_compiled_graph():
    """Process-wide compiled graph (MemorySaver)."""
    return build_graph()
