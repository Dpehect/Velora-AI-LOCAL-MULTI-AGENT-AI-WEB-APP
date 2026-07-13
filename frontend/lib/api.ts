/**
 * Velora backend API client.
 * Set NEXT_PUBLIC_API_URL to the Fly.io (or local) FastAPI base URL.
 */

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

export type MessageOut = {
  role: string;
  name?: string | null;
  content: string;
};

export type AgentRunRequest = {
  task: string;
  thread_id?: string | null;
};

export type AgentRunResponse = {
  thread_id: string;
  task: string;
  status: string;
  next_agent: string;
  supervisor_reasoning: string;
  research_findings: string;
  draft_report: string;
  critic_feedback: string;
  final_report: string;
  revision_count: number;
  messages: MessageOut[];
  message_count: number;
  ok: boolean;
  error?: string | null;
};

export type HealthResponse = {
  status: string;
  model: string;
  ollama_base_url: string;
  phase: string;
  graph_nodes: string[];
};

export async function checkHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/health`, {
    method: "GET",
    signal,
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Health check failed (${res.status})`);
  }
  return res.json();
}

export async function runAgent(
  body: AgentRunRequest,
  signal?: AbortSignal
): Promise<AgentRunResponse> {
  const res = await fetch(`${API_URL}/api/agent/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail ?? data);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }

  return res.json();
}
