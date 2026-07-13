"""Supervisor — routes to researcher or FINISH (local Phase-1)."""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.graph.state import AgentState
from app.llm import get_llm

SUPERVISOR_SYSTEM = """You are the Supervisor of a local multi-agent research system.

Decide the next agent from state. Do not research yourself.

Agents:
- researcher: gather facts (Wikipedia + arXiv) when research_findings is empty
- done: stop when findings exist (or task is empty → error)

Reply with ONLY JSON:
{"next_agent":"researcher"|"done","status":"research"|"done"|"error","reasoning":"short"}
"""


def _rule_based(state: AgentState) -> dict[str, str]:
    task = (state.get("current_task") or "").strip()
    findings = (state.get("research_findings") or "").strip()
    if not task:
        return {
            "next_agent": "FINISH",
            "status": "error",
            "reasoning": "No current_task.",
        }
    if not findings:
        return {
            "next_agent": "researcher",
            "status": "research",
            "reasoning": "Need research findings.",
        }
    return {
        "next_agent": "FINISH",
        "status": "done",
        "reasoning": "Research complete (Phase-1).",
    }


def _parse_json(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    raw = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if fence:
        raw = fence.group(1).strip()
    brace = re.search(r"\{[\s\S]*\}", raw)
    if brace:
        raw = brace.group(0)
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def _normalize(data: dict[str, Any], state: AgentState) -> dict[str, str]:
    nxt = str(data.get("next_agent") or "").strip().lower()
    rules = _rule_based(state)
    if nxt in {"researcher", "research"}:
        # Prevent re-research loops if findings exist
        if (state.get("research_findings") or "").strip():
            return rules
        return {
            "next_agent": "researcher",
            "status": "research",
            "reasoning": str(data.get("reasoning") or rules["reasoning"]),
        }
    if nxt in {"done", "finish", "end"}:
        # Don't finish early without findings
        if not (state.get("research_findings") or "").strip() and (
            state.get("current_task") or ""
        ).strip():
            return rules
        return {
            "next_agent": "FINISH",
            "status": "done",
            "reasoning": str(data.get("reasoning") or rules["reasoning"]),
        }
    return rules


def supervisor_node(state: AgentState) -> dict[str, Any]:
    findings = (state.get("research_findings") or "").strip()
    snapshot = (
        f"current_task: {state.get('current_task') or '(empty)'}\n"
        f"research_findings: {'(empty)' if not findings else f'({len(findings)} chars)'}\n"
    )
    decision = _rule_based(state)
    try:
        resp = get_llm(temperature=0.1).invoke(
            [
                SystemMessage(content=SUPERVISOR_SYSTEM),
                HumanMessage(content=f"State:\n{snapshot}\nReturn JSON only."),
            ]
        )
        content = (
            resp.content if isinstance(resp.content, str) else str(resp.content)
        )
        parsed = _parse_json(content)
        if parsed:
            decision = _normalize(parsed, state)
    except Exception as exc:  # noqa: BLE001
        decision = _rule_based(state)
        decision["reasoning"] = f"Rule-based fallback ({exc})"

    nxt, status, reason = (
        decision["next_agent"],
        decision["status"],
        decision["reasoning"],
    )
    print(f"[Supervisor] next={nxt} status={status} | {reason}")
    return {
        "next_agent": nxt,
        "status": status,
        "supervisor_reasoning": reason,
        "messages": [
            AIMessage(
                content=f"[Supervisor] next={nxt} status={status} | {reason}",
                name="supervisor",
            )
        ],
    }


def route_supervisor(state: AgentState) -> Literal["researcher", "FINISH"]:
    if (state.get("next_agent") or "") == "researcher":
        return "researcher"
    return "FINISH"
