/**
 * API contract types for the Velora backend.
 * Keep in sync with backend/app/schemas/agent.py (HTTP JSON only).
 */

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
