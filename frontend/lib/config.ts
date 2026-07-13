/**
 * Frontend runtime config.
 * The only backend coupling: base URL via env.
 */

function normalizeBaseUrl(url: string | undefined): string {
  const raw = (url || "http://127.0.0.1:8000").trim();
  return raw.replace(/\/$/, "");
}

export const config = {
  /** FastAPI backend origin (no path, no trailing slash) */
  apiUrl: normalizeBaseUrl(process.env.NEXT_PUBLIC_API_URL),
  appName: "Velora AI Lab",
} as const;
