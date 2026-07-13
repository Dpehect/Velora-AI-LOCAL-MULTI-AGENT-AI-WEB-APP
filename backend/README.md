# Velora Backend

FastAPI + LangGraph multi-agent API (Fly.io).

## Layout

Former `src/` / agent modules live under `app/graph/`:

| Module | Role |
|--------|------|
| `graph/state.py` | AgentState |
| `graph/supervisor.py` | Router agent |
| `graph/researcher.py` | Wikipedia + arXiv |
| `graph/writer.py` | draft_report |
| `graph/critic.py` | critic_feedback |
| `graph/tools.py` | research tools |
| `graph/graph.py` | StateGraph compile |
| `routers/agent.py` | HTTP API |
| `main.py` | FastAPI app |

## Run

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Deploy

```bash
fly deploy
fly secrets set OLLAMA_BASE_URL=... OLLAMA_MODEL=qwen2.5:7b
```
