import type { Config } from "tailwindcss";

export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        canvas: "#FAFAFA",
        ink: {
          50: "#F5F5F7",
          100: "#E8E8ED",
          200: "#D2D2D7",
          300: "#A1A1A6",
          400: "#6E6E73",
          500: "#424245",
          600: "#1D1D1F",
        },
        accent: {
          DEFAULT: "#6366F1",
          soft: "#818CF8",
          muted: "#EEF2FF",
          deep: "#4F46E5",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 4px 24px -4px rgba(0,0,0,0.06), 0 2px 8px -2px rgba(0,0,0,0.04)",
        btn: "0 8px 24px -6px rgba(99,102,241,0.42)",
      },
    },
  },
  plugins: [],
} satisfies Config;
