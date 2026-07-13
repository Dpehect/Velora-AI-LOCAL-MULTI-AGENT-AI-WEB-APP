# Velora AI — Local Multi-Agent (Phase 1)

Hierarchical multi-agent research pipeline with **FastAPI**, **LangGraph 1.x**, and **Ollama** (`qwen2.5:7b`). Fully local.

## Architecture

```
START → Supervisor → Researcher → Supervisor → FINISH
              │                        ▲
              └────────────────────────┘
```

| Agent      | Role                                         | Status   |
|------------|----------------------------------------------|----------|
| Supervisor | Routes via `next_agent` / `status`           | ✅ Phase-1 |
| Researcher | Wikipedia + arXiv tools → `research_findings`| ✅ Phase-1 |
| Writer     | Draft report                                 | ⏳ Phase-2 |
| Critic     | Quality review                               | ⏳ Phase-2 |

## Layout

```
app/
  main.py                 # FastAPI
  config.py
  llm.py                  # ChatOllama
  graph/
    state.py              # AgentState
    supervisor.py
    researcher.py
    tools.py              # Wikipedia + arXiv
    graph.py              # StateGraph
requirements.txt
```

## Prerequisites

1. Python 3.11+
2. Ollama at `http://localhost:11434`
3. Model: `ollama pull qwen2.5:7b`

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

Optional `.env`:

```env
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
```

## Run API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Docs: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

```bash
curl -X POST http://localhost:8000/research ^
  -H "Content-Type: application/json" ^
  -d "{\"topic\": \"Retrieval Augmented Generation\"}"
```

## AgentState

- `messages` — history (`add_messages`)
- `current_task` — user topic
- `research_findings` — Researcher brief
- `draft_report` / `critic_feedback` / `final_report` — Phase-2
- `status` — `idle` | `research` | `write` | `critic` | `done` | `error`
- `next_agent` — `researcher` | `writer` | `critic` | `FINISH`
