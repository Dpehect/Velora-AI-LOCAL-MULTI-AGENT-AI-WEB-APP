"use client";

type Props = {
  task: string;
  onTaskChange: (v: string) => void;
  onSubmit: () => void;
  loading: boolean;
  disabled?: boolean;
};

const SUGGESTIONS = [
  "Retrieval Augmented Generation",
  "LangGraph multi-agent systems",
  "Local LLM privacy trade-offs",
];

export function ResearchForm({
  task,
  onTaskChange,
  onSubmit,
  loading,
  disabled,
}: Props) {
  return (
    <div className="rounded-3xl border border-white/90 bg-white/70 p-6 shadow-soft backdrop-blur-xl sm:p-8">
      <label htmlFor="task" className="block text-[13px] font-medium text-ink-500">
        Research topic
      </label>
      <textarea
        id="task"
        rows={3}
        value={task}
        onChange={(e) => onTaskChange(e.target.value)}
        placeholder="What should Velora research and report on?"
        disabled={loading || disabled}
        className="mt-2 w-full resize-y rounded-2xl border border-ink-100 bg-white/90 px-4 py-3 text-[15px] text-ink-600 outline-none ring-accent/30 transition placeholder:text-ink-300 focus:border-accent/40 focus:ring-2 disabled:opacity-60"
      />

      <div className="mt-3 flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            type="button"
            disabled={loading}
            onClick={() => onTaskChange(s)}
            className="rounded-full border border-ink-100 bg-white/80 px-3 py-1 text-[12px] text-ink-400 transition hover:border-accent/30 hover:text-accent disabled:opacity-50"
          >
            {s}
          </button>
        ))}
      </div>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-[13px] text-ink-300">
          Supervisor → Researcher → Writer → Critic
        </p>
        <button
          type="button"
          onClick={onSubmit}
          disabled={loading || disabled || !task.trim()}
          className="inline-flex items-center justify-center rounded-full bg-accent px-7 py-3 text-[14px] font-medium text-white shadow-btn transition hover:bg-accent-deep disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? (
            <span className="inline-flex items-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              Running agents…
            </span>
          ) : (
            "Run pipeline"
          )}
        </button>
      </div>
    </div>
  );
}
