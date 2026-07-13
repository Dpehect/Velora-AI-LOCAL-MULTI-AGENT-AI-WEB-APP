"""Researcher — tool loop with Wikipedia + arXiv → research_findings."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from app.config import settings
from app.graph.state import AgentState
from app.graph.tools import get_research_tools
from app.llm import get_llm

RESEARCHER_SYSTEM = """You are the Researcher. Use tools to gather facts; do not invent citations.

Tools: wikipedia, arxiv.
Prefer one Wikipedia overview + one arXiv search for technical topics.
After tools return, write a concise brief:

### Overview
### Key Facts
### Academic Notes
### Sources
### Gaps
"""


def _text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, str):
                parts.append(b)
            elif isinstance(b, dict) and "text" in b:
                parts.append(str(b["text"]))
            else:
                parts.append(str(b))
        return "\n".join(parts)
    return str(content)


def researcher_node(state: AgentState) -> dict[str, Any]:
    task = (state.get("current_task") or "").strip()
    if not task:
        return {
            "research_findings": "",
            "status": "error",
            "messages": [
                AIMessage(content="[Researcher] No task.", name="researcher")
            ],
        }

    print(f"[Researcher] topic={task!r}")
    tools = get_research_tools()
    by_name = {t.name: t for t in tools}
    llm = get_llm(temperature=0.2).bind_tools(tools)

    history: list = [
        SystemMessage(content=RESEARCHER_SYSTEM),
        HumanMessage(
            content=f"Research this topic with tools, then write the brief.\n\nTopic: {task}"
        ),
    ]
    observations: list[str] = []
    final_text = ""
    tool_calls_logged = 0
    max_iters = max(1, settings.researcher_max_iters)

    for i in range(1, max_iters + 1):
        try:
            ai = llm.invoke(history)
        except Exception as exc:  # noqa: BLE001
            print(f"[Researcher] LLM error: {exc}")
            break
        history.append(ai)
        calls = getattr(ai, "tool_calls", None) or []
        if not calls:
            final_text = _text(ai.content).strip()
            print(f"[Researcher] answer at iter={i}")
            break
        print(f"[Researcher] tools iter={i}: {[c.get('name') for c in calls]}")
        for tc in calls:
            name = tc.get("name") or ""
            args = tc.get("args") or {}
            call_id = tc.get("id") or f"call_{i}_{name}"
            tool = by_name.get(name)
            try:
                result = (
                    tool.invoke(args)
                    if tool and isinstance(args, dict)
                    else (tool.invoke({"query": str(args)}) if tool else f"Unknown tool: {name}")
                )
            except Exception as exc:  # noqa: BLE001
                result = f"Error {name}: {exc}"
            result_str = str(result)
            observations.append(f"## {name}\n{result_str}")
            tool_calls_logged += 1
            history.append(
                ToolMessage(content=result_str[:12000], tool_call_id=call_id, name=name)
            )

    if not final_text:
        if observations:
            try:
                synth = get_llm(temperature=0.2).invoke(
                    [
                        SystemMessage(content=RESEARCHER_SYSTEM),
                        HumanMessage(
                            content=(
                                f"Topic: {task}\n\nUsing only these observations, write the brief.\n\n"
                                + "\n\n".join(observations)[:14000]
                            )
                        ),
                    ]
                )
                final_text = _text(synth.content).strip()
            except Exception:  # noqa: BLE001
                final_text = f"### Overview\n{task}\n\n### Key Facts\n" + "\n\n".join(
                    observations
                )
        else:
            final_text = f"### Overview\nNo data collected for: {task}"

    print(
        f"[Researcher] done findings={len(final_text)} tools={tool_calls_logged}"
    )
    return {
        "research_findings": final_text,
        "current_task": task,
        "status": "research",
        "messages": [
            AIMessage(
                content=f"[Researcher] done findings={len(final_text)} tools={tool_calls_logged}",
                name="researcher",
            )
        ],
    }
