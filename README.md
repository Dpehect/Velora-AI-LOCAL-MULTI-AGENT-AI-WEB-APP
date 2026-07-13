# Velora AI — Local Multi-Agent (Phase 2)

Hierarchical multi-agent research pipeline with **FastAPI**, **LangGraph 1.x**, and **Ollama** (`qwen2.5:7b`). Fully local.

## Architecture

```
START → Supervisor ⇄ Researcher
                  ⇄ Writer
                  ⇄ Critic
                  → FINISH (+ final_report)
```

Typical path:

```
Supervisor → Researcher → Writer → Critic → (Writer if REVISE)* → Critic → done
```

| Agent      | Role                                              | Status   |
|------------|---------------------------------------------------|----------|
| Supervisor | Sole router (`next_agent` / `status`)             | ✅        |
| Researcher | Wikipedia + arXiv → `research_findings`           | ✅        |
| Writer     | Findings (+ feedback) → `draft_report`            | ✅ Phase-2 |
| Critic     | Draft review → `critic_feedback` (APPROVE/REVISE) | ✅ Phase-2 |

## Layout

```
app/
  main.py
  config.py               # max_revisions, Ollama settings
  llm.py
  graph/
    state.py              # AgentState (+ revision_count)
    supervisor.py
    researcher.py
    writer.py
    critic.py
    tools.py
    graph.py
requirements.txt
```

## Prerequisites

1. Python 3.11+
2. Ollama: `ollama pull qwen2.5:7b`
3. `pip install -r requirements.txt`

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

```bash
curl -X POST http://localhost:8000/research ^
  -H "Content-Type: application/json" ^
  -d "{\"topic\": \"Retrieval Augmented Generation\"}"
```

## Routing policy (Supervisor)

1. No task → error / FINISH  
2. No findings → **researcher**  
3. Findings, no draft → **writer**  
4. Draft, no feedback → **critic**  
5. Verdict **REVISE** and `revision_count < max_revisions` → **writer** (then critic again)  
6. **APPROVE** or revision budget exhausted → **FINISH**, copy draft → `final_report`  

Deterministic fallback always applies if the LLM returns invalid JSON.

## AgentState

- `messages`, `current_task`
- `research_findings`, `draft_report`, `critic_feedback`, `final_report`
- `status`, `next_agent`, `supervisor_reasoning`
- `revision_count` — Writer revision passes after Critic REVISE
