"""
Phase-1 integration test: Supervisor → Researcher → Supervisor → FINISH.

Prerequisites
-------------
1. Ollama running locally (http://localhost:11434)
2. Model pulled:  ollama pull qwen2.5:7b
3. Dependencies:  pip install -r requirements.txt

Usage
-----
    python test_phase1.py
    python test_phase1.py "Quantum computing basics"
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

# Ensure project root is on sys.path when run as a script
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import HumanMessage

from src.config import settings
from src.graph import build_graph
from src.state import initial_state


def main(topic: str | None = None) -> int:
    topic = (topic or "LangGraph multi-agent systems").strip()
    print("=" * 72)
    print("Phase-1 Multi-Agent Test (Supervisor + Researcher)")
    print(f"Model : {settings.ollama_model}")
    print(f"Ollama: {settings.ollama_base_url}")
    print(f"Topic : {topic}")
    print("=" * 72)

    app = build_graph()  # MemorySaver for simple tests
    state = initial_state(topic)
    state["messages"] = [HumanMessage(content=f"Research this topic: {topic}")]

    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    print("\n--- Invoking graph ---\n")
    final = app.invoke(state, config=config)

    print("\n" + "=" * 72)
    print("RESULT SUMMARY")
    print("=" * 72)
    print(f"status      : {final.get('status')}")
    print(f"next_agent  : {final.get('next_agent')}")
    print(f"reasoning   : {final.get('supervisor_reasoning')}")
    print(f"findings len: {len(final.get('research_findings') or '')} chars")
    print()
    print("--- research_findings (preview) ---")
    findings = final.get("research_findings") or "(empty)"
    print(findings[:3000] if len(findings) > 3000 else findings)
    if len(findings) > 3000:
        print(f"\n… truncated ({len(findings)} total chars)")
    print()
    print("--- message trail ---")
    for i, m in enumerate(final.get("messages") or []):
        name = getattr(m, "name", None) or m.__class__.__name__
        content = m.content if isinstance(m.content, str) else str(m.content)
        preview = content.replace("\n", " ")[:120]
        print(f"  [{i}] {name}: {preview}")

    ok = bool((final.get("research_findings") or "").strip())
    print()
    if ok:
        print("✓ Phase-1 flow OK: Supervisor routed to Researcher and findings exist.")
        return 0

    print("✗ Phase-1 flow incomplete: research_findings is empty.")
    print("  Check that Ollama is running and the model is pulled.")
    return 1


if __name__ == "__main__":
    arg_topic = " ".join(sys.argv[1:]).strip() or None
    raise SystemExit(main(arg_topic))
