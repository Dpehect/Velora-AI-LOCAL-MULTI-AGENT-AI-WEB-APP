# Velora AI Lab

Local multi-agent research system:

| Layer | Tech | Deploy |
|-------|------|--------|
| **Frontend** | Next.js 15 + Tailwind + TypeScript | Vercel |
| **Backend** | FastAPI + LangGraph + Ollama | Fly.io |

```
├── frontend/     # Vercel
├── backend/      # Fly.io
├── README.md
└── .gitignore
```

## Architecture

```
Supervisor ⇄ Researcher | Writer | Critic → final_report
```

## Local development

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Ollama must be running with the model:
#   ollama pull qwen2.5:7b

uvicorn app.main:app --reload --port 8000
```

- Health: http://127.0.0.1:8000/health  
- Docs: http://127.0.0.1:8000/docs  
- Run: `POST /api/agent/run` `{ "task": "..." }`

### 2. Frontend

```bash
cd frontend
cp .env.example .env.local   # NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
npm install
npm run dev
```

Open http://127.0.0.1:3000

## Deploy

### Vercel (frontend)

- Root Directory: `frontend`
- Env: `NEXT_PUBLIC_API_URL=https://<your-fly-app>.fly.dev`

### Fly.io (backend)

```bash
cd backend
fly deploy
fly secrets set OLLAMA_BASE_URL=... OLLAMA_MODEL=qwen2.5:7b
```

## Backend layout

```
backend/app/
  main.py
  config.py
  llm.py
  graph/          # state, supervisor, researcher, writer, critic, tools
  routers/agent.py
  services/runner.py
  schemas/agent.py
```
