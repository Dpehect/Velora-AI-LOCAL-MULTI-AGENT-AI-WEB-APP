# Velora AI Lab — Backend

**Standalone** FastAPI + LangGraph multi-agent API.  
Deploy target: **Fly.io**. Does not depend on the frontend package.

```
backend/
├── app/
│   ├── main.py              # FastAPI entry
│   ├── config.py            # Settings (env)
│   ├── llm.py               # ChatOllama factory
│   ├── graph/               # LangGraph agents
│   ├── routers/             # HTTP routes
│   ├── schemas/             # Pydantic models
│   └── services/            # Graph runner
├── Dockerfile
├── fly.toml
├── requirements.txt
├── .env.example
└── README.md
```

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) with `qwen2.5:7b`

```bash
ollama pull qwen2.5:7b
```

## Setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
# from backend/ with venv active
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| URL | Purpose |
|-----|---------|
| http://127.0.0.1:8000/health | Health |
| http://127.0.0.1:8000/docs | OpenAPI |
| `POST /api/agent/run` | Run pipeline |

## API contract (consumed by frontend)

### `POST /api/agent/run`

```json
// request
{ "task": "Retrieval Augmented Generation", "thread_id": null }

// response (shape)
{
  "thread_id": "uuid",
  "task": "...",
  "status": "done",
  "next_agent": "FINISH",
  "supervisor_reasoning": "...",
  "research_findings": "...",
  "draft_report": "...",
  "critic_feedback": "...",
  "final_report": "...",
  "revision_count": 0,
  "messages": [{ "role": "ai", "name": "supervisor", "content": "..." }],
  "message_count": 0,
  "ok": true,
  "error": null
}
```

### `GET /health`

```json
{
  "status": "ok",
  "model": "qwen2.5:7b",
  "ollama_base_url": "http://localhost:11434",
  "phase": "3",
  "graph_nodes": ["supervisor", "researcher", "writer", "critic"]
}
```

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `qwen2.5:7b` | Chat model |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama host |
| `CORS_ORIGINS` | `*` | Comma-separated frontend origins |
| `MAX_REVISIONS` | `2` | Writer↔Critic loop budget |

Production example:

```env
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

## Graph flow

```
START → Supervisor ⇄ Researcher | Writer | Critic → FINISH
```

## Deploy (Fly.io)

```bash
cd backend
fly launch   # first time only
fly secrets set OLLAMA_BASE_URL=... OLLAMA_MODEL=qwen2.5:7b CORS_ORIGINS=https://...
fly deploy
```

## Independence rules

- No imports from `../frontend`
- Own venv, own deps (`requirements.txt`)
- Own env file (`.env`)
- Frontend talks **only** over HTTP to this API
