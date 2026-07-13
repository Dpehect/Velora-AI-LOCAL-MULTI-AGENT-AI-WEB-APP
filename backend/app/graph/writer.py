"""Writer agent — turns research_findings into a professional draft_report."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.graph.state import AgentState
from app.llm import get_llm

WRITER_SYSTEM = """You are the Writer in a hierarchical multi-agent research system.

Your job is to transform research notes into a polished, professional report.
You do NOT invent facts beyond what research_findings support.
You do NOT call tools. You only write.

## Voice & quality
- Clear, neutral, professional English (suitable for stakeholders / technical readers).
- Prefer precision over hype. No marketing fluff.
- Use concrete statements; flag uncertainty when findings are thin.
- Structure for skimmability: short paragraphs, meaningful headings.

## Required report structure (Markdown)

# {Topic Title}

## Executive Summary
3–6 sentences covering what the topic is, why it matters, and the main takeaway.

## Background
Context and definitions grounded in the research notes.

## Key Findings
- Bullet points or short numbered items
- Each finding should be traceable to the notes (no fabricated stats)

## Analysis
Deeper synthesis: how pieces connect, trade-offs, implications.
If academic sources appear in the notes, weave them in naturally (title/URL if present).

## Practical Implications
What a practitioner or team should do with this knowledge.

## Limitations & Open Questions
Gaps, uncertainty, what was not covered by the research notes.

## Sources
List sources mentioned in research_findings (Wikipedia, arXiv titles/URLs, etc.).
If a source is missing, write "Not provided in research notes."

## Closing
1 short paragraph conclusion.

## Constraints
- Length: roughly 600–1200 words unless the topic is very narrow.
- Do not invent citations, paper titles, or statistics not present in the notes.
- If revision feedback is provided, address EVERY high-priority item explicitly.
- Output ONLY the Markdown report — no preamble, no JSON wrapper.
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


def writer_node(state: AgentState) -> dict[str, Any]:
    """
    Produce or revise draft_report from research_findings (+ optional critic_feedback).
    """
    task = (state.get("current_task") or "").strip() or "Untitled topic"
    findings = (state.get("research_findings") or "").strip()
    feedback = (state.get("critic_feedback") or "").strip()
    prior_draft = (state.get("draft_report") or "").strip()
    revision_count = int(state.get("revision_count") or 0)

    if not findings:
        msg = "[Writer] Cannot write: research_findings is empty."
        print(msg)
        return {
            "draft_report": "",
            "status": "error",
            "messages": [AIMessage(content=msg, name="writer")],
        }

    is_revision = bool(feedback) and bool(prior_draft)
    if is_revision:
        human = (
            f"## Topic\n{task}\n\n"
            f"## Research findings (source of truth)\n{findings}\n\n"
            f"## Previous draft\n{prior_draft}\n\n"
            f"## Critic feedback to address\n{feedback}\n\n"
            "Revise the draft into an improved full report. "
            "Apply the feedback carefully while remaining faithful to the research findings. "
            "Output the complete revised Markdown report only."
        )
        mode = "revision"
        new_revision_count = revision_count + 1
    else:
        human = (
            f"## Topic\n{task}\n\n"
            f"## Research findings (source of truth)\n{findings}\n\n"
            "Write a complete professional Markdown report from these findings. "
            "Output the report only."
        )
        mode = "initial"
        new_revision_count = revision_count

    print(f"[Writer] mode={mode} task={task!r} findings_chars={len(findings)}")

    llm = get_llm(temperature=0.35)
    try:
        response = llm.invoke(
            [
                SystemMessage(content=WRITER_SYSTEM),
                HumanMessage(content=human),
            ]
        )
        draft = _extract_text(response.content).strip()
    except Exception as exc:  # noqa: BLE001
        msg = f"[Writer] LLM error: {exc}"
        print(msg)
        return {
            "status": "error",
            "messages": [AIMessage(content=msg, name="writer")],
        }

    if not draft:
        draft = (
            f"# {task}\n\n"
            "## Executive Summary\n"
            "Draft generation returned empty content; raw findings follow.\n\n"
            f"## Key Findings\n{findings[:3000]}\n"
        )

    print(f"[Writer] Done. draft_chars={len(draft)} revision_count={new_revision_count}")

    # Clear critic_feedback after a revision so Supervisor routes to Critic again
    # (stale REVISE would otherwise re-trigger Writer forever).
    updates: dict[str, Any] = {
        "draft_report": draft,
        "revision_count": new_revision_count,
        "status": "write",
        "messages": [
            AIMessage(
                content=f"[Writer] Done. mode={mode} draft_chars={len(draft)}",
                name="writer",
            )
        ],
    }
    if is_revision:
        updates["critic_feedback"] = ""

    return updates
