# Velora

```
velora/
├── frontend/     # Next.js 15 → Vercel
├── backend/      # FastAPI + LangGraph + Ollama → LOCAL ONLY
├── README.md
└── .gitignore
```

| Package | Where it runs |
|---------|----------------|
| **frontend/** | Vercel (or `npm run dev`) |
| **backend/** | Your computer only (not deployed) |

## Architecture (local backend)

```
POST /run → Supervisor → Researcher → Supervisor → findings
                ↑______________|
```

Model: **Ollama `qwen2.5:7b`** on localhost.

## Quick start

### 1. Backend (local)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
ollama pull qwen2.5:7b
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: http://127.0.0.1:8000/health  
- Run: `POST /run` `{ "task": "..." }`  
- Docs: http://127.0.0.1:8000/docs  

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

http://127.0.0.1:3000

## Layout

```
backend/app/
  main.py                 # CORS + POST /run
  config.py / llm.py
  graph/
    state.py
    supervisor.py
    researcher.py
    tools.py
    graph.py

frontend/
  app/
  components/LabApp.tsx
  lib/api.ts              # calls local /run
```

No Docker / Fly.io — backend stays on your machine.
