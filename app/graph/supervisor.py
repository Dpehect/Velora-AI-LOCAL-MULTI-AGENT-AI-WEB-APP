"""Supervisor agent — sole router for the multi-agent graph."""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.graph.state import AgentState, NextAgent, Status
from app.llm import get_llm

# Phase-1: only researcher is implemented; writer/critic map to FINISH with a note.
VALID_TARGETS: set[str] = {"researcher", "writer", "critic", "FINISH", "done"}

SUPERVISOR_SYSTEM = """You are the Supervisor of a hierarchical multi-agent research system.

Your ONLY job is to decide the next agent based on the current state.
You do NOT write research yourself. You do NOT invent facts.

## Agents
- researcher: Gathers facts with Wikipedia + arXiv tools. Use when research_findings is empty or clearly insufficient for the task.
- writer: Turns research_findings into a draft report. (Phase-2 — not implemented yet.)
- critic: Reviews draft quality. (Phase-2 — not implemented yet.)
- done: Pipeline complete — stop.

## Phase-1 rules (strict)
1. If research_findings is empty/whitespace AND current_task is non-empty → next_agent = "researcher", status = "research".
2. If research_findings is non-empty → next_agent = "done", status = "done"
   (writer/critic are not available in Phase-1; finish after research).
3. If current_task is empty → next_agent = "done", status = "error".
4. Never choose "writer" or "critic" in Phase-1.

## Response format
Reply with ONLY a single JSON object (no markdown fences, no prose):
{"next_agent":"researcher"|"done","status":"research"|"done"|"error","reasoning":"short reason"}
"""


def _state_snapshot(state: AgentState) -> str:
    findings = (state.get("research_findings") or "").strip()
    draft = (state.get("draft_report") or "").strip()
    critic = (state.get("critic_feedback") or "").strip()
    final = (state.get("final_report") or "").strip()
    return (
        f"current_task: {state.get('current_task') or '(empty)'}\n"
        f"status: {state.get('status') or 'idle'}\n"
        f"research_findings: {'(empty)' if not findings else f'({len(findings)} chars) ' + findings[:500]}\n"
        f"draft_report: {'(empty)' if not draft else f'({len(draft)} chars)'}\n"
        f"critic_feedback: {'(empty)' if not critic else f'({len(critic)} chars)'}\n"
        f"final_report: {'(empty)' if not final else f'({len(final)} chars)'}\n"
    )


def _rule_based_decision(state: AgentState) -> dict[str, str]:
    """
    Deterministic fallback so routing always works even if the LLM
    returns malformed JSON.
    """
    task = (state.get("current_task") or "").strip()
    findings = (state.get("research_findings") or "").strip()

    if not task:
        return {
            "next_agent": "FINISH",
            "status": "error",
            "reasoning": "No current_task provided.",
        }
    if not findings:
        return {
            "next_agent": "researcher",
            "status": "research",
            "reasoning": "No research findings yet — send Researcher.",
        }
    # Phase-1: stop after research (writer not wired)
    return {
        "next_agent": "FINISH",
        "status": "done",
        "reasoning": "Phase-1: research complete; writer/critic not implemented — finishing.",
    }


def _parse_llm_json(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    raw = text.strip()
    # Strip markdown fences if present
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if fence:
        raw = fence.group(1).strip()
    # Extract first {...} block
    brace = re.search(r"\{[\s\S]*\}", raw)
    if brace:
        raw = brace.group(0)
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        return None
    return None


def _normalize_decision(data: dict[str, Any], state: AgentState) -> dict[str, str]:
    next_raw = str(data.get("next_agent") or data.get("next") or "").strip().lower()
    status_raw = str(data.get("status") or "").strip().lower()
    reasoning = str(data.get("reasoning") or data.get("reason") or "").strip()

    # Alias map
    if next_raw in {"finish", "done", "end", "stop"}:
        next_agent: NextAgent = "FINISH"
    elif next_raw in {"researcher", "research"}:
        next_agent = "researcher"
    elif next_raw in {"writer", "write"}:
        # Phase-1: collapse unimplemented agents to FINISH if findings exist
        next_agent = "FINISH"
        reasoning = (reasoning or "Writer not implemented in Phase-1.") + " → FINISH"
    elif next_raw in {"critic", "review"}:
        next_agent = "FINISH"
        reasoning = (reasoning or "Critic not implemented in Phase-1.") + " → FINISH"
    else:
        # Invalid → rule-based
        return _rule_based_decision(state)

    # Enforce Phase-1 invariants
    findings = (state.get("research_findings") or "").strip()
    task = (state.get("current_task") or "").strip()

    if not task:
        return _rule_based_decision(state)
    if next_agent == "researcher" and findings:
        # Avoid infinite research loops unless findings are tiny
        if len(findings) >= 80:
            next_agent = "FINISH"
            status_raw = "done"
            reasoning = (
                reasoning
                or "Findings already present; Phase-1 finishes after research."
            )
    if next_agent == "FINISH" and not findings and task:
        # LLM tried to stop too early
        return _rule_based_decision(state)

    if status_raw not in {"research", "write", "critic", "done", "error", "idle"}:
        status_raw = "research" if next_agent == "researcher" else "done"

    status: Status = status_raw  # type: ignore[assignment]
    if next_agent == "researcher":
        status = "research"
    elif next_agent == "FINISH":
        status = "done" if findings else status

    return {
        "next_agent": next_agent,
        "status": status,
        "reasoning": reasoning or "Supervisor decision.",
    }


def supervisor_node(state: AgentState) -> dict[str, Any]:
    """
    LangGraph node: decide next_agent + status from current state.
    Uses LLM for explainable decisions with deterministic fallback.
    """
    snapshot = _state_snapshot(state)
    llm = get_llm(temperature=0.1)

    messages = [
        SystemMessage(content=SUPERVISOR_SYSTEM),
        HumanMessage(
            content=(
                "Decide the next step for this state:\n\n"
                f"{snapshot}\n"
                "Return JSON only."
            )
        ),
    ]

    decision = _rule_based_decision(state)
    try:
        response = llm.invoke(messages)
        content = response.content if isinstance(response.content, str) else str(response.content)
        parsed = _parse_llm_json(content)
        if parsed:
            decision = _normalize_decision(parsed, state)
    except Exception as exc:  # noqa: BLE001
        decision = _rule_based_decision(state)
        decision["reasoning"] = f"LLM unavailable ({exc}); used rule-based routing."

    next_agent = decision["next_agent"]
    status = decision["status"]
    reasoning = decision["reasoning"]

    print(f"[Supervisor] next_agent={next_agent} | status={status} | reason={reasoning}")

    note = f"[Supervisor] next_agent={next_agent} | status={status} | reason={reasoning}"
    return {
        "next_agent": next_agent,
        "status": status,
        "supervisor_reasoning": reasoning,
        "messages": [AIMessage(content=note, name="supervisor")],
    }


def route_supervisor(state: AgentState) -> Literal["researcher", "FINISH"]:
    """
    Conditional edge map from Supervisor.
    Phase-1: only researcher | FINISH. writer/critic reserved for Phase-2.
    """
    nxt = (state.get("next_agent") or "FINISH").strip()
    if nxt == "researcher":
        return "researcher"
    # writer / critic / FINISH / anything else → end for Phase-1
    return "FINISH"
