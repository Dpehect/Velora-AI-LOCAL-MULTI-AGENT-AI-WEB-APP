"""Researcher agent — Wikipedia + arXiv tool loop → research_findings."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from app.config import settings
from app.graph.state import AgentState
from app.graph.tools import get_research_tools
from app.llm import get_llm

RESEARCHER_SYSTEM = """You are the Researcher in a multi-agent system.

Goals
-----
1. Use tools to gather reliable information about the user's topic.
2. You MUST call tools when you need facts — do not invent citations.
3. Prefer: one Wikipedia call for overview + one arXiv call for academic notes
   (when the topic is scientific/technical). For non-technical topics, Wikipedia alone is fine.
4. After tools return, write a concise research brief.

Tools
-----
- wikipedia: factual encyclopedia summary
- arxiv: academic paper search

Final brief format (plain text / light markdown)
-----------------------------------------------
### Overview
### Key Facts
### Academic / Technical Notes
### Sources
### Gaps / Uncertainty

Keep the brief under ~800 words. Be concrete. No filler.
"""


def _tool_map():
    tools = get_research_tools()
    return {t.name: t for t in tools}


def _extract_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(str(block["text"]))
            else:
                parts.append(str(block))
        return "\n".join(parts)
    return str(content)


def _build_brief_from_observations(task: str, observations: list[str]) -> str:
    """Fallback brief if the model never produces a free-text answer."""
    body = "\n\n".join(observations) if observations else "(no tool results)"
    return (
        f"### Overview\nResearch notes for: {task}\n\n"
        f"### Key Facts\n{body}\n\n"
        f"### Academic / Technical Notes\nSee sources above.\n\n"
        f"### Sources\nTool observations collected by Researcher.\n\n"
        f"### Gaps / Uncertainty\nVerify critical claims against primary sources.\n"
    )


def researcher_node(state: AgentState) -> dict[str, Any]:
    """
    LangGraph node: tool-augmented research loop.

    Flow
    ----
    1. Bind Wikipedia + arXiv tools to ChatOllama.
    2. Iterate: model may emit tool_calls → execute → append ToolMessages.
    3. When the model responds without tool_calls, treat content as the brief.
    4. Write result into research_findings.
    """
    task = (state.get("current_task") or "").strip()
    if not task:
        # Try last human message
        for m in reversed(list(state.get("messages") or [])):
            if isinstance(m, HumanMessage):
                task = _extract_text(m.content).strip()
                break

    if not task:
        msg = "[Researcher] No current_task to research."
        print(msg)
        return {
            "research_findings": "",
            "status": "error",
            "messages": [AIMessage(content=msg, name="researcher")],
        }

    print(f"[Researcher] Starting research on: {task!r}")

    tools = get_research_tools()
    tool_by_name = _tool_map()
    llm = get_llm(temperature=0.2)
    llm_with_tools = llm.bind_tools(tools)

    history: list = [
        SystemMessage(content=RESEARCHER_SYSTEM),
        HumanMessage(
            content=(
                f"Research this topic thoroughly using tools, then produce the brief.\n\n"
                f"Topic: {task}"
            )
        ),
    ]

    observations: list[str] = []
    tool_calls_logged = 0
    final_text = ""
    max_iters = max(1, settings.researcher_max_iters)

    for iteration in range(1, max_iters + 1):
        try:
            ai: AIMessage = llm_with_tools.invoke(history)  # type: ignore[assignment]
        except Exception as exc:  # noqa: BLE001
            print(f"[Researcher] LLM error on iter={iteration}: {exc}")
            break

        history.append(ai)
        tool_calls = getattr(ai, "tool_calls", None) or []

        if not tool_calls:
            final_text = _extract_text(ai.content).strip()
            print(f"[Researcher] Direct answer (iter={iteration}), no tool calls.")
            break

        names = [tc.get("name") for tc in tool_calls]
        print(f"[Researcher] Tool calls (iter={iteration}): {names}")

        for tc in tool_calls:
            name = tc.get("name") or ""
            args = tc.get("args") or {}
            call_id = tc.get("id") or f"call_{iteration}_{name}"
            tool = tool_by_name.get(name)

            if tool is None:
                result = f"Unknown tool: {name}"
            else:
                try:
                    # StructuredTool prefers invoke with dict
                    if isinstance(args, dict):
                        result = tool.invoke(args)
                    else:
                        result = tool.invoke({"query": str(args)})
                except Exception as exc:  # noqa: BLE001
                    result = f"Error running {name}: {exc}"

            result_str = str(result)
            observations.append(f"## Tool: {name}\n{result_str}")
            tool_calls_logged += 1
            history.append(
                ToolMessage(content=result_str[:12000], tool_call_id=call_id, name=name)
            )

    # If the model only called tools and never wrote a brief, force a synthesis turn
    if not final_text:
        if observations:
            synth_llm = get_llm(temperature=0.2)
            try:
                synth = synth_llm.invoke(
                    [
                        SystemMessage(content=RESEARCHER_SYSTEM),
                        HumanMessage(
                            content=(
                                f"Topic: {task}\n\n"
                                "Using ONLY the tool observations below, write the research brief "
                                "in the required format. Do not call tools.\n\n"
                                + "\n\n".join(observations)[:14000]
                            )
                        ),
                    ]
                )
                final_text = _extract_text(synth.content).strip()
            except Exception as exc:  # noqa: BLE001
                print(f"[Researcher] Synthesis failed: {exc}")
                final_text = _build_brief_from_observations(task, observations)
        else:
            final_text = _build_brief_from_observations(task, observations)

    findings = final_text.strip()
    print(
        f"[Researcher] Done. findings_chars={len(findings)}, "
        f"tool_calls_logged={tool_calls_logged}"
    )

    return {
        "research_findings": findings,
        "current_task": task,
        "status": "research",
        "messages": [
            AIMessage(
                content=f"[Researcher] Done. findings_chars={len(findings)}, tool_calls_logged={tool_calls_logged}",
                name="researcher",
            )
        ],
    }
