# Velora — Backend

FastAPI + LangGraph + Ollama. Deploy: **Fly.io**.

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Scaffold only — agents and routes not implemented yet.

```bash
fly deploy   # from this directory
```
