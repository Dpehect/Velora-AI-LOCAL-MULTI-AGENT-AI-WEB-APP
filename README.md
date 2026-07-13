# Velora AI Lab

```
velora/
├── frontend/     # Next.js 15 → Vercel
├── backend/      # FastAPI + LangGraph → Fly.io
├── README.md
└── .gitignore
```

| Package | Stack | Deploy |
|---------|--------|--------|
| `frontend/` | Next.js 15, Tailwind, TypeScript | Vercel |
| `backend/` | FastAPI, LangGraph, Ollama | Fly.io |

## Backend layout

```
backend/app/
  main.py                 # FastAPI entry + CORS
  config.py
  llm.py
  graph/
    state.py
    supervisor.py
    researcher.py
    writer.py
    critic.py
    tools.py              # Wikipedia + arXiv
    graph.py
  routers/agent.py        # POST /api/agent/run
  services/runner.py
  schemas/agent.py
```

## Run

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
ollama pull qwen2.5:7b
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
cp .env.example .env.local   # NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
npm install
npm run dev
```

- UI: http://127.0.0.1:3000  
- API docs: http://127.0.0.1:8000/docs  

## API

`POST /api/agent/run` body: `{ "task": "..." }`  
Returns `final_report`, `status`, `messages`, research/draft/critic fields.
