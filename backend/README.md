# Velora Backend (local only)

Runs on **your machine**. Not deployed to Fly/Vercel/Docker cloud.

```
backend/
├── app/
│   ├── main.py              # FastAPI + POST /run + CORS
│   ├── config.py
│   ├── llm.py               # ChatOllama (qwen2.5:7b)
│   └── graph/
│       ├── state.py
│       ├── supervisor.py
│       ├── researcher.py
│       ├── tools.py         # Wikipedia + arXiv
│       └── graph.py
├── requirements.txt
├── .env.example
└── README.md
```

## Prerequisites

1. Python 3.11+
2. [Ollama](https://ollama.com) installed and running
3. Model:

```bash
ollama pull qwen2.5:7b
```

## Setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Liveness |
| `POST /run` | `{ "task": "..." }` → research pipeline |
| `/docs` | Swagger UI |

Example:

```bash
curl -X POST http://127.0.0.1:8000/run ^
  -H "Content-Type: application/json" ^
  -d "{\"task\": \"Retrieval Augmented Generation\"}"
```

## Graph (Phase-1)

```
START → Supervisor → Researcher → Supervisor → END
```

Writer / Critic not included yet.

## CORS

Open for local frontend (`localhost:3000`). Edit `CORS_ORIGINS` in `.env`.

When the frontend is on Vercel, point it at your PC via tunnel (e.g. ngrok) or keep both local.
