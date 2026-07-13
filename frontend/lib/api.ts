/**
 * Backend API client helpers (scaffold).
 * Set NEXT_PUBLIC_API_URL to the Fly.io backend URL in production.
 */

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";
