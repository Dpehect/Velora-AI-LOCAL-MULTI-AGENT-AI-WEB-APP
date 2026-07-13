"""
Graph execution service — single place that prepares state and invokes LangGraph.
"""

from __future__ import annotations

import uuid
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage

from app.graph.graph import get_compiled_graph
from app.graph.state import AgentState, initial_state
from app.schemas.agent import AgentRunResponse, MessageOut


def _message_role(msg: BaseMessage) -> str:
    if isinstance(msg, HumanMessage):
        return "human"
    if isinstance(msg, AIMessage):
        return "ai"
    if isinstance(msg, SystemMessage):
        return "system"
    if isinstance(msg, ToolMessage):
        return "tool"
    return "other"


def _message_content(msg: BaseMessage) -> str:
    content = getattr(msg, "content", "")
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(str(block["text"]))
            else:
                parts.append(str(block))
        return "\n".join(parts)
    return str(content)


def serialize_messages(messages: Any) -> list[MessageOut]:
    """Convert LangChain messages → API-friendly list."""
    out: list[MessageOut] = []
    if not messages:
        return out
    for msg in messages:
        if not isinstance(msg, BaseMessage):
            out.append(MessageOut(role="other", name=None, content=str(msg)))
            continue
        name = getattr(msg, "name", None)
        out.append(
            MessageOut(
                role=_message_role(msg),
                name=name,
                content=_message_content(msg),
            )
        )
    return out


def run_agent_pipeline(
    task: str,
    *,
    thread_id: str | None = None,
    recursion_limit: int = 40,
) -> AgentRunResponse:
    """
    Run the full multi-agent graph for a user task.

    Parameters
    ----------
    task:
        Maps to AgentState.current_task.
    thread_id:
        Optional checkpoint thread; generated when omitted.
    recursion_limit:
        LangGraph max supersteps (supervisor loops).
    """
    cleaned = (task or "").strip()
    if not cleaned:
        return AgentRunResponse(
            thread_id=thread_id or str(uuid.uuid4()),
            task="",
            status="error",
            next_agent="FINISH",
            ok=False,
            error="task must not be empty",
        )

    tid = (thread_id or str(uuid.uuid4())).strip()
    graph = get_compiled_graph()

    state: AgentState = initial_state(cleaned)
    state["messages"] = [
        HumanMessage(content=f"Research and produce a report on: {cleaned}")
    ]

    config: dict[str, Any] = {
        "configurable": {"thread_id": tid},
        "recursion_limit": recursion_limit,
    }

    try:
        final = graph.invoke(state, config=config)
    except Exception as exc:  # noqa: BLE001
        return AgentRunResponse(
            thread_id=tid,
            task=cleaned,
            status="error",
            next_agent="FINISH",
            ok=False,
            error=f"Graph invocation failed: {exc}. Is Ollama running and the model pulled?",
            messages=[],
            message_count=0,
        )

    messages = serialize_messages(final.get("messages"))
    final_report = str(final.get("final_report") or "").strip()
    draft = str(final.get("draft_report") or "").strip()
    # Prefer final_report; fall back to draft if finalize was skipped
    deliverable = final_report or draft

    status = str(final.get("status") or "done")
    ok = status not in {"error"} and bool(
        (final.get("research_findings") or "").strip() or deliverable
    )

    return AgentRunResponse(
        thread_id=tid,
        task=cleaned,
        status=status,
        next_agent=str(final.get("next_agent") or "FINISH"),
        supervisor_reasoning=str(final.get("supervisor_reasoning") or ""),
        research_findings=str(final.get("research_findings") or ""),
        draft_report=draft,
        critic_feedback=str(final.get("critic_feedback") or ""),
        final_report=deliverable,
        revision_count=int(final.get("revision_count") or 0),
        messages=messages,
        message_count=len(messages),
        ok=ok,
        error=None if ok else "Pipeline finished without usable output.",
    )
