# Velora AI — Local Multi-Agent (Phase 3)

Hierarchical multi-agent research pipeline with **FastAPI**, **LangGraph 1.x**, and **Ollama** (`qwen2.5:7b`). Fully local.

## Architecture

```
START → Supervisor ⇄ Researcher | Writer | Critic → FINISH (+ final_report)
```

| Agent      | Role                                   |
|------------|----------------------------------------|
| Supervisor | Sole router                            |
| Researcher | Wikipedia + arXiv → findings           |
| Writer     | Findings → draft_report                |
| Critic     | Draft → APPROVE / REVISE feedback      |

## Run API

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
ollama pull qwen2.5:7b

uvicorn app.main:app --reload
```

- Docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  

### Run the pipeline

```bash
curl -X POST http://127.0.0.1:8000/api/agent/run ^
  -H "Content-Type: application/json" ^
  -d "{\"task\": \"Retrieval Augmented Generation\"}"
```

**Request**

```json
{ "task": "string", "thread_id": "optional-uuid" }
```

**Response** (selected fields)

```json
{
  "thread_id": "...",
  "task": "...",
  "status": "done",
  "final_report": "# ...",
  "research_findings": "...",
  "draft_report": "...",
  "critic_feedback": "...",
  "messages": [{ "role": "ai", "name": "supervisor", "content": "..." }],
  "ok": true
}
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness + model config |
| `GET` | `/` | API index |
| `POST` | `/api/agent/run` | Run full multi-agent graph |
| `GET` | `/api/agent/graph` | Topology for UI |

## Layout

```
app/
  main.py                 # FastAPI app + CORS + /health
  config.py
  llm.py
  routers/
    agent.py              # /api/agent/*
  services/
    runner.py             # graph.invoke wrapper
  schemas/
    agent.py              # Pydantic models
  graph/
    state.py
    supervisor.py
    researcher.py
    writer.py
    critic.py
    tools.py
    graph.py
```

## Optional env

```env
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
MAX_REVISIONS=2
CORS_ORIGINS=*
```
