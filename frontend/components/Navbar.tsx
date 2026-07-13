"use client";

import Link from "next/link";

type Props = {
  backendOk?: boolean | null;
  model?: string;
};

export function Navbar({ backendOk, model }: Props) {
  return (
    <header className="sticky top-0 z-40 border-b border-ink-100/80 bg-canvas/75 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4 sm:px-6">
        <Link href="/" className="group flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-white shadow-soft ring-1 ring-black/[0.04]">
            <span className="relative flex h-9 w-9 items-center justify-center">
              <svg viewBox="0 0 64 64" className="h-8 w-8" aria-hidden>
                <defs>
                  <linearGradient id="vg" x1="12" y1="8" x2="52" y2="56">
                    <stop stopColor="#818CF8" />
                    <stop offset="0.5" stopColor="#6366F1" />
                    <stop offset="1" stopColor="#4F46E5" />
                  </linearGradient>
                </defs>
                <rect x="4" y="4" width="56" height="56" rx="16" fill="#EEF2FF" opacity="0.7" />
                <path
                  d="M18 22.5c0 0 6.5 18.5 14 24.5 7.5-6 14-24.5 14-24.5"
                  stroke="url(#vg)"
                  strokeWidth="3.25"
                  strokeLinecap="round"
                  fill="none"
                />
                <circle cx="32" cy="47" r="3.25" fill="url(#vg)" />
              </svg>
            </span>
          </span>
          <span className="flex flex-col leading-none">
            <span className="text-[15px] font-semibold tracking-tight text-ink-600">Velora</span>
            <span className="mt-0.5 text-[10px] font-medium uppercase tracking-[0.14em] text-ink-300">
              AI Lab
            </span>
          </span>
        </Link>

        <div className="flex items-center gap-3 text-[12px] text-ink-400">
          {model ? (
            <span className="hidden rounded-full border border-ink-100 bg-white/70 px-3 py-1 sm:inline">
              {model}
            </span>
          ) : null}
          <span
            className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 ${
              backendOk === true
                ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                : backendOk === false
                  ? "border-rose-200 bg-rose-50 text-rose-700"
                  : "border-ink-100 bg-white/70 text-ink-400"
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                backendOk === true
                  ? "bg-emerald-500"
                  : backendOk === false
                    ? "bg-rose-500"
                    : "bg-ink-300 animate-pulse"
              }`}
            />
            {backendOk === true ? "API online" : backendOk === false ? "API offline" : "Checking…"}
          </span>
        </div>
      </div>
    </header>
  );
}
