/**
 * Talks to the local FastAPI backend (not deployed).
 * Set NEXT_PUBLIC_API_URL to http://127.0.0.1:8000 for local dev.
 */

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

export type RunRequest = {
  task: string;
  thread_id?: string | null;
};

export type RunResponse = {
  thread_id: string;
  task: string;
  status: string;
  next_agent: string;
  supervisor_reasoning: string;
  research_findings: string;
  ok: boolean;
  error?: string | null;
};

export type HealthResponse = {
  status: string;
  model: string;
  ollama_base_url: string;
  mode: string;
  nodes: string[];
};

export async function checkHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/health`, { signal, cache: "no-store" });
  if (!res.ok) throw new Error(`Health failed (${res.status})`);
  return res.json();
}

export async function runResearch(
  body: RunRequest,
  signal?: AbortSignal
): Promise<RunResponse> {
  const res = await fetch(`${API_URL}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json();
}
