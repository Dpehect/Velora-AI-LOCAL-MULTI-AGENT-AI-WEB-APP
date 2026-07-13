"""Supervisor agent — sole router for the multi-agent graph (Phase-2)."""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.config import settings
from app.graph.critic import parse_critic_verdict
from app.graph.state import AgentState, NextAgent, Status
from app.llm import get_llm

SUPERVISOR_SYSTEM = """You are the Supervisor of a hierarchical multi-agent research system.

Your ONLY job is to decide the next agent from the current state.
You do NOT write research, reports, or criticism yourself. You do NOT invent facts.

## Agents
- researcher: Gathers facts (Wikipedia + arXiv). Use when research_findings is empty/insufficient.
- writer: Turns research_findings into draft_report. Also revises when critic_feedback says REVISE.
- critic: Reviews draft_report for quality/accuracy; writes critic_feedback (APPROVE or REVISE).
- done: Pipeline complete — stop (maps to FINISH).

## Phase-2 routing policy (strict priority)
1. If current_task is empty → next_agent = "done", status = "error".
2. If research_findings is empty → next_agent = "researcher", status = "research".
3. If research_findings present AND draft_report empty → next_agent = "writer", status = "write".
4. If draft_report present AND critic_feedback empty → next_agent = "critic", status = "critic".
5. If critic_feedback verdict is REVISE AND revision_count < max_revisions → next_agent = "writer", status = "write".
6. If critic_feedback verdict is APPROVE (or revisions exhausted) → next_agent = "done", status = "done".
7. Do NOT re-run researcher once solid findings exist (unless findings are clearly empty).
8. Do NOT skip critic after a new/revised draft — critic_feedback must match the latest draft cycle.
   After writer revises, treat as needing a fresh critic pass (if feedback is stale, still send critic).

## Response format
Reply with ONLY a single JSON object (no markdown fences, no prose):
{"next_agent":"researcher"|"writer"|"critic"|"done","status":"research"|"write"|"critic"|"done"|"error","reasoning":"short reason"}
"""


def _state_snapshot(state: AgentState) -> str:
    findings = (state.get("research_findings") or "").strip()
    draft = (state.get("draft_report") or "").strip()
    critic = (state.get("critic_feedback") or "").strip()
    final = (state.get("final_report") or "").strip()
    revision_count = int(state.get("revision_count") or 0)
    verdict = parse_critic_verdict(critic) if critic else "NONE"
    return (
        f"current_task: {state.get('current_task') or '(empty)'}\n"
        f"status: {state.get('status') or 'idle'}\n"
        f"revision_count: {revision_count} (max_revisions: {settings.max_revisions})\n"
        f"critic_verdict: {verdict}\n"
        f"research_findings: {'(empty)' if not findings else f'({len(findings)} chars) ' + findings[:400]}\n"
        f"draft_report: {'(empty)' if not draft else f'({len(draft)} chars) ' + draft[:300]}\n"
        f"critic_feedback: {'(empty)' if not critic else f'({len(critic)} chars) ' + critic[:350]}\n"
        f"final_report: {'(empty)' if not final else f'({len(final)} chars)'}\n"
    )


def _rule_based_decision(state: AgentState) -> dict[str, Any]:
    """
    Deterministic routing — always valid even if the LLM misbehaves.
    Enforces the Phase-2 lifecycle and revision budget.
    """
    task = (state.get("current_task") or "").strip()
    findings = (state.get("research_findings") or "").strip()
    draft = (state.get("draft_report") or "").strip()
    feedback = (state.get("critic_feedback") or "").strip()
    revision_count = int(state.get("revision_count") or 0)
    max_rev = settings.max_revisions
    verdict = parse_critic_verdict(feedback) if feedback else "UNKNOWN"

    if not task:
        return {
            "next_agent": "FINISH",
            "status": "error",
            "reasoning": "No current_task provided.",
            "finalize": False,
        }

    if not findings:
        return {
            "next_agent": "researcher",
            "status": "research",
            "reasoning": "No research findings — send Researcher.",
            "finalize": False,
        }

    if not draft:
        return {
            "next_agent": "writer",
            "status": "write",
            "reasoning": "Findings ready — send Writer for draft_report.",
            "finalize": False,
        }

    if not feedback:
        return {
            "next_agent": "critic",
            "status": "critic",
            "reasoning": "Draft ready — send Critic for review.",
            "finalize": False,
        }

    # Feedback exists — decide revise vs done
    if verdict == "REVISE" and revision_count < max_rev:
        return {
            "next_agent": "writer",
            "status": "write",
            "reasoning": (
                f"Critic requested REVISE "
                f"(revision_count={revision_count}/{max_rev}) — send Writer."
            ),
            "finalize": False,
            "clear_feedback_for_rewrite": True,
        }

    # APPROVE, UNKNOWN after feedback, or revision budget exhausted
    if verdict == "REVISE" and revision_count >= max_rev:
        reason = (
            f"Revision budget exhausted ({revision_count}/{max_rev}); "
            "accepting current draft as final."
        )
    elif verdict == "APPROVE":
        reason = "Critic APPROVE — finalize report."
    else:
        reason = f"Critic verdict={verdict}; finalizing with current draft."

    return {
        "next_agent": "FINISH",
        "status": "done",
        "reasoning": reason,
        "finalize": True,
    }


def _parse_llm_json(text: str) -> dict[str, Any] | None:
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
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        return None
    return None


def _normalize_decision(data: dict[str, Any], state: AgentState) -> dict[str, Any]:
    next_raw = str(data.get("next_agent") or data.get("next") or "").strip().lower()
    status_raw = str(data.get("status") or "").strip().lower()
    reasoning = str(data.get("reasoning") or data.get("reason") or "").strip()

    if next_raw in {"finish", "done", "end", "stop"}:
        next_agent: NextAgent = "FINISH"
    elif next_raw in {"researcher", "research"}:
        next_agent = "researcher"
    elif next_raw in {"writer", "write"}:
        next_agent = "writer"
    elif next_raw in {"critic", "review"}:
        next_agent = "critic"
    else:
        return _rule_based_decision(state)

    # Safety: re-validate against hard invariants via rules
    rules = _rule_based_decision(state)
    # If LLM disagrees with deterministic pipeline stage, prefer rules
    # (prevents loops / skips).
    if next_agent != rules["next_agent"]:
        return {
            **rules,
            "reasoning": (
                f"LLM chose {next_agent} but policy requires {rules['next_agent']}: "
                f"{rules['reasoning']}"
            ),
        }

    status_map = {
        "researcher": "research",
        "writer": "write",
        "critic": "critic",
        "FINISH": "done",
    }
    status: Status = status_map.get(next_agent, "done")  # type: ignore[assignment]
    if status_raw == "error" and next_agent == "FINISH":
        status = "error"

    return {
        "next_agent": next_agent,
        "status": status,
        "reasoning": reasoning or rules.get("reasoning") or "Supervisor decision.",
        "finalize": bool(rules.get("finalize")) and next_agent == "FINISH",
        "clear_feedback_for_rewrite": bool(rules.get("clear_feedback_for_rewrite")),
    }


def supervisor_node(state: AgentState) -> dict[str, Any]:
    """
    LangGraph node: decide next_agent + status; optionally finalize final_report.
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
        content = (
            response.content
            if isinstance(response.content, str)
            else str(response.content)
        )
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

    updates: dict[str, Any] = {
        "next_agent": next_agent,
        "status": status,
        "supervisor_reasoning": reasoning,
        "messages": [
            AIMessage(
                content=f"[Supervisor] next_agent={next_agent} | status={status} | reason={reasoning}",
                name="supervisor",
            )
        ],
    }

    # Promote draft → final when pipeline completes successfully
    if decision.get("finalize") and next_agent == "FINISH" and status == "done":
        draft = (state.get("draft_report") or "").strip()
        if draft:
            updates["final_report"] = draft

    # When sending Writer for REVISE, clear feedback after snapshot... 
    # Actually Writer needs feedback. Clear AFTER writer? 
    # Writer reads critic_feedback; Critic should re-review after revision.
    # So: on revise path keep feedback for writer; after writer runs feedback is stale.
    # Supervisor on next visit after writer: draft exists + feedback exists + was REVISE
    # → problem: rule would REVISE again without new critic pass.
    #
    # Fix: when routing to writer for revise, set a flag OR clear feedback after writer.
    # Writer increments revision_count when feedback present. After writer, feedback still REVISE.
    # Rule: if draft exists and feedback is REVISE, go writer — but then infinite loop without critic.
    #
    # Better approach: clear critic_feedback when writer finishes a revision (in writer_node),
    # OR track draft_version. Simplest: clear feedback in writer when doing revision after using it.
    #
    # Implemented in writer? Currently writer keeps feedback. I'll clear feedback in writer after revision
    # so next supervisor step sees draft + empty feedback → critic.
    # Already need that - update writer to clear critic_feedback after revision.

    return updates


def route_supervisor(
    state: AgentState,
) -> Literal["researcher", "writer", "critic", "FINISH"]:
    """Conditional edge map from Supervisor — full Phase-2 table."""
    nxt = (state.get("next_agent") or "FINISH").strip()
    if nxt == "researcher":
        return "researcher"
    if nxt == "writer":
        return "writer"
    if nxt == "critic":
        return "critic"
    return "FINISH"
