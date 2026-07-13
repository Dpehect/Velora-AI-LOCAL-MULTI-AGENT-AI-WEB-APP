# Velora AI Lab — Frontend

**Standalone** Next.js 15 + Tailwind + TypeScript UI.  
Deploy target: **Vercel**. Does not embed or import backend Python code.

```
frontend/
├── app/                 # Next.js App Router
├── components/          # UI components
├── lib/                 # API client + utils
├── types/               # Shared TS types (API contract)
├── public/
├── package.json
├── vercel.json
├── .env.example
└── README.md
```

## Prerequisites

- Node.js 18+
- Backend API running (see `../backend/README.md`) **or** a deployed Fly.io URL

## Setup

```bash
cd frontend
npm install
cp .env.example .env.local
```

Edit `.env.local`:

```env
# Local backend
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

# Production (Fly.io example)
# NEXT_PUBLIC_API_URL=https://velora-ai-lab-api.fly.dev
```

## Run

```bash
npm run dev
```

Open http://127.0.0.1:3000

| Script | Command |
|--------|---------|
| Dev | `npm run dev` |
| Build | `npm run build` |
| Start | `npm start` |
| Lint | `npm run lint` |

## How it talks to the backend

Only over HTTP — no shared runtime with Python:

| Frontend | Backend |
|----------|---------|
| `lib/api.ts` | `POST /api/agent/run` |
| `checkHealth()` | `GET /health` |

Types live in `types/agent.ts` and mirror the backend response schema  
documented in `backend/README.md`.

## Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes (prod) | Backend base URL, no trailing slash |

## Deploy (Vercel)

1. Import this monorepo on Vercel  
2. **Root Directory:** `frontend`  
3. Framework: Next.js  
4. Env: `NEXT_PUBLIC_API_URL=https://<your-fly-app>.fly.dev`  
5. Deploy  

`vercel.json` is already in this folder.

## Independence rules

- No imports from `../backend`
- Own `node_modules`, own scripts
- Own env (`.env.local`)
- Backend URL is configuration only (`NEXT_PUBLIC_API_URL`)
