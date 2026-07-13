"""LangGraph StateGraph assembly for the hierarchical multi-agent system."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.agents.researcher import researcher_node
from src.agents.supervisor import route_supervisor, supervisor_node
from src.config import settings
from src.state import AgentState


def build_graph(*, checkpointer: Any | None = None):
    """
    Build and compile the hierarchical research graph (Phase-1).

    Topology
    --------
        START → supervisor → (conditional)
                              ├─ researcher → supervisor
                              └─ FINISH → END

    Writer / Critic nodes will be added in the next phase and wired into
    the same Supervisor routing table.
    """
    graph = StateGraph(AgentState)

    # --- nodes ---
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("researcher", researcher_node)
    # Phase-2 placeholders (uncomment when implementing):
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


def build_graph_with_sqlite(db_path: str | None = None):
    """
    Compile with a durable SQLite checkpointer (langgraph-checkpoint-sqlite).

    Falls back to MemorySaver if the sqlite package is unavailable.
    """
    path = db_path or settings.checkpoint_db
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    try:
        from langgraph.checkpoint.sqlite import SqliteSaver

        # SqliteSaver.from_conn_string is a context manager in recent versions;
        # for a long-lived app, open the connection yourself. For scripts we
        # use MemorySaver by default and document Sqlite usage in tests.
        # Here we prefer the context-manager pattern's connection via
        # SqliteSaver(conn) when possible.
        import sqlite3

        conn = sqlite3.connect(path, check_same_thread=False)
        checkpointer = SqliteSaver(conn)
        return build_graph(checkpointer=checkpointer)
    except Exception as exc:  # noqa: BLE001
        print(f"[graph] SqliteSaver unavailable ({exc}); using MemorySaver.")
        return build_graph(checkpointer=MemorySaver())
