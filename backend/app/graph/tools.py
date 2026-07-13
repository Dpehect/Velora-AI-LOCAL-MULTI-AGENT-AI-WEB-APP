"""Local research tools: Wikipedia + Arxiv (robust User-Agent + API)."""

from __future__ import annotations

from typing import List

import requests
from langchain_core.tools import StructuredTool, Tool
from pydantic import BaseModel, Field

# Wikipedia requires a descriptive User-Agent (anonymous bots get 403).
USER_AGENT = (
    "VeloraAILab/0.1 (local multi-agent research; educational; "
    "contact: local-dev@velora.invalid)"
)
WIKI_API = "https://en.wikipedia.org/w/api.php"
SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
)


class WikiInput(BaseModel):
    query: str = Field(description="Search query or article title for Wikipedia.")


class ArxivInput(BaseModel):
    query: str = Field(
        description="Search query for arXiv (paper title, topic, or keywords)."
    )


def _wikipedia_search(query: str) -> str:
    """Run a Wikipedia lookup via MediaWiki API with a proper User-Agent."""
    query = (query or "").strip()
    if not query:
        return "Error: empty Wikipedia query."

    try:
        # 1) Search for best title
        search_resp = SESSION.get(
            WIKI_API,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": 3,
                "format": "json",
                "utf8": 1,
            },
            timeout=20,
        )
        search_resp.raise_for_status()
        search_data = search_resp.json()
        hits = (search_data.get("query") or {}).get("search") or []
        if not hits:
            return f"No Wikipedia results for: {query}"

        title = hits[0].get("title") or query

        # 2) Extract plain-text extract for that title
        extract_resp = SESSION.get(
            WIKI_API,
            params={
                "action": "query",
                "prop": "extracts|info",
                "exintro": 1,
                "explaintext": 1,
                "titles": title,
                "inprop": "url",
                "format": "json",
                "utf8": 1,
            },
            timeout=20,
        )
        extract_resp.raise_for_status()
        pages = (extract_resp.json().get("query") or {}).get("pages") or {}
        page = next(iter(pages.values()), {}) if pages else {}
        extract = (page.get("extract") or "").strip()
        fullurl = page.get("fullurl") or f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        page_title = page.get("title") or title

        if not extract:
            # Fallback: use search snippets
            snippets = []
            for h in hits[:3]:
                snip = (h.get("snippet") or "").replace("<span class=\"searchmatch\">", "").replace("</span>", "")
                snippets.append(f"- {h.get('title')}: {snip}")
            return (
                f"Title: {page_title}\nURL: {fullurl}\n\n"
                + "\n".join(snippets)
            )[:2000]

        if len(extract) > 1800:
            extract = extract[:1800] + "…"

        return f"Title: {page_title}\nURL: {fullurl}\n\n{extract}"
    except Exception as exc:  # noqa: BLE001
        # Last resort: langchain wrapper (may still 403 without UA)
        try:
            from langchain_community.tools import WikipediaQueryRun
            from langchain_community.utilities import WikipediaAPIWrapper

            wrapper = WikipediaAPIWrapper(
                top_k_results=2,
                doc_content_chars_max=1800,
                lang="en",
            )
            tool = WikipediaQueryRun(api_wrapper=wrapper)
            result = tool.run(query)
            if result and str(result).strip():
                return str(result).strip()
        except Exception as exc2:  # noqa: BLE001
            return f"Wikipedia error: {exc} | fallback: {exc2}"
        return f"Wikipedia error: {exc}"


def _arxiv_search(query: str) -> str:
    """Run an arXiv search; return titles/abstracts as plain text."""
    query = (query or "").strip()
    if not query:
        return "Error: empty arXiv query."

    try:
        import arxiv

        search = arxiv.Search(
            query=query,
            max_results=3,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        results = []
        if hasattr(arxiv, "Client"):
            client = arxiv.Client(
                page_size=3,
                delay_seconds=1.0,
                num_retries=2,
            )
            # Client may also need UA in some environments
            results = list(client.results(search))
        elif hasattr(search, "results"):
            results = list(search.results())
        else:
            return "arXiv client API unavailable in this environment."

        if not results:
            return f"No arXiv results for: {query}"

        blocks: list[str] = []
        for i, paper in enumerate(results, 1):
            abstract = (paper.summary or "").replace("\n", " ").strip()
            if len(abstract) > 600:
                abstract = abstract[:600] + "…"
            authors = ", ".join(a.name for a in (paper.authors or [])[:4])
            blocks.append(
                f"[{i}] {paper.title}\n"
                f"Authors: {authors}\n"
                f"Published: {getattr(paper, 'published', '')}\n"
                f"URL: {paper.entry_id}\n"
                f"Abstract: {abstract}"
            )
        return "\n\n".join(blocks)
    except Exception as exc:  # noqa: BLE001
        try:
            from langchain_community.tools import ArxivQueryRun
            from langchain_community.utilities import ArxivAPIWrapper

            wrapper = ArxivAPIWrapper(top_k_results=3, doc_content_chars_max=1200)
            tool = ArxivQueryRun(api_wrapper=wrapper)
            return str(tool.run(query)).strip() or f"arXiv error: {exc}"
        except Exception as exc2:  # noqa: BLE001
            return f"arXiv error: {exc} | fallback: {exc2}"


def get_research_tools() -> List[StructuredTool | Tool]:
    """Bound tools for the Researcher agent."""
    wikipedia_tool = StructuredTool.from_function(
        name="wikipedia",
        description=(
            "Search Wikipedia for factual background on a topic or entity. "
            "Input should be a concise search query or article title."
        ),
        func=_wikipedia_search,
        args_schema=WikiInput,
    )
    arxiv_tool = StructuredTool.from_function(
        name="arxiv",
        description=(
            "Search arXiv for academic papers related to a scientific or technical topic. "
            "Input should be keywords or a paper-related query."
        ),
        func=_arxiv_search,
        args_schema=ArxivInput,
    )
    return [wikipedia_tool, arxiv_tool]
