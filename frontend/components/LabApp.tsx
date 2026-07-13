"use client";

import { useCallback, useEffect, useState } from "react";
import {
  AgentRunResponse,
  checkHealth,
  runAgent,
} from "@/lib/api";
import { Navbar } from "@/components/Navbar";
import { ResearchForm } from "@/components/ResearchForm";
import { ResultPanel } from "@/components/ResultPanel";

export function LabApp() {
  const [task, setTask] = useState("Retrieval Augmented Generation");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AgentRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [model, setModel] = useState<string>("");

  useEffect(() => {
    const ctrl = new AbortController();
    checkHealth(ctrl.signal)
      .then((h) => {
        setBackendOk(h.status === "ok");
        setModel(h.model);
      })
      .catch(() => setBackendOk(false));
    return () => ctrl.abort();
  }, []);

  const onSubmit = useCallback(async () => {
    const cleaned = task.trim();
    if (!cleaned || loading) return;

    setLoading(true);
    setError(null);

    try {
      const data = await runAgent({ task: cleaned });
      setResult(data);
      if (!data.ok && data.error) {
        setError(data.error);
      }
      setBackendOk(true);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
      setResult(null);
      if (msg.includes("Failed to fetch") || msg.includes("NetworkError")) {
        setBackendOk(false);
      }
    } finally {
      setLoading(false);
    }
  }, [task, loading]);

  return (
    <div className="min-h-screen bg-canvas text-ink-600">
      <div className="pointer-events-none fixed inset-0 overflow-hidden" aria-hidden>
        <div className="absolute -right-20 -top-24 h-[420px] w-[420px] rounded-full bg-accent/[0.08] blur-[100px]" />
        <div className="absolute -left-24 bottom-0 h-[360px] w-[360px] rounded-full bg-indigo-200/30 blur-[100px]" />
      </div>

      <Navbar backendOk={backendOk} model={model} />

      <main className="relative mx-auto max-w-6xl px-5 pb-20 pt-10 sm:px-6 sm:pt-14">
        <section className="mb-10 max-w-2xl">
          <p className="mb-3 text-[12px] font-semibold uppercase tracking-[0.16em] text-accent">
            Multi-agent research
          </p>
          <h1 className="text-[clamp(1.9rem,4vw,2.75rem)] font-semibold leading-tight tracking-tight text-ink-600">
            Intelligence, quietly powerful.
          </h1>
          <p className="mt-4 text-[16px] leading-relaxed text-ink-400">
            Local pipeline: Supervisor routes Researcher, Writer, and Critic over
            LangGraph + Ollama. Enter a topic and get a structured report.
          </p>
        </section>

        <div className="grid gap-6 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <ResearchForm
              task={task}
              onTaskChange={setTask}
              onSubmit={onSubmit}
              loading={loading}
              disabled={backendOk === false}
            />
            {backendOk === false ? (
              <p className="mt-4 text-[13px] text-ink-400">
                Start the backend:{" "}
                <code className="rounded bg-white px-1.5 py-0.5 text-[12px] text-ink-500">
                  cd backend && uvicorn app.main:app --reload
                </code>
              </p>
            ) : null}
          </div>
          <div className="lg:col-span-3">
            <ResultPanel result={result} error={error} />
          </div>
        </div>
      </main>

      <footer className="relative border-t border-ink-100/70 py-8 text-center text-[13px] text-ink-300">
        Velora AI Lab · FastAPI · LangGraph · Ollama
      </footer>
    </div>
  );
}
