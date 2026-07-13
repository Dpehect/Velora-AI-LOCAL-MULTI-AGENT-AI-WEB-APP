import type { NextConfig } from "next";

/**
 * Frontend-only Next config.
 * Does not bundle or import the Python backend.
 */
const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Allow images/assets from same origin; API is external (NEXT_PUBLIC_API_URL).
  poweredByHeader: false,
};

export default nextConfig;
