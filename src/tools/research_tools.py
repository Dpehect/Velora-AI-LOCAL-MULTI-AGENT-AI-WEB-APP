"""Local-only research tools: Wikipedia and Arxiv."""

from __future__ import annotations

from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper

from src.config import settings


def get_research_tools() -> list:
    """
    Return the Researcher's allowed tools.

    Constraints (by design):
    - WikipediaQueryRun  → general knowledge / encyclopedic context
    - ArxivQueryRun      → academic papers / technical depth
    - No web search, no paid APIs.
    """
    wikipedia = WikipediaQueryRun(
        api_wrapper=WikipediaAPIWrapper(
            top_k_results=settings.wiki_top_k,
            doc_content_chars_max=settings.wiki_chars,
        ),
        description=(
            "Search Wikipedia for encyclopedic background on a topic. "
            "Input should be a short, focused search query string."
        ),
    )

    arxiv = ArxivQueryRun(
        api_wrapper=ArxivAPIWrapper(
            top_k_results=settings.arxiv_top_k,
            doc_content_chars_max=settings.arxiv_chars,
        ),
        description=(
            "Search arXiv for scientific preprints related to a topic. "
            "Input should be a short academic-style search query string."
        ),
    )

    return [wikipedia, arxiv]


def run_tool_by_name(tools: list, name: str, query: str) -> str:
    """Execute a tool by name; return a clear error string on failure."""
    tool_map = {t.name: t for t in tools}
    tool = tool_map.get(name)
    if tool is None:
        return f"Error: unknown tool '{name}'. Available: {list(tool_map)}"
    try:
        return str(tool.invoke(query))
    except Exception as exc:  # noqa: BLE001 — surface tool errors to the LLM
        return f"Error running {name}: {exc}"
