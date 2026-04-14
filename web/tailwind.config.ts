import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#eef2ff",
          100: "#e0e7ff",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
        },
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      animation: {
        "fade-in":   "fadeIn 0.3s ease-in-out",
        "slide-up":  "slideUp 0.4s ease-out",
        "progress":  "progress 1.5s ease-in-out infinite",
      },
      keyframes: {
        fadeIn:   { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        slideUp:  { "0%": { opacity: "0", transform: "translateY(12px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        progress: { "0%": { width: "0%" }, "50%": { width: "70%" }, "100%": { width: "100%" } },
      },
    },
  },
  plugins: [],
};

export default config;
