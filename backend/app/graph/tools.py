"""Local research tools: Wikipedia + arXiv."""

from __future__ import annotations

from typing import List

import requests
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

USER_AGENT = (
    "VeloraLocal/0.1 (local multi-agent; educational; contact: local@velora.dev)"
)
WIKI_API = "https://en.wikipedia.org/w/api.php"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})


class WikiInput(BaseModel):
    query: str = Field(description="Wikipedia search query or article title.")


class ArxivInput(BaseModel):
    query: str = Field(description="arXiv search keywords.")


def _wikipedia_search(query: str) -> str:
    query = (query or "").strip()
    if not query:
        return "Error: empty Wikipedia query."
    try:
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
        hits = (search_resp.json().get("query") or {}).get("search") or []
        if not hits:
            return f"No Wikipedia results for: {query}"
        title = hits[0].get("title") or query

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
        fullurl = page.get("fullurl") or (
            f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
        )
        page_title = page.get("title") or title
        if len(extract) > 1800:
            extract = extract[:1800] + "…"
        if not extract:
            return f"Title: {page_title}\nURL: {fullurl}\n(No extract.)"
        return f"Title: {page_title}\nURL: {fullurl}\n\n{extract}"
    except Exception as exc:  # noqa: BLE001
        return f"Wikipedia error: {exc}"


def _arxiv_search(query: str) -> str:
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
        if hasattr(arxiv, "Client"):
            results = list(arxiv.Client(page_size=3, delay_seconds=1.0).results(search))
        else:
            results = list(search.results())  # type: ignore[attr-defined]
        if not results:
            return f"No arXiv results for: {query}"
        blocks: list[str] = []
        for i, paper in enumerate(results, 1):
            abstract = (paper.summary or "").replace("\n", " ").strip()
            if len(abstract) > 500:
                abstract = abstract[:500] + "…"
            authors = ", ".join(a.name for a in (paper.authors or [])[:3])
            blocks.append(
                f"[{i}] {paper.title}\nAuthors: {authors}\n"
                f"URL: {paper.entry_id}\nAbstract: {abstract}"
            )
        return "\n\n".join(blocks)
    except Exception as exc:  # noqa: BLE001
        return f"arXiv error: {exc}"


def get_research_tools() -> List[StructuredTool]:
    return [
        StructuredTool.from_function(
            name="wikipedia",
            description="Search Wikipedia for factual background.",
            func=_wikipedia_search,
            args_schema=WikiInput,
        ),
        StructuredTool.from_function(
            name="arxiv",
            description="Search arXiv for academic papers.",
            func=_arxiv_search,
            args_schema=ArxivInput,
        ),
    ]
