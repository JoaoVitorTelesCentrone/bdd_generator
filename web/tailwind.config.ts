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
          bg:        "#C8CEC8",
          surface:   "#D3D9D3",
          surface2:  "#CBCFCB",
          primary:   "#1a2c21",
          secondary: "#a3fb73",
          hover:     "#8ee05a",
          mid:       "#4D6B57",
          muted:     "#5E7A6B",
          dim:       "#7A9487",
          border:    "#B8C4B8",
          border2:   "#C2CAC2",
        },
      },
      fontFamily: {
        sans:    ["'DM Sans'", "system-ui", "sans-serif"],
        code:    ["'JetBrains Mono'", "'Consolas'", "monospace"],
      },
      animation: {
        "fade-in":      "fadeIn 0.3s ease-in-out",
        "slide-up":     "slideUp 0.4s ease-out",
        "progress":     "progress 1.5s ease-in-out infinite",
        "cursor-blink": "cursorBlink 1.1s step-start infinite",
        "pulse-accent": "pulseAccent 2s ease-in-out infinite",
      },
      keyframes: {
        fadeIn:      { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        slideUp:     { "0%": { opacity: "0", transform: "translateY(8px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
        progress:    { "0%": { width: "0%" }, "50%": { width: "70%" }, "100%": { width: "100%" } },
        cursorBlink: { "0%, 100%": { opacity: "1" }, "50%": { opacity: "0" } },
        pulseAccent: { "0%, 100%": { opacity: "1" }, "50%": { opacity: "0.6" } },
      },
    },
  },
  plugins: [],
};

export default config;
