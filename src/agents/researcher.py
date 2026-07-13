"""Researcher agent: Wikipedia + Arxiv tool loop, then synthesis."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from src.config import settings
from src.llm import get_llm
from src.prompts.prompts import RESEARCHER_SYSTEM
from src.state import AgentState
from src.tools.research_tools import get_research_tools, run_tool_by_name


def _build_research_brief_prompt(task: str, tool_transcript: str, critic: str) -> str:
    parts = [
        f"## Research topic\n{task}\n",
        f"## Tool results\n{tool_transcript or '(no tool results)'}\n",
        "Synthesize a structured research brief in Markdown as specified "
        "in your system instructions. Base claims on the tool results.",
    ]
    if critic.strip():
        parts.insert(
            1,
            f"## Critic feedback to address\n{critic.strip()}\n",
        )
    return "\n".join(parts)


def researcher_node(state: AgentState) -> dict[str, Any]:
    """
    Researcher node with a bounded tool-calling loop.

    Flow
    ----
    1. Bind Wikipedia + Arxiv tools to ChatOllama.
    2. Let the model request tools (up to ``max_tool_iterations``).
    3. Execute tools locally and feed results back.
    4. Force a final synthesis pass into ``research_findings``.
    """
    task = (state.get("current_task") or "").strip()
    if not task:
        msg = "[Researcher] No current_task provided."
        print(msg)
        return {
            "research_findings": "",
            "messages": [AIMessage(content=msg, name="researcher")],
        }

    tools = get_research_tools()
    llm = get_llm(temperature=0.1)
    llm_with_tools = llm.bind_tools(tools)

    critic = (state.get("critic_feedback") or "").strip()
    user_blob = f"Research topic: {task}"
    if critic:
        user_blob += f"\n\nAddress this critic feedback while researching:\n{critic}"

    history: list = [
        SystemMessage(content=RESEARCHER_SYSTEM),
        HumanMessage(content=user_blob),
    ]

    tool_transcript_parts: list[str] = []
    new_messages: list = []

    print(f"[Researcher] Starting research on: {task!r}")

    for iteration in range(settings.max_tool_iterations):
        ai: AIMessage = llm_with_tools.invoke(history)  # type: ignore[assignment]
        history.append(ai)
        new_messages.append(ai)

        tool_calls = getattr(ai, "tool_calls", None) or []
        if not tool_calls:
            # Model answered without tools — keep content if useful, still
            # try a dedicated synthesis if empty.
            if isinstance(ai.content, str) and ai.content.strip():
                print(f"[Researcher] Direct answer (iter={iteration + 1}), no tool calls.")
            break

        print(f"[Researcher] Tool calls (iter={iteration + 1}): {[tc.get('name') for tc in tool_calls]}")

        for tc in tool_calls:
            name = tc.get("name", "")
            args = tc.get("args") or {}
            # WikipediaQueryRun / ArxivQueryRun typically take {"query": "..."}
            query = (
                args.get("query")
                or args.get("input")
                or next(iter(args.values()), "")
                if args
                else ""
            )
            query = str(query).strip() or task

            result = run_tool_by_name(tools, name, query)
            tool_transcript_parts.append(
                f"### {name}(query={query!r})\n{result}\n"
            )
            tool_msg = ToolMessage(
                content=result[:8000],  # keep context bounded
                tool_call_id=tc.get("id", name),
                name=name,
            )
            history.append(tool_msg)
            new_messages.append(tool_msg)

    tool_transcript = "\n".join(tool_transcript_parts)

    # Always run a final synthesis without tools so findings are structured.
    synth_llm = get_llm(temperature=0.2)
    synth_messages = [
        SystemMessage(content=RESEARCHER_SYSTEM),
        HumanMessage(
            content=_build_research_brief_prompt(task, tool_transcript, critic)
        ),
    ]
    # If the last AI message already looks like a full brief and tools ran,
    # still re-synthesize for consistent structure.
    final = synth_llm.invoke(synth_messages)
    findings = (
        final.content if isinstance(final.content, str) else str(final.content)
    ).strip()

    if not findings and tool_transcript:
        findings = f"## Raw tool results\n\n{tool_transcript}"

    summary = (
        f"[Researcher] Done. findings_chars={len(findings)}, "
        f"tool_calls_logged={len(tool_transcript_parts)}"
    )
    print(summary)
    new_messages.append(AIMessage(content=summary, name="researcher"))

    return {
        "research_findings": findings,
        "status": "research",
        "messages": new_messages,
    }
