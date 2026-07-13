# Velora Frontend

Next.js 15 + Tailwind + TypeScript → **Vercel**.

Backend is **local only** — set the API URL to your machine (or a tunnel).

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

`NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`

## Vercel

Root Directory: `frontend`  
Env: `NEXT_PUBLIC_API_URL` → local tunnel URL if you expose the PC API.
