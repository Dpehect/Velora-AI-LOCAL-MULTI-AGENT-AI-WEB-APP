# Velora Frontend

Next.js 15 + Tailwind + TypeScript lab UI (Vercel).

Does **not** use the old `ai-lab-landing/` static site.

## Run

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

`NEXT_PUBLIC_API_URL` → backend base URL (default `http://127.0.0.1:8000`).

## Deploy (Vercel)

Root Directory: `frontend`  
Env: `NEXT_PUBLIC_API_URL=https://your-api.fly.dev`
