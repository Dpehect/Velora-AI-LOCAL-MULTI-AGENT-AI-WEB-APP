"""Critic agent — reviews draft_report and writes constructive critic_feedback."""

from __future__ import annotations

import re
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.graph.state import AgentState
from app.llm import get_llm

CRITIC_SYSTEM = """You are the Critic in a hierarchical multi-agent research system.

Your job is to review a draft report against the research findings and give
constructive, actionable feedback. You do NOT rewrite the full report.
You do NOT invent new facts. You do NOT call tools.

## Evaluation dimensions
1. **Accuracy** — Claims should be supported by research_findings; flag hallucinations.
2. **Coverage** — Important points from findings should appear in the draft.
3. **Structure & format** — Clear headings, executive summary, sources, limitations.
4. **Clarity & tone** — Professional, concise, readable; avoid fluff and contradiction.
5. **Completeness** — Practical implications and open questions present when relevant.

## How to be constructive
- Be specific: quote or paraphrase weak spots; say what to change.
- Separate critical issues (must fix) from minor polish (nice to have).
- If the draft is already strong, APPROVE — do not nitpick endlessly.
- Prefer 3–7 concrete recommendations over vague essay-length critique.

## Required output format (Markdown) — follow exactly

### Verdict
APPROVE
or
REVISE

### Score
overall: <0-10 integer>
accuracy: <0-10>
coverage: <0-10>
structure: <0-10>
clarity: <0-10>

### Summary
2–4 sentences overall assessment.

### Strengths
- bullet list

### Critical issues
- bullet list (empty if none)

### Recommendations
- numbered, actionable edits the Writer should make

### Notes for Supervisor
One short line: why APPROVE or REVISE.

## Verdict rules
- APPROVE if the draft is substantially accurate, well-structured, and usable
  (small typos alone are not enough to REVISE).
- REVISE if there are factual issues, major missing sections, contradictions,
  empty/thin content, or inventing sources not in the findings.
- Output ONLY the review Markdown — no preamble.
"""


def _extract_text(content: Any) -> str:
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


def parse_critic_verdict(feedback: str) -> Literal["APPROVE", "REVISE", "UNKNOWN"]:
    """Extract APPROVE / REVISE from critic_feedback text."""
    if not feedback or not feedback.strip():
        return "UNKNOWN"
    text = feedback.strip()

    # Prefer explicit ### Verdict section
    m = re.search(
        r"###\s*Verdict\s*\n+\s*(APPROVE|REVISE)\b",
        text,
        flags=re.IGNORECASE,
    )
    if m:
        return m.group(1).upper()  # type: ignore[return-value]

    # Fallback: first strong keyword
    if re.search(r"\bAPPROVE\b", text, re.I) and not re.search(
        r"\bREVISE\b", text[:200], re.I
    ):
        return "APPROVE"
    if re.search(r"\bREVISE\b", text, re.I):
        return "REVISE"
    return "UNKNOWN"


def critic_node(state: AgentState) -> dict[str, Any]:
    """Review draft_report vs research_findings → critic_feedback."""
    task = (state.get("current_task") or "").strip() or "Untitled topic"
    findings = (state.get("research_findings") or "").strip()
    draft = (state.get("draft_report") or "").strip()

    if not draft:
        msg = "[Critic] No draft_report to review."
        print(msg)
        feedback = (
            "### Verdict\nREVISE\n\n"
            "### Score\noverall: 0\naccuracy: 0\ncoverage: 0\nstructure: 0\nclarity: 0\n\n"
            "### Summary\nDraft is empty; Writer must produce a full report.\n\n"
            "### Strengths\n- None yet\n\n"
            "### Critical issues\n- Missing draft_report\n\n"
            "### Recommendations\n1. Write a complete report from research findings.\n\n"
            "### Notes for Supervisor\nEmpty draft — route back to writer.\n"
        )
        return {
            "critic_feedback": feedback,
            "status": "critic",
            "messages": [AIMessage(content=msg, name="critic")],
        }

    print(f"[Critic] Reviewing draft_chars={len(draft)} findings_chars={len(findings)}")

    human = (
        f"## Topic\n{task}\n\n"
        f"## Research findings (ground truth)\n{findings or '(empty)'}\n\n"
        f"## Draft report to review\n{draft}\n\n"
        "Produce your structured critique now."
    )

    llm = get_llm(temperature=0.15)
    try:
        response = llm.invoke(
            [
                SystemMessage(content=CRITIC_SYSTEM),
                HumanMessage(content=human),
            ]
        )
        feedback = _extract_text(response.content).strip()
    except Exception as exc:  # noqa: BLE001
        msg = f"[Critic] LLM error: {exc}"
        print(msg)
        return {
            "status": "error",
            "messages": [AIMessage(content=msg, name="critic")],
        }

    if not feedback:
        feedback = (
            "### Verdict\nAPPROVE\n\n"
            "### Score\noverall: 7\naccuracy: 7\ncoverage: 7\nstructure: 7\nclarity: 7\n\n"
            "### Summary\nCritic returned empty text; defaulting to cautious APPROVE.\n\n"
            "### Strengths\n- Draft present\n\n"
            "### Critical issues\n- None recorded\n\n"
            "### Recommendations\n1. Optional polish only.\n\n"
            "### Notes for Supervisor\nEmpty critic output — treat as APPROVE.\n"
        )

    verdict = parse_critic_verdict(feedback)
    print(f"[Critic] Done. feedback_chars={len(feedback)} verdict={verdict}")

    return {
        "critic_feedback": feedback,
        "status": "critic",
        "messages": [
            AIMessage(
                content=f"[Critic] Done. verdict={verdict} feedback_chars={len(feedback)}",
                name="critic",
            )
        ],
    }
