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

## Vercel + local backend

Root Directory: `frontend`

**Important:** A Vercel site is **HTTPS**. Browsers block calls to `http://127.0.0.1:8000` (mixed content).  
So `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000` will show **Backend offline** on the live site.

### Fix: tunnel your PC API (HTTPS)

1. Backend on PC:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
2. Tunnel (pick one):
   ```bash
   # Cloudflare (free)
   cloudflared tunnel --url http://127.0.0.1:8000

   # or ngrok
   ngrok http 8000
   ```
3. Copy the `https://....` URL.
4. Vercel → Project → Settings → Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://YOUR-TUNNEL-URL
   ```
5. Redeploy frontend (env is baked in at build time for `NEXT_PUBLIC_*`).

### Local UI only (no Vercel)

```bash
npm run dev
# .env.local → NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```
