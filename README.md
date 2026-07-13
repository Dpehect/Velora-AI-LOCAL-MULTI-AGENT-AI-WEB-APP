# Velora AI Lab

Local multi-agent research system — **Next.js** frontend (Vercel) + **FastAPI / LangGraph** backend (Fly.io) + **Ollama**.

```
velora/   (this repo)
├── frontend/          # Vercel — Next.js 15 + Tailwind + TypeScript
├── backend/           # Fly.io  — FastAPI + LangGraph + Ollama client
├── README.md
└── .gitignore
```

## Stack

| Layer    | Tech                         | Deploy  |
|----------|------------------------------|---------|
| Frontend | Next.js 15, Tailwind, TS     | Vercel  |
| Backend  | FastAPI, LangGraph, Ollama   | Fly.io  |
| LLM      | Ollama (`qwen2.5:7b`)        | Local / private host |

> **Scaffold status:** Folder structure and base configs are in place. Agent logic and UI will be filled in subsequent steps.

## Structure

```
frontend/
├── app/                 # App Router
├── components/          # UI components
├── lib/                 # utilities / API client
├── public/
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── next.config.ts
└── vercel.json

backend/
├── app/
│   ├── graph/           # LangGraph (state, supervisor, researcher, …)
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── Dockerfile
├── fly.toml
├── requirements.txt
└── .env.example
```

## Local development

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Health: http://127.0.0.1:8000/health

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://127.0.0.1:3000

Copy `frontend/.env.example` → `frontend/.env.local` and set:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## Deploy (later)

### Vercel (frontend)

- Root Directory: `frontend`
- Framework: Next.js
- Env: `NEXT_PUBLIC_API_URL=<fly-backend-url>`

### Fly.io (backend)

```bash
cd backend
fly launch   # or: fly apps create velora-ai-lab-api
fly deploy
```

Configure Ollama URL via secrets:

```bash
fly secrets set OLLAMA_BASE_URL=https://your-ollama-host OLLAMA_MODEL=qwen2.5:7b
```
