# Velora AI Lab

Two **independent** packages in one repo. They only talk over **HTTP**.

```
velora/
├── frontend/     # Next.js 15 → Vercel
├── backend/      # FastAPI + LangGraph → Fly.io
├── README.md     # this file (hub only)
└── .gitignore
```

| Package | Stack | Deploy | Docs |
|---------|--------|--------|------|
| [`frontend/`](./frontend) | Next.js 15, Tailwind, TypeScript | Vercel | [frontend/README.md](./frontend/README.md) |
| [`backend/`](./backend) | FastAPI, LangGraph, Ollama | Fly.io | [backend/README.md](./backend/README.md) |

## Separation rules

1. **No shared runtime** — frontend never imports Python; backend never imports Next/React.
2. **No shared `node_modules` / venv** — each package installs its own deps.
3. **Single coupling point** — `NEXT_PUBLIC_API_URL` (frontend) → FastAPI base URL (backend).
4. **Own env files** — `frontend/.env.local`, `backend/.env`.
5. **Own deploy configs** — `frontend/vercel.json`, `backend/Dockerfile` + `fly.toml`.

```
┌─────────────┐   HTTP    ┌─────────────┐   HTTP    ┌────────┐
│  Frontend   │ ────────► │   Backend   │ ────────► │ Ollama │
│  (Vercel)   │  JSON API │   (Fly.io)  │           │        │
└─────────────┘           └─────────────┘           └────────┘
```

## Quick start (two terminals)

### Terminal A — Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Terminal B — Frontend

```bash
cd frontend
npm install
cp .env.example .env.local      # NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
npm run dev
```

- UI: http://127.0.0.1:3000  
- API: http://127.0.0.1:8000/docs  

## Deploy overview

| Step | Where | Action |
|------|--------|--------|
| 1 | Fly.io | `cd backend && fly deploy` (+ Ollama secrets) |
| 2 | Vercel | Root Directory = `frontend`, set `NEXT_PUBLIC_API_URL` |
| 3 | Backend | `CORS_ORIGINS=https://your-app.vercel.app` |

Details: [backend/README.md](./backend/README.md) · [frontend/README.md](./frontend/README.md)
