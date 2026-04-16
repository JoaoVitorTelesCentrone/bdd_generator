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
        bist: {
          primary:   "#1a2c21",
          secondary: "#a3fb73",
          accent:    "#eef9e8",
          muted:     "#7a9b87",
          surface:   "#243d2c",
          dim:       "#5a7a65",
          hover:     "#8ee05a",
          border:    "rgba(163, 251, 115, 0.18)",
        },
      },
      fontFamily: {
        mono: ["'Consolas'", "'JetBrains Mono'", "ui-monospace", "'Cascadia Code'", "monospace"],
        display: ["'Share Tech Mono'", "'Consolas'", "monospace"],
      },
      animation: {
        "fade-in":       "fadeIn 0.3s ease-in-out",
        "slide-up":      "slideUp 0.4s ease-out",
        "progress":      "progress 1.5s ease-in-out infinite",
        "cursor-blink":  "cursorBlink 1.1s step-start infinite",
        "scan":          "scanLine 3s linear infinite",
        "pulse-lime":    "pulseLime 2s ease-in-out infinite",
      },
      keyframes: {
        fadeIn:     { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        slideUp:    { "0%": { opacity: "0", transform: "translateY(10px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        progress:   { "0%": { width: "0%" }, "50%": { width: "70%" }, "100%": { width: "100%" } },
        cursorBlink:{ "0%, 100%": { opacity: "1" }, "50%": { opacity: "0" } },
        scanLine:   { "0%": { transform: "translateY(-100%)" }, "100%": { transform: "translateY(100vh)" } },
        pulseLime:  { "0%, 100%": { opacity: "1" }, "50%": { opacity: "0.6" } },
      },
    },
  },
  plugins: [],
};

export default config;
