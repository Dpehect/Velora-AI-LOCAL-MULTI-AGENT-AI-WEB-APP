# Velora

Monorepo scaffold: **frontend** (Vercel) + **backend** (Fly.io).

```
velora/
├── frontend/          # Next.js 15 + Tailwind + TypeScript → Vercel
├── backend/           # FastAPI + LangGraph + Ollama → Fly.io
├── README.md
└── .gitignore
```

## Packages

| Folder | Stack | Deploy |
|--------|--------|--------|
| [`frontend/`](./frontend) | Next.js 15, Tailwind, TypeScript | Vercel |
| [`backend/`](./backend) | FastAPI, LangGraph, Ollama | Fly.io |

> **Status:** Folder structure + base configs only. Application logic is not implemented yet.

## Layout

```
frontend/
├── app/
├── components/
├── lib/
├── public/
├── package.json
├── tsconfig.json
└── vercel.json

backend/
├── app/
│   ├── graph/          # LangGraph placeholders
│   ├── routers/
│   └── main.py
├── Dockerfile
├── fly.toml
├── requirements.txt
└── .env.example
```

## Local (later)

```bash
# Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm run dev
```
