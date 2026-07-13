"""Supervisor agent: sole hierarchical decision-maker."""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.llm import get_llm
from src.prompts.prompts import SUPERVISOR_SYSTEM
from src.state import AgentState, NextAgent, Status

VALID_AGENTS: set[str] = {"researcher", "writer", "critic", "FINISH"}
VALID_STATUS: set[str] = {"research", "write", "critic", "done"}

# Phase-1: only researcher is implemented. Map unimplemented workers to FINISH
# after research succeeds so the graph can terminate in tests.
PHASE1_IMPLEMENTED: set[str] = {"researcher", "FINISH"}


def _state_snapshot(state: AgentState) -> str:
    """Compact human-readable snapshot for the Supervisor prompt."""
    findings = (state.get("research_findings") or "").strip()
    draft = (state.get("draft_report") or "").strip()
    critic = (state.get("critic_feedback") or "").strip()
    final = (state.get("final_report") or "").strip()

    def _preview(text: str, n: int = 400) -> str:
        if not text:
            return "(empty)"
        return text if len(text) <= n else text[:n] + "…"

    return (
        f"current_task: {state.get('current_task', '')}\n"
        f"status: {state.get('status', '')}\n"
        f"research_findings: {_preview(findings)}\n"
        f"draft_report: {_preview(draft)}\n"
        f"critic_feedback: {_preview(critic)}\n"
        f"final_report: {_preview(final)}\n"
        f"has_research: {bool(findings)}\n"
        f"has_draft: {bool(draft)}\n"
        f"has_critic: {bool(critic)}\n"
        f"has_final: {bool(final)}\n"
    )


def _extract_json(text: str) -> dict[str, Any] | None:
    """Parse a JSON object from model output (tolerates fences / prose)."""
    if not text:
        return None
    text = text.strip()

    # Direct parse
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    # Fenced ```json ... ```
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        try:
            data = json.loads(fence.group(1))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    # First {...} block
    brace = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if brace:
        try:
            data = json.loads(brace.group(0))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    return None


def _heuristic_decision(state: AgentState) -> dict[str, str]:
    """
    Deterministic fallback when the LLM output is unusable.

    Mirrors the Supervisor policy so the graph never stalls.
    """
    findings = (state.get("research_findings") or "").strip()
    draft = (state.get("draft_report") or "").strip()
    critic = (state.get("critic_feedback") or "").strip()
    final = (state.get("final_report") or "").strip()

    if final:
        return {
            "next_agent": "FINISH",
            "status": "done",
            "reasoning": "Final report already present.",
        }
    if not findings:
        return {
            "next_agent": "researcher",
            "status": "research",
            "reasoning": "No research findings yet; send Researcher.",
        }
    if not draft:
        # Phase-1: Writer not wired → finish after research for testability
        return {
            "next_agent": "FINISH",
            "status": "done",
            "reasoning": "Research complete; Writer not yet implemented (phase-1).",
        }
    if not critic:
        return {
            "next_agent": "critic",
            "status": "critic",
            "reasoning": "Draft ready; send Critic.",
        }

    critic_upper = critic.upper()
    if "APPROVED" in critic_upper:
        return {
            "next_agent": "FINISH",
            "status": "done",
            "reasoning": "Critic approved the draft.",
        }
    if "REWRITE" in critic_upper or "INSUFFICIENT" in critic_upper:
        if "RESEARCH" in critic_upper or "INSUFFICIENT" in critic_upper:
            return {
                "next_agent": "researcher",
                "status": "research",
                "reasoning": "Critic requested more research.",
            }
        return {
            "next_agent": "writer",
            "status": "write",
            "reasoning": "Critic requested a rewrite.",
        }

    return {
        "next_agent": "FINISH",
        "status": "done",
        "reasoning": "Default stop after review cycle.",
    }


def _normalize_decision(raw: dict[str, Any], state: AgentState) -> dict[str, str]:
    """Validate / coerce model decision; fall back to heuristic if invalid."""
    next_agent = str(raw.get("next_agent", "")).strip()
    status = str(raw.get("status", "")).strip()
    reasoning = str(raw.get("reasoning", "")).strip() or "Supervisor decision."

    if next_agent not in VALID_AGENTS:
        return _heuristic_decision(state)

    # Align status with agent if model left it blank / wrong
    if status not in VALID_STATUS:
        status = {
            "researcher": "research",
            "writer": "write",
            "critic": "critic",
            "FINISH": "done",
        }[next_agent]

    # Phase-1 guard: unimplemented agents → FINISH (after research if possible)
    if next_agent not in PHASE1_IMPLEMENTED:
        if (state.get("research_findings") or "").strip():
            return {
                "next_agent": "FINISH",
                "status": "done",
                "reasoning": (
                    f"Phase-1: '{next_agent}' not implemented; "
                    f"stopping after research. ({reasoning})"
                ),
            }
        return {
            "next_agent": "researcher",
            "status": "research",
            "reasoning": (
                f"Phase-1: '{next_agent}' not implemented and no research yet; "
                f"routing to researcher. ({reasoning})"
            ),
        }

    return {
        "next_agent": next_agent,
        "status": status,
        "reasoning": reasoning,
    }


def supervisor_node(state: AgentState) -> dict[str, Any]:
    """
    Supervisor node.

    Reads the full shared state, asks the local LLM for a routing decision,
    validates it, and writes ``next_agent`` + ``status`` back into state.
    """
    llm = get_llm(temperature=0.0)
    snapshot = _state_snapshot(state)

    messages = [
        SystemMessage(content=SUPERVISOR_SYSTEM),
        HumanMessage(
            content=(
                "Inspect the current pipeline state and decide the next agent.\n\n"
                f"## State\n{snapshot}"
            )
        ),
    ]

    try:
        response = llm.invoke(messages)
        content = response.content if isinstance(response.content, str) else str(response.content)
        parsed = _extract_json(content)
        decision = _normalize_decision(parsed or {}, state)
    except Exception as exc:  # noqa: BLE001
        decision = _heuristic_decision(state)
        decision["reasoning"] = f"LLM error ({exc}); used heuristic. {decision['reasoning']}"

    next_agent: NextAgent = decision["next_agent"]  # type: ignore[assignment]
    status: Status = decision["status"]  # type: ignore[assignment]
    reasoning = decision["reasoning"]

    log = (
        f"[Supervisor] next_agent={next_agent} | status={status} | "
        f"reason={reasoning}"
    )
    print(log)

    return {
        "next_agent": next_agent,
        "status": status,
        "supervisor_reasoning": reasoning,
        "messages": [AIMessage(content=log, name="supervisor")],
    }


def route_supervisor(state: AgentState) -> str:
    """
    Conditional edge function after the Supervisor node.

    Returns a graph path key matching ``add_conditional_edges`` mapping:
    researcher | writer | critic | FINISH
    """
    nxt = (state.get("next_agent") or "FINISH").strip()
    if nxt not in VALID_AGENTS:
        return "FINISH"
    # Phase-1: only researcher is a real node
    if nxt not in PHASE1_IMPLEMENTED:
        return "FINISH"
    return nxt
