"""FastAPI entrypoint — scaffold only."""

from fastapi import FastAPI

app = FastAPI(title="Velora AI Lab API", version="0.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "velora-backend"}
