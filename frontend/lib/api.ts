/**
 * HTTP client for the Velora backend.
 * No Python imports — network only.
 */

import { config } from "@/lib/config";
import type {
  AgentRunRequest,
  AgentRunResponse,
  HealthResponse,
} from "@/types/agent";

export type {
  AgentRunRequest,
  AgentRunResponse,
  HealthResponse,
  MessageOut,
} from "@/types/agent";

export const API_URL = config.apiUrl;

async function parseError(res: Response): Promise<string> {
  let detail = `Request failed (${res.status})`;
  try {
    const data = await res.json();
    if (typeof data.detail === "string") detail = data.detail;
    else if (data.detail) detail = JSON.stringify(data.detail);
    else if (data.error) detail = String(data.error);
  } catch {
    /* ignore */
  }
  return detail;
}

export async function checkHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const res = await fetch(`${API_URL}/health`, {
    method: "GET",
    signal,
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(await parseError(res));
  }
  return res.json();
}

export async function runAgent(
  body: AgentRunRequest,
  signal?: AbortSignal
): Promise<AgentRunResponse> {
  const res = await fetch(`${API_URL}/api/agent/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
    signal,
  });

  if (!res.ok) {
    throw new Error(await parseError(res));
  }

  return res.json();
}
