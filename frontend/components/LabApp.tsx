"use client";

import { useCallback, useEffect, useState } from "react";
import {
  RunResponse,
  checkHealth,
  runResearch,
} from "@/lib/api";

export function LabApp() {
  const [task, setTask] = useState("Retrieval Augmented Generation");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [model, setModel] = useState("");

  useEffect(() => {
    const c = new AbortController();
    checkHealth(c.signal)
      .then((h) => {
        setBackendOk(h.status === "ok");
        setModel(h.model);
      })
      .catch(() => setBackendOk(false));
    return () => c.abort();
  }, []);

  const onRun = useCallback(async () => {
    const t = task.trim();
    if (!t || loading) return;
    setLoading(true);
    setError(null);
    try {
      const data = await runResearch({ task: t });
      setResult(data);
      if (!data.ok && data.error) setError(data.error);
      setBackendOk(true);
    } catch (e) {
      setResult(null);
      setError(e instanceof Error ? e.message : String(e));
      setBackendOk(false);
    } finally {
      setLoading(false);
    }
  }, [task, loading]);

  return (
    <div className="min-h-screen bg-[#FAFAFA] text-[#1D1D1F]">
      <header className="border-b border-black/5 bg-white/70 backdrop-blur-xl">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-5 py-4">
          <div>
            <p className="text-sm font-semibold tracking-tight">Velora AI Lab</p>
            <p className="text-[11px] uppercase tracking-widest text-[#6E6E73]">
              Local multi-agent
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-[#6E6E73]">
            {model ? (
              <span className="rounded-full border border-black/5 bg-white px-3 py-1">
                {model}
              </span>
            ) : null}
            <span
              className={`rounded-full border px-3 py-1 ${
                backendOk
                  ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                  : backendOk === false
                    ? "border-rose-200 bg-rose-50 text-rose-700"
                    : "border-black/5 bg-white"
              }`}
            >
              {backendOk === true
                ? "Backend online"
                : backendOk === false
                  ? "Backend offline"
                  : "Checking…"}
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-5 py-12">
        <h1 className="max-w-xl text-3xl font-semibold tracking-tight sm:text-4xl">
          Research, locally.
        </h1>
        <p className="mt-3 max-w-lg text-[#6E6E73]">
          Supervisor + Researcher via LangGraph and Ollama on your machine.
          Frontend may be on Vercel; API stays local.
        </p>

        <div className="mt-10 grid gap-6 lg:grid-cols-5">
          <section className="rounded-3xl border border-white bg-white/80 p-6 shadow-sm lg:col-span-2">
            <label className="text-sm font-medium text-[#424245]" htmlFor="task">
              Topic
            </label>
            <textarea
              id="task"
              rows={4}
              value={task}
              onChange={(e) => setTask(e.target.value)}
              disabled={loading}
              className="mt-2 w-full resize-y rounded-2xl border border-black/10 px-4 py-3 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
              placeholder="What should we research?"
            />
            <button
              type="button"
              onClick={onRun}
              disabled={loading || !task.trim() || backendOk === false}
              className="mt-4 w-full rounded-full bg-indigo-500 px-5 py-3 text-sm font-medium text-white shadow-md shadow-indigo-500/25 transition hover:bg-indigo-600 disabled:opacity-50"
            >
              {loading ? "Running agents…" : "POST /run"}
            </button>
            {backendOk === false ? (
              <p className="mt-3 text-xs text-[#6E6E73]">
                Start backend:{" "}
                <code className="rounded bg-[#F5F5F7] px-1">
                  cd backend && uvicorn app.main:app --reload
                </code>
              </p>
            ) : null}
          </section>

          <section className="rounded-3xl border border-white bg-white/80 p-6 shadow-sm lg:col-span-3">
            {error ? (
              <p className="text-sm text-rose-600 whitespace-pre-wrap">{error}</p>
            ) : null}
            {!result && !error ? (
              <p className="text-sm text-[#A1A1A6]">
                Results appear here after a successful /run.
              </p>
            ) : null}
            {result ? (
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2 text-xs">
                  <span className="rounded-full bg-indigo-50 px-2.5 py-1 text-indigo-700">
                    {result.status}
                  </span>
                  <span className="rounded-full bg-[#F5F5F7] px-2.5 py-1 text-[#6E6E73]">
                    next: {result.next_agent}
                  </span>
                </div>
                {result.supervisor_reasoning ? (
                  <p className="text-xs text-[#6E6E73]">{result.supervisor_reasoning}</p>
                ) : null}
                <pre className="max-h-[50vh] overflow-auto whitespace-pre-wrap break-words text-sm leading-relaxed text-[#1D1D1F]">
                  {result.research_findings || "(empty)"}
                </pre>
              </div>
            ) : null}
          </section>
        </div>
      </main>
    </div>
  );
}
