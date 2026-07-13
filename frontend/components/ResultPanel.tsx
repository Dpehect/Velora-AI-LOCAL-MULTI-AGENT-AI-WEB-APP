"use client";

import { useState } from "react";
import type { AgentRunResponse } from "@/types/agent";
import { shortId } from "@/lib/utils";

type Tab = "final" | "findings" | "draft" | "critic" | "messages";

type Props = {
  result: AgentRunResponse | null;
  error?: string | null;
};

export function ResultPanel({ result, error }: Props) {
  const [tab, setTab] = useState<Tab>("final");

  if (error) {
    return (
      <div className="rounded-3xl border border-rose-100 bg-rose-50/80 p-6 text-[14px] text-rose-800 shadow-soft">
        <p className="font-semibold">Request failed</p>
        <p className="mt-2 whitespace-pre-wrap text-rose-700/90">{error}</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="rounded-3xl border border-dashed border-ink-100 bg-white/40 px-6 py-16 text-center shadow-soft">
        <p className="text-[15px] text-ink-400">
          Run a topic to see the final report and agent trail.
        </p>
      </div>
    );
  }

  const tabs: { id: Tab; label: string }[] = [
    { id: "final", label: "Final report" },
    { id: "findings", label: "Research" },
    { id: "draft", label: "Draft" },
    { id: "critic", label: "Critic" },
    { id: "messages", label: "Messages" },
  ];

  const body: Record<Tab, string> = {
    final: result.final_report || result.draft_report || "(empty)",
    findings: result.research_findings || "(empty)",
    draft: result.draft_report || "(empty)",
    critic: result.critic_feedback || "(empty)",
    messages: result.messages
      .map(
        (m, i) =>
          `[${i}] ${m.role}${m.name ? `/${m.name}` : ""}\n${m.content}`
      )
      .join("\n\n---\n\n") || "(no messages)",
  };

  return (
    <div className="rounded-3xl border border-white/90 bg-white/70 shadow-soft backdrop-blur-xl overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-ink-100/80 px-5 py-4 sm:px-6">
        <div className="flex flex-wrap items-center gap-2 text-[12px]">
          <StatusChip status={result.status} ok={result.ok} />
          <span className="rounded-full bg-ink-50 px-2.5 py-1 text-ink-400">
            revisions: {result.revision_count}
          </span>
          <span className="rounded-full bg-ink-50 px-2.5 py-1 text-ink-400">
            thread: {shortId(result.thread_id)}
          </span>
        </div>
        {result.supervisor_reasoning ? (
          <p className="max-w-md text-right text-[12px] text-ink-300">
            {result.supervisor_reasoning}
          </p>
        ) : null}
      </div>

      <div className="flex gap-1 overflow-x-auto border-b border-ink-100/60 px-3 pt-3 sm:px-4">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={`rounded-t-xl px-3 py-2 text-[13px] font-medium transition ${
              tab === t.id
                ? "bg-accent-muted text-accent"
                : "text-ink-400 hover:text-ink-600"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <pre className="max-h-[min(60vh,640px)] overflow-auto whitespace-pre-wrap break-words px-5 py-5 font-sans text-[14px] leading-relaxed text-ink-600 sm:px-6">
        {body[tab]}
      </pre>
    </div>
  );
}

function StatusChip({ status, ok }: { status: string; ok: boolean }) {
  const tone = ok
    ? "bg-emerald-50 text-emerald-700 border-emerald-100"
    : "bg-amber-50 text-amber-800 border-amber-100";
  return (
    <span className={`rounded-full border px-2.5 py-1 font-medium ${tone}`}>
      {status || (ok ? "done" : "error")}
    </span>
  );
}
